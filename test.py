from coinbaseClient import CoinbaseClient
from productBroker import ProductBroker

broker = ProductBroker("ETH-BTC", *ProductBroker.getCredentials())