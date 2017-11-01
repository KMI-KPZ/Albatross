from bokeh import events
from bokeh.layouts import column, widgetbox, row
from bokeh.models import Button, CustomJS
from bokeh.palettes import RdYlBu3
from bokeh.models.widgets import Select, TextInput, Div
from bokeh.plotting import figure, curdoc, reset_output
from bokeh.io.doc import set_curdoc

div_menu = Div()
p = figure()
layout = row([column(div_menu), column(p), column()])
curdoc().template_variables["load"] = '0'
curdoc().title = "Albatross"
#print(curdoc().template)
curdoc().add_root(layout, FILE="templates/index.html")

    

