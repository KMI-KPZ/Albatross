import urllib
import json
import os
import subprocess
import xml.etree.ElementTree
import lxml.etree as le
import gzip
from lxml import etree
from bokeh.application.handlers import FunctionHandler
from functools import partial
from html5lib.constants import namespaces
from bokeh.models import Button, CustomJS, Div, MultiSelect, Paragraph
from bokeh.layouts import column, widgetbox, row
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets.tables import TableColumn, DataTable

class DataSources():
    
    _source_to_download = ColumnDataSource(dict(link=[], title=[]))
    _source_download = ColumnDataSource(dict(link=[], title=[]))
    _p_new = Paragraph(text="Online Available Data")
    _p_to_dl = Paragraph(text="Selected for Download")
    _p_dl = Paragraph(text="Downloaded Datasets")
    _general_columns = [TableColumn(field="title", title="Title"), TableColumn(field="link", title="Link")]
    
    def __init__(self, layout):
        self.layout = layout
        
        # layout texts
    
            
    def showTOC(self):
        global namespaces, title, link, source
        title = []
        link = []
        
        EULink = 'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=table_of_contents.xml'
        
        
        def findXMLLink(r):
            global link
            global title
            
            if r.find('nt:children', namespaces).findall('nt:leaf', namespaces) is not None:
                for li in r.find('nt:children', namespaces).findall('nt:leaf', namespaces):
                    
                    if li.find('nt:title[@language="en"]', namespaces) is not None and li.find('nt:downloadLink[@format="tsv"]', namespaces) is not None:
                        # title
                        title.append(li.find('nt:title[@language="en"]', namespaces).text)
                        # link
                        link.append(li.find('nt:downloadLink[@format="tsv"]', namespaces).text)
        
        
        def iterateXML(xml):
            """
                Iterate the XML (all children) and extract the Links
                Links and Title will be saved in global vars link and title
                :param element xml: and XML Element (xml.etree.ElementTree)    
            """                        
            for r in xml.find('nt:children', namespaces).findall('nt:branch', namespaces):
                if r.find('nt:children', namespaces) is not None:
                  #  #find the links
                    findXMLLink(r)
                    #iterate
                    iterateXML(r)
                else:
                    findXMLLink(r)

        
        def add_to_new_list(attr, old, new):
            """
                Callback to add a new item to download list
            """
            global namespaces, title
            
            def findLinkandDL(r):
                """
                :param element r: eurostats xml element
                """
                global namespaces
                
                if r.find('nt:children', namespaces):
                    
                    linking = r.find('nt:children', namespaces).findall('nt:leaf', namespaces)
                    if linking and len(linking) > 0:
                        for li in linking:
                            
                            #check exists
                            realLink = li.find('nt:downloadLink[@format="tsv"]', namespaces)
                            if realLink is not None:
                                
                                #check if it is in new List
                                link = li.find('nt:downloadLink[@format="tsv"]', namespaces).text
                                ldata = self._source_to_download.data
                                ldataI = ldata['link']
                                #download
                                for check in ldataI:
                                    
                                    if(check == link):
                                    
                                        filename = link.split('/')[-1]
                                        if not os.path.isfile("data/sandbox/eurostat/original-data/" + filename):
                                            testfile = urllib.request.urlretrieve(link, "data/sandbox/eurostat/original-data/" + filename)
                                            testfile = urllib.request.urlretrieve(link, "data/sandbox/eurostat/tsv/" + filename)
                                
                                        sdmxLink = li.find('nt:downloadLink[@format="sdmx"]', namespaces).text
                                        filename = sdmxLink.split('/')[-1]
                                        if not os.path.isfile("data/sandbox/eurostat/original-data/" + filename):
                                            testfile = urllib.request.urlretrieve(sdmxLink, "data/sandbox/eurostat/original-data/" + filename) 
                                        
                                        print('Sucessfull Download')
            
            def iterateAndDL(xmld):
                
                """
                    loop xml to find and download links
                    :param element xmld: Eurostats TOC XML Element
                """
                root = xmld.find('nt:children', namespaces).findall('nt:branch', namespaces)
                    
                if root:
                    for r in root:
                        if r.find('nt:children', namespaces) is not None:
                            findLinkandDL(r)
                            iterateAndDL(r)

            
            def downloadCSV():
                """
                    Callback function to iterate selection to Download and set new view
                """
                
                ET = xml.etree.ElementTree
                e = ET.parse('data/toc.xml').getroot()
                for b in e.findall('nt:branch', namespaces):
                    iterateAndDL(b)
                #reset tables
                #self._source_download = ColumnDataSource(get_eurostats_source_file_list(self))
                self._source_to_download = ColumnDataSource(dict(link=[], title=[]))
        
                #data_table_download = DataTable(source=self._source_download, columns=self._general_columns, width=400, height=400, selectable=True)
                data_table_to_download = DataTable(source=self._source_to_download, columns=self._general_columns, width=400, height=400)
                #layout
                self.layout.children[2] = column(row(self._p_to_dl), widgetbox(data_table_to_download))


            #todo: extra function
            if isinstance(new['1d']['indices'][0], int) and new['1d']['indices'][0] is not None:
                ldata = self._source_to_download.data
                ldata['link'].append(source.data['link'][new['1d']['indices'][0]])
                ldata['title'].append(source.data['title'][new['1d']['indices'][0]])
                
                self._source_to_download = ColumnDataSource(ldata)
                #data_table_download = DataTable(source=self._source_download, columns=self._general_columns, width=400, height=400, selectable=True)
                data_table_to_download = DataTable(source=self._source_to_download, columns=self._general_columns, width=400, height=400)
        
                button_dl = Button(label="Download", button_type="success")
                button_dl.on_click(downloadCSV)
                
                #layout
                lyr = column(self._p_to_dl, widgetbox(data_table_to_download), button_dl)
                
                self.layout.children[2] = lyr
            
                
        def get_eurostats_source_file_list(self): 
            """ 
            This function generates the file names for every RDF in the "data/rdf/eurostats" subdirectory. 
         
            :return: a list of dictionaries containing the id and file names of the RDFs found. 
            """ 
            rdf_path_prefix = "data/sandbox/eurostat/tsv" 
            observation_list = [] 
            titles = []
            
            for file in os.listdir(rdf_path_prefix): 
                observation_name = str(os.path.basename(file).split('.')[0]) 
                observation_list.append(observation_name)
                titles.append(self.match_file_to_name(observation_name))
                                
            return dict(link=observation_list, title=titles) 
        
            
        #load TOC - TODO: load if updated...
        if not os.path.isfile("data/toc.xml"):
            testfile = urllib.request.urlopen()
            testfile.retrieve(EULink, "data/toc.xml")
        ET = xml.etree.ElementTree
        e = ET.parse('data/toc.xml').getroot()
        ET.register_namespace('nt', 'urn:eu.europa.ec.eurostat.navtree')
        namespaces = {'nt': 'urn:eu.europa.ec.eurostat.navtree'} # add more as needed
        
        for b in e.findall('nt:branch', namespaces):
            iterateXML(b)
        
        data=dict(title=title, link=link)
        source = ColumnDataSource(data)
        #self._source_download = ColumnDataSource(get_eurostats_source_file_list(self))
        self._source_to_download = ColumnDataSource(dict(link=[], title=[]))
        
        data_table = DataTable(source=source, columns=self._general_columns, width=500, height=600, selectable=True)
        #data_table_download = DataTable(source=self._source_download, columns=self._general_columns, width=400, height=400, selectable=True)
        data_table_to_download = DataTable(source=self._source_to_download, columns=self._general_columns, width=400, height=400)
        source.on_change('selected', add_to_new_list)
        
        #layout
        
        second_layer = [row(self._p_to_dl), row(widgetbox(data_table_to_download))]
        
        self.layout.children[1] = column(row(self._p_new), row(widgetbox(data_table), width=500))
        self.layout.children[2] = column(second_layer, width=400)
        
    def match_file_to_name(self, name):
        '''
        
        '''
        global namespaces
        
        ET = xml.etree.ElementTree
        e = le.parse('data/toc.xml')
        ET.register_namespace('nt', 'urn:eu.europa.ec.eurostat.navtree')
        
        
        for node in e.findall('.//nt:downloadLink[@format="tsv"]', namespaces):
            if name in node.text:
                parent = node.find('..', namespaces)
                title = parent.find('nt:title[@language="en"]', namespaces);
        
        return title.text