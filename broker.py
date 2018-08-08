import time
from threading import Event, Thread

from PyQt5.QtCore import QObject, pyqtSignal
from coinbasepro.authenticated_client import AuthenticatedClient


class Broker(AuthenticatedClient, QObject):
    sigRateDiff = pyqtSignal("PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject")
    profileId = None
    dealingFlag = Event()

    def __init__(self, key, b64secret, passphrase, api_url="https://api.pro.coinbase.com", timeout=30):
        QObject.__init__(self)
        AuthenticatedClient.__init__(self, key, b64secret, passphrase, api_url="https://api.pro.coinbase.com",
                                     timeout=30)
        self.polling = Event()
        self.interestIn = ["BCH", "BTC", "LTC", "ETH"]
        self.products = {}
        self.wallet = {}
        self.initBroker()

    def initBroker(self):
        products = {}

        for account in self.get_accounts():
            self.wallet[account["currency"]] = account
            if self.profileId is None: self.profileId = account["profile_id"]

        for product in self.get_products():
            baseCurrency, quoteCurrency = product[u"id"].split("-")
            if baseCurrency not in self.interestIn or quoteCurrency not in self.interestIn: continue

            products[product[u"id"]] = {
                "from": product["base_currency"],
                "to": product["quote_currency"],
                "min": product["base_min_size"],
                "max": product["base_max_size"],
                "increment": product["quote_increment"],
            }

            lastDeals = self.get_fills(product_id=product[u"id"])[0]
            if len(lastDeals) > 0:
                products[product[u"id"]]["lastPrice"] = float(lastDeals[0]["price"])
            else:
                historicRates = self.get_product_historic_rates(product_id=product[u"id"], granularity=60)
                products[product[u"id"]]["lastPrice"] = historicRates[0][4]

            time.sleep(0.2)

        print(products)
        self.products = products
        return products

    @staticmethod
    def getCredentials(fn="./credentials.conf"):
        with open(fn) as of:
            return of.readline().split(":")

    @staticmethod
    def getSqlCredentials(fn="./sqlCredentials.conf"):
        with open(fn) as of:
            return of.readline().split(":")

    @staticmethod
    def get_change(current, previous):
        if current == 0:
            return -100
        elif previous == 0:
            return 100

        coefficient = 1
        if current > previous:
            coefficient = -1
            current, previous = previous, current
        return coefficient * ((current - previous) / current) * 100

    # def get_change(current, previous):
    #     return ((current - previous) / current) * 100

    def onRateDiff(self, product, diff, currentRates):
        pass

    def startPolling(self):
        self.polling.set()
        Thread(target=self._poll).start()

    def _poll(self):
        while self.polling.isSet():
            for product_id, product in self.products.items():
                poutput = self.get_product_trades(product_id=product_id, limit=1, result=[])
                currentRates = float(poutput[0]["price"])
                previousRates = product["lastPrice"]
                ratesDiff = Broker.get_change(currentRates, previousRates)
                self.onRateDiff(product_id, ratesDiff, [currentRates, previousRates])
                self.sigRateDiff.emit(product_id, ratesDiff, [currentRates, previousRates])
                time.sleep(0.25)
            time.sleep(1)
