import os
import json
import rdflib as rdf
import logging
import copy


def get_eurostats_file_list():
    """
    This function generates the file names for every RDF in the "data/rdf/eurostats" subdirectory.

    :return: A list of dictionaries containing the id and file names of the RDFs found.
    """
    rdf_path_prefix = "../../data/rdf/eurostats/"
    geojson_path_prefix = "../../data/geojson/eurostats/"
    observation_list = []

    logging.info(" checking for existing geojson")
    nuts_files = [
        [str(os.path.basename(file).split('.')[0]) for file in os.listdir(geojson_path_prefix + "nuts_1/")],
        [str(os.path.basename(file).split('.')[0]) for file in os.listdir(geojson_path_prefix + "nuts_2/")],
        [str(os.path.basename(file).split('.')[0]) for file in os.listdir(geojson_path_prefix + "nuts_3/")]
    ]

    logging.info(" found {} geojson(s)".format(
        len(nuts_files[0]) +
        len(nuts_files[1]) +
        len(nuts_files[2])
    ))

    logging.info(" generating file lists for {} RDFs".format(len(os.listdir(rdf_path_prefix))))
    for file in os.listdir(rdf_path_prefix):
        observation = {}
        observation_name = str(os.path.basename(file).split('.')[0])
        observation['id'] = observation_name
        observation['rdf'] = rdf_path_prefix + file
        observation['geojson'] = {
            'nuts1': {'path': geojson_path_prefix + "nuts_1/" + observation_name + ".geojson", 'exists': observation_name in nuts_files[0]},
            'nuts2': {'path': geojson_path_prefix + "nuts_2/" + observation_name + ".geojson", 'exists': observation_name in nuts_files[1]},
            'nuts3': {'path': geojson_path_prefix + "nuts_3/" + observation_name + ".geojson", 'exists': observation_name in nuts_files[2]},
        }
        observation_list.append(observation)
    logging.info(" done generating file lists for {}".format([tmp_id['id'] for tmp_id in observation_list]))
    return observation_list


def extract_observations(file):
    logging.info(" parsing  '{}'".format(file))
    g = rdf.Graph()
    g.parse(file, format="xml")

    logging.info(" querying '{}'".format(file))
    return g.query("""
        prefix obs: <http://purl.org/linked-data/sdmx/2009/measure#>
        prefix prop: <http://eurostat.linked-statistics.org/property#>
        prefix qb: <http://purl.org/linked-data/cube#>
        prefix sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>

        select distinct ?designation ?time ?value ?unit
        where {
            ?observation a qb:Observation.
            ?observation prop:geo ?designation.
            ?observation prop:unit ?unit.
            ?observation sdmx-dimension:timePeriod ?time.
            ?observation obs:obsValue ?value.
        }
    """)


def write_geojson(file_list):

    logging.info(" opening nuts base files")
    with open('../../data/nuts_rg_60M_2013_lvl_3.geojson') as f:
        nuts3 = json.load(f)
    with open('../../data/nuts_rg_60M_2013_lvl_2.geojson') as f:
        nuts2 = json.load(f)
    with open('../../data/nuts_rg_60M_2013_lvl_1.geojson') as f:
        nuts1 = json.load(f)

    nuts = [nuts1, nuts2, nuts3]

    for file in file_list:
        logging.info(" processing {}".format(file['id']))
        geojson = copy.deepcopy(nuts)
        process_file(file, geojson)

        logging.info(" writing back geojson for {}".format(file['id']))
        for lvl in range(0, len(geojson)):
            logging.info(" open file {}".format(file['geojson']['nuts{}'.format(lvl + 1)]['path']))
            with open(file['geojson']['nuts{}'.format(lvl + 1)]['path'], 'w') as outfile:
                json.dump(geojson[lvl], fp=outfile, indent=4)


def process_file(file, nuts):
    for row in file['results']:
        # recover uncluttered information from the sparql result
        geo = row[0].split('#')[1]
        time = row[1]
        value = row[2]
        unit = row[3].split('#')[1]

        # search for the NUTS_ID (geo) in the NUTS level 1 to 3
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

        if nuts_lvl != -1:
            observation = {
                'period': time,
                'unit': unit,
                'value': value
            }

            # check if any of the nested elements in the JSON already exist
            if 'OBSERVATIONS' in nuts[nuts_lvl]['features'][index]['properties']:
                if file['id'] in nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS']:
                    duplicate = False
                    for observations in nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'][file['id']]:
                        if observations['period'] == observation['period']:
                            duplicate = True
                            break
                    if not duplicate:
                        nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'][file['id']].append(observation)
                else:
                    nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'][file['id']] = [observation]
            else:
                nuts[nuts_lvl]['features'][index]['properties']['OBSERVATIONS'] = {
                    file['id']: [observation]
                }
        else:
            logging.warning(" unable to find NUTS_ID {} in {}".format(geo, file['id']))


def main():
    """
    Program Entry Point
    """

    logging.basicConfig(level=logging.INFO)

    eurostats = get_eurostats_file_list()
    for f in eurostats:
        f['results'] = extract_observations(f['rdf'])

    write_geojson(eurostats)

if __name__ == "__main__":
    main()
