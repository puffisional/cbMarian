from cbMarian.broker import Broker


class ProductBroker(Broker):

    def onRateDiff(self, lastMarketTrade):
        lastBrokerDeals = self.brokerDeals["closed"]

        side = lastBrokerDeals[0]["side"]
        for index, lastBrokerDeal in enumerate(lastBrokerDeals):
            if lastBrokerDeal["side"] != side:
                lastBrokerDeal = lastBrokerDeals[index - 1]
                break

        lastBrokerRate = float(lastBrokerDeal["price"])

        if lastBrokerDeal["side"] == "sell":
            currentRate = float(lastMarketTrade["asks"][0][0])
        elif lastBrokerDeal["side"] == "buy":
            currentRate = float(lastMarketTrade["bids"][0][0])

        # print(self.product, lastBrokerDeal["side"], currentRate)
        rateDiff, rateDiffPercent = self.get_change(currentRate, lastBrokerRate)

        self.sigRateDiff.emit(self, rateDiff, rateDiffPercent, currentRate, lastBrokerRate)

        if len(self.brokerDeals["opened"]) > 0: return
        deal = self.checkDeal(rateDiff, rateDiffPercent, currentRate, lastBrokerRate)

        if deal is not None:
            if deal["side"] == "buy":
                dealOutput = self.buy(**deal)
                print(deal)
                print(dealOutput)
            elif deal["side"] == "sell":
                dealOutput = self.sell(**deal)
                print(deal)
                print(dealOutput)

        self.refreshDeals()

    def checkDeal(self, rateDiff, rateDiffPercent, currentRate, lastBrokerRate):
        deal = None
        if currentRate < lastBrokerRate:
            condA = self.settings["buy"]["thresholdType"] == "percent"
            condB = abs(rateDiffPercent) >= self.settings["buy"]["thresholdValue"]
            condC = self.settings["buy"]["thresholdType"] == "scalar"
            condD = abs(rateDiff) >= self.settings["buy"]["thresholdValue"]
            if (condA and condB) or (condC and condD):
                deal = self.prepareBuyOrder(currentRate)
        elif currentRate > lastBrokerRate:
            condA = self.settings["sell"]["thresholdType"] == "percent"
            condB = abs(rateDiffPercent) >= self.settings["sell"]["thresholdValue"]
            condC = self.settings["sell"]["thresholdType"] == "scalar"
            condD = abs(rateDiff) >= self.settings["sell"]["thresholdValue"]
            if (condA and condB) or (condC and condD):
                deal = self.prepareSellOrder(currentRate)

        return deal
