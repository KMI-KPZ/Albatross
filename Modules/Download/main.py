import os
import json
        
def get_files(prefix): 
    """ 
        This function generates the file names from prefix
     
        :param str prefix: String of the path 
        :return: a list of dictionaries containing the id and file names of the RDFs found. 
    """ 
    
    observation_list = []
    for file in os.listdir(prefix):
        observation = {}
        observation_name = str(os.path.basename(file).split('.')[0])
        observation['id'] = observation_name
        observation['url'] = prefix + file
        observation_list.append(observation)
    return observation_list


def return_view_args():
    rdf_obslist = get_files("data/rdf/eurostats/")
    original_obslist = get_files("data/sandbox/eurostat/tsv")

    a_dir = r"data/geojson/eurostats/"
    geojson_levels = [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

    geojson_files = {}
    geojson_lvl = []
    for lvl in geojson_levels:
        geojson_files[lvl] = get_files(os.path.join(a_dir, lvl + "/"))
        geojson_lvl.append({'dir_name': lvl, 'display_name': lvl.upper().replace("_", " ")})

    return dict(rdf_obslist=rdf_obslist, original_obslist=original_obslist, geojson_levels=geojson_lvl, geojson_files=geojson_files)
    
    