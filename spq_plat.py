from bokeh import events
from bokeh.layouts import column, widgetbox, row
from bokeh.models import Button, CustomJS
from bokeh.palettes import RdYlBu3
from bokeh.models.widgets import Select, TextInput, Div
from bokeh.plotting import figure, curdoc, reset_output

div_menu = Div()
p = figure()
layout = row([column(div_menu), column(p), column()])
curdoc().add_root(layout)

    
