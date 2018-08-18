from cbMarian.broker import Broker


class ProductBroker(Broker):

    def onRateDiff(self, lastMarketTrade):
        self.refreshDeals()
        lastBrokerDeals = self.brokerDeals["closed"] + self.brokerDeals["opened"]

        side = lastBrokerDeals[0]["side"]
        dealList = []
        for index, lastBrokerDeal in enumerate(lastBrokerDeals):
            dealList.append((float(lastBrokerDeal["price"]), lastBrokerDeal))
            if lastBrokerDeal["side"] != side:
                break

        sortedDeals = sorted(dealList, key=lambda x: x[0])

        tradeRates = {
            # currentRate, lastBrokerRate, rateDiff, rateDiffPercent
            "sell": (float(lastMarketTrade["asks"][0][0]), sortedDeals[-1][0],
                     *self.get_change(float(lastMarketTrade["asks"][0][0]), sortedDeals[-1][0])),
            "buy": (float(lastMarketTrade["bids"][0][0]), sortedDeals[0][0],
                     *self.get_change(float(lastMarketTrade["bids"][0][0]), sortedDeals[0][0])),
        }
        # if lastBrokerDeal["side"] == "sell":
        #     currentRate = float(lastMarketTrade["asks"][0][0])
        #     lastBrokerRate = sortedDeals[-1][0]
        # elif lastBrokerDeal["side"] == "buy":
        #     currentRate = float(lastMarketTrade["bids"][0][0])
        #     lastBrokerRate = sortedDeals[0][0]

        # print(self.product, lastBrokerDeal["side"], currentRate)
        # rateDiff, rateDiffPercent = self.get_change(currentRate, lastBrokerRate)

        self.sigRateDiff.emit(self, tradeRates)

        if len(self.brokerDeals["opened"]) > 0: return

        deal = self.checkDeal(tradeRates["sell"], tradeRates["buy"])

        if deal is not None:
            if deal["side"] == "buy":
                dealOutput = self.buy(**deal)
            elif deal["side"] == "sell":
                dealOutput = self.sell(**deal)
            print(deal)
            print(dealOutput)

    def checkDeal(self, sellTrade, buyTrade):
        deal = None
        currentRate, lastBrokerRate, rateDiff, rateDiffPercent = buyTrade
        if currentRate < lastBrokerRate:
            condA = self.settings["buy"]["thresholdType"] == "percent"
            condB = abs(rateDiffPercent) >= self.settings["buy"]["thresholdValue"]
            condC = self.settings["buy"]["thresholdType"] == "scalar"
            condD = abs(rateDiff) >= self.settings["buy"]["thresholdValue"]
            if (condA and condB) or (condC and condD):
                deal = self.prepareBuyOrder(currentRate, abs(rateDiffPercent))
                return deal

        currentRate, lastBrokerRate, rateDiff, rateDiffPercent = sellTrade
        if currentRate > lastBrokerRate:
            condA = self.settings["sell"]["thresholdType"] == "percent"
            condB = abs(rateDiffPercent) >= self.settings["sell"]["thresholdValue"]
            condC = self.settings["sell"]["thresholdType"] == "scalar"
            condD = abs(rateDiff) >= self.settings["sell"]["thresholdValue"]
            if (condA and condB) or (condC and condD):
                deal = self.prepareSellOrder(currentRate, abs(rateDiffPercent))
                return deal

        return deal


