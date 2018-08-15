import json

import requests
from coinbasepro.coinbasepro_auth import CoinbaseExchangeAuth


class SimulatedClient():

    def __init__(self, key, b64secret, passphrase, api_url="https://api.pro.coinbase.com", timeout=30):
        self.auth = CoinbaseExchangeAuth(key, b64secret, passphrase)
        self.timeout = timeout

    def get_account(self, account_id):
        r = requests.get(self.url + '/accounts/' + account_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_accounts(self):
        return self.get_account('')

    def get_account_history(self, account_id):
        result = []
        r = requests.get(self.url + '/accounts/{}/ledger'.format(account_id), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if "cb-after" in r.headers:
            self.history_pagination(account_id, result, r.headers["cb-after"])
        return result

    def history_pagination(self, account_id, result, after):
        r = requests.get(self.url + '/accounts/{}/ledger?after={}'.format(account_id, str(after)), auth=self.auth,
                         timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if "cb-after" in r.headers:
            self.history_pagination(account_id, result, r.headers["cb-after"])
        return result

    def get_account_holds(self, account_id):
        result = []
        r = requests.get(self.url + '/accounts/{}/holds'.format(account_id), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if "cb-after" in r.headers:
            self.holds_pagination(account_id, result, r.headers["cb-after"])
        return result

    def holds_pagination(self, account_id, result, after):
        r = requests.get(self.url + '/accounts/{}/holds?after={}'.format(account_id, str(after)), auth=self.auth,
                         timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if "cb-after" in r.headers:
            self.holds_pagination(account_id, result, r.headers["cb-after"])
        return result

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

    def paginate_orders(self, product_id, status, result, after):
        url = self.url + '/orders'

        params = {
            "after": str(after),
        }
        if product_id:
            params["product_id"] = product_id
        if status:
            params["status"] = status
        r = requests.get(url, auth=self.auth, params=params, timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
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

    def paginate_fills(self, result, after, order_id='', product_id=''):
        url = self.url + '/fills?after={}&'.format(str(after))
        if order_id:
            url += "order_id={}&".format(str(order_id))
        if product_id:
            url += "product_id={}&".format(product_id)
        r = requests.get(url, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if 'cb-after' in r.headers:
            return self.paginate_fills(result, r.headers['cb-after'], order_id=order_id, product_id=product_id)
        return result

    def get_fundings(self, result='', status='', after=''):
        if not result:
            result = []
        url = self.url + '/funding?'
        if status:
            url += "status={}&".format(str(status))
        if after:
            url += 'after={}&'.format(str(after))
        r = requests.get(url, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if 'cb-after' in r.headers:
            return self.get_fundings(result, status=status, after=r.headers['cb-after'])
        return result

    def repay_funding(self, amount='', currency=''):
        payload = {
            "amount": amount,
            "currency": currency  # example: USD
        }
        r = requests.post(self.url + "/funding/repay", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def margin_transfer(self, margin_profile_id="", transfer_type="", currency="", amount=""):
        payload = {
            "margin_profile_id": margin_profile_id,
            "type": transfer_type,
            "currency": currency,  # example: USD
            "amount": amount
        }
        r = requests.post(self.url + "/profiles/margin-transfer", data=json.dumps(payload), auth=self.auth,
                          timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_position(self):
        r = requests.get(self.url + "/position", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def close_position(self, repay_only=""):
        payload = {
            "repay_only": repay_only or False
        }
        r = requests.post(self.url + "/position/close", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def deposit(self, amount="", currency="", payment_method_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "payment_method_id": payment_method_id
        }
        r = requests.post(self.url + "/deposits/payment-method", data=json.dumps(payload), auth=self.auth,
                          timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def coinbase_deposit(self, amount="", currency="", coinbase_account_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "coinbase_account_id": coinbase_account_id
        }
        r = requests.post(self.url + "/deposits/coinbase-account", data=json.dumps(payload), auth=self.auth,
                          timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def withdraw(self, amount="", currency="", payment_method_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "payment_method_id": payment_method_id
        }
        r = requests.post(self.url + "/withdrawals/payment-method", data=json.dumps(payload), auth=self.auth,
                          timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def coinbase_withdraw(self, amount="", currency="", coinbase_account_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "coinbase_account_id": coinbase_account_id
        }
        r = requests.post(self.url + "/withdrawals/coinbase-account", data=json.dumps(payload), auth=self.auth,
                          timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def crypto_withdraw(self, amount="", currency="", crypto_address=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "crypto_address": crypto_address
        }
        r = requests.post(self.url + "/withdrawals/crypto", data=json.dumps(payload), auth=self.auth,
                          timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_payment_methods(self):
        r = requests.get(self.url + "/payment-methods", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_coinbase_accounts(self):
        r = requests.get(self.url + "/coinbase-accounts", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def create_report(self, report_type="", start_date="", end_date="", product_id="", account_id="", report_format="",
                      email=""):
        payload = {
            "type": report_type,
            "start_date": start_date,
            "end_date": end_date,
            "product_id": product_id,
            "account_id": account_id,
            "format": report_format,
            "email": email
        }
        r = requests.post(self.url + "/reports", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_report(self, report_id=""):
        r = requests.get(self.url + "/reports/" + report_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_trailing_volume(self):
        r = requests.get(self.url + "/users/self/trailing-volume", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_deposit_address(self, account_id):
        r = requests.post(self.url + '/coinbase-accounts/{}/addresses'.format(account_id), auth=self.auth,
                          timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def _get(self, path, params=None):
        """Perform get request"""

        r = requests.get(self.url + path, params=params, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_products(self):
        return self._get('/products')

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
        return self._get('/currencies')

    def get_time(self):
        return self._get('/time')
