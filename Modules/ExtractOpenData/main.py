import urllib
import json
import os
import xml.etree.ElementTree
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
        testfile = urllib.URLopener()
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

    
    
def add_to_new_list(attr, old, new):
    global source_download
    columns_d = [TableColumn(field="link", title="Link")]
    #todo: extra function
    if isinstance(new['1d']['indices'][0], int) and new['1d']['indices'][0] is not None:
        ldata = source_download.data
        ldata['link'].append(source.data['link'][new['1d']['indices'][0]])
        source_download = ColumnDataSource(ldata)
        data_table_download = DataTable(source=source_download, columns=columns_d, width=400, height=1000, selectable=True)
        spq_plat.layout.children[2] = column(widgetbox(data_table_download), width=400)
    
    