import rumps
from urllib2 import Request, urlopen, URLError
import json
import requests
import os.path
import os
import time
from threading import Event, Thread

URL_MARKET = 'https://api.cryptowat.ch/markets/'


this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, "data", "lastState.json")

# check if data file with users preference exists, otherwise create one with
# btcusd and ethusd set as preferences
if os.path.isfile(DATA_PATH):
    with open(DATA_PATH, 'r') as fl:
        initialData = json.load(fl)

else:
    initialData = { 'results': [
    {'coin' : 'BTC', 'pair' : 'btcusd', 'market' : 'gdax'},
    {'coin' : 'ETH', 'pair' : 'ethusd', 'market' : 'gdax'}
    ] }
    with open(DATA_PATH, 'w') as fl:
        json.dump(initialData, fl)

def updateThread(interval, func, *args):
    stopped = Event()
    def loop():
        while not stopped.wait(interval): # the first call is in `interval` secs
            func(*args)
    Thread(target=loop).start()
    return stopped.set


class BarApp(rumps.App):

    def update(self):

        titleString = ""

        for coinData in initialData.get('results'):

            coin = coinData.get('coin')
            market = coinData.get('market')
            pair = coinData.get('pair')

            try:
                response = urlopen(URL_MARKET + market +'/'+pair+'/'+'summary').read()
                coinInfo = json.loads(response)
                coinPrice = coinInfo.get('result').get('price').get('last')
                coinChange = coinInfo.get('result').get('price').get('change').get('percentage')

                # to set color changing text later
                if (coinChange > 0.5):
                    titleString += "{} {} ".format(coin, coinPrice.__str__())
                elif (coinChange < -0.5):
                    titleString += "{} {} ".format(coin, coinPrice.__str__())
                else:
                    titleString += "{} {} ".format(coin, coinPrice.__str__())

            except URLError, e:
                print 'Error code:', e

        self.title = titleString

if __name__ == "__main__":
    app = BarApp('title')
    app.update()
    updateThread(10, app.update)
    app.run()
