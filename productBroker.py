import time
from threading import Event, Thread

import dateutil.parser
from PyQt5.QtCore import QObject
from coinbasepro.authenticated_client import AuthenticatedClient

from coinbaseClient import CoinbaseClient


class ProductBroker(AuthenticatedClient, CoinbaseClient, QObject):
    pollingFlag = Event()
    allowTrading = False

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
                "allowTrade": True,
                "maxLife": 1800,
                "thresholdType": "percent",  # percent | scalar
                "thresholdValue": 0.3,
                "maxTradeRatio": 0.25,
                "post_only": True
            },
            "sell": {
                "allowTrade": True,
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
        self.startPolling()

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
        if len(self.brokerDeals["opened"]) > 0: return

        currentRate = float(lastMarketTrade["price"])
        lastBrokerRate = float(self.brokerDeals["closed"][0]["price"])
        rateDiff, rateDiffPercent = self.get_change(currentRate, lastBrokerRate)
        deal = self.checkDeal(rateDiff, rateDiffPercent, currentRate, lastBrokerRate)

        if deal is not None:
            # dealObj = {'created_at': '2018-08-09T13:19:49.569Z', 'trade_id': 5390956, 'product_id': 'ETH-BTC', 'order_id': 'b5661499-57cf-480b-8f28-7d78d8bd7f90', 'user_id': '5b5eb29048a82f0769dc2b15', 'profile_id': '001891ac-5aa4-4927-a18b-38c7b0bc9372', 'liquidity': 'M', 'price': '0.05685000', 'size': '0.02103507', 'fee': '0.0000000000000000', 'side': 'buy', 'settled': True, 'usd_volume': '7.5793564224000000'}
            # dealObj["expires_at"] = float(self.get_time()["epoch"]) + self.settings[deal["side"]]["maxLife"]
            print(deal)
            # self.currentDeals.append(dealObj)

    def startPolling(self):
        self.pollingFlag.set()
        Thread(target=self._poll).start()

    def stopPolling(self):
        self.pollingFlag.clear()

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

    def _poll(self):
        count = 25
        while self.pollingFlag.isSet():
            count -= 1
            if count <= 0:
                self.refreshDeals()
                currentTime = float(self.get_time()["epoch"])
                for deal in self.brokerDeals["opened"]:
                    creationTime = dateutil.parser.parse(deal["created_at"]).timestamp()
                    timeDiff = currentTime - creationTime
                    if timeDiff >= self.settings[deal["side"]]["maxLife"]:
                        self.cancel_order(deal["id"])
                count = 25

            lastMarketTrade = self.get_product_trades(product_id=self.product, limit=1, result=[])[0]
            self.onRateDiff(lastMarketTrade)
            time.sleep(0.25)

    # Static methods -------------------------------------------------------------------

    @staticmethod
    def getCredentials(fn="./credentials.conf"):
        with open(fn) as of:
            return of.readline().split(":")

    @staticmethod
    def getSqlCredentials(fn="./sqlCredentials.conf"):
        with open(fn) as of:
            return of.readline().split(":")
