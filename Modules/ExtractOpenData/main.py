import urllib
import urllib2
import os
import xml.etree.ElementTree
from html5lib.constants import namespaces

EULink = 'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=table_of_contents.xml'

def findXMLLink(r):
    if r.find('nt:children', namespaces).findall('nt:leaf', namespaces) is not None:
        for li in r.find('nt:children', namespaces).findall('nt:leaf', namespaces):
            if li.find('nt:title[@language="en"]', namespaces) is not None:
                print li.find('nt:title[@language="en"]', namespaces).text
            if li.find('nt:downloadLink[@format="tsv"]', namespaces) is not None:
                print li.find('nt:downloadLink[@format="tsv"]', namespaces).text
            

def iterateXML(xml):
    for r in xml.find('nt:children', namespaces).findall('nt:branch', namespaces):
        print r.find('nt:title[@language="en"]', namespaces).text
        if r.find('nt:children', namespaces) is not None:
            findXMLLink(r)
            #iterate
            iterateXML(r)
        else:
            findXMLLink(r)

def showTOC():
    global namespaces
    
    if not os.path.isfile("data/toc.xml"):
        testfile = urllib.URLopener()
        testfile.retrieve(EULink, "data/toc.xml")
    ET = xml.etree.ElementTree
    e = ET.parse('data/toc.xml').getroot()
    ET.register_namespace('nt', 'urn:eu.europa.ec.eurostat.navtree')
    namespaces = {'nt': 'urn:eu.europa.ec.eurostat.navtree'} # add more as needed

    print 'xml open'
    for b in e.findall('nt:branch', namespaces):
        print b.find('nt:title[@language="en"]', namespaces).text
        iterateXML(b)            
    
    print 'Rdy'    
    