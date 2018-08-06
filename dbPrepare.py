from gdax.public_client import PublicClient
import pymysql

c = PublicClient()
products = c.get_products()

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='svn78KE!#', db='cbmarian')
cur = conn.cursor()
for product in products:
    cur.execute("create table {0}(dt int unique, low float, high float, open float, close float, volume float)".format(product[u"id"].replace("-","_")))

conn.close()