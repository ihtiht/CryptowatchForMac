import rumps
import time
import sys
import ssl

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

try:
    from urllib.error import URLError as urlerror
except ImportError:
    from urllib2 import URLError as urlerror

import json
from . import database as db
from . import config

# Cryptowatch API links
URL_MARKET = 'https://api.cryptowat.ch/markets'

# TODO:
# sort timers
# working menu update
# last time update to limit market info requests
# multiple coins
# formatting for coins displayed in scientific notation
# network handler class to handle network exceptions
# release ;)

class CryptoBar(rumps.App):

     # timer needs to be available across class to set/reset
     main_update_time = None
     menu_update_time = None

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

         # initalize menu and title
         self.menuUpdate()
         self.mainUpdate()

         self.setTimer()

     # timers setup, to be run after initialization
     def setTimer(self):
         # set timers
         self.main_update_timer = rumps.Timer(self.mainUpdate,
             self.main_update_time)
         self.menu_update_timer = rumps.Timer(self.menuUpdate,
             self.menu_update_time)
         self.main_update_timer.start()
         self.menu_update_timer.start()
         print(rumps.timers())

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
                 ssl._create_default_https_context = ssl._create_unverified_context
                 response = urlopen(URL_MARKET +'/'+ market +'/'+pair+'/'+'summary').read()
                 coinInfo = json.loads(response)
                 coinPrice = coinInfo.get('result').get('price').get('last')
                 titleString += "{} {} ".format(coin, coinPrice)

             except urlerror as e:
                 print ('Error code:', e)

         self.title = titleString

     # update the available markets
     def menuUpdate(self):
         # will store markets and corresponding pairs for market
         marketDictionary = {}

         try:
             # get all markets and pairs from the API
             ssl._create_default_https_context = ssl._create_unverified_context
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
                 if not marketExchange in marketDictionary :
                     marketDictionary[marketExchange] = []
                     marketDictionary.get(lastExchange).sort()

                 # add the pair in the array
                 pairArray = marketDictionary.get(marketExchange)
                 pairArray.append(marketPair)

                 # store last exchange to sort its pairs when we move to a
                 # different exchange
                 lastExchange = marketExchange

             marketDictionary.get(lastExchange).sort()

         except urlerror as e:
             print ('Error code:', e)

         # sorted market List
         marketKeyList = marketDictionary.keys()
         marketKeyList = sorted(marketKeyList)

         # menuArray stores the final arrays,
         menuArray = []

         # iterate over the exchanges and add an exchange menu item
         for key in marketKeyList:
             # initalize temporary arrays to store the Menu Items
             subMenuArray = []
             subPairArray = []

             subMenuArray.append(rumps.MenuItem(key.title()))

             # iterate over pairs and add pairs in exchange submenu
             for pair in marketDictionary.get(key):
                 pair = pair.upper()
                 subPairArray.append(rumps.MenuItem(pair, callback = self.onPairClick))

             # add the exchange (key) and corresponding submenu
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
         # markets submenu setup
         if 'Markets' in self.menu:
             self.menu['Markets'].clear()
             self.menu['Markets'].update(menuArray)
         else:
             self.menu.add(rumps.MenuItem('Markets'))
             self.menu['Markets'].update(menuArray)
             self.menu.add(None)

         # initalize preferences
         if not 'Preferences...' in self.menu:
             self.menu.add(rumps.MenuItem('Preferences...'))
             self.setPreferences()
             self.menu.add(None)

         # to quit application
         if not 'Quit' in self.menu:
             self.menu.add(None)
             self.menu.add(rumps.MenuItem('Quit', callback = rumps.quit_application))

     # setup preferences menu and initalize timers
     def setPreferences(self):
         # make menu items for a list of times and add them to the menu
         # changing times here won't affect the original times, will have to
         # redefine in callbacks too
         mainUpdateTimes = [rumps.MenuItem(time, callback = self.onMainTimeClick)
         for time in ['5 sec', '10 sec', '30 sec', '60 sec']]
         menuUpdateTimes = [rumps.MenuItem(time, callback = self.onMenuTimeClick)
         for time in ['30 min', '1 hour', '2 hours', 'on startup only']]

         self.menu.add(rumps.MenuItem('Price update time'))
         self.menu['Price update time'].update(mainUpdateTimes)

         self.menu.add(rumps.MenuItem('Menu update time'))
         self.menu['Menu update time'].update(menuUpdateTimes)

         self.menu['Price update time'][self.main_update_time.__str__() + ' sec'].state = 1

         if self.menu_update_time == 1800:
             self.menu['Menu update time']['30 min'].state = 1
         elif self.menu_update_time == 3600:
             self.menu['Menu update time']['1 hour'].state = 1
         elif self.menu_update_time == 7200:
             self.menu['Menu update time']['2 hours'].state = 1
         else:
             self.menu['Menu update time']['on startup only'] = 1

     # change Main time update in config file and in the script
     def onMainTimeClick(self, sender):
         # set states to 0, then set senders state to 1
         for key in self.menu['Price update time']:
             self.menu['Price update time'][key].state = 0

         self.menu['Price update time'][sender.title].state = 1
         config.writeToFile('TIMERS', 'main_update_time', sender.title.split()[0])
         self.main_update_timer.interval = sender.title.split()[0]

     # change Menu time update in config file and in the script
     def onMenuTimeClick(self, sender):
         print ('click')

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
             self.menu['Markets'][market.title()].state = 1

     # remove an item from database
     def removeData(self, title):
         # iterate over main data and check if state for a pair with title
         # sender is now 0
         # to keep count, makes removing element easier
         i = 0;
         for coinData in self.main_data.get('results'):
             # get pair and check for title and state 0
             pair = coinData.get('pair')
             market = coinData.get('market')

             # delete from main_data if conditions are met
             if ((pair.upper() == title) and
                 (self.menu['Markets'][market.title()][pair.upper()].state == 0)):
                 del self.main_data.get('results')[i]
                 removedMarket = market.title()
                 break
             else:
                 i += 1

         self.mainUpdate()
         # check if the market from which the pair was removed still has a
         # pair to put a marker
         self.menu['Markets'][removedMarket].state = 0

         for pair in self.menu['Markets'][removedMarket]:
             if self.menu['Markets'][removedMarket][pair].state == 1:
                 self.menu['Markets'][removedMarket].state = 1
                 break

         # overwrite new data to file
         db.writeToData(self.main_data)

     # add an item to database
     def addData(self, title):
         # iterate over markets and check if they have the pairs
         # if true, check if the pair for the market is already in database
         for market in self.menu['Markets']:
             # to keep check if it was in data or not
             check = False

             if (title in self.menu['Markets'][market] and self.menu['Markets'][market][title].state == 1):

                 for coinData in self.main_data.get('results'):
                     # get pair and check if it's same
                     checkPair = coinData.get('pair')
                     checkMarket = coinData.get('market')

                     if (checkMarket.title() == market and checkPair.upper() == title):
                         check = True
                         break

                 # if no match was found
                 if (check == False):
                     # to seperate the coin we want vs what it's compared against
                     coinsArray = ['USD', 'USDT', 'BTC', 'ETH', 'JPY', 'KRW', '',
                         'AUD', 'EUR', 'CNY', 'RUR', 'GBP', 'CAD', 'ZAR', 'MEX',
                         'XMR', 'SGD', 'HKD', 'IDR', 'INR', 'PHP']

                     for coin in coinsArray:
                         # greater than 1 ensures we don't split from the coin we want
                         if title.find(coin) > 1:
                             index = title.find(coin)
                             mCoin = title[0:index]
                             break

                     self.main_data.get('results').append({'coin':mCoin.upper(),'pair':title.lower(),'market':market.lower()})
                     self.menu['Markets'][market].state = 1

                     self.mainUpdate()
                     db.writeToData(self.main_data)
                     break
