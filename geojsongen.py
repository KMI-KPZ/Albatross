import sparql
import os
import xml.etree.ElementTree

e = xml.etree.ElementTree.parse(os.path.join(os.path.dirname(__file__), 'config.xml')).getroot()


results = sparql.query();
final = '{ "type": "FeatureCollection", "features": ['
finalfeatures = ''

#TODO: Implement https://pypi.python.org/pypi/geojson
#todo: named properties
# loop the results and set properties with the help of the config 
for result in results["results"]["bindings"]:
    for prop in e.findall('properties'):
        i = 0;
        properties = '';
        for p in prop.findall('property'):
            feature = result[p.find('sparql').find('select').text]["value"]
            properties = properties + '"prop_'+ str(i) + '": "' + feature + '",'
            i = i +1;
        properties = properties[:-1]
    er = result["geosc"]["value"].split('(', 1)
    #testing
    #finalfeatures = ''

    if er[0] == 'POLYGON':
        #replacing to valid geojson
        Gcoord = result["geosc"]["value"].replace('(', '[').replace(')',']').replace(',', '] [').replace(' ', ', ').replace('POLYGON', '\"coordinates\": [') + ']';
        Gtype = "Polygon"
        finalfeatures = finalfeatures + ' { "type": "Feature", "geometry": { "type": "' + Gtype + '", ' + Gcoord + ' }, "properties": { ' + properties + ' }  }'     
final = final + finalfeatures + ' ]}'
file = open(os.path.join(os.path.dirname(__file__), 'testfile.geojson'),'w')
file.write(final.encode('ascii', 'xmlcharrefreplace')) 
file.close