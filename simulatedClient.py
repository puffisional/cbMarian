import json

import requests
from coinbasepro.coinbasepro_auth import CoinbaseExchangeAuth


class SimulatedClient():

    def __init__(self, environment, authId=0):
        self.authId = authId
        self.env = environment

    def get_account(self, account_id):
        return self.env.request_get_accounts(account_id, self.authId)

    def get_accounts(self):
        return self.get_account('')

    def buy(self, **kwargs):
        kwargs["side"] = "buy"
        if "product_id" not in kwargs:
            kwargs["product_id"] = self.product_id
        r = requests.post(self.url + '/orders',
                          data=json.dumps(kwargs),
                          auth=self.auth,
                          timeout=self.timeout)
        return r.json()

    def sell(self, **kwargs):
        kwargs["side"] = "sell"
        r = requests.post(self.url + '/orders',
                          data=json.dumps(kwargs),
                          auth=self.auth,
                          timeout=self.timeout)
        return r.json()

    def cancel_order(self, order_id):
        r = requests.delete(self.url + '/orders/' + order_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def cancel_all(self, product_id=''):
        url = self.url + '/orders/'
        params = {}
        if product_id:
            params["product_id"] = product_id
        r = requests.delete(url, auth=self.auth, params=params, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_order(self, order_id):
        r = requests.get(self.url + '/orders/' + order_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_orders(self, product_id='', status=[]):
        result = []
        url = self.url + '/orders/'
        params = {}
        if product_id:
            params["product_id"] = product_id
        if status:
            params["status"] = status
        r = requests.get(url, auth=self.auth, params=params, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if 'cb-after' in r.headers:
            self.paginate_orders(product_id, status, result, r.headers['cb-after'])
        return result

    def get_fills(self, order_id='', product_id='', before='', after='', limit=''):
        result = []
        url = self.url + '/fills?'
        if order_id:
            url += "order_id={}&".format(str(order_id))
        if product_id:
            url += "product_id={}&".format(product_id)
        if before:
            url += "before={}&".format(str(before))
        if after:
            url += "after={}&".format(str(after))
        if limit:
            url += "limit={}&".format(str(limit))
        r = requests.get(url, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if 'cb-after' in r.headers and limit is not len(r.json()):
            return self.paginate_fills(result, r.headers['cb-after'], order_id=order_id, product_id=product_id)
        return result

    def get_trailing_volume(self):
        return self.env.request_get_trailing_volume()

    def get_products(self):
        return self.env.request_get_products()

    def get_product_order_book(self, product_id, level=1):
        # Supported levels are 1, 2 or 3
        level = level if level in range(1, 4) else 1
        return self._get('/products/{}/book'.format(str(product_id)), params={'level': level})

    def get_product_ticker(self, product_id):
        return self._get('/products/{}/ticker'.format(str(product_id)))

    def get_product_trades(self, product_id, before='', after='', limit='', result=[]):
        url = self.url + '/products/{}/trades'.format(str(product_id))
        params = {}

        if before:
            params['before'] = str(before)
        if after:
            params['after'] = str(after)
        if limit and limit < 100:
            # the default limit is 100
            # we only add it if the limit is less than 100
            params['limit'] = limit

        r = requests.get(url, params=params)
        # r.raise_for_status()

        result.extend(r.json())

        if 'cb-after' in r.headers and limit is not len(result):
            # update limit
            limit -= len(result)
            if limit <= 0:
                return result

            # TODO: need a way to ensure that we don't get rate-limited/blocked
            # time.sleep(0.4)
            return self.get_product_trades(product_id=product_id, after=r.headers['cb-after'], limit=limit,
                                           result=result)

        return result

    def get_product_historic_rates(self, product_id, start=None, end=None,
                                   granularity=None):

        params = {}
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end
        if granularity is not None:
            acceptedGrans = [60, 300, 900, 3600, 21600, 86400]
            if granularity not in acceptedGrans:
                newGranularity = min(acceptedGrans, key=lambda x: abs(x - granularity))
                print(granularity, ' is not a valid granularity level, using', newGranularity, ' instead.')
                granularity = newGranularity
            params['granularity'] = granularity

        return self._get('/products/{}/candles'.format(str(product_id)), params=params)

    def get_product_24hr_stats(self, product_id):
        return self._get('/products/{}/stats'.format(str(product_id)))

    def get_currencies(self):
        return self.env.request_get_currencies()

    def get_time(self):
        return self.env.request_get_time()
