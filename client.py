from coinbase.wallet.client import Client as coinbaseClient
from coinbase.wallet.model import APIObject

class Client(coinbaseClient):

    BASE_API_URI = 'https://api.pro.coinbase.com/'

    def _get(self, *args, **kwargs):
        return self._request('get', *args, **kwargs)

    def get_buy_price(self, **params):
        """https://developers.coinbase.com/api/v2#get-buy-price"""
        if 'currency_pair' in params:
            currency_pair = params['currency_pair']
        else:
            currency_pair = 'BTC-EUR'
        currency_pair = params.get('currency_pair', 'BTC-USD')
        response = self._get('v2', 'prices', currency_pair, 'buy', params=params)
        return self._make_api_object(response, APIObject)

    def get_sell_price(self, **params):
        """https://developers.coinbase.com/api/v2#get-sell-price"""
        if 'currency_pair' in params:
            currency_pair = params['currency_pair']
        else:
            currency_pair = 'BTC-EUR'
        currency_pair = params.get('currency_pair', 'BTC-USD')
        response = self._get('v2', 'prices', currency_pair, 'sell', params=params)
        return self._make_api_object(response, APIObject)

    def get_spot_price(self, **params):
        """https://developers.coinbase.com/api/v2#get-spot-price"""
        if 'currency_pair' in params:
            currency_pair = params['currency_pair']
        else:
            currency_pair = 'BTC-EUR'
        currency_pair = params.get('currency_pair', 'BTC-USD')
        response = self._get('v2', 'prices', currency_pair, 'spot', params=params)
        return self._make_api_object(response, APIObject)

    def get_historic_prices(self, **params):
        """https://developers.coinbase.com/api/v2#get-historic-prices"""
        if 'currency_pair' in params:
            currency_pair = params['currency_pair']
        else:
            currency_pair = 'BTC-EUR'
        response = self._get('v2', 'prices', currency_pair, 'historic', params=params)
        return self._make_api_object(response, APIObject)