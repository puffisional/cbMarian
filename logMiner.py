import datetime
from gdax.public_client import PublicClient
import time
import pymysql

c = PublicClient()
products = c.get_products()

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='svn78KE!#', db='cbmarian')
cur = conn.cursor()

cur = conn.cursor()
startT = endT = 1514764800
generStart = time.time()
while endT < generStart:
    for product in products:
        endT = startT + 3*60*60
        tableName = product[u"id"].replace("-", "_")
        try:
            endTf = datetime.datetime.fromtimestamp(endT).isoformat()
            startTf = datetime.datetime.fromtimestamp(startT).isoformat()
            out = c.get_product_historic_rates(product[u"id"], granularity=60, start=startTf, end=endTf)
            if len(out) == 0 : continue

            cmd = "INSERT INTO "+tableName+" (dt, low, high, open, close, volume) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.executemany(cmd, out)
        except Exception as e:
            print(out)
        time.sleep(0.3)
    print("commit", startTf, endTf)
    conn.commit()
    startT = endT


conn.close()