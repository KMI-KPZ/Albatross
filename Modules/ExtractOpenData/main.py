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
import spq_plat
from numpy.core import multiarray
from bokeh.core.properties import Enum
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets.tables import TableColumn, DataTable
from bokeh.models.widgets.groups import CheckboxGroup
from bokeh.core.enums import enumeration

global div_block
div_block = []
global link
global title
link = []
title = []
    
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
    global div_block
    
    for r in xml.find('nt:children', namespaces).findall('nt:branch', namespaces):
        #div block
        #div_block += '<p>' + r.find('nt:title[@language="en"]', namespaces).text + '</p>'
        #button = Button(label=r.find('nt:title[@language="en"]', namespaces).text)
        #button.on_click(FunctionHandler(callback_iterate(button)))
        if r.find('nt:children', namespaces) is not None:
          #  #find the links
            findXMLLink(r)
            #iterate
            iterateXML(r)
        else:
            findXMLLink(r)


global source_download
data_download = dict(link=[])
source_download = ColumnDataSource(data_download)        

def showTOC():
    global namespaces
    global div_block
    global multiarray
    global title 
    global link
    global source
    
    #load TOC - TODO: load if updated...
    if not os.path.isfile("data/toc.xml"):
        testfile = urllib.request.urlopen()
        testfile.retrieve(EULink, "data/toc.xml")
    ET = xml.etree.ElementTree
    e = ET.parse('data/toc.xml').getroot()
    ET.register_namespace('nt', 'urn:eu.europa.ec.eurostat.navtree')
    namespaces = {'nt': 'urn:eu.europa.ec.eurostat.navtree'} # add more as needed
    for b in e.findall('nt:branch', namespaces):
       
        #div block
        #div_block += '<p>' +b.find('nt:title[@language="en"]', namespaces).text + '</p>'
        iterateXML(b)
    
    data=dict(title=title, link=link)
    source = ColumnDataSource(data)
    
    columns = [TableColumn(field="title", title="Title"), TableColumn(field="link", title="Linke")]
    columns_d = [TableColumn(field="link", title="Link")]
    
    data_table = DataTable(source=source, columns=columns, width=500, height=1000, selectable=True)
    data_table_download = DataTable(source=source_download, columns=columns_d, width=400, height=1000, selectable=True)
    source.on_change('selected', add_to_new_list)
    
    
    spq_plat.layout.children[1] = column(widgetbox(data_table), width=500)
    spq_plat.layout.children[2] = column(widgetbox(data_table_download), width=400)
    #print(multiarray)
    #spq_plat.layout.children[2] = widgetbox(multiarray)        

    print('rdy')
    
def findLinkandDL(r):
    global source_download
    global namespaces
    
    if r.find('nt:children', namespaces):
        child = r.find('nt:children', namespaces)
        linking = child.findall('nt:leaf', namespaces)
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
                            print(link)
                            filename = link.split('/')[-1]
                            if not os.path.isfile("data/sandbox/eurostat/original-data/" + filename):
                                testfile = urllib.request.urlretrieve(link, "data/sandbox/eurostat/original-data/" + filename)
                                testfile = urllib.request.urlretrieve(link, "data/sandbox/eurostat/tsv/" + filename)
                            inF = gzip.open("data/sandbox/eurostat/original-data/" + filename, 'rb')
                            outF = open("data/sandbox/eurostat/raw-data/" + filename[:-3], 'wb')
                            outF.write( inF.read() )
                            inF.close()
                            outF.close() 
                            #only for testing
                            sdmxLink = li.find('nt:downloadLink[@format="sdmx"]', namespaces).text
                            filename = sdmxLink.split('/')[-1]
                            if not os.path.isfile("data/sandbox/eurostat/original-data/" + filename):
                                testfile = urllib.request.urlretrieve(sdmxLink, "data/sandbox/eurostat/original-data/" + filename) 
                            
                      

def iterateAndDL(xmld):
    root = xmld.find('nt:children', namespaces).findall('nt:branch', namespaces)
    
    if root:
        for r in root:
            if r.find('nt:children', namespaces) is not None:
                findLinkandDL(r)
                iterateAndDL(r)
 
def IandD():
    
    ET = xml.etree.ElementTree
    e = ET.parse('data/toc.xml').getroot()
    ET.register_namespace('nt', 'urn:eu.europa.ec.eurostat.navtree')
    
    for b in e.findall('nt:branch', namespaces):
        iterateAndDL(b)
    
    
def downloadCSV():
    IandD()
    
    print('rdy Download')
    
    
def add_to_new_list(attr, old, new):
    global source_download
    columns_d = [TableColumn(field="link", title="Link")]
    #todo: extra function
    if isinstance(new['1d']['indices'][0], int) and new['1d']['indices'][0] is not None:
        ldata = source_download.data
        ldata['link'].append(source.data['link'][new['1d']['indices'][0]])
        source_download = ColumnDataSource(ldata)
        data_table_download = DataTable(source=source_download, columns=columns_d, width=400, height=1000, selectable=True)
        button_dl = Button(label="Download", button_type="success")
        button_dl.on_click(downloadCSV)
        spq_plat.layout.children[2] = column(row(widgetbox(data_table_download), width=400), row(button_dl))


def sourceToRDF():
    subprocess.call(['sh', '../../services/eurostat/parser/Main.sh', '-i', 'sdmx-code/sdmx-code.ttl', ' -l'])
    
    print('je')


def get_eurostats_file_list():
    """
    This function generates the file names for every RDF in the "data/rdf/eurostats" subdirectory.

    :return: a list of dictionaries containing the id and file names of the RDFs found.
    """
    rdf_path_prefix = "data/rdf/eurostats/"
    geojson_path_prefix = "data/geojson/eurostats/"
    observation_list = []
    for file in os.listdir(rdf_path_prefix):
        observation = {}
        observation_name = str(os.path.basename(file).split('.')[0])
        observation['id'] = observation_name
        observation['rdf'] = rdf_path_prefix + file
        observation['geojson'] = {
            'nuts1': geojson_path_prefix + "nuts1_" + observation_name + ".geojson",
            'nuts2': geojson_path_prefix + "nuts2_" + observation_name + ".geojson",
            'nuts3': geojson_path_prefix + "nuts3_" + observation_name + ".geojson"
        }
        observation_list.append(observation)
    return observation_list


def rdf_to_geojson():
    """
    Callback that generates the list of ready-to-transform-to-GeoJSON RDF files
    """
    files = get_eurostats_file_list()
    ids = [id['id'] for id in files]
    data = dict(id=ids)
    source = ColumnDataSource(data)
    columns = [TableColumn(field="id", title="ID")]
    data_table = DataTable(source=source, columns=columns, width=500, height=800, selectable=True)

    spq_plat.layout.children[1] = column(widgetbox(data_table), width=500)