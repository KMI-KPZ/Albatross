from bokeh.plotting import figure
from bokeh.models import WMTSTileSource,\
    ColumnDataSource, \
    LogColorMapper, \
    HoverTool, ranges, LabelSet
from bokeh.models.widgets import Select
from bokeh.layouts import column, row
from bokeh.palettes import PuBu
from bokeh.palettes import Inferno256 as palette
from bokeh.models.glyphs import Patches
import os
import numpy as np
import geopandas as gpd
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from bokeh.models.widgets.markups import Paragraph
import xml.etree.ElementTree
import lxml.etree as le



class Nuts:
    
    _selected_year = None
    _years = []
    year_select = Select(title="Years", value=" ", options=[" "])
    
    
    def __init__(self, layout):
        self.lvl_select_options = [" ", "Level 1", "Level 2", "Level 3"]
        eurostats = self.get_eurostats_geojson_list()

        # collect ID by level
        available_ids = {
            "Level 1": [self.get_real_name(k) for k, v in eurostats.items() if 1 in v],
            "Level 2": [ self.get_real_name(k) for k, v in eurostats.items() if 2 in v],
            "Level 3": [self.get_real_name(k) for k, v in eurostats.items() if 3 in v]
        }
        available_ids['Level 1'].append(" ")
        available_ids['Level 2'].append(" ")
        available_ids['Level 3'].append(" ")
        self.id_select = Select(title="ID Select:", value=" ", options=available_ids["Level 1"])
        self.id_select.on_change("value", self.on_dataset_select)
        self.lvl_select = Select(title="Nuts Level:", value=" ", options=self.lvl_select_options)
        self.lvl_select.on_change("value", self.on_lvl_select)
        self.layout = layout

        # Note: this takes a while; maybe it makes sense to load it concurrent
        self.lvl_geodata = {
            "Level 1": self.produce_column_data(r"data/geojson/eurostats/nuts_rg_60M_2013_lvl_1.geojson"),
            "Level 2": self.produce_column_data(r"data/geojson/eurostats/nuts_rg_60M_2013_lvl_2.geojson"),
            "Level 3": self.produce_column_data(r"data/geojson/eurostats/nuts_rg_60M_2013_lvl_3.geojson")
        }

        self.dataset_path_prefix = r"data/geojson/eurostats/"

        # self.current_dataset = gpd.GeoDataFrame.from_file(r"data/geojson/eurostats/nuts_2/trng_lfse_04.geojson")
        self.current_dataset = gpd.GeoDataFrame()
        self.current_map_CDS = ColumnDataSource({'x': [], 'y': [], 'classified': []})
        # self.update_datasource(self.current_map_CDS, self.current_dataset, 'Level 2', 'trng_lfse_04', 10)
        
        
    def get_real_name(self, k):
        """
        @param str k: represents the filename of eurostats
        @return option tuple (value, label)
        """
        label = self.match_file_to_name(k)
        tuple = (k, label)
        return tuple
    
    def match_file_to_name(self, name):
        '''
            getting the real name from xml
            :param str xml: filename
            :return xml title text
        '''
        global namespaces
        
        ET = xml.etree.ElementTree
        e = le.parse('data/toc.xml')
        namespaces = {'nt': 'urn:eu.europa.ec.eurostat.navtree'} # add more as needed
        for node in e.findall('.//nt:downloadLink[@format="tsv"]', namespaces):
            if name in node.text:
                parent = node.find('..', namespaces)
                title = parent.find('nt:title[@language="en"]', namespaces);
        
        return title.text
    
    def on_year_select(self, attr, old, new):
        """
        updatefunction for years
        """
        self._selected_year = new
        self.update_datasource(self.current_map_CDS, self.current_dataset, self.lvl_select.value, self.id_select.value, 10)

    
    def get_selected_year_index(self, observation):
        """
        Return the index for the selected year. will also set the list _years
        :param obersavation: The observation preselection observation[name]
        :return false or id
        """
        
        for id, v in enumerate(observation):
            
            if v['period'] not in self._years:
                self._years.append(v['period'])
            if v['period'] == self._selected_year:
                return id
        
        return False
        

    def update_datasource(self, datasource, dataset, level, observation_name, period):
        """
        Updates the datasource to contain the datasets observations (observation_name and period)
        in the passed NUTS level.
        :param datasource: The ColumnDataSource to update.
        :param dataset: The dataset to get the observations from.
        :param level: The NUTS Level.
        :param observation_name: The name of the observation.
        :param period: The period of interest.
        :return:
        """
        nan_indices = []
        values = []
        units = []
        self._years = []
        for index, nuts_id in enumerate(self.lvl_geodata[level].data['NUTS_ID']):
            raw_indices = dataset.loc[:, 'NUTS_ID'][dataset.loc[:, 'NUTS_ID'] == nuts_id]
            
            raw_index = raw_indices.index[0]
            if 'OBSERVATIONS' in dataset.loc[raw_index, :].keys():
                observations = dataset.loc[raw_index, :]['OBSERVATIONS']
                
                if observations is None:
                    nan_indices.append(index)
                else:
                    # init first year if not set yet
                    if self._selected_year is None:
                        self._selected_year = observations[observation_name][0]['period']
                    year_index = self.get_selected_year_index(observations[observation_name])
                    #if year is set... do it
                    if year_index is not False:
                        values.append(float(observations[observation_name][year_index]['value']))
                        units.append(observations[observation_name][year_index]['unit'])
                    else:
                        nan_indices.append(index)
                
            else:
                nan_indices.append(index)
        
        self._years.sort()
        self.set_new_year_selector()
        
        tmp_data = {}
        for key in self.lvl_geodata[level].data.keys():
            tmp_data[key] = np.delete(self.lvl_geodata[level].data[key], nan_indices)

        tmp_data['observation'] = values
        tmp_data['unit'] = units
        tmp_data['classified'] = self.classifier(values, 20)
        datasource.data = ColumnDataSource(tmp_data).data
    
    def set_new_year_selector(self):
        if self._selected_year is not None:
            self.year_select = Select(title="Year (Period)", value=self._selected_year, options=self._years)
            self.year_select.on_change("value", self.on_year_select)
            
            self.layout.children[1].children[1].children[1].children[0] = self.year_select
            

    @staticmethod
    def classifier(data, num_level):
        """
        Categorizes each element in data into one of the num_level classes.
        The class separation is linear.
        :param data: the list of elements that will be classified.
        :param num_level: number of classes.
        :return: The list of associated classes.
        """
        ud = []
        if len(data) is not 0:
            _data = [float(i) for i in data]
            step_size = round((max(_data) - min(_data)) / num_level)
            breaks = [x for x in range(int(min(_data)), int(max(_data)), int(step_size))]

            for d in _data:
                lvl = 0
                for i, b in enumerate(breaks):
                    if b <= d:
                        lvl = i
                    else:
                        break
                ud.append(lvl)
        return ud

    def on_lvl_select(self, attr, old, new):
        """
        Callback for ``self.lvl_select``. The method re-searches the available geojson's and sets
        the options of ``self.id_select`` to the newly selected level, while trying to remain in the
        same dataset. If the dataset is not in the selected NUTS level, the selected and displayed
        dataset is changed.

        This method triggers a redraw of the map and the observation plot.

        :param attr: attribute that triggered this callback
        :param old: the old value of the attribute
        :param new: the new value of the attribute
        """
        eurostats = self.get_eurostats_geojson_list()

        # collect ID by level
        available_ids = {
            "Level 1": [self.get_real_name(k) for k, v in eurostats.items() if 1 in v],
            "Level 2": [self.get_real_name(k) for k, v in eurostats.items() if 2 in v],
            "Level 3": [self.get_real_name(k) for k, v in eurostats.items() if 3 in v]
        }
        old_selection = self.id_select.value
        self.id_select.options = available_ids[new]
        if old_selection in available_ids[new]:
            self.id_select.value=old_selection

        self.current_dataset = gpd.GeoDataFrame.from_file(
            self.dataset_path_prefix + "nuts_" + new[-1] + "/" + self.id_select.value + ".geojson")
        self.update_datasource(self.current_map_CDS, self.current_dataset, new, self.id_select.value, 10)

    def on_dataset_select(self, attr, old, new):
        self.current_dataset = gpd.GeoDataFrame.from_file(
            self.dataset_path_prefix + "nuts_" + self.lvl_select.value[-1] + "/" + new + ".geojson")
        self.update_datasource(self.current_map_CDS, self.current_dataset, self.lvl_select.value, new, 10)

    @staticmethod
    def get_poly_coordinates(line, geom, coord_type):
        """
        Returns the coordinates ('x' or 'y') of edges of a Polygon exterior.

        :param line: The current line to extract coordinates from.
        :param geom: The geometry key in the line.
        :param coord_type: either 'x' or 'y'.
        :return: x or y values of the polygon edges.
        """

        # Parse the exterior of the coordinate
        exterior = line[geom].exterior

        if coord_type == 'x':
            # Get the x coordinates of the exterior
            return list(exterior.coords.xy[0])
        elif coord_type == 'y':
            # Get the y coordinates of the exterior
            return list(exterior.coords.xy[1])

    @staticmethod
    def explode(input_data):
        """
        Extracts geometry from the geojson passed by input_data.
        The types of geometry that are extracted are Polygon and MultiPolygon.

        :param input_data: Path to the geojson
        :return: Dataframe with the geometry.
        """
        input_dataframe = gpd.GeoDataFrame.from_file(input_data)
        output_dataframe = gpd.GeoDataFrame(columns=input_dataframe.columns)
        for idx, row in input_dataframe.iterrows():
            if type(row.geometry) == Polygon:
                output_dataframe = output_dataframe.append(row, ignore_index=True)
            if type(row.geometry) == MultiPolygon:
                multdf = gpd.GeoDataFrame(columns=input_dataframe.columns)
                recs = len(row.geometry)
                multdf = multdf.append([row] * recs, ignore_index=True)
                for geom in range(recs):
                    multdf.loc[geom, 'geometry'] = row.geometry[geom]
                output_dataframe = output_dataframe.append(multdf, ignore_index=True)
        return output_dataframe

    @staticmethod
    def get_eurostats_geojson_list():
        """
        Generates dictionary of the eurostats geojson files and their NUTS level
        example: {'aei_pr_soiler': [1, 2, 3], 'trng_lfse_04': [1, 2]}

        :return: Dictionary of eurostats ID's and NUTS level that where found in data/geojson/eurostats/nuts_*
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

    def produce_column_data(self, input_data):
        """
        Generates a ColumnDataSource from the geojson path passed by input_data containing
        the coordinates for patches to draw on a map.
        
        :param input_data: Path to a geojson.
        :return: ColumnDataSource containing the coordinates for patches to draw on a map.
        """
        raw_data = self.explode(input_data)

        # Transform CRS
        raw_data.crs = {'init': 'epsg:4326'}
        raw_data = raw_data.to_crs({'init': 'epsg:3857'})

        # Get coordinates
        raw_data['x'] = raw_data.apply(self.get_poly_coordinates, geom='geometry', coord_type='x', axis=1)
        raw_data['y'] = raw_data.apply(self.get_poly_coordinates, geom='geometry', coord_type='y', axis=1)

        dataframe = raw_data.drop('geometry', axis=1).copy()
        return ColumnDataSource(dataframe)
    
    def tap_callback(self, attr, old, new):
        
        new_data = {}
        new_data['observation'] = [0]
        new_data['NUTS_ID']  = ['0']
        new_data['unit'] = [' ']
        old_data = self.current_map_CDS.data
        
        for indices in new["1d"]["indices"]:
            
            new_data['observation'].append(old_data['observation'][indices])
            new_data['unit'].append(old_data['unit'][indices])
            new_data['NUTS_ID'].append(old_data['NUTS_ID'][indices])
        
        testdata_source = ColumnDataSource(new_data)
        # dont work with to large datasets
        x_label = "Region"
        y_label = "Selected Indicator in {}".format(new_data['unit'][1])
        title = "Visualisation"
        p2 = figure(plot_width=500, plot_height=300, tools="save",
        x_axis_label = x_label,
        y_axis_label = y_label,
        title=title,
        x_minor_ticks=2,
        x_range = testdata_source.data["NUTS_ID"],
        y_range= ranges.Range1d(start=min(testdata_source.data['observation']),end=max(testdata_source.data['observation'])))
        
        labels = LabelSet(x='NUTS_ID', y='observation', text='observation', level='glyph',
        x_offset=-13.5, y_offset=0, source=testdata_source, render_mode='canvas')
        p2.vbar(source=testdata_source,x='NUTS_ID',top='observation',bottom=0,width=0.3,color=PuBu[7][2])
        p2.toolbar.logo = None

        self.layout.children[2] = column(p2)

    def show_data(self):
        """
        Setup plots and commit them into the layout.
        """
        # Plot map
        tools = "pan,wheel_zoom,box_zoom,reset,tap"
        p = figure(
            width=800,
            height=600,
            title="",
            tools=tools,
            x_range=(-2.45*10**6, 5.12*10**6),
            y_range=( 3.73*10**6, 1.13*10**7)
        )
        p.title.text_font_size = "25px"
        p.title.align = "center"
        p.toolbar.logo = None

        # Set Tiles
        tile_source = WMTSTileSource(
            url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg'
        )
        p.add_tile(tile_source)
        p.axis.visible = False

        #print(self.lvl_geodata['Level 3'].data)

        color_mapper = LogColorMapper(palette=palette)
        glyphs = p.patches(
            'x', 'y', source=self.current_map_CDS,
            fill_color={'field': 'classified', 'transform': color_mapper},
            fill_alpha=0.5,
            line_color="black",
            line_width=0.3
        )
        glyphs.nonselection_glyph = Patches(
            fill_alpha=0.2,
            line_width=0.3,
            fill_color={'field': 'classified', 'transform': color_mapper}
        )
        glyphs.selection_glyph = Patches(
            fill_alpha=0.8,
            line_width=0.8,
            fill_color={'field': 'classified', 'transform': color_mapper}
        )
        glyphs.hover_glyph = Patches(
            line_width=1,
            fill_color={'field': 'classified', 'transform': color_mapper}
        )
         # set the callback for the tap tool
        glyphs.data_source.on_change('selected', self.tap_callback)
        
        hover = HoverTool()
        hover.tooltips = [('NUTS_ID', '@NUTS_ID'), ('aei_pr_soiler', '@observation')]
        p.add_tools(hover)

        
        p2 = Paragraph(text="No data selected. Please select region.")
        
        self.layout.children[1] = column([row(self.id_select),row(self.lvl_select, self.year_select), p])
        self.layout.children[2] = column(p2)
        self.set_new_year_selector()
        