import rumps
import time
import requests
from urllib2 import Request, urlopen, URLError
import json
from . import database as db
from . import config

# Cryptowatch API links
URL_MARKET = 'https://api.cryptowat.ch/markets'


class CryptoBar(rumps.App):

    # timer needs to be available across class to set/reset
    main_update_time = 10
    menu_update_time = 3600

    main_update_timer = None
    menu_update_timer = None

    last_update_time = None

    # main data to store selected cryptos
    main_data = None


    # Overriding rumps setup for initialization
    def __init__(self, *args, **kwargs):
        super(CryptoBar, self).__init__(*args, **kwargs)

        self.main_data = db.getCoinData()
        self.setConfig()

        self.setTimer()
        # initalize menu and title
        self.menuUpdate()
        self.mainUpdate()

    # timers setup, to be run after initialization
    def setTimer(self):
        # set timers
        self.main_update_timer = rumps.Timer(callback = self.mainUpdate,
            interval = self.main_update_time).start()
        self.menu_update_timer = rumps.Timer(callback = self.menuUpdate,
            interval = self.menu_update_time).start()

    # set global timer variables from configuration
    def setConfig(self):
        # get config information from config.py
        self.main_update_time = int(config.getConfigData('TIMERS', 'main_update_time'))
        self.menu_update_time = int(config.getConfigData('TIMERS', 'menu_update_time'))
        self.last_update_time = config.getConfigData('TIMERS', 'last_update_time')

    # update the titleString with new price
    def mainUpdate(self):
        titleString = ""

        # check every coin in main_data
        for coinData in self.main_data.get('results'):

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
        db.writeToMenu(marketDictionary)
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
        if self.menu.has_key('Markets'):
            del self.menu['Markets']

        # to quit application
        if not self.menu.has_key('Quit'):
            self.menu.add(rumps.MenuItem('Quit', callback = rumps.quit_application))
            self.menu.insert_before('Quit', None)

        # initalize preferences
        if not self.menu.has_key('Preferences...'):
            self.menu.insert_before('Quit', rumps.MenuItem('Preferences...'))
            self.menu.insert_after('Preferences...', None)
            self.setPreferences()

        # markets submenu setup
        self.menu.insert_before('Preferences...', rumps.MenuItem('Markets'))
        self.menu['Markets'].update(menuArray)
        self.menu.insert_after('Markets', None)

    # setup preferences menu and initalize timers
    def setPreferences(self):
        # make menu items for a list of times and add them to the menu
        # changing times here won't affect the original times, will have to
        # redifine in callbacks too
        mainUpdateTimes = [rumps.MenuItem(time, callback = self.onMainTimeClick)
        for time in ['5 sec', '10 sec', '30 sec', '60 sec']]
        menuUpdateTimes = [rumps.MenuItem(time, callback = self.onMenuTimeClick)
        for time in ['30 min', '1 hour', '2 hours', 'on startup only']]

        self.menu.insert_after('Preferences...', rumps.MenuItem('Price update time'))
        self.menu['Price update time'].update(mainUpdateTimes)

        self.menu.insert_after('Price update time', rumps.MenuItem('Menu update time'))
        self.menu['Menu update time'].update(menuUpdateTimes)

    # change Main time update in config file and in the script
    def onMainTimeClick(self, sender):
        print 'Click'

    # change Menu time update in config file and in the script
    def onMenuTimeClick(self, sender):
        print 'Click'

    # reset states on menu update
    def resetStates(self):
        # main_data is available across application
        # check every coin in main_data
        for coinData in self.main_data.get('results'):

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
        for i in xrange(len(self.main_data.get('results'))):

            # get pair and check for title and state 0
            pair = self.main_data.get('results')[i].get('pair')
            market = self.main_data.get('results')[i].get('market')

            # delete from main_data if conditions are met
            if ((pair.upper() == title) and
                (self.menu['Markets'][market.title()][pair.upper()].state == 0)):
                del self.main_data.get('results')[i]
                removedMarket = market.title()
                break

        self.mainUpdate()
        # check if the market from which the pair was removed still has a
        # pair to put a marker
        self.menu['Markets'][removedMarket].state = 0

        for pair in self.menu['Markets'][removedMarket].viewkeys():
            if self.menu['Markets'][removedMarket][pair].state == 1:
                self.menu['Markets'][removedMarket].state = -1
                break

        # overwrite new data to file
        db.writeToData(self.main_data)

    # add an item to database
    def addData(self, title):
        # iterate over markets and check if they have the pairs
        # if true, check if the pair for the market is already in database
        for market in self.menu['Markets'].viewkeys():
            # to keep check if it was in data or not
            check = False

            if (self.menu['Markets'][market].has_key(title) and self.menu['Markets'][market][title].state == 1):

                for i in xrange(len(self.main_data.get('results'))):
                    # get pair and check if it's same
                    checkPair = self.main_data.get('results')[i].get('pair')
                    checkMarket = self.main_data.get('results')[i].get('market')

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

                    self.main_data.get('results').append({'coin':mCoin.upper(),'pair':title.lower(),'market':market.lower()})
                    self.menu['Markets'][market].state = -1

                    self.mainUpdate()
                    db.writeToData(self.main_data)
                    break
