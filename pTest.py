from coinbasepro import public_client

pc = public_client.PublicClient()
print(pc.get_product_order_book("BCH-BTC"))