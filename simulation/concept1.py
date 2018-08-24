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
        print(priceChange)
        trade = None
        if priceChange > 0.01:
            if self.currency == cA:
                trade = self.sell(self.balance, newRatio)
            else:
                trade = self.buy(self.balance, newRatio)
        elif priceChange < -0.01:
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
        self.balance = size / ratio
        self.currency, self.lastRatio = self.cA if self.currency == self.cB else self.cB, ratio
        return "sell", self.balance, self.currency

    def buy(self, size, ratio):
        self.balance = self.balance * ratio
        self.currency, self.lastRatio = self.cA if self.currency == self.cB else self.cB, ratio
        return "buy", self.balance, self.currency

    @staticmethod
    def get_change(current, previous):
        return ((current - previous) / previous) * 100.0


if __name__ == "__main__":

    bussiness = trader("ETH-BTC", 1000)
    ratios = uniform(0.5, 0.65)

    for ratio in (1, 1.01, 0.98, 0.97, 0.96, 0.95): #uniform(0.99, 1.01, 100): #(1.1, 1, 0.9, 1, 0.9, 0.8, 0.7, 0.8, 0.9, 1):  # uniform(0.9, 1.1, 10):
        trade = bussiness.newRatio(ratio, (CURRENCY_A, CURRENCY_B))
        print(trade)
