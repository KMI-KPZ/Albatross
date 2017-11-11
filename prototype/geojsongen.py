import os
import xml.etree.ElementTree

import sparql

e = xml.etree.ElementTree.parse(os.path.join(os.path.dirname(__file__), 'config.xml')).getroot()


results = sparql.query();
final = '{ "type": "FeatureCollection", "features": ['
finalfeatures = ''

#TODO: Implement https://pypi.python.org/pypi/geojson
#todo: named properties
# loop the results and set properties with the help of the config
cust_id = 0
 
for result in results["results"]["bindings"]:
    
    
    for prop in e.findall('properties'):
        
        i = 0
        
        properties = '"NUTS_ID": "CUSTOM_' + str(cust_id) + '", ';
        properties += '"OBSERVATIONS": { ';
        
        
        for p in prop.findall('property'):
            if i == 0:
                obs_name = p.find('name').text
                properties += '"' + obs_name + '": [ ';
            
            obs_value = result[p.find('sparql').find('select').text]["value"]
            obs_period = result[prop.find('date').text]['value']
            obs_unit = result[p.find('sparql').find('unit').text]["value"]
            
            properties += '''
            {
                 "unit": "''' + obs_unit + '''",
                 "value": "''' + obs_value + '''",
                 "period": "''' + obs_period + '''"
             
            },'''
            i = i +1;
        properties = properties[:-1]
        properties += '] }'
        cust_id = cust_id + 1
    er = result["geosc"]["value"].split('(', 1)
    #testing
    #TODO MULTIPOLYGON etc.
    if er[0] == 'POLYGON':
        #replacing to valid geojson
        Gcoord = result["geosc"]["value"].replace('(', '[').replace(')',']').replace(',', '] [').replace(' ', ', ').replace('POLYGON', '\"coordinates\": [') + ']';
        Gtype = "Polygon"
        finalfeatures = finalfeatures + ' { "type": "Feature", "geometry": { "type": "' + Gtype + '", ' + Gcoord + ' }, "properties": { ' + properties + ' }  }'
        finalfeatures = finalfeatures + """,""" 
    
finalfeatures = finalfeatures[:-1]        
final = final + finalfeatures + ' ]}'
file = open(os.path.join(os.path.dirname(__file__), 'testfile.geojson'),'w')
file.write(final.encode('ascii', 'xmlcharrefreplace')) 
file.close