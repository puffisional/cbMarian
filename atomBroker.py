from cbMarian.broker import Broker


class AtomBroker(Broker):

    def __init__(self, product, initBalance, key, b64secret, passphrase):
        self.cA, self.cB = product.split("-")
        self.balance = initBalance
        self.currency = self.cA
        Broker.__init__(self, product, key, b64secret, passphrase)
        self.settings["buy"]["thresholdValue"] = 0.01
        self.settings["sell"]["thresholdValue"] = 0.01

        self.lastRatio = self.get_product_historic_rates(self.product)[0][1]

    def onRateDiff(self, lastMarketTrade):
        bid, ask = float(lastMarketTrade["bids"][0][0]), float(lastMarketTrade["asks"][0][0])
        newRatio = (bid + ask) / 2.

        priceChange, priceChangePercent = self.get_change(newRatio, self.lastRatio)
        deal = self.checkDeal(priceChangePercent, newRatio)
        print(deal)
        if deal is not None:
            # if deal["side"] == "buy":
            #     dealOutput = self.buy(**deal)
            # elif deal["side"] == "sell":
            #     dealOutput = self.sell(**deal)
            print(deal)
            # print(dealOutput)

            self.refreshDeals()

    def checkDeal(self, rateDiffPercent, newRatio):
        deal = None
        print(rateDiffPercent, self.settings["sell"]["thresholdValue"])
        if rateDiffPercent > self.settings["sell"]["thresholdValue"]:
            if self.currency == self.cA:
                deal = self.prepareSellOrder(newRatio, abs(rateDiffPercent))
            else:
                deal = self.prepareBuyOrder(newRatio, abs(rateDiffPercent))
        elif rateDiffPercent < -self.settings["buy"]["thresholdValue"]:
            if self.currency == self.cA:
                deal = self.prepareBuyOrder(newRatio, abs(rateDiffPercent))
            else:
                deal = self.prepareSellOrder(newRatio, abs(rateDiffPercent))

        return deal

    def prepareBuyOrder(self, currentRate, rateDiffPercent):
        if not self.settings["buy"]["allowTrade"]: return False

        dealParameters = self._initEmptyDeal("buy", currentRate)
        self.refreshWallet()

        quotedWallet = self.quotedWallet()
        minimumAmount = self.settings["info"]["base_min_size"]
        baseBuySize = round((self.balance * currentRate / dealParameters["price"]), 8)

        # print(dealParameters)

        if baseBuySize < minimumAmount:
            return None
        if baseBuySize * dealParameters["price"] > quotedWallet["available"]:
            return None

        dealParameters["price"] = round(dealParameters["price"], 8)
        dealParameters["size"] = baseBuySize

        return dealParameters

    def prepareSellOrder(self, currentRate, rateDiffPercent):
        if not self.settings["sell"]["allowTrade"]: return False

        dealParameters = self._initEmptyDeal("sell", currentRate)
        self.refreshWallet()

        baseWallet, quotedWallet = self.baseWallet(), self.quotedWallet()
        minimumAmount = self.settings["info"]["base_min_size"]
        baseSellSize = round(self.balance * currentRate, 8)

        if baseSellSize < minimumAmount:
            return None

        dealParameters["price"] = round(dealParameters["price"], 8)
        dealParameters["size"] = baseSellSize

        return dealParameters

if __name__ == "__main__":
    ab = AtomBroker("ETH-BTC", 0.05, *AtomBroker.getCredentials())
    print(ab.balance)
