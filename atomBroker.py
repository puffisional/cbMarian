from cbMarian.broker import Broker


class AtomBroker(Broker):
    lastDeal = None

    def __init__(self, product, initBalance, key, b64secret, passphrase):
        self.cA, self.cB = product.split("-")
        Broker.__init__(self, product, key, b64secret, passphrase)

        if initBalance != "auto":
            self.balance = initBalance
            self.currency = self.cA
            self.lastRatio = self.get_product_historic_rates(self.product)[0][1]
        else:
            lastBrokerDeal = self.brokerDeals["closed"][0]
            self.lastRatio = float(lastBrokerDeal["price"])
            if lastBrokerDeal["side"] == "sell":
                self.balance = float(lastBrokerDeal["size"]) * self.lastRatio
                self.currency = self.cB
            else:
                self.balance = float(lastBrokerDeal["size"])
                self.currency = self.cA
            print(self.balance, self.currency, self.lastRatio)


        self.settings["buy"]["thresholdValue"] = 0.5
        self.settings["sell"]["thresholdValue"] = 0.5


    def onRateDiff(self, lastMarketTrade):
        if len(self.brokerDeals["opened"]) > 0: return

        if self.lastDeal is not None:
            lastDealStatus = self.get_order(self.lastDeal["id"])
            if lastDealStatus["status"] == "done" and lastDealStatus["settled"]:
                if lastDealStatus["side"] == "sell":
                    self.balance = float(lastDealStatus["size"]) * float(lastDealStatus["price"])
                else:
                    self.balance = float(lastDealStatus["size"]) / float(lastDealStatus["price"])

                self.currency, self.lastRatio = self.cA if self.currency == self.cB else self.cB, float(
                    lastDealStatus["price"])
                self.lastDeal = None

            return

        bid, ask = float(lastMarketTrade["bids"][0][0]), float(lastMarketTrade["asks"][0][0])
        newRatio = (bid + ask) / 2.
        priceChange, priceChangePercent = self.get_change(newRatio, self.lastRatio)
        deal = self.checkDeal(priceChangePercent, newRatio)

        print(priceChangePercent)

        if deal is not None:
            if deal["side"] == "buy":
                newRatio = ask
                priceChange, priceChangePercent = self.get_change(newRatio, self.lastRatio)
                print(priceChangePercent)
                deal = self.checkDeal(priceChangePercent, newRatio)
            elif deal["side"] == "sell":
                newRatio = bid
                priceChange, priceChangePercent = self.get_change(newRatio, self.lastRatio)
                print(priceChangePercent)
                deal = self.checkDeal(priceChangePercent, newRatio)
            else:
                deal = None

        print(deal, newRatio)
        if deal is not None:
            if deal["side"] == "buy":
                dealOutput = self.buy(**deal)
            elif deal["side"] == "sell":
                dealOutput = self.sell(**deal)

            self.lastDeal = dealOutput
            print(deal, newRatio)
            print(self.balance, self.currency)
            print(dealOutput)

            self.refreshDeals()

    def checkDeal(self, rateDiffPercent, newRatio):
        deal = None
        if rateDiffPercent < -self.settings["sell"]["thresholdValue"]:
            if self.currency == self.cA:
                deal = self.prepareSellOrder(newRatio)
            else:
                deal = self.prepareBuyOrder(newRatio)
        elif rateDiffPercent > self.settings["buy"]["thresholdValue"]:
            if self.currency == self.cA:
                deal = self.prepareBuyOrder(newRatio)
            else:
                deal = self.prepareSellOrder(newRatio)

        return deal

    def prepareBuyOrder(self, currentRate):
        if not self.settings["buy"]["allowTrade"]: return None
        if self.currency == self.cA: return None

        dealParameters = self._initEmptyDeal("buy", currentRate)
        quotedWallet = self.quotedWallet()
        minimumAmount = self.settings["info"]["base_min_size"]
        baseBuySize = round(self.balance / currentRate, 8)

        if baseBuySize < minimumAmount:
            return None
        if baseBuySize * dealParameters["price"] > quotedWallet["available"]:
            return None

        dealParameters["price"] = round(dealParameters["price"], 8)
        dealParameters["size"] = baseBuySize

        return dealParameters

    def prepareSellOrder(self, currentRate):
        if not self.settings["sell"]["allowTrade"]: return None
        if self.currency == self.cB: return None

        dealParameters = self._initEmptyDeal("sell", currentRate)
        minimumAmount = self.settings["info"]["base_min_size"]
        baseSellSize = round(self.balance, 8)

        if baseSellSize < minimumAmount:
            return None

        dealParameters["price"] = round(dealParameters["price"], 8)
        dealParameters["size"] = baseSellSize

        return dealParameters


if __name__ == "__main__":
    ab = AtomBroker("ETH-BTC", 0.05, *AtomBroker.getCredentials())
    print(ab.balance)
