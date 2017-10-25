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
from bokeh.io.doc import set_curdoc