import os
import sys
import json

# data path to database.json
root_dir = os.path.dirname(sys.modules['__main__'].__file__)
data_path = os.path.join(root_dir, "data", "database.json")
markets_path = os.path.join(root_dir, "data", "markets.json")

# to get data from json database file
def getCoinData():
    # database file included with build
     if os.path.isfile(data_path):
         with open(data_path, 'r') as fl:
             # data contains which coins are actually selected
             data = json.load(fl)
             return data
     # if file not found, create an initial setup file
     else:
         data = { 'results': [
         {'coin' : 'BTC', 'pair' : 'btcusd', 'market' : 'gdax'},
         {'coin' : 'ETH', 'pair' : 'ethusd', 'market' : 'gdax'}
         ] }
         with open(data_path, 'w') as fl:
             json.dump(data, fl)
         return data

# write data to json database file
def writeData(data):
     # overwrite new data to file
     with open(data_path, 'w') as fl:
         json.dump(data, fl)

# write data to markets file
def writeMarkets(data):
     # overwrite new data to file
     with open(markets_path, 'w') as fl:
         json.dump(data, fl)
