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
import index


def get_sub_direct(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

"""
    Defines Menu based on the Modules directory.
    Each module needs an config.xml and and main.py module.
    The xml configure the sidemenu of the page and the callbacks
    sidemenu is the fist layout child of spq_plat.layout
"""
def define_menu():
    # create menu
    t = []
    modulelist = get_sub_direct('Modules');
    modulelist.sort()
    for sub in modulelist:
        
        if sub != 'Menu' and os.path.isfile(os.path.dirname(__file__) + '/../' + sub + '/config.xml'):
            e = xml.etree.ElementTree.parse(os.path.join(os.path.dirname(__file__), '../' + sub + '/config.xml')).getroot()
            titleMenu = e.find('menu').find('title').text;
            
            name = 'Modules.' + sub + '.main'
            spec = importlib.util.find_spec(name)
        
            if spec is None:
                print("can't find the itertools module")
            else:
                # If you chose to perform the actual import ...
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Adding the module to sys.modules is optional.
                #sys.modules[name] = module
        
            menu_inner = '<h3>' + titleMenu + '<h3>';
            button_box = []
            for point in e.find('menu').findall('point'):
                #set button
                button_inner = Button(label=point.find('name').text, button_type="success")
                function = point.find('callback').text
                f = getattr(module, function);
                button_inner.on_click(f)
                button_box.append(button_inner)
            
            t.append(row(column([Div(text=menu_inner, height=15), widgetbox(button_box, height=55)])))
    
    index.change_layout(0, column(t));
