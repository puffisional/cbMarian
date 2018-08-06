import time
import pymysql
from cbMarian.broker import Broker
from coinbasepro.authenticated_client import PublicClient

c = PublicClient()
products = c.get_products()

user, passwd = Broker.getSqlCredentials()
conn = pymysql.connect(host='localhost', port=3306, user=user, passwd=passwd, db='cbmarian')
cur = conn.cursor()
for product in products:
    cur.execute("create table {0}(dt int unique, low float, high float, open float, close float, volume float)".format(
        product[u"id"].replace("-", "_")))
    cur.execute("create table {0}_tick(dt int unique)".format(product[u"id"].replace("-", "_")))
    cur.execute("insert into {0}_tick values({1})".format(product[u"id"].replace("-", "_"), time.time() - 129600))
    conn.commit()

conn.close()
