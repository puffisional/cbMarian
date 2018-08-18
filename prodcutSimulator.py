import random


class ProductSimulator():

    def __init__(self, product, initialTradePrice):
        self.product = product
        self.initialTradePrice = initialTradePrice
        self.tradePrice = initialTradePrice

    def getCurrentRate(self):
        self.tradePrice += random.uniform(-0.1, 0.1)
        self.tradePrice = abs(self.tradePrice)
        return self.tradePrice

if __name__ == "__main__":

    ps = ProductSimulator("ETH-BTC", 1)
    for i in range(10000):
        print(ps.getCurrentRate())