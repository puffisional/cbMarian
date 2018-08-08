import decimal
from threading import Thread

from cbMarian.broker import Broker

SELL = 0
BUY = 1


class FuturesBroker(Broker):
    dealTreshold = 1
    dealCoeficient = 0.3
    orderPosted = False
    ordersCount = 0

    def onRateDiff(self, product, diff, currentRates):
        if self.dealingFlag.isSet(): return
        if abs(diff) > self.dealTreshold:

            orders = self.get_orders()[0]
            ordersCount = len(orders)
            if ordersCount != self.ordersCount:
                self.ordersCount = ordersCount
                self.initBroker()
                return

            for order in orders:
                if order["product_id"] == product: return

            Thread(target=self._deal, args=(product, diff, currentRates)).start()

    def _deal(self, product, diff, currentRates):
        self.dealingFlag.set()

        baseCurrency, quoteCurrency = product.split("-")
        baseBalance = (baseCurrency, float(self.wallet[baseCurrency]["balance"]))
        quoteBalance = (quoteCurrency, float(self.wallet[quoteCurrency]["balance"]))

        dealParameters = {
            "price": currentRates[0],
            "product_id": product,
            "cancel_after": "5 min",
            "post_only": True
        }

        if diff > 0 and baseBalance[1] > 0:
            # SELL

            dealParameters["size"] = round(baseBalance[1] * self.dealCoeficient, 8)
            if float(self.products[product]["min"]) > dealParameters["size"]:
                if baseBalance[1] < float(self.products[product]["min"]):
                    self.dealingFlag.clear()
                    return
                else:
                    dealParameters["size"] = float(self.products[product]["min"])

            dealParameters["price"] += 0.00001
            dealParameters["price"] = round(dealParameters["price"], abs(
                decimal.Decimal(self.products[product]["increment"]).as_tuple().exponent))
            dealParameters["side"] = "sell"
            deal = self.sell(**dealParameters)

        elif diff < 0 and quoteBalance[1] > 0:
            # BUY

            dealParameters["size"] = round((quoteBalance[1] / currentRates[0]) * self.dealCoeficient, 8)
            if float(self.products[product]["min"]) > dealParameters["size"]:
                if baseBalance[1] < float(self.products[product]["min"]) * currentRates[0]:
                    self.dealingFlag.clear()
                    return
                else:
                    dealParameters["size"] = float(self.products[product]["min"])

            dealParameters["price"] -= 0.00001
            dealParameters["price"] = round(dealParameters["price"], abs(
                decimal.Decimal(self.products[product]["increment"]).as_tuple().exponent))
            dealParameters["side"] = "buy"
            deal = self.buy(**dealParameters)
        else:
            self.dealingFlag.clear()
            return

        print(dealParameters)
        print(deal)
        self.dealingFlag.clear()
