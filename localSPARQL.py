#! /usr/bin/env python3

import rdflib as rdf
import logging
import json

logging.basicConfig(level=logging.INFO)

filename = 'data/aei_pr_soiler.rdf'

g = rdf.Graph()
logging.info(" parsing file: {}".format(filename))
g.parse(filename, format='xml')

logging.info(" querying ...")
results = g.query("""
prefix : <.>
prefix soiler: <http://eurostat.linked-statistics.org/data/aei_pr_soiler.#>
prefix obs: <http://purl.org/linked-data/sdmx/2009/measure#>
prefix prop: <http://eurostat.linked-statistics.org/property#>
prefix qb: <http://purl.org/linked-data/cube#>
prefix geo: <http://eurostat.linked-statistics.org/dic/geo#>
prefix sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>
prefix unit: <http://eurostat.linked-statistics.org/dic/unit#>

select ?designation ?time ?value ?unit
where {
  ?observation a qb:Observation.
  ?observation prop:geo ?designation.
  ?observation prop:unit ?unit.
  ?observation sdmx-dimension:timePeriod ?time.
  ?observation obs:obsValue ?value.
}
""")
logging.info(" done querying!")


for row in results:
    geo = row[0].split('#')[1]
    time = row[1]
    value = row[2]
    unit = row[3].split('#')[1]
    # print("{:5}\t{}\t{:>7} {}".format(geo, time, value, unit))

    print(json.dumps(
        {
            "properties": {
                "NUTS_ID": geo,
                "OBSERVATIONS": {
                    "soil": (
                        {
                            "period": time,
                            "unit": unit,
                            "value": value
                        }
                    )
                }
            }
        },
        indent=4,
        separators=(',', ':')
    ))
