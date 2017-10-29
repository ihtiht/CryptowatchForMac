import rumps
from urllib2 import Request, urlopen, URLError
import json
import requests
import os.path

# check if data file with users preference exists, otherwise create one with
# btcusd and ethusd set as preferences
if os.path.isfile('data/lastState.json'):

else:

    initialData = { 'results': [
    {'coin' : 'BTC', 'pair' : 'btcusd', 'market' : 'gdax'},
    {'coin' : 'ETH', 'pair' : 'ethusd', 'market' : 'gdax'} ]
    }
    with open('data/lastState.json', 'w') as file:
        json.dump(initialData, file)

class BarApp(rumps.App):

    @rumps.clicked("Update")
    def update(self, _):

        try:
            response = urlopen('https://api.cryptowat.ch/markets/gdax/btcusd/price').read()
            BTCPriceInfo = json.loads(response)
            BTCPrice = BTCPriceInfo.get('result').get('price')
            self.title = "BTC " + BTCPrice.__str__()

        except URLError, e:
            print 'Error code:', e

if __name__ == "__main__":
    app = BarApp('title', menu = ['Update'])
    app.run()
