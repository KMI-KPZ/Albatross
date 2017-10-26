import os
import xml.etree.ElementTree
import bokeh
import importlib
from functools import partial
from random import random
from bokeh import events
from bokeh.layouts import column, widgetbox, row
from bokeh.models import Button, CustomJS
from bokeh.palettes import RdYlBu3
from bokeh.models.widgets import Select, TextInput, Div
from bokeh.plotting import figure, curdoc, reset_output
from bokeh.io import set_curdoc
import spq_plat


def get_sub_direct(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

    
def define_menu():
    # create menu
    t = []
    for sub in get_sub_direct('Modules'):
        
        if sub != 'Menu' and sub != '__pycache__':
            e = xml.etree.ElementTree.parse(os.path.join(os.path.dirname(__file__), '../' + sub + '/config.xml')).getroot()
            titleMenu = e.find('menu').find('title').text;
            print(titleMenu)
            module = importlib.import_module('Modules.' + titleMenu + '.main') 
        
        
            menu_inner = '<h3>' + titleMenu + '<h3>';
            button_box = []
            for point in e.find('menu').findall('point'):
            #set button
                print(point.find('name').text)
                button_inner = Button(label=point.find('name').text, button_type="success")
                function = point.find('callback').text
                f = getattr(module, function);
                button_inner.on_click(f)
                button_box.append(button_inner)
            
            t.append(row(Div(text=menu_inner), column(button_box)))
    print(t)
    spq_plat.layout.children[0] = column(t);
