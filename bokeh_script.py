import geopandas as gpd
import pysal as ps
import math
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper
from bokeh.palettes import Greys256 as palette
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.layouts import widgetbox
from bokeh.models.widgets import Select
from bokeh.tile_providers import WMTSTileSource
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon


# STAMEN_TONER = WMTSTileSource(
#     url='http://tile.stamen.com/toner/{Z}/{X}/{Y}.png',
#     attribution=(
#         'Map tiles by <a href="http://stamen.com">Stamen Design</a>, '
#         'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>.'
#         'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, '
#         'under <a href="http://www.openstreetmap.org/copyright">ODbL</a>'
#     )
# )


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


def produce_column_data(indata):
    raw_data = explode(indata)

    # Transform CRS
    raw_data.crs = {'init': 'epsg:4326'}
    raw_data = raw_data.to_crs({'init': 'epsg:3857'})

    # Get coordinates
    raw_data['x'] = raw_data.apply(get_poly_coords, geom='geometry', coord_type='x', axis=1)
    raw_data['y'] = raw_data.apply(get_poly_coords, geom='geometry', coord_type='y', axis=1)

    # Classify for color mapper
    min_area = math.floor(raw_data['SHAPE_AREA'].min())
    max_area = math.ceil(raw_data['SHAPE_AREA'].max())
    lvls = 21
    step_size = round((max_area - min_area)/lvls)
    breaks = [x for x in range(min_area, max_area, step_size)]
    classifier = ps.User_Defined.make(bins=breaks)
    pt_classif = raw_data[['SHAPE_AREA']].apply(classifier)

    # Rename classifier column
    pt_classif.columns = ['SHAPE_AREA_ud']
    raw_data = raw_data.join(pt_classif)

    # Make a copy, drop the geometry column and create ColumnDataSource
    dataframe = raw_data.drop('geometry', axis=1).copy()
    return ColumnDataSource(dataframe)


# File paths
data = {
    "Level 1": produce_column_data(r"data/nuts_rg_60M_2013_lvl_1.geojson"),
    "Level 2": produce_column_data(r"data/nuts_rg_60M_2013_lvl_2.geojson"),
    "Level 3": produce_column_data(r"data/nuts_rg_60M_2013_lvl_3.geojson")
}
options = [
    "Level 1",
    "Level 2",
    "Level 3"
]

color_mapper = LogColorMapper(palette=palette)


patch_source = ColumnDataSource(data["Level 1"].data)

p = figure(
    width=800,
    height=600,
    title="NUTS Areas",
)
p.title.text_font_size = "25px"
p.title.align = "center"


# Set Tiles
tile_source = WMTSTileSource(
    url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg'
)
p.add_tile(tile_source)

# Plot grid
p.patches('x', 'y', source=patch_source,
          fill_color={'field': 'SHAPE_AREA_ud', 'transform': color_mapper},
          fill_alpha=0.5, line_color="black", line_width=0.3)


def select_on_change(attr, old, new):
    patch_source.data = data[new].data


# define Select
select = Select(title="Nuts Level:", value="Level 1", options=options)
select.on_change("value", select_on_change)


hover = HoverTool()
hover.tooltips = [('NUTS_ID', '@NUTS_ID'), ('Area', '@SHAPE_AREA')]
p.add_tools(hover)

# do some styling
p.toolbar.logo = None
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.axis.visible = None
p.xaxis.major_tick_line_color = None
p.xaxis.minor_tick_line_color = None
p.yaxis.major_tick_line_color = None
p.yaxis.minor_tick_line_color = None


curdoc().add_root(p)
curdoc().add_root(widgetbox(select))
