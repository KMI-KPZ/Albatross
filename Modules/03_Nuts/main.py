import geopandas as gpd
import math
import numpy as np
from bokeh.models import \
    ColumnDataSource, \
    HoverTool, \
    LogColorMapper, \
    LassoSelectTool
from bokeh.models.glyphs import Patches
from bokeh.palettes import Greys256 as palette
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models.ranges import FactorRange
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Select
from bokeh.models import WMTSTileSource
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
import spq_plat

# TODO: neither lasso nor box select work at the moment
# TODO: the bar graph is only a demonstration for the selection


# STAMEN_TONER = WMTSTileSource(
#     url='http://tile.stamen.com/toner/{Z}/{X}/{Y}.png',
#     attribution=(
#         'Map tiles by <a href="http://stamen.com">Stamen Design</a>, '
#         'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>.'
#         'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, '
#         'under <a href="http://www.openstreetmap.org/copyright">ODbL</a>'
#     )
# )

# callback for the level select
def select_on_change(attr, old, new):
    patch_source.data = data[new].data


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

# callback for the tap tool
def tap_callback(attr, old, new):
    new_area_data = {'ID': glyphs.data_source.data["NUTS_ID"][new["1d"]["indices"]],
                     'AREA': glyphs.data_source.data["SHAPE_AREA"][new["1d"]["indices"]]}
    p2.x_range.factors = new_area_data['ID'].tolist()
    area_vbars.data_source.data = ColumnDataSource(new_area_data).data

    colors = []
    xs = []
    ys = []
    for k in new_area_data['ID']:
        color_list = np.random.rand(3) * 255
        color = "#{:02x}{:02x}{:02x}".format(
            int(round(color_list[0])),
            int(round(color_list[1])),
            int(round(color_list[2]))
        )
        rand_y_offset = np.random.rand(200)
        rand_x_offset = np.random.rand(1) * math.pi / 2
        x = np.linspace(0, 4 * math.pi, 200)
        curve = np.sin(x + rand_x_offset) * 3 + rand_y_offset
        colors.append(color)
        xs.append(x.tolist())
        ys.append(curve.tolist())

    new_random = ColumnDataSource({'colors': colors, 'xs': xs, 'ys': ys})
    curve_source.data = new_random.data


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
    breaks = [x for x in range(int(min_area), int(max_area), int(step_size))]
    classifier = ps.User_Defined.make(bins=breaks)
    pt_classif = raw_data[['SHAPE_AREA']].apply(classifier)

    # Rename classifier column
    pt_classif.columns = ['SHAPE_AREA_ud']
    raw_data = raw_data.join(pt_classif)

    # Make a copy, drop the geometry column and create ColumnDataSource
    dataframe = raw_data.drop('geometry', axis=1).copy()
    return ColumnDataSource(dataframe)


def show_data():
    global glyphs
    global p
    global p2
    global area_vbars
    global curve_source
    global data
    global patch_source
    # Data sources
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
    
    # area size plot
    area_data = {'ID': [], 'AREA': []}
    area_source = ColumnDataSource(area_data)
    
    color_mapper = LogColorMapper(palette=palette)
    
    patch_source = ColumnDataSource(data["Level 1"].data)


    # Plot map
    TOOLS = "pan,wheel_zoom,box_zoom,reset,tap"
    p = figure(
        width=800,
        height=600,
        title="NUTS Areas",
        tools=TOOLS
    )
    p.title.text_font_size = "25px"
    p.title.align = "center"
    p.select(LassoSelectTool).select_every_mousemove = False
    
    # Set Tiles
    tile_source = WMTSTileSource(
        url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg'
    )
    p.add_tile(tile_source)
    
    glyphs = p.patches('x', 'y', source=patch_source,
                       fill_color={'field': 'SHAPE_AREA_ud', 'transform': color_mapper},
                       fill_alpha=0.5, line_color="black", line_width=0.3)
    glyphs.nonselection_glyph = Patches(
        fill_alpha=0.2,
        line_width=0.3,
        fill_color={'field': 'SHAPE_AREA_ud', 'transform': color_mapper}
    )
    glyphs.selection_glyph = Patches(
        fill_alpha=0.8,
        line_width=0.8,
        fill_color={'field': 'SHAPE_AREA_ud', 'transform': color_mapper}
    )
    glyphs.hover_glyph = Patches(
        line_width=1,
        fill_color={'field': 'SHAPE_AREA_ud', 'transform': color_mapper}
    )


    # Plot bar graph
    p2 = figure(
        width=800,
        height=200,
        title="Areas",
        x_range=FactorRange()
    )
    area_vbars = p2.vbar(
        x="ID",
        width=0.5,
        bottom=0,
        top="AREA",
        source=area_source
    )
    
    ####################################
    # some random data to draw
    curve_source = ColumnDataSource({'colors': [[]], 'xs': [[]], 'ys': [[]]})
    p3 = figure(width=800, height=200, title="random data")
    p3.multi_line(xs='xs', ys='ys', color='colors', source=curve_source)
    ####################################
    
    # define Select
    select = Select(title="Nuts Level:", value="Level 1", options=options)
    select.on_change("value", select_on_change)
    
    # setup hover tool
    hover = HoverTool()
    hover.tooltips = [('NUTS_ID', '@NUTS_ID'), ('Area', '@SHAPE_AREA')]
    p.add_tools(hover)

    # set the callback for the tap tool
    glyphs.data_source.on_change('selected', tap_callback)
    
    # do some styling
    p.toolbar.logo = None
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = None
    p.xaxis.major_tick_line_color = None
    p.xaxis.minor_tick_line_color = None
    p.yaxis.major_tick_line_color = None
    p.yaxis.minor_tick_line_color = None
    
    p.min_border = 20
    p2.min_border = 20
    p2.min_border = 20
    
    p2.toolbar.logo = None

    spq_plat.layout.children[1] = row(
        [p, column([p2, p3])]
    )
    spq_plat.layout.children[2] = widgetbox(select) 
    