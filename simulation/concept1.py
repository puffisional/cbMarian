from numpy.random import uniform

SIDE_BUY = 1
SIDE_SELL = -1

CURRENCY_A = 1
CURRENCY_B = -1


class atom():
    currency = CURRENCY_A
    ratio = 0.75
    side = SIDE_BUY

    def __init__(self, balance, threshold):
        self.balance = balance
        self.threshold = threshold


class trader():
    # ratio, budget, side
    lastTrade = (None, None, None)

    def __init__(self, tradingAtom):
        self.tradingAtom = tradingAtom
        self.lastTrade = (tradingAtom.ratio, tradingAtom, tradingAtom.side)

    def newRatio(self, newRatio, product):
        ratio, atom, side = self.lastTrade
        priceChange = self.get_change(newRatio, ratio)
        if priceChange > atom.threshold:
            return self.sell(atom, product, newRatio)
        elif priceChange < -atom.threshold:
            return self.buy(atom, product, newRatio)
        return "Ignore", atom.threshold, priceChange

    def sell(self, atom, product, ratio):
        cA, cB = product
        if atom.currency == cA:
            return self.buy(atom, product, ratio)
        else:
            atom.currency, atom.ratio, atom.side = -atom.currency, ratio, SIDE_SELL
            atom.balance = atom.balance * ratio
            self.lastTrade = (atom.ratio, atom, SIDE_SELL)
            return "sell", atom.balance, atom.currency

    def buy(self, atom, product, ratio):
        cA, cB = product
        if atom.currency == cB:
            return self.sell(atom, product, ratio)
        else:
            atom.currency, atom.ratio, atom.side = -atom.currency, ratio, SIDE_BUY
            print(atom.balance, ratio)
            atom.balance = atom.balance / ratio
            self.lastTrade = (atom.ratio, atom, SIDE_BUY)
            return "buy", atom.balance, atom.currency

    @staticmethod
    def get_change(current, previous):
        return ((current - previous) / previous) * 100.0


if __name__ == "__main__":

    bussiness = trader(atom(1000, 15))
    ratios = uniform(0.5, 1, 25)

    for ratio in [0.5, 0.75]:
        print(bussiness.newRatio(ratio, (CURRENCY_A, CURRENCY_B)))
