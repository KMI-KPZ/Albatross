import os
        
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
    geojson_obslist = get_files("data/geojson/eurostats/")
    
    
    return dict(rdf_obslist=rdf_obslist, original_obslist=original_obslist, geojson_obslist=geojson_obslist)
    
    