# Albatross

Run `index.py`

The service will be accessible at [http://127.0.0.1:5006](http://127.0.0.1:5006).

## Description

The application has two parts, first of all, the given (3-star) Open Data (focusing NUTS-3 datasets - https://data.europa.eu/euodp/en/data/dataset/L3AfXzHroGVUIo1xzwJlw
http://appsso.eurostat.ec.europa.eu/nui/show.do?dataset=aei_fm_ms&lang=de
http://appsso.eurostat.ec.europa.eu/nui/show.do?dataset=ef_r_nuts&lang=de) will be transformed into 5-star Open Data (http://5stardata.info/en/), by means of RDF transformation. 
The focus on geospatial and temporal Open Data opens the possibility to use RDF Cubes (https://www.w3.org/TR/vocab-data-cube/) for that purpose. 
We test an automated approach to link these cubes, using a LIMES service (https://github.com/dice-group/LIMES). 
The goal is to deliver an application, that automates this process. 
The second step is to use this RDF data and visualise them. The visualisation will have two integrated components. On the one hand the data will be visible on a Map (using bokeh), and one the other hand the data will be visualised as charts (e.g. temporal development bar chart). The charts will be configurable to visualised the right information for user purposes. The map visualisation will be dynamic with zooming functions and flexible hover information about target regions (local Polygons and NUTS-3 Regions). The application additionally will have the feature to download this visualisation in graphical formats (PNG), RDFs and GeoJSONs.


## Requirements

- Install current version of the JRE to use services of [LIMES](https://github.com/dice-group/LIMES) and [Eurostats dataset](https://github.com/linked-statistics/eurostat)
- Install current version of Python3
- [Install Geopandas](http://geopandas.org/): `sudo pip install geopandas`
- [Install MatPlotLib](https://matplotlib.org/): `sudo apt-get install python-matplotlib`
- [Install Pysal](http://pysal.readthedocs.io/en/latest/index.html): `sudo pip install -U pysal`
- [Install Bokeh](https://bokeh.pydata.org/en/latest/): `sudo pip install bokeh`
- [Install lxml](http://lxml.de/): `sudo pip install lxml`
- [Install SPARQLWrapper](https://rdflib.github.io/sparqlwrapper/): `sudo pip install SPARQLWrapper`
- [Install Tornado](http://www.tornadoweb.org/en/stable/): `sudo pip install tornado`