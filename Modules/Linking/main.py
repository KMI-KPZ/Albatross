import tornado
import tornado.ioloop
import tornado.web
import os, uuid

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
        if(str(os.path.basename(file).split('.')[1]) == 'xml'):
            observation['id'] = observation_name
            observation['url'] = prefix + file
            observation_list.append(observation)
    return observation_list


def return_view_args():
    files = get_files("services/limes")
    return dict(files=files)
