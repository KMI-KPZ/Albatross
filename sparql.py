from SPARQLWrapper import SPARQLWrapper, JSON
import xml.etree.ElementTree
import os

e = xml.etree.ElementTree.parse(os.path.join(os.path.dirname(__file__), 'config.xml')).getroot()


# TODO improve xml query
def build_query_select():
    # read xml file
    # first only selects without using them as properties for geojson
    for atype in e.findall('sparql'):
        select = atype.findall('select')
        select_string = ''
        for t in select:
            select_string = select_string + ' ?' + t.text
    # here add to select the properties including geo-data and date as special sets
    for prop in e.findall('properties'):
        for p in prop.findall('property'):
            select_string = select_string + ' ?' + p.find('sparql').find('select').text
        select_string = select_string + ' ?' + prop.find('date').text
        select_string = select_string + ' ?' + prop.find('geo').text
    
    return select_string


def build_query_where():
    for atype in e.findall('sparql'):
        where_string = atype.find('where').text
    return where_string;


def build_query_from():
    for atype in e.findall('sparql'):
        fromstring = '<' + atype.find('from').text + '>'
    return fromstring;


def build_query_endpoint():
    for atype in e.findall('sparql'):
        end_string = atype.find('endpoint').text
    return end_string;


def build_query_prefix():
    pre_string = '';
    for a in e.findall('sparql'):
        for atype in a.findall('prefixes'):
            for pre in atype.findall('prefix'):
                pre_string = pre_string + """PREFIX """ + pre.get('short') + """: <""" + pre.text + """>
                """
    return pre_string

    
def query():
    sparql = SPARQLWrapper(build_query_endpoint())
    sparql.setQuery(
        build_query_prefix() +
        """
        
        select """ + build_query_select() + """
        from """ + build_query_from() + """
        where 
        {
            """ + build_query_where() + """
        }
        
    
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    return results
    # for result in results["results"]["bindings"]:
    #   print(result["geosc"]["value"])
