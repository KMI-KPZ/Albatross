from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://www.foodie-cloud.org/sparql")
sparql.setQuery("""
prefix obs: <http://purl.org/linked-data/sdmx/2009/measure#>
prefix prop: <http://eurostat.linked-statistics.org/property#>
prefix qb: <http://purl.org/linked-data/cube#>
prefix sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>

select distinct ?designation ?time ?value ?unit
from <http://eurostat.linked-statistics.org/data/aei_pr_soiler.rdf>
where {
  ?observation a qb:Observation.
  ?observation prop:geo ?designation.
  ?observation prop:unit ?unit.
  ?observation sdmx-dimension:timePeriod ?time.
  ?observation obs:obsValue ?value.
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    geo = result['designation']['value'].split('#')[-1]
    time = result['time']['value']
    value = result['value']['value']
    unit = result['unit']['value'].split('#')[-1]
    print("| {:>5} | {:>20} | {:>10,.5f} | {:>10} |".format(geo, time, float(value), unit))