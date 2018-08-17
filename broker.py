import datetime

import dateutil.parser
from PyQt5.QtCore import QObject, pyqtSignal
from coinbasepro.authenticated_client import AuthenticatedClient

class Broker(AuthenticatedClient, QObject):
    allowTrading = True
    sigRateDiff = pyqtSignal("PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject")
    sigDealsRefresh = pyqtSignal("PyQt_PyObject")
    sigWalletRefresh = pyqtSignal("PyQt_PyObject")

    def __init__(self, product, key, b64secret, passphrase):
        QObject.__init__(self)
        AuthenticatedClient.__init__(self, key, b64secret, passphrase, api_url="https://api.pro.coinbase.com",
                                     timeout=30)
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
                "allowTrade": True,
                "maxLife": 120,
                "thresholdType": "percent",  # percent | scalar
                "thresholdValue": 0.3,
                "maxTradeRatio": 0.25,
                "allowMinimumTrade": False,
                "post_only": False
            },
            "sell": {
                "allowTrade": True,
                "maxLife": 120,
                "thresholdType": "percent",  # percent | scalar
                "thresholdValue": 0.3,
                "maxTradeRatio": 0.3,
                "allowMinimumTrade": False,
                "post_only": False
            }
        }

        self.refreshProductInfo()
        self.refreshWallet()
        self.refreshDeals()

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

        self.sigWalletRefresh.emit(self.wallet)

    def refreshDeals(self):
        opened, closed = [], []
        for order in self.get_orders(product_id=self.product)[0]:
            opened.append(order)

        for fill in self.get_fills(product_id=self.product)[0]:
            closed.append(fill)

        self.brokerDeals = {
            "opened": opened,
            "closed": closed
        }

        self.sigDealsRefresh.emit(self.brokerDeals)

    def baseWallet(self):
        return self.wallet[self.baseCurrency]

    def quotedWallet(self):
        return self.wallet[self.quotedCurrency]

    def onRateDiff(self, lastMarketTrade):
        pass

    def checkDeal(self, rateDiff, rateDiffPercent, currentRate, lastBrokerRate):
        pass

    def prepareBuyOrder(self, currentRate):
        if not self.settings["buy"]["allowTrade"]: return False

        dealParameters = self._initEmptyDeal("buy", currentRate)
        # dealParameters["price"] -= 0.00001
        self.refreshWallet()

        quotedWallet = self.quotedWallet()
        maxTradeRatio = self.settings["buy"]["maxTradeRatio"]
        minimumAmount = self.settings["info"]["base_min_size"]
        baseBuySize = round((quotedWallet["available"] * maxTradeRatio / dealParameters["price"]), 8)

        if baseBuySize < minimumAmount:
            return None
        if baseBuySize * dealParameters["price"] > quotedWallet["available"]:
            return None

        dealParameters["price"] = round(dealParameters["price"], 8)
        dealParameters["size"] = baseBuySize

        return dealParameters

    def prepareSellOrder(self, currentRate):
        if not self.settings["sell"]["allowTrade"]: return False

        dealParameters = self._initEmptyDeal("sell", currentRate)
        # dealParameters["price"] += 0.00001
        self.refreshWallet()

        baseWallet, quotedWallet = self.baseWallet(), self.quotedWallet()
        maxTradeRatio = self.settings["sell"]["maxTradeRatio"]
        minimumAmount = self.settings["info"]["base_min_size"]
        baseSellSize = round(baseWallet["available"] * maxTradeRatio, 8)

        if baseSellSize < minimumAmount:
            return None

        dealParameters["price"] = round(dealParameters["price"], 8)
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
    def getLocalDt(serverDt):
        return dateutil.parser.parse(serverDt) + datetime.timedelta(0, 7200)

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
        return current - previous, ((current - previous) / previous) * 100.0