import math
import networkx as nx

from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models.graphs import from_networkx

G = nx.karate_club_graph()

plot = figure(
    title="Network Integration Demonstration",
    x_range=(-1.1, 1.1),
    y_range=(-1.1, 1.1),
    tools="",
    toolbar_location=None
)

graph = from_networkx(G, nx.shell_layout, scale=2, center=(0,0))
plot.renderers.append(graph)

output_file("graph.html")
show(plot)

