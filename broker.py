import datetime
import time
from threading import Event, Thread

import pymysql
from PyQt5.QtCore import QObject, pyqtSignal
from coinbasepro.authenticated_client import AuthenticatedClient


class Broker(AuthenticatedClient, QObject):
    interest = 0.1
    sigRateDiff = pyqtSignal("PyQt_PyObject", "PyQt_PyObject")

    def __init__(self, key, b64secret, passphrase, api_url="https://api.pro.coinbase.com", timeout=30):
        QObject.__init__(self)
        AuthenticatedClient.__init__(self, key, b64secret, passphrase, api_url="https://api.pro.coinbase.com",
                                     timeout=30)
        self.polling = Event()
        self.interestIn = ["BCH", "BTC", "LTC", "ETH"]
        self.products = self.initProducts()

    def initProducts(self):
        products = {}
        user, passwd = self.getSqlCredentials()
        conn = pymysql.connect(host='localhost', port=3306, user=user, passwd=passwd, db='cbmarian')
        cur = conn.cursor()

        for product in self.get_products():
            A, B = product[u"id"].split("-")
            if A not in self.interestIn or B not in self.interestIn: continue

            products[product[u"id"]] = {
                "from": product["base_currency"],
                "to": product["quote_currency"],
                "min": product["base_min_size"],
                "max": product["base_max_size"],
                "increment": product["quote_increment"],
                "currentDiff": 0,
            }

            tickTableName = product[u"id"].replace("-", "_")
            cur.execute("select * from {0}_tick order by dt DESC limit 1".format(tickTableName))
            fetch = cur.fetchmany(1)
            products[product[u"id"]]["lastTradeTime"] = fetch[0][0]
            products[product[u"id"]]["lastTrade"] = {}

            startDt = datetime.datetime.fromtimestamp(products[product[u"id"]]["lastTradeTime"]).isoformat()
            endDt = datetime.datetime.fromtimestamp(products[product[u"id"]]["lastTradeTime"] + 3600).isoformat()
            historicRates = self.get_product_historic_rates(product_id=product[u"id"], start=startDt, end=endDt,
                                                            granularity=60)
            for rates in historicRates:
                if rates[0] >= products[product[u"id"]]["lastTradeTime"]:
                    products[product[u"id"]]["lastTrade"] = rates[1:5]
                    print(products[product[u"id"]]["lastTradeTime"], rates)
                    break
            time.sleep(0.2)

        conn.close()
        return products

    @staticmethod
    def getCredentials(fn="./credentials.conf"):
        with open(fn) as of:
            return of.readline().split(":")

    @staticmethod
    def getSqlCredentials(fn="./sqlCredentials.conf"):
        with open(fn) as of:
            return of.readline().split(":")

    def startPolling(self):
        self.polling.set()
        Thread(target=self._poll).start()

    @staticmethod
    def get_change(current, previous):
        print(current, previous)
        return 100. * (previous - current) / current

    def onRateDiff(self, product, diff):
        pass
        # print(product, diff)

    def _poll(self):
        while self.polling.isSet():
            for product_id, product in self.products.items():
                poutput = self.get_product_historic_rates(product_id=product_id, granularity=60)
                if len(poutput) == 0: continue
                # try:
                currentRates = poutput[0][1:5]
                previousRates = product["lastTrade"]
                ratesDiff = [Broker.get_change(v, previousRates[i]) for i, v in enumerate(currentRates)]
                self.onRateDiff(product_id, ratesDiff)
                self.sigRateDiff.emit(product_id, ratesDiff)
                # except:
                #     pass
                time.sleep(1)
