import datetime
import time


class SimulatedEnvironment():
    accounts = []

    def __init__(self):
        self._initCurrencies()
        self._initProducts()
        self._initOrderBook()
        self._generateAccounts()

    def _generateAccounts(self, size=100):
        self.accounts = []
        for i in range(size):
            self.accounts.append([
                {'id': '0', 'currency': 'BTC', 'balance': '1.0', 'available': '1.0', 'hold': '0.0', 'profile_id': i},
                {'id': '1', 'currency': 'LTC', 'balance': '1.0', 'available': '1.0', 'hold': '0.0', 'profile_id': i},
                {'id': '2', 'currency': 'EUR', 'balance': '1.0', 'available': '1.0', 'hold': '0.0', 'profile_id': i},
                {'id': '3', 'currency': 'ETH', 'balance': '1.0', 'available': '1.0', 'hold': '0.0', 'profile_id': i},
                {'id': '4', 'currency': 'ETC', 'balance': '1.0', 'available': '1.0', 'hold': '0.0', 'profile_id': i},
                {'id': '5', 'currency': 'BCH', 'balance': '1.0', 'available': '1.0', 'hold': '0.0', 'profile_id': i},
            ])

    def _initCurrencies(self):
        self.currencies = [
            {'id': 'BTC', 'name': 'Bitcoin', 'min_size': '0.00000001', 'status': 'online', 'message': None},
            {'id': 'EUR', 'name': 'Euro', 'min_size': '0.01000000', 'status': 'online', 'message': None},
            {'id': 'LTC', 'name': 'Litecoin', 'min_size': '0.00000001', 'status': 'online', 'message': None},
            {'id': 'GBP', 'name': 'British Pound', 'min_size': '0.01000000', 'status': 'online', 'message': None},
            {'id': 'USD', 'name': 'United States Dollar', 'min_size': '0.01000000', 'status': 'online',
             'message': None},
            {'id': 'ETH', 'name': 'Ether', 'min_size': '0.00000001', 'status': 'online', 'message': None},
            {'id': 'BCH', 'name': 'Bitcoin Cash', 'min_size': '0.00000001', 'status': 'online', 'message': None},
            {'id': 'ETC', 'name': 'Ether Classic', 'min_size': '0.00000001', 'status': 'online', 'message': None}]

    def _initProducts(self):
        self.products = [
            {'id': 'ETC-EUR', 'base_currency': 'ETC', 'quote_currency': 'EUR', 'base_min_size': '0.1',
             'base_max_size': '5000', 'quote_increment': '0.01', 'display_name': 'ETC/EUR', 'status': 'online',
             'margin_enabled': False, 'status_message': '', 'min_market_funds': '10', 'max_market_funds': '100000',
             'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'BTC-USD', 'base_currency': 'BTC', 'quote_currency': 'USD', 'base_min_size': '0.001',
             'base_max_size': '70', 'quote_increment': '0.01', 'display_name': 'BTC/USD', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '10',
             'max_market_funds': '1000000', 'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'BCH-BTC', 'base_currency': 'BCH', 'quote_currency': 'BTC', 'base_min_size': '0.01',
             'base_max_size': '200', 'quote_increment': '0.00001', 'display_name': 'BCH/BTC', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '0.001', 'max_market_funds': '30',
             'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'BCH-USD', 'base_currency': 'BCH', 'quote_currency': 'USD', 'base_min_size': '0.01',
             'base_max_size': '350', 'quote_increment': '0.01', 'display_name': 'BCH/USD', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '10',
             'max_market_funds': '1000000', 'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'BTC-EUR', 'base_currency': 'BTC', 'quote_currency': 'EUR', 'base_min_size': '0.001',
             'base_max_size': '50', 'quote_increment': '0.01', 'display_name': 'BTC/EUR', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '10',
             'max_market_funds': '600000', 'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'BTC-GBP', 'base_currency': 'BTC', 'quote_currency': 'GBP', 'base_min_size': '0.001',
             'base_max_size': '20', 'quote_increment': '0.01', 'display_name': 'BTC/GBP', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '10',
             'max_market_funds': '200000', 'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'ETH-BTC', 'base_currency': 'ETH', 'quote_currency': 'BTC', 'base_min_size': '0.01',
             'base_max_size': '600', 'quote_increment': '0.00001', 'display_name': 'ETH/BTC', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '0.001', 'max_market_funds': '50',
             'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'ETH-EUR', 'base_currency': 'ETH', 'quote_currency': 'EUR', 'base_min_size': '0.01',
             'base_max_size': '400', 'quote_increment': '0.01', 'display_name': 'ETH/EUR', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '10',
             'max_market_funds': '400000', 'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'ETH-USD', 'base_currency': 'ETH', 'quote_currency': 'USD', 'base_min_size': '0.01',
             'base_max_size': '700', 'quote_increment': '0.01', 'display_name': 'ETH/USD', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '10',
             'max_market_funds': '1000000', 'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'LTC-BTC', 'base_currency': 'LTC', 'quote_currency': 'BTC', 'base_min_size': '0.1',
             'base_max_size': '2000', 'quote_increment': '0.00001', 'display_name': 'LTC/BTC', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '0.001', 'max_market_funds': '30',
             'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'LTC-EUR', 'base_currency': 'LTC', 'quote_currency': 'EUR', 'base_min_size': '0.1',
             'base_max_size': '1000', 'quote_increment': '0.01', 'display_name': 'LTC/EUR', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '10',
             'max_market_funds': '200000', 'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'LTC-USD', 'base_currency': 'LTC', 'quote_currency': 'USD', 'base_min_size': '0.1',
             'base_max_size': '4000', 'quote_increment': '0.01', 'display_name': 'LTC/USD', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '10',
             'max_market_funds': '1000000', 'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'BCH-EUR', 'base_currency': 'BCH', 'quote_currency': 'EUR', 'base_min_size': '0.01',
             'base_max_size': '120', 'quote_increment': '0.01', 'display_name': 'BCH/EUR', 'status': 'online',
             'margin_enabled': False, 'status_message': None, 'min_market_funds': '10',
             'max_market_funds': '200000', 'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'ETC-USD', 'base_currency': 'ETC', 'quote_currency': 'USD', 'base_min_size': '0.1',
             'base_max_size': '5000', 'quote_increment': '0.01', 'display_name': 'ETC/USD', 'status': 'online',
             'margin_enabled': False, 'status_message': '', 'min_market_funds': '10', 'max_market_funds': '100000',
             'post_only': False, 'limit_only': False, 'cancel_only': False},
            {'id': 'ETC-BTC', 'base_currency': 'ETC', 'quote_currency': 'BTC', 'base_min_size': '0.1',
             'base_max_size': '5000', 'quote_increment': '0.00001', 'display_name': 'ETC/BTC', 'status': 'online',
             'margin_enabled': False, 'status_message': '', 'min_market_funds': '0.001', 'max_market_funds': '30',
             'post_only': False, 'limit_only': False, 'cancel_only': False}]

    def _initOrderBook(self):
        self.orderBook = {}
        for product in self.products:
            self.orderBook[product["id"]] = {
                "buy": [],
                "sold": [],
                "filled": [],
            }
        print(self.orderBook )

    def request_get_accounts(self, accountId, authId):
        if accountId == '':
            return self.accounts[authId]
        else:
            return self.accounts[authId][accountId]

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
        epochTime = time.time()
        isoTime = datetime.datetime.fromtimestamp(epochTime).isoformat()
        return {'iso': isoTime, 'epoch': epochTime}

    def request_get_currencies(self):
        return self.currencies
