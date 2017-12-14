#!/usr/bin/env python3

import os
import xml.etree.ElementTree
import importlib
import bokeh
import  inspect
from bokeh.layouts import column, widgetbox, row
from bokeh.models import Button
from bokeh.models.widgets import  Div
from bokeh.themes.theme import Theme
import tornado.ioloop
import tornado.web
from bokeh.server.server import Server
from jinja2 import Environment, FileSystemLoader
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.embed import server_document
from tornado.web import RequestHandler
from collections import defaultdict
from shutil import copyfile

data_by_user = defaultdict(lambda: dict(file_names=[], dates=[], downloads=[]))
doc_by_user_str = dict()
source_by_user_str = dict()

def get_sub_direct(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]
    

        
"""
Generic IndexHandler 
generates Startpage
"""
class IndexHandler(RequestHandler):
    def get(self):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('frameing.html')
        script = server_document('http://localhost:5006/')
        args=dict(template="index.html",  menu=GenericHandler.build_menu(GenericHandler))
        self.write(template.render(script=script,  **args))
"""
Build the application...
"""
class GenericHandler(tornado.web.RequestHandler):
    _template = ''
    _url = ''
    _function = ''
    _module = None
    _server = 'http://localhost:5006/'
    _menu = None
    
    def initialize(self, key = ''):
        self.build_menu()
        self._url=key
        if key != '':
            self.module_manager()
            
        
    '''
    manages the module choosen wtihin the init
    '''
    def build_menu(self):
        if self._menu is None:
            self._menu = []
            modulelist = get_sub_direct('Modules');
            modulelist.sort()
            for sub in modulelist:
                if sub != 'Menu' and os.path.isfile(os.path.join(os.path.dirname(__file__), 'Modules', sub, 'config.xml')):
                    e = xml.etree.ElementTree.parse(os.path.join(os.path.dirname(__file__), 'Modules', sub, 'config.xml')).getroot()
                    #build menu
                    children = []
                    for point in e.find('menu').findall('point'):
                        label=point.find('name').text
                        url=point.find('url').text
                        children.append({url:label})
                        
                    self._menu.append({e.find('menu').find('url').text: {'name': e.find('menu').find('title').text,  'children':children }})
    
        return self._menu
    
    def load_spec(self,  sub):
        name = 'Modules.' + sub + '.main'
        spec = importlib.util.find_spec(name)
    
        if spec is not None:
            # If you chose to perform the actual import ...
            self._module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self._module)
        return self._module
        
    def set_spec(self, sub,  template):
        
        directory = 'templates/modules/'+sub+ '/';
        dst = os.path.join(os.path.dirname(__file__),'modules/'+sub+ '/'+ template)
        dst_template = os.path.join(os.path.dirname(__file__),'templates/' + dst)
        src = os.path.join(os.path.dirname(__file__),'Modules/' + sub + '/template/' + template)
        if not os.path.isfile(src): print(src + ': not found ERROR')
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.isfile(dst_template): 
            copyfile(src, dst_template)
        
        self._template = dst
        self.load_spec(sub)
        
    def module_manager(self):
        
        modulelist = get_sub_direct('Modules');
        modulelist.sort()
        for sub in modulelist:
            if sub != 'Menu' and os.path.isfile(os.path.join(os.path.dirname(__file__), 'Modules', sub, 'config.xml')):
                e = xml.etree.ElementTree.parse(os.path.join(os.path.dirname(__file__), 'Modules', sub, 'config.xml')).getroot()
                
                if(e.find('menu').find('url').text == self._url):
                    self._function =e.find('menu').find('callback').text
                    temp_template = e.find('template').text
                    self.set_spec(sub,  temp_template)
                    
                for point in e.find('menu').findall('point'):
                    if point.find('url').text == self._url:
                        self._function = point.find('callback').text
                        temp_template = e.find('template').text
                        self.set_spec(sub,  temp_template)
            
        
    def get_all_urls():
        modulelist = get_sub_direct('Modules');
        modulelist.sort()
        urls = []
        url_children = []
        types = []
        
        for sub in modulelist:
            if sub != 'Menu' and os.path.isfile(os.path.join(os.path.dirname(__file__), 'Modules', sub, 'config.xml')):
                e = xml.etree.ElementTree.parse(os.path.join(os.path.dirname(__file__), 'Modules', sub, 'config.xml')).getroot()
                
                urls.append(e.find('menu').find('url').text);
                types.append(e.find('type').text);
                temp_children = []
                
                for point in e.find('menu').findall('point'):
                        sub_url=point.find('url').text
                        temp_children.append(sub_url)
                
                url_children.append(temp_children)
        
        return dict(urls=urls, types=types,  children=url_children)  
    
    def get_function_handler_for_bokeh(self , url):
        modulelist = get_sub_direct('Modules');
        modulelist.sort()
        for sub in modulelist:
            if sub != 'Menu' and os.path.isfile(os.path.join(os.path.dirname(__file__), 'Modules', sub, 'config.xml')):
                e = xml.etree.ElementTree.parse(os.path.join(os.path.dirname(__file__), 'Modules', sub, 'config.xml')).getroot()
                
                if(e.find('menu').find('url').text == url):
                    
                    function =e.find('menu').find('callback').text
                    module = self.load_spec(self,sub)
                    classd = getattr(module,  'Layout')(GenericHandler.build_menu(GenericHandler))
                    
                for point in e.find('menu').findall('point'):
                    if(point.find('url').text == url):
                        function =point.find('callback').text
                        module = self.load_spec(self, sub)
                        classd = getattr(module,  'Layout')(GenericHandler.build_menu(GenericHandler))
        print(url)            
        return FunctionHandler(getattr(classd, function))
        
    def get(self):
        env = Environment(loader=FileSystemLoader('templates'))
        
        #todo think routing
        template = env.get_template('frameing.html')
        
        script = server_document(self._server+self._url)
        
        function_name = (self._function)
        args = getattr(self._module,  function_name)()
        req_args = dict(template=self._template,  menu=self._menu,  args=args)
        
        self.write(template.render(script=script, **req_args)) 
        
    def post(self):
        print('somepost')
        #todo do somethong
        #req_args = Modules.Linking.main.post(self.request)
        
        #todo get redirect from function
        #req_args = Modules.Linking.main.redirect()
        
        #do redirect
        self.redirect(redirect)

def start_server():
    
    script_path = os.path.join(os.path.dirname(__file__), 'data')
    css_path = os.path.join(os.path.dirname(__file__), 'static/css')
    
    extra_patterns =[
        (r"/data/(.*)", tornado.web.StaticFileHandler, {"path": script_path}), 
        (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": css_path}), 
        (r"/fonts/(.*)", tornado.web.StaticFileHandler, {"path": 'fonts'}), 
        (r"/",  IndexHandler)]
    bokeh_apps = dict()
    
    module_dict = GenericHandler.get_all_urls()
    
    #set the extra patter and the bokeh applications based on the module config.xmls
    urls = module_dict['urls']
    print(module_dict)
    for i, ival in enumerate(urls):
        if module_dict['types'][i] == 'tornado':
            extra_patterns.append((r"/"+ival,  GenericHandler,  dict(key=ival)))
            for child in module_dict['children'][i]:
                extra_patterns.append((r"/"+child,  GenericHandler,  dict(key=child)))
        elif module_dict['types'][i] == 'bokeh':
            
            function_handler = GenericHandler.get_function_handler_for_bokeh(GenericHandler, ival)
            bokeh_app = bokeh.application.Application(function_handler)
            bokeh_apps['/'+ival] = bokeh_app 
            
            for child in module_dict['children'][i]:
                function_handler = GenericHandler.get_function_handler_for_bokeh(GenericHandler,  child)
                bokeh_app = bokeh.application.Application(function_handler)
                bokeh_apps['/'+child] = bokeh_app 
    
    server = Server(bokeh_apps, num_procs=1, extra_patterns=extra_patterns)
    server.start()
    return server

if __name__ == '__main__':
    from bokeh.util.browser import view
    server = start_server()
    print('Opening Tornado app with embedded Bokeh application on http://localhost:5006/')
    
    io_loop = tornado.ioloop.IOLoop.current()
    server.io_loop.add_callback(view, "http://localhost:5006/")
    server.io_loop.start()
    

