import rumps
from urllib2 import Request, urlopen, URLError
import json
import requests
import re
import os.path
import os
import time
from threading import Event, Thread

# Cryptowatch API links
URL_MARKET = 'https://api.cryptowat.ch/markets'

# path for lastState.json file in app's contents
this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, "data", "lastState.json")

# data_file included with build
if os.path.isfile(DATA_PATH):
    with open(DATA_PATH, 'r') as fl:
        initialData = json.load(fl)

# if file not found, create a file in data path (if the user doesn't run build)
else:
    initialData = { 'results': [
    {'coin' : 'BTC', 'pair' : 'btcusd', 'market' : 'gdax'},
    {'coin' : 'ETH', 'pair' : 'ethusd', 'market' : 'gdax'}
    ] }
    with open(DATA_PATH, 'w') as fl:
        json.dump(initialData, fl)

# thread to run a function after every interval
def updateThread(interval, func, *args):
    stopped = Event()
    def loop():
        while not stopped.wait(interval): # the first call is in `interval` secs
            func(*args)
    Thread(target=loop).start()
    return stopped.set


class BarApp(rumps.App):

    # update the titleString with new price
    def mainUpdate(self):

        titleString = ""

        # check every coin in initialData
        for coinData in initialData.get('results'):

            coin = coinData.get('coin')
            market = coinData.get('market')
            pair = coinData.get('pair')

            try:
                response = urlopen(URL_MARKET +'/'+ market +'/'+pair+'/'+'summary').read()
                coinInfo = json.loads(response)
                coinPrice = coinInfo.get('result').get('price').get('last')
                coinChange = coinInfo.get('result').get('price').get('change').get('percentage')

                # to set color changing text later, green if price is greater
                # than 24h old price by 0.5%, red if lower than old price by -0.5%
                if (coinChange > 0.5):
                    titleString += "{} {} ".format(coin, coinPrice.__str__())
                elif (coinChange < -0.5):
                    titleString += "{} {} ".format(coin, coinPrice.__str__())
                else:
                    titleString += "{} {} ".format(coin, coinPrice.__str__())

            except URLError, e:
                print 'Error code:', e

        self.title = titleString

    # update the available markets
    def menuUpdate(self):

        # will store markets and corresponding pairs for market
        marketDictionary = {}

        try:
            # get all markets and pairs from the API
            respone = urlopen(URL_MARKET).read()
            marketInfo = json.loads(respone)

            # initalize lastExchange for first run
            lastExchange = (marketInfo.get('result'))[0].get('exchange').__str__()

            # iterate over the JSON data and get exchange and pair
            for market in marketInfo.get('result'):
                marketExchange = market.get('exchange')
                marketPair = market.get('pair')

                # if the exchange is not already in the dictionary, add
                # it and set value to an empty array; sort last exchange's pairs
                if not marketDictionary.has_key(marketExchange.__str__()):
                    marketDictionary[marketExchange.__str__()] = []
                    marketDictionary.get(lastExchange).sort()

                # add the pair in the array
                pairArray = marketDictionary.get(marketExchange.__str__())
                pairArray.append(marketPair.__str__())

                # store last exchange to sort its pairs when we move to a
                # different exchange
                lastExchange = marketExchange.__str__()

            marketDictionary.get(lastExchange).sort()

        except URLError, e:
            print 'Error code:', e

        # sorted market List
        marketKeyList = marketDictionary.keys()
        marketKeyList.sort()

        # menuArray stores the final arrays,
        menuArray = []

        # iterate over the exchanges and add an exchange menu item
        for key in marketKeyList:
            # initalize temporary arrays to store the Menu Items
            subMenuArray = []
            subPairArray = []

            subMenuArray.append(rumps.MenuItem(key.title()))

            # iterate over pairs and add pairs in exchange sub-menu
            for pair in marketDictionary.get(key):
                pair = pair.upper()
                subPairArray.append(rumps.MenuItem(pair))

            # add the exchange (key) and corresponding sub-menu
            # to the main menu
            subMenuArray.append(subPairArray)
            menuArray.append(subMenuArray)

        # check for current values and update list accordingly
        if self.menu.has_key('Markets'):
            del self.menu['Markets']

        if self.menu.has_key('Quit'):
            self.menu.insert_before('Quit',rumps.MenuItem('Markets'))
            self.menu.insert_after('Markets', None)
            self.menu['Markets'].update(menuArray)
        else:
            self.menu.add(rumps.MenuItem('Markets'))
            self.menu.insert_after('Markets', None)
            self.menu['Markets'].update(menuArray)


if __name__ == "__main__":

    # app setup and initialization
    menuArray = []

    app = BarApp('Cryptowatch')
    app.menuUpdate()
    app.mainUpdate()

    # run update thread for titleString update (every 10 sec)
    # and menuUpdate (every hour). The menu doesn't need to be updated
    # that often since markets and pairs are added/removed very infrequently
    updateThread(10, app.mainUpdate)
    updateThread(15, app.menuUpdate)

    # start app with update threads running in background
    app.run()
