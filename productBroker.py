import time
from threading import Event, Thread

import dateutil.parser
from PyQt5.QtCore import QObject, pyqtSignal
from coinbasepro.authenticated_client import AuthenticatedClient

from coinbaseClient import CoinbaseClient


class ProductBroker(AuthenticatedClient, CoinbaseClient, QObject):

    allowTrading = False
    sigRateDiff = pyqtSignal("PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject")

    def __init__(self, product, key, b64secret, passphrase):
        QObject.__init__(self)
        AuthenticatedClient.__init__(self, key, b64secret, passphrase, api_url="https://api.pro.coinbase.com",
                                     timeout=30)
        CoinbaseClient.__init__(self)
        self.product = product
        self.baseCurrency, self.quotedCurrency = product.split("-")
        self.wallet = {
            self.baseCurrency: None,
            self.quotedCurrency: None,
        }
        self.brokerDeals = {
            "opened": None,
            "closed": None
        }
        self.settings = {
            "info": {},
            "buy": {
                "allowTrade": False,
                "maxLife": 1800,
                "thresholdType": "percent",  # percent | scalar
                "thresholdValue": 0.3,
                "maxTradeRatio": 0.25,
                "post_only": True
            },
            "sell": {
                "allowTrade": False,
                "maxLife": 1800,
                "thresholdType": "percent",  # percent | scalar
                "thresholdValue": 0.3,
                "maxTradeRatio": 0.25,
                "post_only": True
            }
        }

        self.refreshProductInfo()
        self.refreshWallet()
        self.refreshDeals()
        # self.startPolling()

    def refreshProductInfo(self):
        for product in self.get_products():
            if product["id"] == self.product:
                for param in ['base_min_size', 'base_max_size', 'quote_increment', "min_market_funds",
                              "max_market_funds"]:
                    product[param] = float(product[param])

                self.settings["info"] = product

    def refreshWallet(self):
        for account in self.get_accounts():
            if account["currency"] == self.baseCurrency:
                self.wallet[self.baseCurrency] = account
            elif account["currency"] == self.quotedCurrency:
                self.wallet[self.quotedCurrency] = account

        for wallet in self.wallet.values():
            for param in ['balance', 'available', 'hold']:
                wallet[param] = float(wallet[param])

    def refreshDeals(self):
        opened, closed = [], []
        for order in self.get_orders()[0]:
            if order["product_id"] == self.product:
                opened.append(order)

        for fill in self.get_fills()[0]:
            if fill["product_id"] == self.product:
                closed.append(fill)

        self.brokerDeals = {
            "opened": opened,
            "closed": closed
        }

    def baseWallet(self):
        return self.wallet[self.baseCurrency]

    def quotedWallet(self):
        return self.wallet[self.quotedCurrency]

    def onRateDiff(self, lastMarketTrade):

        currentRate = float(lastMarketTrade["price"])
        lastBrokerRate = float(self.brokerDeals["closed"][0]["price"])
        rateDiff, rateDiffPercent = self.get_change(currentRate, lastBrokerRate)
        self.sigRateDiff.emit(self, rateDiff, rateDiffPercent, currentRate, lastBrokerRate)

        if len(self.brokerDeals["opened"]) > 0: return
        deal = self.checkDeal(rateDiff, rateDiffPercent, currentRate, lastBrokerRate)

        if deal is not None:
            if deal["side"] == "buy":
                self.buy(deal)
            elif deal["side"] == "sell":
                self.sell(deal)

    def checkDeal(self, rateDiff, rateDiffPercent, currentRate, lastBrokerRate):
        deal = None
        if currentRate < lastBrokerRate:
            condA = self.settings["buy"]["thresholdType"] == "percent"
            condB = abs(rateDiffPercent) >= self.settings["buy"]["thresholdValue"]
            condC = self.settings["buy"]["thresholdType"] == "scalar"
            condD = abs(rateDiff) >= self.settings["buy"]["thresholdValue"]
            if (condA and condB) or (condC and condD):
                deal = self.prepareSellOrder(currentRate)
        elif currentRate > lastBrokerRate:
            condA = self.settings["sell"]["thresholdType"] == "percent"
            condB = abs(rateDiffPercent) >= self.settings["sell"]["thresholdValue"]
            condC = self.settings["sell"]["thresholdType"] == "scalar"
            condD = abs(rateDiff) >= self.settings["sell"]["thresholdValue"]
            if (condA and condB) or (condB and condC):
                deal = self.prepareBuyOrder(currentRate)

        return deal

    def prepareBuyOrder(self, currentRate):
        if not self.settings["buy"]["allowTrade"]: return False

        dealParameters = self._initEmptyDeal("buy", currentRate)
        dealParameters["price"] -= 0.00001
        self.refreshWallet()

        baseWallet, quotedWallet = self.baseWallet(), self.quotedWallet()
        maxTradeRatio = self.settings["buy"]["maxTradeRatio"]
        minimumAmount = self.settings["info"]["base_min_size"]
        baseBuySize = baseWallet["available"] * maxTradeRatio

        if baseBuySize < minimumAmount:
            return None
        if baseBuySize * dealParameters["price"] > baseWallet["available"]:
            return None

        dealParameters["size"] = baseBuySize

        return dealParameters

    def prepareSellOrder(self, currentRate):
        if not self.settings["sell"]["allowTrade"]: return False

        dealParameters = self._initEmptyDeal("sell", currentRate)
        dealParameters["price"] += 0.00001
        self.refreshWallet()

        baseWallet, quotedWallet = self.baseWallet(), self.quotedWallet()
        maxTradeRatio = self.settings["sell"]["maxTradeRatio"]
        minimumAmount = self.settings["info"]["base_min_size"]
        baseSellSize = baseWallet["available"] * maxTradeRatio

        if baseSellSize < minimumAmount:
            return None
        dealParameters["size"] = baseSellSize

        return dealParameters

    def _initEmptyDeal(self, orderType, currentRate):
        return {
            "price": currentRate,
            "size": None,
            "product_id": self.product,
            "post_only": self.settings[orderType]["post_only"],
            "side": orderType,
        }

    # Static methods -------------------------------------------------------------------

    @staticmethod
    def getCredentials(fn="./credentials.conf"):
        with open(fn) as of:
            return of.readline().split(":")

    @staticmethod
    def getSqlCredentials(fn="./sqlCredentials.conf"):
        with open(fn) as of:
            return of.readline().split(":")
