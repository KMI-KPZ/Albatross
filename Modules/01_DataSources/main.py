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
    
    def __init__(self, layout):
        self.layout = layout
        
    """
    TODO: List of Endpoint which may used for GeoJSON creation
    """
    def listEndpoints(s):
        print('something takes a part of me')

            
    def showTOC(s):
        global namespaces, title, link, source, source_download
        title = []
        link = []

        EULink = 'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=table_of_contents.xml'
        data_download = dict(link=[])
        source_download = ColumnDataSource(data_download)
        
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
            global source_download, namespaces, title
            
            def findLinkandDL(r):
                """
                :param element r: eurostats xml element
                """
                global source_download, namespaces
                
                if r.find('nt:children', namespaces):
                    
                    linking = r.find('nt:children', namespaces).findall('nt:leaf', namespaces)
                    if linking and len(linking) > 0:
                        for li in linking:
                            
                            #check exists
                            realLink = li.find('nt:downloadLink[@format="tsv"]', namespaces)
                            if realLink is not None:
                                
                                #check if it is in new List
                                link = li.find('nt:downloadLink[@format="tsv"]', namespaces).text
                                ldata = source_download.data
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
                    Callback function to iterate selection to Download
                """
                
                ET = xml.etree.ElementTree
                e = ET.parse('data/toc.xml').getroot()
                ET.register_namespace('nt', 'urn:eu.europa.ec.eurostat.navtree')
                    
                for b in e.findall('nt:branch', namespaces):
                    iterateAndDL(b)

            columns_d = [TableColumn(field="link", title="Link")]
            
            #todo: extra function
            if isinstance(new['1d']['indices'][0], int) and new['1d']['indices'][0] is not None:
                ldata = source_download.data
                ldata['link'].append(source.data['link'][new['1d']['indices'][0]])
                source_download = ColumnDataSource(ldata)
                data_table_download = DataTable(source=source_download, columns=columns_d, width=400, height=800, selectable=True)
                button_dl = Button(label="Download", button_type="success")
                button_dl.on_click(downloadCSV)
                #layout
                s.layout.children[1] = column(row(widgetbox(data_table_download), width=400), row(button_dl))
                

        
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
        
        columns = [TableColumn(field="title", title="Title"), TableColumn(field="link", title="Linke")]
        columns_d = [TableColumn(field="link", title="Link")]
        
        data_table = DataTable(source=source, columns=columns, width=500, height=800, selectable=True)
        data_table_download = DataTable(source=source_download, columns=columns_d, width=400, height=800, selectable=True)
        source.on_change('selected', add_to_new_list)
        #layout
        s.layout.children[1] = column(widgetbox(data_table), width=500)
        s.layout.children[2] = column(widgetbox(data_table_download), width=400)
        