import datetime
import random
from time import sleep

from coinbasepro.public_client import PublicClient
from cbMarian.simulation.simulatedClient import SimulatedClient
from simulation.simulatedProduct import SimulatedProduct


class SimulatedServer():
    accounts = []
    coinbaseClient = PublicClient()
    dealId = 0
    tick = 0
    startTime = datetime.datetime.now()
    accountTrades = []

    def __init__(self):
        self._generateAccounts()
        self._initCurrencies()
        self._initProducts()
        self._initOrderBook()

    def _generateAccounts(self, size=100):
        self.accounts = []
        currencies = self.coinbaseClient.get_currencies()
        for i in range(size):
            accountWallet = []
            self.accountTrades.append({
                "opened": {},
                "closed": {}
            })

            for j, currency in enumerate(currencies):
                balance = random.uniform(0, 500)
                accountWallet.append(
                    {'id': j, 'currency': currency["id"], 'balance': balance, 'available': balance, 'hold': '0.0', 'profile_id': i}
                )
            self.accounts.append(accountWallet)

    def _initProducts(self):
        self.products = self.coinbaseClient.get_products()
        self.simulatedProducts = {}
        for product in self.products:
            # tradePrice = self.coinbaseClient.get_product_historic_rates(product["id"])[0][1]
            tradePrice = 1
            self.simulatedProducts[product["id"]] = SimulatedProduct(product["id"], tradePrice)
            # sleep(0.4)

    def _initCurrencies(self):
        self.currencies = self.coinbaseClient.get_currencies()

    def _initOrderBook(self):
        self.orderBook = {}
        for product in self.products:
            self.orderBook[product["id"]] = {
                "buy": {},
                "sell": {},
            }

    def request_cancel_order(self, profileId, orderId):
        for order in self.orderBook.values():
            if orderId in order["buy"]:
                del order["buy"][orderId]
            elif orderId in order["sell"]:
                del order["sell"][orderId]

        del self.accountTrades[profileId]["opened"][orderId]

    def request_get_time(self):
        currentTime = self.startTime + datetime.timedelta(self.tick)
        epochTime = currentTime.time()
        isoTime = currentTime.isoformat()
        return {'iso': isoTime, 'epoch': epochTime}

    def _id(self):
        return "-".join(list(map(str, random._urandom(10))))

    def request_trade(self, profileId, price, size, product_id, post_only, side):
        trade = {
            "id": self._id(),
            "price": price,
            "size": size,
            "product_id": product_id,
            "side": side,
            "stp": "dc",
            "type": "limit",
            "time_in_force": "GTC",
            "post_only": post_only,
            "created_at": self.request_get_time()["iso"],
            "fill_fees": "0.0000000000000000",
            "filled_size": "0.00000000",
            "executed_value": "0.0000000000000000",
            "status": "open",
            "settled": False
        }
        self.accountTrades[profileId]["opened"][trade["id"]] = trade
        self.orderBook[product_id][side][trade["id"]] = trade
        return trade

    def simulationTick(self):
        self.tick += 1


if __name__ == "__main__":

    ss = SimulatedServer()
    sc = SimulatedClient(ss, 0)

    # trade = sc.buy(
    #     **{
    #         "price": 1,
    #         "size": 1,
    #         "product_id": "ETC-EUR",
    #         "post_only": True,
    #         "side": "buy",
    #     }
    # )
    #
    # sc.cancel_order(trade["id"])
    # print(ss.accountTrades)