import os
import json


def get_eurostats_file_list():
    """
    This function generates the file names for every RDF in the "data/rdf/eurostats" subdirectory.

    Returns:
        a list of dictionaries containing the id and file names of the RDFs found.
    """
    rdf_path_prefix = "../../data/rdf/eurostats/"
    geojson_path_prefix = "../../data/geojson/eurostats/"
    observation_list = []
    for file in os.listdir(rdf_path_prefix):
        observation = {}
        observation_name = str(os.path.basename(file).split('.')[0])
        observation['id'] = observation_name
        observation['rdf'] = rdf_path_prefix + file
        observation['geojson'] = {
            'nuts1': geojson_path_prefix + "nuts1_" + observation_name + ".geojson",
            'nuts2': geojson_path_prefix + "nuts2_" + observation_name + ".geojson",
            'nuts3': geojson_path_prefix + "nuts3_" + observation_name + ".geojson"
        }
        observation_list.append(observation)
    return observation_list


def main():
    """
    Program Entry Point
    """
    ids = [id['id'] for id in get_eurostats_file_list()]
    with open('test.json', 'w') as handle:
        json.dump(get_eurostats_file_list()[0], indent=4, fp=handle)
    print(ids)


if __name__ == "__main__":
    main()
