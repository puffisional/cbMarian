from coinbasepro import PublicClient

class CoinbaseClient(PublicClient):

    @staticmethod
    def get_change(current, previous):
        return current - previous, ((current - previous) / previous) * 100.0