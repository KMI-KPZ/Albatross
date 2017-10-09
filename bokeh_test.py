import os
import geopandas as gpd
import matplotlib.pyplot as plt

from bokeh.plotting import figure, save
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper
from bokeh.palettes import RdYlBu11 as palette



# Filepaths
#grid_fp = os.path.join(os.path.dirname(__file__), 'data/TravelTimes_to_5975375_RailwayStation.shp')
grid_fp = os.path.join(os.path.dirname(__file__), 'data/nuts_rg_60M_2013_lvl_3.geojson')
roads_fp = os.path.join(os.path.dirname(__file__), 'data/roads.shp') 
metro_fp = os.path.join(os.path.dirname(__file__), 'data/metro.shp')

# Read files
grid = gpd.read_file(grid_fp)
roads = gpd.read_file(roads_fp)
metro = gpd.read_file(metro_fp)

# Get the CRS of the grid
gridCRS = grid.crs

# create color_mapper
color_mapper = LogColorMapper(palette=palette)

# Reproject geometries using the crs of travel time grid
roads['geometry'] = roads['geometry'].to_crs(crs=gridCRS)
metro['geometry'] = metro['geometry'].to_crs(crs=gridCRS)

def getPolyCoords(row, geom, coord_type):
    """Returns the coordinates ('x' or 'y') of edges of a Polygon exterior"""
    
    # Parse the exterior of the coordinate
    # Test .. need to apply mulitpolygons
    if hasattr(row[geom], 'exterior'):
        exterior = row[geom].exterior
        if coord_type == 'x':
            # Get the x coordinates of the exterior
            return list( exterior.coords.xy[0] )
        elif coord_type == 'y':
             # Get the y coordinates of the exterior
            return list( exterior.coords.xy[1] )
    
# Get the Polygon x and y coordinates
grid['x'] = grid.apply(getPolyCoords, geom='geometry', coord_type='x', axis=1)
grid['y'] = grid.apply(getPolyCoords, geom='geometry', coord_type='y', axis=1)

g_df = grid.drop('geometry', axis=1).copy()
print g_df
gsource = ColumnDataSource(g_df)
p = figure(title="Test")

# Plot grid
print gsource
p.patches('x', 'y', source=gsource,
          fill_color={'field': 'STAT_LEVL_', 'transform': color_mapper},
          fill_alpha=1.0, line_color="black", line_width=0.05)
print p;

# Visualize the travel time into 9 classes using "Quantiles" classification scheme
# Add also a little bit of transparency with `alpha` parameter
# (ranges from 0 to 1 where 0 is fully transparent and 1 has no transparency)
#my_map = grid.plot(
 #  # column="car_r_t",
  #  linewidth=0.03,
#    cmap="Reds",
  #  scheme="quantiles",
  #  k=9,
  #  alpha=0.9
#)

# Add roads on top of the grid
# (use ax parameter to define the map on top of which the second items are plotted)
#roads.plot(
#    ax=my_map,
#    color="grey",
#    linewidth=1.5
#)

# Add metro on top of the previous map
#metro.plot(
#    ax=my_map,
#    color="red",
#    linewidth=2.5
#)

# Remove the empty white-space around the axes
#plt.tight_layout()

# Save the figure as png file with resolution of 300 dpi
#outfp = os.path.join(os.path.dirname(__file__), 'static_map.png')
#plt.savefig(outfp, dpi=800)

#use HTML output
outfp = os.path.join(os.path.dirname(__file__), 'static_map.html')
save(p, outfp)