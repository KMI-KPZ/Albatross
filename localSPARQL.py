#! /usr/bin/env python3

import rdflib as rdf
import logging
import json

logging.basicConfig(level=logging.WARNING)

# TODO: filename and observation_name need to be a parameter
filename = 'data/aei_pr_soiler.rdf'
observation_name = 'soil'

g = rdf.Graph()
logging.info(" parsing file: {}".format(filename))
g.parse(filename, format='xml')

logging.info(" querying ...")

# TODO: maybe use sparql.py and the config.xml
results = g.query("""
prefix : <.>
prefix soiler: <http://eurostat.linked-statistics.org/data/aei_pr_soiler.#>
prefix obs: <http://purl.org/linked-data/sdmx/2009/measure#>
prefix prop: <http://eurostat.linked-statistics.org/property#>
prefix qb: <http://purl.org/linked-data/cube#>
prefix geo: <http://eurostat.linked-statistics.org/dic/geo#>
prefix sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>
prefix unit: <http://eurostat.linked-statistics.org/dic/unit#>

select distinct ?designation ?time ?value ?unit
where {
  ?observation a qb:Observation.
  ?observation prop:geo ?designation.
  ?observation prop:unit ?unit.
  ?observation sdmx-dimension:timePeriod ?time.
  ?observation obs:obsValue ?value.
}
""")
logging.info(" done querying!")

logging.info(" open geojson")

# TODO: use nuts_files to store the path to the GeoJSON
with open('data/nuts_rg_60M_2013_lvl_3.geojson') as f:
    nuts3 = json.load(f)
with open('data/nuts_rg_60M_2013_lvl_2.geojson') as f:
    nuts2 = json.load(f)
with open('data/nuts_rg_60M_2013_lvl_1.geojson') as f:
    nuts1 = json.load(f)

nuts_files = [
    'data/nuts1_test_B.geojson',
    'data/nuts2_test_B.geojson',
    'data/nuts3_test_B.geojson'
]
nuts = [nuts1, nuts2, nuts3]
# nuts = []
# for lvl in nuts_files:
#     with open(lvl) as f:
#         nuts.append(json.load(f))

for row in results:
    # recover uncluttered information from the sparql result
    geo = row[0].split('#')[1]
    time = row[1]
    value = row[2]
    unit = row[3].split('#')[1]

    # search for the NUTS_ID (geo) in the NUTS levels 1 to 3
    logging.info(" searching for NUTS_ID {}".format(geo))
    index = -1
    nuts_lvl = -1
    found = False
    while not found:
        index += 1
        done = []
        # prepare break condition
        for lvl in range(0, len(nuts)):
            done.append(False)

        # check if the ID matches in any of the NUTS levels
        for lvl in range(0, len(nuts)):
            if index < len(nuts[lvl]['features']):
                if nuts[lvl]['features'][index]['properties']['NUTS_ID'] == geo:
                    nuts_lvl = lvl
                    found = True
                    break
            else:
                done[lvl] = True
        if all(done):
            break

    if nuts_lvl == -1:
        logging.warning(" unable to find NUTS_ID {}".format(geo))
    else:
        logging.info(" found NUTS_ID in level {} at index {}".format(nuts_lvl+1, index))

        observation = {
            'period': time,
            'unit': unit,
            'value': value
        }

        # check if any of the nested elements in the JSON already exist
        if 'OBSERVATIONS' in nuts[nuts_lvl]['features'][index]['properties']:
            if 'soil' in nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS']:
                nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'][observation_name].append(observation)
            else:
                nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'][observation_name] = [observation]
        else:
            nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'] = {
                observation_name: [observation]
            }

# write back to all the GeoJSON
logging.info(" writing back data to geojson")
for lvl in range(0, len(nuts)):
    with open(nuts_files[lvl], 'w') as outfile:
        json.dump(nuts[lvl], outfile)
