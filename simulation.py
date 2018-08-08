from numpy import sign

# cash, time, rate
ETH = 0
BTC = 1

# ProductId, Time, previousRate, previousDiff
product = ["ETH-BTC", 0, 1.0, 0]
tradingCoeficient = 0.3
threshold = 10

rateChart = [1, 1.1, 0.9, 1.2, 1.1, 1.0, 1.12, 1.15, 1.33, 1.2, 1.0, 1.15, 1.33, 1.05, 1, 1.2, 1.1, 1.05, 1.15, 1.23, 2.46]


def get_change(current, previous):
    if current == 0: return -100
    elif previous == 0: return 100

    coeficient = 1
    if current > previous:
        coeficient = -1
        current, previous = previous, current
    return coeficient * ((current - previous) / current) * 100

deals = []
for dt, rate in enumerate(rateChart):
    change = get_change(rate, product[2])

    print(dt, rate, product[2], change, ETH, BTC)
    if abs(change) < threshold: continue

    deal = {"time": dt, "product_id": product[0]}

    if sign(change) > 0 and ETH > 0:
        # SELL
        deal["amount"] = ETH * tradingCoeficient
        deal["price"] = rate
        deal["side"] = "sell"
        ETH -= deal["amount"]
        BTC += deal["price"]
        product[2] = rate
    elif sign(change) < 0 and BTC > 0:
        # BUY
        deal["amount"] = round((BTC / rate) * tradingCoeficient, 8)
        deal["price"] = rate
        deal["side"] = "buy"
        ETH += deal["amount"]
        BTC -= deal["price"]
        product[2] = rate

    deals.insert(0, deal)

for deal in deals:
    print(deal)

print(ETH, BTC)
