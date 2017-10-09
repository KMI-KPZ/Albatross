import geopandas as gpd
import pysal as ps
import math
import os
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper
from bokeh.palettes import Plasma256 as palette
from bokeh.plotting import show, output_file, figure
from bokeh.tile_providers import STAMEN_TONER
from bokeh.models import WMTSTileSource
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon


def get_poly_coords(row, geom, coord_type):
    """Returns the coordinates ('x' or 'y') of edges of a Polygon exterior"""

    # Parse the exterior of the coordinate
    exterior = row[geom].exterior

    if coord_type == 'x':
        # Get the x coordinates of the exterior
        return list(exterior.coords.xy[0])
    elif coord_type == 'y':
        # Get the y coordinates of the exterior
        return list(exterior.coords.xy[1])


def get_line_coords(row, geom, coord_type):
    """Returns a list of coordinates ('x' or 'y') of a LineString geometry"""
    if coord_type == 'x':
        return list(row[geom].coords.xy[0])
    elif coord_type == 'y':
        return list(row[geom].coords.xy[1])


def get_point_coords(row, geom, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return row[geom].x
    elif coord_type == 'y':
        return row[geom].y


def explode(indata):
    indf = gpd.GeoDataFrame.from_file(indata)
    outdf = gpd.GeoDataFrame(columns=indf.columns)
    for idx, row in indf.iterrows():
        if type(row.geometry) == Polygon:
            outdf = outdf.append(row, ignore_index=True)
        if type(row.geometry) == MultiPolygon:
            multdf = gpd.GeoDataFrame(columns=indf.columns)
            recs = len(row.geometry)
            multdf = multdf.append([row] * recs, ignore_index=True)
            for geom in range(recs):
                multdf.loc[geom, 'geometry'] = row.geometry[geom]
            outdf = outdf.append(multdf, ignore_index=True)
    return outdf


# File paths
grid_fp = r"data/nuts_rg_60M_2013_lvl_3.geojson"

#integrate new data
grid_fp = os.path.join(os.path.dirname(__file__), 'testfile.geojson')

# Read files
grid = explode(grid_fp)
#grid_ex = explode(grid_test)

# Set and transform CRS
grid.crs = {'init' :'epsg:4326'}
grid = grid.to_crs({'init': 'epsg:3857'})

#grid_ex.crs = {'init' :'epsg:4326'}
#grid_ex = grid_ex.to_crs({'init': 'epsg:3857'})


# Get the x and y coordinates
grid['x'] = grid.apply(get_poly_coords, geom='geometry', coord_type='x', axis=1)
grid['y'] = grid.apply(get_poly_coords, geom='geometry', coord_type='y', axis=1)

#grid_ex['x'] = grid_ex.apply(get_poly_coords, geom='geometry', coord_type='x', axis=1)
#grid_ex['y'] = grid_ex.apply(get_poly_coords, geom='geometry', coord_type='y', axis=1)


# Create color mapper
color_mapper = LogColorMapper(palette=palette)
#min = math.floor(grid['SHAPE_AREA'].min())
#max = math.ceil(grid['SHAPE_AREA'].max())
lvls = 21
#step_size = round((max - min)/lvls)
#breaks = [x for x in range(min, max, step_size)]
#classifier = ps.User_Defined.make(bins=breaks)
#pt_classif = grid[['SHAPE_AREA']].apply(classifier)

#grid_ex = grid_ex.join(pt_classif)


# Make a copy, drop the geometry column and create ColumnDataSource
g_df = grid.drop('geometry', axis=1).copy()
gsource = ColumnDataSource(g_df)

#g_df_ex = grid_ex.drop('geometry', axis=1).copy()
#gsource_ex = ColumnDataSource(g_df_ex)


p = figure(width=800, height=600, title="NUTS LVL 3")
tile_options = {}
tile_options['url'] = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg'
tile_source = WMTSTileSource(**tile_options)
p.add_tile(tile_source)

# Plot grid
p.patches('x', 'y', source=gsource,
          fill_color={'field': 'prop_0', 'transform': color_mapper},
          fill_alpha=0.5, line_color="black", line_width=0.1)

# Plot grid
#p.patches('x', 'y', source=gsource_ex,
 #         fill_color={'field': 'SHAPE_AREA_ud', 'transform': color_mapper},
  #        fill_alpha=0.5, line_color="yellow", line_width=0.1)


hover = HoverTool(tooltips=[
    ("index", "$index"),
    ("(x,y)", "($x, $y)"),
    ("prop2", "@prop_0"),
    ("prop1", "@prop_1"),
])


p.add_tools(hover)


output_file("travel_time_map.html")
show(p)