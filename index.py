import os
import xml.etree.ElementTree
import importlib
import bokeh
from bokeh import events
from bokeh.layouts import column, widgetbox, row, layout
from bokeh.models import Button, CustomJS
from bokeh.palettes import RdYlBu3
from bokeh.models.widgets import Select, TextInput, Div
from bokeh.plotting import figure, curdoc, reset_output
from jinja2.environment import Template
from bokeh.themes.theme import Theme
from bokeh.events import ButtonClick
import tornado.ioloop
import tornado.web
from bokeh.server.server import Server
from jinja2 import Environment, FileSystemLoader
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.embed import server_document
from tornado.web import RequestHandler
from tornado import gen
from collections import defaultdict
from tornado.options import define, options




data_by_user = defaultdict(lambda: dict(file_names=[], dates=[], downloads=[]))
doc_by_user_str = dict()
source_by_user_str = dict()

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
        
        if sub != 'Menu' and os.path.isfile(os.path.dirname(__file__) + 'Modules/' + sub + '/config.xml'):
            e = xml.etree.ElementTree.parse(os.path.join(os.path.dirname(__file__), 'Modules/' + sub + '/config.xml')).getroot()
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
    print(t)
    return column(t);


class IndexHandler(RequestHandler):
    def get(self):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('index.html')
        script = server_document('http://localhost:5006/index')
            
        self.write(template.render(script=script, template="Tornado"))


class MainHandler(tornado.web.RequestHandler):
    @staticmethod
    def def_platform(doc):
        
        user_str = doc.session_context.id
        
        doc.title = "Albatross"
        #print(curdoc().template)
        theme = Theme(filename="theme.yaml")
        doc.theme = theme
        first_column = define_menu()
        
        doc_by_user_str[user_str] = doc
        
        doc.add_root(first_column)
        
        
        
    @classmethod
    def get_bokeh_app(cls):
        if cls._bokeh_app is None:
            cls._bokeh_app = bokeh.application.Application(FunctionHandler(MainHandler.def_platform))
        return cls._bokeh_app
    
    @gen.coroutine
    def get(self):
        print('er');
        user_str = str(self.current_user)
        script = autoload_server(model=None, session_id=user_str,  # NOTE: MUST be string
                                 app_path='/index',
                                 url='http://localhost:5006')
        
        self.render(
                'index.html',
                script=script
)
class Application(tornado.web.Application):
    def __init__(self):
        
        handlers = [
            (r'/', MainHandler),
            (r'/ws', IndexHandler),
        ]
        settings = {
            "debug": True,
            "static_path": os.path.join(os.path.dirname(__file__), "static")
        }
        tornado.web.Application.__init__(self, handlers, **settings)

def start_server():
    
    bokeh_app = bokeh.application.Application(FunctionHandler(MainHandler.def_platform))
    server = Server({'/index': bokeh_app}, num_procs=1, extra_patterns=[('/', IndexHandler)])
    server.start()
    return server

if __name__ == '__main__':
    from bokeh.util.browser import view
    server = start_server()
    print('Opening Tornado app with embedded Bokeh application on http://localhost:5006/')
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    
    io_loop = tornado.ioloop.IOLoop.current()
    server.io_loop.add_callback(view, "http://localhost:5006/")
    server.io_loop.start()
    

