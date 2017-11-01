import os

directory = os.path.join(os.path.dirname(__file__),'data/sandbox/eurostat/data/')
for filename in os.listdir(directory):
    print(filename)
    if filename.endswith(".rdf"): 
        print(os.path.join(directory, filename))
        #filename = filename.split('/')[-1]
        os.rename(os.path.join(directory, filename), os.path.join("data/rdf/eurostats/", filename))
    