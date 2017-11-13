import os
import json


# to get data from json database file
def getMainData(path):
    # database file included with build
    if os.path.isfile(path):
        with open(path, 'r') as fl:
            # data contains which coins are actually selected
            data = json.load(fl)
            return data

    # if file not found, create an initial setup file
    else:
        data = { 'results': [
        {'coin' : 'BTC', 'pair' : 'btcusd', 'market' : 'gdax'},
        {'coin' : 'ETH', 'pair' : 'ethusd', 'market' : 'gdax'}
        ] }
        with open(path, 'w') as fl:
            json.dump(data, fl)
        return data


# write data to json database file
def writeToFile(path, data):
    # overwrite new data to file
    with open(path, 'w') as fl:
        json.dump(data, fl)
