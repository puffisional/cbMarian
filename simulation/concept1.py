from numpy.random import uniform

SIDE_BUY = 1
SIDE_SELL = -1

CURRENCY_A = 1
CURRENCY_B = -1


class trader():
    # ratio, budget

    def __init__(self, product, initBalance):
        self.cA, self.cB = product.split("-")
        self.balance = initBalance
        self.currency = self.cA
        self.lastRatio = 1

    def newRatio(self, newRatio, product):
        cA, cB = product

        # if atom.currency == cB:
        #     newRatio = 1 / newRatio
        #
        # print(newRatio, ratio)
        priceChange = self.get_change(newRatio, self.lastRatio)
        print(priceChange, ratio)
        trade = None
        if priceChange < 0.1:
            if self.currency == cA:
                trade = self.sell(self.balance, newRatio)
            else:
                trade = self.buy(self.balance, newRatio)
        elif priceChange > -0.1:
            if self.currency == cA:
                trade = self.buy(self.balance, newRatio)
            else:
                trade = self.sell(self.balance, newRatio)

        #
        if trade is not None:
            self.lastTrade = newRatio
        #
        return trade, self.balance

    def sell(self, size, ratio):
        if self.currency == self.cB: return
        self.balance = size * ratio
        self.currency, self.lastRatio = self.cA if self.currency == self.cB else self.cB, ratio
        return "sell", self.balance, self.currency

    def buy(self, size, ratio):
        if self.currency == self.cA: return
        self.balance = size / ratio
        self.currency, self.lastRatio = self.cA if self.currency == self.cB else self.cB, ratio
        return "buy", self.balance, self.currency

    @staticmethod
    def get_change(current, previous):
        return ((current - previous) / previous) * 100.0


if __name__ == "__main__":

    bussiness = trader("ETH-BTC", 1000)
    ratios = uniform(0.99, 1.01, 100)

    for ratio in ratios: #ratios: #uniform(0.99, 1.01, 1000): #(1.1, 1, 0.9, 1, 0.9, 0.8, 0.7, 0.8, 0.9, 1):  # uniform(0.9, 1.1, 10):
        trade = bussiness.newRatio(ratio, (CURRENCY_A, CURRENCY_B))
        print(trade)
