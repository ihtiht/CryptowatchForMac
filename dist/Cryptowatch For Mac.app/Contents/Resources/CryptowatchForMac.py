import rumps
import json
import re
import os.path
import os
import time
import requests
from urllib2 import Request, urlopen, URLError
from threading import Event, Thread

# Cryptowatch API links
URL_MARKET = 'https://api.cryptowat.ch/markets'

# path for lastState.json file in app's contents
this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, "data", "lastState.json")

# data_file included with build
if os.path.isfile(DATA_PATH):
    with open(DATA_PATH, 'r') as fl:
        # mainData contains which coins are actually selected
        mainData = json.load(fl)

# if file not found, create a file in data path (if the user doesn't run build)
else:
    mainData = { 'results': [
    {'coin' : 'BTC', 'pair' : 'btcusd', 'market' : 'gdax'},
    {'coin' : 'ETH', 'pair' : 'ethusd', 'market' : 'gdax'}
    ] }
    with open(DATA_PATH, 'w') as fl:
        json.dump(mainData, fl)

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

        # check every coin in mainData
        for coinData in mainData.get('results'):

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
                    titleString += "{} {} ".format(coin, coinPrice)
                elif (coinChange < -0.5):
                    titleString += "{} {} ".format(coin, coinPrice)
                else:
                    titleString += "{} {} ".format(coin, coinPrice)

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
            lastExchange = (marketInfo.get('result'))[0].get('exchange')

            # iterate over the JSON data and get exchange and pair
            for market in marketInfo.get('result'):
                marketExchange = market.get('exchange')
                marketPair = market.get('pair')

                # if the exchange is not already in the dictionary, add
                # it and set value to an empty array; sort last exchange's pairs
                if not marketDictionary.has_key(marketExchange):
                    marketDictionary[marketExchange] = []
                    marketDictionary.get(lastExchange).sort()

                # add the pair in the array
                pairArray = marketDictionary.get(marketExchange)
                pairArray.append(marketPair)

                # store last exchange to sort its pairs when we move to a
                # different exchange
                lastExchange = marketExchange

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
                subPairArray.append(rumps.MenuItem(pair, callback = self.onPairClick))

            # add the exchange (key) and corresponding sub-menu
            # to the main menu
            subMenuArray.append(subPairArray)
            menuArray.append(subMenuArray)

        # check for current values and update list accordingly
        self.setMenu(menuArray)
        # set states of selected coins on update as on
        self.resetStates()

    # if a pair item is clicked
    def onPairClick(self, sender):
        sender.state = not sender.state
        if (sender.state == 0):
            self.removeData(sender.title)
        else:
            self.addData(sender.title)


    # menu setup on update
    def setMenu(self, menuArray):
        self.menu.clear()

        # markets submenu setup
        self.menu.add(rumps.MenuItem('Markets'))
        self.menu['Markets'].update(menuArray)
        self.menu.insert_after('Markets', None)

        # to quit application
        self.menu.add(rumps.MenuItem('Quit', callback = rumps.quit_application))


    # reset states on menu update
    def resetStates(self):
        # mainData is available across application
        # check every coin in mainData
        for coinData in mainData.get('results'):

            coin = coinData.get('coin')
            market = coinData.get('market')
            pair = coinData.get('pair')

            # get submenu pair of submenu exchange of submenu markets of main menu
            # basically checking what coins are selcted and setting them to on
            self.menu['Markets'][market.title()][pair.upper()].state = 1
            self.menu['Markets'][market.title()].state = -1


    # remove an item from database
    def removeData(self, title):
        # iterate over main data and check if state for a pair with title
        # sender is now 0
        for i in xrange(len(mainData.get('results'))):

            # get pair and check for title and state 0
            pair = mainData.get('results')[i].get('pair')
            market = mainData.get('results')[i].get('market')

            # delete from mainData if conditions are met
            if ((pair.upper() == title) and
                (self.menu['Markets'][market.title()][pair.upper()].state == 0)):
                del mainData.get('results')[i]
                removedMarket = market.title()
                break

        self.mainUpdate()
        # check if the market from which the pair was removed still has a
        # pair to put a marker
        self.menu['Markets'][removedMarket].state = 0

        for pair in self.menu['Markets'][removedMarket].viewkeys():
            if (self.menu['Markets'][removedMarket][pair].state == 1):
                self.menu['Markets'][removedMarket].state = -1
                break

        # overwrite new data to file
        with open(DATA_PATH, 'w') as fl:
            json.dump(mainData, fl)


    # add an item to database
    def addData(self, title):
        # iterate over markets and check if they have the pairs
        # if true, check if the pair for the market is already in database
        for market in self.menu['Markets'].viewkeys():
            # to keep check if it was in data or not
            check = False

            if (self.menu['Markets'][market].has_key(title) and self.menu['Markets'][market][title].state == 1):

                for i in xrange(len(mainData.get('results'))):
                    # get pair and check if it's same
                    checkPair = mainData.get('results')[i].get('pair')
                    checkMarket = mainData.get('results')[i].get('market')

                    if (checkMarket == market and checkPair == title):
                        check = True
                        break

                # if no match was found
                if (check == False):
                    # to seperate the coin we want vs what it's compared against
                    coinsArray = ['USD', 'USDT', 'BTC', 'ETH', 'JPY', 'KRW', '-',
                        'AUD', 'EUR', 'CNY', 'RUR', 'GBP', 'CAD', 'ZAR', 'MEX',
                        'XMR', 'SGD', 'HKD', 'IDR', 'INR', 'PHP']

                    for coin in coinsArray:
                        # greater than 1 ensures we don't split from the coin we want
                        if title.find(coin) > 1:
                            index = title.find(coin)
                            mCoin = title[0:index]
                            break

                    mainData.get('results').append({'coin':mCoin.upper(),'pair':title.lower(),'market':market.lower()})
                    self.menu['Markets'][market].state = -1

                    self.mainUpdate()
                    # overwrite new data to file
                    with open(DATA_PATH, 'w') as fl:
                        json.dump(mainData, fl)
                    break



if __name__ == "__main__":

    # app setup and initialization
    menuArray = []

    app = BarApp('Cryptowatch', quit_button = None)
    app.menuUpdate()
    app.mainUpdate()

    # run update thread for titleString update (every 10 sec)
    # and menuUpdate (every hour). The menu doesn't need to be updated
    # that often since markets and pairs are added/removed very infrequently
    updateThread(10, app.mainUpdate)
    updateThread(3600, app.menuUpdate)

    # start app with update threads running in background
    app.run()
