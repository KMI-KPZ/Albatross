import os
import xml.etree.ElementTree
import bokeh
import importlib
from functools import partial
from random import random
from bokeh import events, document
from bokeh.layouts import column, widgetbox, row
from bokeh.models import Button, CustomJS
from bokeh.palettes import RdYlBu3
from bokeh.models.widgets import Select, TextInput, Div
from bokeh.plotting import figure, curdoc, reset_output


class Testing():
    
    def __init__(self, layout):
        self.layout = layout
    
    def call_vis(s):
        global i
        global ds
       
        i = 0
        # create a callback that will add a number in a random location
        def callback():
            global i
            # BEST PRACTICE --- update .data in one step with a new dict
            new_data = dict()
            new_data['x'] = ds.data['x'] + [random()*70 + 15]
            new_data['y'] = ds.data['y'] + [random()*70 + 15]
            new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i%3]]
            new_data['text'] = ds.data['text'] + [str(i)]
            ds.data = new_data
            i = i + 1
        
        p1 = figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
        # create a plot and style its properties
        p1.border_fill_color = 'black'
        p1.background_fill_color = 'black'
        p1.outline_line_color = None
        p1.grid.grid_line_color = None
    
        # add a text renderer to our plot (no data yet)
        button = Button(label="Press Me")
        button.on_click(callback)
    
        
        r = p1.text(x=[], y=[], text=[], text_color=[], text_font_size="20pt",
               text_baseline="middle", text_align="center")
        
        ds = r.data_source
        user_id = curdoc().session_context.id
        s.layout.children[1] = p1
        s.layout.children[2] = button
        
    def call():
        s.layout.children[1] = widgetbox(Div());
        return 1