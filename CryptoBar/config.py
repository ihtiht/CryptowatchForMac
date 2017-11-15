import os
import sys
import json

# data path to database.json
root_dir = os.path.dirname(sys.modules['__main__'].__file__)
data_path = os.path.join(root_dir, "configuration", "config.json")

# read and return the required data, will send as string
def getConfigData(section, var):
    with open(data_path, 'r') as fl:
        # data contains the config information
        data = json.load(fl)
    return data.get(section).get(var)

# write data to configuration file
def writeToFile(section, var, data):
    with open(data_path, 'r') as fl:
        # data contains which coins are actually selected
        data = json.load(fl)
    del data[section][var]
    data.get(section).append({var : data})
