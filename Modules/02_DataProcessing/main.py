import urllib
import json
import copy
import rdflib as rdf
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
    
   
    
    def sourceToRDF(s):
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
                    
                    # filename = filename.split('/')[-1]
                    os.rename(os.path.join(directory, filename), os.path.join("data/rdf/eurostats/", filename))
        
        data_table = s.show_rdf_files('ID')
        
        files = s.get_eurostats_source_file_list() 
        rdf_data_table = s.generate_rdf_column_data_source(files)
        button_dl = Button(label="Convert CSV to RDF", button_type="success")
        button_dl.on_click(callback_generate_RDF)
        #layout
        s.layout.children[1] = column([widgetbox(data_table), widgetbox(button_dl)], width=500)
        s.layout.children[2] = column(widgetbox(rdf_data_table), width=500)
        
        
    
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
    
    
    def generate_rdf_column_data_source(s, files, column_title="ID"):
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
        data_table = DataTable(source=table_source, columns=columns, width=500, height=800, selectable=True)
        return data_table
    
    
    def show_rdf_files(s, column_title="ID"):
        """ 
        Generate data table of existing RDF Files.
    
        :param string column_title: Title of the data table column.
        :return: Data table containing the file IDs.
        """ 
        files = s.get_eurostats_file_list()
        
        data_table = s.generate_rdf_column_data_source(files, column_title=column_title)
        return data_table
    
    
    def rdf_to_geojson(s): 
        """ 
        Callback that generates the list of ready-to-transform-to-GeoJSON RDF files 
        """
        converter = RDFToGeoJSON(s.layout)

        convert_button = Button(label="Convert to GeoJSON", button_type="success")
        convert_button.on_click(converter.transform)

        s.layout.children[1] = column(widgetbox(converter.rdf_table), convert_button)
        # s.layout.children[2] = column(converter.geojson_table)
    

class RDFToGeoJSON:
    def __init__(self, layout):
        self._layout = layout
        self._selected = []
        self._file_list = self._get_eurostats()

        self._rdf_table_source = ColumnDataSource(dict(id=[f['id'] for f in self._file_list]))
        self._rdf_table_source.on_change('selected', self._on_select)
        rdf_table_columns = [TableColumn(field='id', title='RDF ID')]
        self.rdf_table = DataTable(
            source=self._rdf_table_source,
            columns=rdf_table_columns,
            width=300,
            height=500,
            selectable=True
        )

        geojson_data = {'id': [], 'lvl': []}
        for file in self._file_list:
            if file['geojson']['nuts1']['exists']:
                geojson_data['id'].append(file['id'])
                geojson_data['lvl'].append(1)

            if file['geojson']['nuts2']['exists']:
                geojson_data['id'].append(file['id'])
                geojson_data['lvl'].append(2)

            if file['geojson']['nuts3']['exists']:
                geojson_data['id'].append(file['id'])
                geojson_data['lvl'].append(3)
        self._geojson_table_source = ColumnDataSource(geojson_data)
        geojson_table_columns = [
            TableColumn(field='lvl', title='NUTS Level'),
            TableColumn(field='id',  title='ID')
        ]
        self.geojson_table = DataTable(
            source=self._geojson_table_source,
            columns=geojson_table_columns,
            width=300,
            height=500,
            selectable=True
        )
        convert_button = Button(label="Convert to GeoJSON", button_type="success")
        convert_button.on_click(self.transform)
        self._layout.children[1] = column(widgetbox(self.rdf_table), convert_button)
        self._layout.children[2] = column(self.geojson_table)

    def _on_select(self, attr, old, new):
        self._selected = [self._file_list[index] for index in new['1d']['indices']]

    def transform(self):
        print("converting")
        for f in self._selected:
            print(".")
            f['results'] = self._extract_observations(f['rdf'])

        print("writing")
        self._write_geojson(self._selected)
        print("done converting")

        self._file_list = self._get_eurostats()
        geojson_data = {'id': [], 'lvl': []}
        for file in self._file_list:
            if file['geojson']['nuts1']['exists']:
                geojson_data['id'].append(file['id'])
                geojson_data['lvl'].append(1)

            if file['geojson']['nuts2']['exists']:
                geojson_data['id'].append(file['id'])
                geojson_data['lvl'].append(2)

            if file['geojson']['nuts3']['exists']:
                geojson_data['id'].append(file['id'])
                geojson_data['lvl'].append(3)
        self._geojson_table_source = ColumnDataSource(geojson_data)
        geojson_table_columns = [
            TableColumn(field='lvl', title='NUTS Level'),
            TableColumn(field='id', title='ID')
        ]
        self.geojson_table = DataTable(
            source=self._geojson_table_source,
            columns=geojson_table_columns,
            width=300,
            height=500,
            selectable=True
        )
        self._layout.children[2] = column(self.geojson_table)

    def _get_eurostats(self):
        """
        This function generates the file names for every RDF in the "data/rdf/eurostats" subdirectory.

        :return: A list of dictionaries containing the id and file names of the RDFs found.
        """
        rdf_path_prefix = "data/rdf/eurostats/"
        geojson_path_prefix = "data/geojson/eurostats/"
        observation_list = []

        nuts_files = [
            [str(os.path.basename(file).split('.')[0]) for file in os.listdir(geojson_path_prefix + "nuts_1/")],
            [str(os.path.basename(file).split('.')[0]) for file in os.listdir(geojson_path_prefix + "nuts_2/")],
            [str(os.path.basename(file).split('.')[0]) for file in os.listdir(geojson_path_prefix + "nuts_3/")]
        ]

        for file in os.listdir(rdf_path_prefix):
            observation = {}
            observation_name = str(os.path.basename(file).split('.')[0])
            observation['id'] = observation_name
            observation['rdf'] = rdf_path_prefix + file
            observation['geojson'] = {
                'nuts1': {'path': geojson_path_prefix + "nuts_1/" + observation_name + ".geojson",
                          'exists': observation_name in nuts_files[0]},
                'nuts2': {'path': geojson_path_prefix + "nuts_2/" + observation_name + ".geojson",
                          'exists': observation_name in nuts_files[1]},
                'nuts3': {'path': geojson_path_prefix + "nuts_3/" + observation_name + ".geojson",
                          'exists': observation_name in nuts_files[2]},
            }
            observation_list.append(observation)
        return observation_list

    def _extract_observations(self, file):
        g = rdf.Graph()
        g.parse(file, format="xml")

        return g.query("""
            prefix obs: <http://purl.org/linked-data/sdmx/2009/measure#>
            prefix prop: <http://eurostat.linked-statistics.org/property#>
            prefix qb: <http://purl.org/linked-data/cube#>
            prefix sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>

            select distinct ?designation ?time ?value ?unit
            where {
                ?observation a qb:Observation.
                ?observation prop:geo ?designation.
                ?observation prop:unit ?unit.
                ?observation sdmx-dimension:timePeriod ?time.
                ?observation obs:obsValue ?value.
            }
        """)

    def _write_geojson(self, file_list):

        with open('data/geojson/eurostats/nuts_rg_60M_2013_lvl_3.geojson') as f:
            nuts3 = json.load(f)
        with open('data/geojson/eurostats/nuts_rg_60M_2013_lvl_2.geojson') as f:
            nuts2 = json.load(f)
        with open('data/geojson/eurostats/nuts_rg_60M_2013_lvl_1.geojson') as f:
            nuts1 = json.load(f)

        nuts = [nuts1, nuts2, nuts3]

        for file in file_list:
            geojson = copy.deepcopy(nuts)
            self._process_file(file, geojson)

            for lvl in range(0, len(geojson)):
                with open(file['geojson']['nuts{}'.format(lvl + 1)]['path'], 'w') as outfile:
                    json.dump(geojson[lvl], fp=outfile, indent=4)

    def _process_file(self, file, nuts):
        for row in file['results']:
            # recover uncluttered information from the sparql result
            geo = row[0].split('#')[1]
            time = row[1]
            value = row[2]
            unit = row[3].split('#')[1]

            # search for the NUTS_ID (geo) in the NUTS level 1 to 3
            index = -1
            nuts_lvl = -1
            found = False
            while not found:
                index += 1
                done = []
                # prepare break condition
                for lvl in range(0, len(nuts)):
                    done.append(False)

                # check if the ID matches in any of the NUTS levels
                for lvl in range(0, len(nuts)):
                    if index < len(nuts[lvl]['features']):
                        if nuts[lvl]['features'][index]['properties']['NUTS_ID'] == geo:
                            nuts_lvl = lvl
                            found = True
                            break
                    else:
                        done[lvl] = True
                if all(done):
                    break

            if nuts_lvl != -1:
                observation = {
                    'period': time,
                    'unit': unit,
                    'value': value
                }

                # check if any of the nested elements in the JSON already exist
                if 'OBSERVATIONS' in nuts[nuts_lvl]['features'][index]['properties']:
                    if file['id'] in nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS']:
                        duplicate = False
                        for observations in nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'][file['id']]:
                            if observations['period'] == observation['period']:
                                duplicate = True
                                break
                        if not duplicate:
                            nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'][file['id']].append(
                                observation)
                    else:
                        nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'][file['id']] = [observation]
                else:
                    nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'] = {
                        file['id']: [observation]
                    }
