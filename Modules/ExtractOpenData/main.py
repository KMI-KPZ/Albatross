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
            
            if li.find('nt:title[@language="en"]', namespaces) is not None:
                # title
                title.append(li.find('nt:title[@language="en"]', namespaces).text)
                
            if li.find('nt:downloadLink[@format="tsv"]', namespaces) is not None:
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
    
    data_table = DataTable(source=source, columns=columns, width=700, height=1000, selectable=True)
    source.on_change('selected', add_to_new_list)
    
    
    
    spq_plat.layout.children[1] = column(widgetbox(data_table))
    #print(multiarray)
    #spq_plat.layout.children[2] = widgetbox(multiarray)        

    print('rdy')
    
def add_to_new_list(attr, old, new):
    #todo put it into Columndatasource
    spq_plat.layout.children[2] = column(Div(text=source.data['link'][new['1d']['indices'][0]]))
    
    