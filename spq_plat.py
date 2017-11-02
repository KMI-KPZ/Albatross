from bokeh import events
from bokeh.layouts import column, widgetbox, row
from bokeh.models import Button, CustomJS
from bokeh.palettes import RdYlBu3
from bokeh.models.widgets import Select, TextInput, Div
from bokeh.plotting import figure, curdoc, reset_output
from jinja2.environment import Template
from bokeh.themes.theme import Theme
from bokeh.events import ButtonClick


div_menu = Div()
p = figure()
layout = row([column(div_menu), column(p), column()])
curdoc().title = "Albatross"
#print(curdoc().template)
curdoc().add_root(layout)
html = open("templates/index.html", 'r').read()
temp = Template(html)
curdoc().template = temp
theme = Theme(filename="theme.yaml")
curdoc().theme = theme


    

