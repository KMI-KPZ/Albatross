import urllib
import json
import os
import subprocess
import xml.etree.ElementTree
from bokeh.models import Button
from bokeh.layouts import column, widgetbox, row
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets.tables import TableColumn, DataTable
from bokeh.io import curdoc



global div_block
div_block = []
global link
global title
link = []
title = []

selected_rdf = []
    
EULink = 'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=table_of_contents.xml'

layout = column([column(), column()])


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
    
    data_table = DataTable(source=source, columns=columns, width=500, height=800, selectable=True)
    data_table_download = DataTable(source=source_download, columns=columns_d, width=400, height=800, selectable=True)
    source.on_change('selected', add_to_new_list)
    
    
    layout.children[0] = column(widgetbox(data_table), width=500)
    layout.children[1] = column(widgetbox(data_table_download), width=400)
    curdoc().add_root(layout)
    #print(multiarray)
    #spq_plat.layout.children[2] = widgetbox(multiarray)        

"""
    TODO: List of Endpoint which may used for GeoJSON creation
"""
def listEndpoints():
    print('something takes a part of me')

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
                            
                            filename = link.split('/')[-1]
                            if not os.path.isfile("data/sandbox/eurostat/original-data/" + filename):
                                testfile = urllib.request.urlretrieve(link, "data/sandbox/eurostat/original-data/" + filename)
                                testfile = urllib.request.urlretrieve(link, "data/sandbox/eurostat/tsv/" + filename)
                            #inF = gzip.open("data/sandbox/eurostat/original-data/" + filename, 'rb')
                           # outF = open("data/sandbox/eurostat/raw-data/" + filename[:-3], 'wb')
                           # outF.write( inF.read() )
                           # inF.close()
                           # outF.close() 
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
    
def downloadCSV():
    ET = xml.etree.ElementTree
    e = ET.parse('data/toc.xml').getroot()
    ET.register_namespace('nt', 'urn:eu.europa.ec.eurostat.navtree')
    
    for b in e.findall('nt:branch', namespaces):
        iterateAndDL(b)
    
    
def add_to_new_list(attr, old, new):
    global source_download
    columns_d = [TableColumn(field="link", title="Link")]
    #todo: extra function
    if isinstance(new['1d']['indices'][0], int) and new['1d']['indices'][0] is not None:
        ldata = source_download.data
        ldata['link'].append(source.data['link'][new['1d']['indices'][0]])
        source_download = ColumnDataSource(ldata)
        data_table_download = DataTable(source=source_download, columns=columns_d, width=400, height=800, selectable=True)
        button_dl = Button(label="Download", button_type="success")
        button_dl.on_click(downloadCSV)
        layout.children[1] = column(row(widgetbox(data_table_download), width=400), row(button_dl))
        curdoc().add_root(layout)


def callback_generate_RDF():
    """
    Callback on button generates RDF from exsiting Source
    """
    # call java
    subprocess.call(['sh', 'Main.sh', '-i', 'sdmx-code/sdmx-code.ttl'], cwd='services/eurostat/parser/')
    # move rdf
    directory = 'data/sandbox/eurostat/data/'
    for filename in os.listdir(directory):
        print(filename)
        if filename.endswith(".rdf"): 
            print(os.path.join(directory, filename))
            #filename = filename.split('/')[-1]
            os.rename(os.path.join(directory, filename), os.path.join("data/rdf/eurostats/", filename))


def sourceToRDF():
    """
    Callback generates view on RDF and Eurostats Source Files
    """
    data_table = show_rdf_files()
    layout.children[1] = column(widgetbox(data_table), width=500)
    
    files = get_eurostats_source_file_list() 
    data_table = generate_rdf_column_data_source(files)
    button_dl = Button(label="Convert CSV to RDF", button_type="success")
    button_dl.on_click(callback_generate_RDF)
    layout.children[0] = column([widgetbox(data_table), widgetbox(button_dl)], width=500)
    curdoc().add_root(layout)


def get_eurostats_source_file_list(): 
    """ 
    This function generates the file names for every RDF in the "data/rdf/eurostats" subdirectory. 
 
    :return: a list of dictionaries containing the id and file names of the RDFs found. 
    """ 
    rdf_path_prefix = "data/sandbox/eurostat/tsv" 
    observation_list = [] 
    for file in os.listdir(rdf_path_prefix): 
        observation = {} 
        observation_name = str(os.path.basename(file).split('.')[0]) 
        observation['id'] = observation_name 
        observation['source'] = rdf_path_prefix + file 
        observation_list.append(observation) 
    return observation_list 

            
def get_eurostats_file_list(): 
    """ 
    This function generates the file names for every RDF in the "data/rdf/eurostats" subdirectory. 
 
    :return: a list of dictionaries containing the id and file names of the RDFs found. 
    """ 
    rdf_path_prefix = "data/rdf/eurostats/"
    observation_list = []
    for file in os.listdir(rdf_path_prefix):
        observation = {}
        observation_name = str(os.path.basename(file).split('.')[0])
        observation['id'] = observation_name
        observation_list.append(observation)
    return observation_list


def get_eurostats_geojson_list():
    """
    Generates dictionary of the eurostats geojson files and their NUTS level

    :return: Dirctionary of eurostats ID's and NUTS level that where found in data/geojson/eurostats/nuts_*
    """
    geojson_path_prefix = "data/geojson/eurostats/nuts_"
    file_list = {}
    for i in range(1, 4):
        for file in os.listdir(geojson_path_prefix + str(i)):
            geojson_name = str(os.path.basename(file).split('.')[0])
            if geojson_name in file_list:
                file_list[geojson_name].append(i)
            else:
                file_list[geojson_name] = [i]
    return file_list


def generate_rdf_column_data_source(files, column_title="ID"):
    """
    Generate data table based on files list with ``id``.

    :param List files: List of Dictionaries that contain the key ``id``.
    :param string column_title: Title of the data table column.
    :return: Data table containing the file IDs.
    """
    ids = [tmp_id['id'] for tmp_id in files]
    data = dict(id=ids) 
    table_source = ColumnDataSource(data)
    columns = [TableColumn(field="id", title=column_title)]
    data_table = DataTable(source=table_source, columns=columns, width=500, height=500, selectable=True)
    return data_table


def show_rdf_files(column_title="ID"):
    """ 
    Generate data table of existing RDF Files.

    :param string column_title: Title of the data table column.
    :return: Data table containing the file IDs.
    """ 
    files = get_eurostats_file_list()
    data_table = generate_rdf_column_data_source(files, column_title=column_title)
    return data_table


def rdf_to_geojson(): 
    """ 
    Callback that generates the list of ready-to-transform-to-GeoJSON RDF files 
    """
    converter = RDFToGeoJSON()

    layout.children[1] = column(widgetbox(converter.rdf_table))
    layout.children[2] = column(widgetbox(converter.geojson_table))
    curdoc().add_root(layout)

    # rdf_data_table = show_rdf_files(column_title="RDF ID")
    #
    # button_convert = Button(label="Convert", button_type="success")
    #
    # button_convert.on_click(b.callback)
    #
    # spq_plat.layout.children[1] = column(widgetbox(rdf_data_table), widgetbox(button_convert), width=300)
    #
    # data = {'id': [], 'lvl': []}
    # file_list = get_eurostats_geojson_list()
    # for key, value in file_list.items():
    #     for i in value:
    #         data['id'].append(key)
    #         data['lvl'].append(i)
    #
    # geojson_table_source = ColumnDataSource(data)
    # columns = [TableColumn(field='lvl', title="NUTS Level"),
    #            TableColumn(field='id', title="ID")]
    # geojson_data_table = DataTable(source=geojson_table_source, columns=columns, width=500, height=500, selectable=True)
    # spq_plat.layout.children[2] = column(widgetbox(geojson_data_table), width=500)


