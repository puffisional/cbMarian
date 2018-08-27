import time

import pymysql
from coinbasepro.authenticated_client import PublicClient

from cbMarian.broker import Broker

myProducts = ["LTC-EUR", "BTC-EUR", "ETH-EUR", "ETC-EUR"]
pc = PublicClient()
user, passwd = Broker.getSqlCredentials()
conn = pymysql.connect(host='localhost', port=3306, user=user, passwd=passwd, db='cbmarian')
cur = conn.cursor()

while True:
    for product in myProducts:
        lastMarketBook = pc.get_product_order_book(product)
        tableName = "{0}_book".format(product.replace("-", "_"))
        cmd = "INSERT IGNORE INTO " + tableName + " (dt, bid, bid_amount, bid_counts, ask, ask_amount, ask_counts) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        print(lastMarketBook)
        cur.execute(cmd, [lastMarketBook["sequence"], lastMarketBook["bids"][0][0], lastMarketBook["bids"][0][1], lastMarketBook["bids"][0][2],
                              lastMarketBook["asks"][0][0], lastMarketBook["asks"][0][1], lastMarketBook["asks"][0][2]])
        time.sleep(0.2)
    conn.commit()

conn.close()
