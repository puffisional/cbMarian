import datetime
import time
from coinbasepro.public_client import PublicClient

class SimulatedClient():

    def __init__(self, server, authId):
        self.server = server
        self.authId = authId

    def request_get_accounts(self, accountId=''):
        if accountId == '':
            return self.server.accounts[self.authId]
        else:
            return self.server.accounts[self.authId][accountId]

    def buy(self, **kwargs):
        return self.server.request_trade(self.authId, **kwargs)

    def sell(self, **kwargs):
        return self.server.request_trade(self.authId, **kwargs)

    def cancel_order(self, order_id):
        self.server.request_cancel_order(self.authId, order_id)

    def request_get_trailing_volume(self):
        return [
            {'product_id': 'BCH-BTC', 'volume': '0.48114240', 'exchange_volume': '42609.67403534',
             'recorded_at': '2018-08-16T00:05:00.88532Z'},
            {'product_id': 'ETC-BTC', 'volume': '3.57823773', 'exchange_volume': '332494.84453535',
             'recorded_at': '2018-08-16T00:05:00.88532Z'},
            {'product_id': 'ETH-BTC', 'volume': '1.21049721', 'exchange_volume': '257038.41619626',
             'recorded_at': '2018-08-16T00:05:00.88532Z'},
            {'product_id': 'LTC-BTC', 'volume': '8.02767564', 'exchange_volume': '392577.17089734',
             'recorded_at': '2018-08-16T00:05:00.88532Z'}]

    def request_get_products(self):
        return self.products

    def request_get_time(self):
        return self.server.request_get_time()

    def request_get_currencies(self):
        return self.currencies