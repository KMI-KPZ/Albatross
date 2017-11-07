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
from bokeh.plotting import curdoc


class DataProcessing():
    
    def __init__(self, layout):
        self.layout = layout
    
   
    
    def sourceToRDF(self):
        """
        Callback generates view on RDF and Eurostats Source Files
        """
        def callback_generate_RDF():
            """
            Callback on button generates RDF from exsiting Source
            """
            # call java
            subprocess.call(['sh', 'Main.sh', '-i', 'sdmx-code/sdmx-code.ttl'], cwd='services/eurostat/parser/')
            # move rdf
            directory = 'data/sandbox/eurostat/data/'
            for filename in os.listdir(directory):
                
                if filename.endswith(".rdf"): 
                    
                    #filename = filename.split('/')[-1]
                    os.rename(os.path.join(directory, filename), os.path.join("data/rdf/eurostats/", filename))
        
        data_table = self.show_rdf_files('ID')
        
        files = self.get_eurostats_source_file_list() 
        rdf_data_table = self.generate_rdf_column_data_source(files)
        button_dl = Button(label="Convert CSV to RDF", button_type="success")
        button_dl.on_click(callback_generate_RDF)
        #layout
        self.layout.children[1] = column([Paragraph(text="Downloaded Sources"),widgetbox(data_table), widgetbox(button_dl)], width=400)
        self.layout.children[2] = column([Paragraph(text="Existing RDF"), widgetbox(rdf_data_table)], width=400)
        
        
    
    def get_eurostats_source_file_list(s): 
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
    
                
    def get_eurostats_file_list(s): 
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
    
    
    def get_eurostats_geojson_list(s):
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
                    file_list[geojson_name]= [i]
        return file_list
    
    
    def generate_rdf_column_data_source(self, files, column_title="ID"):
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
        data_table = DataTable(source=table_source, columns=columns, width=500, height=400, selectable=True)
        return data_table
    
    
    def show_rdf_files(self, column_title="ID"):
        """ 
        Generate data table of existing RDF Files.
    
        :param string column_title: Title of the data table column.
        :return: Data table containing the file IDs.
        """ 
        files = self.get_eurostats_file_list()
        
        data_table = self.generate_rdf_column_data_source(files, column_title=column_title)
        return data_table
    
    
    def rdf_to_geojson(s): 
        """ 
        Callback that generates the list of ready-to-transform-to-GeoJSON RDF files 
        """ 
        data_table = s.show_rdf_files(column_title="RDF ID")
        
        data = {'id': [], 'lvl': []}
        file_list = s.get_eurostats_geojson_list()
        for key, value in file_list.items():
            for i in value:
                data['id'].append(key)
                data['lvl'].append(i)
    
        geojson_table_source = ColumnDataSource(data)
        columns = [TableColumn(field='lvl', title="NUTS Level"),
                   TableColumn(field='id', title="ID")]
        geojson_data_table = DataTable(source=geojson_table_source, columns=columns, width=500, height=400, selectable=True)
        #layout
        s.layout.children[1] = column(widgetbox(data_table), width=500)
        s.layout.children[2] = column(widgetbox(geojson_data_table), width=500)
    
