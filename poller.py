import time
from threading import Event, Thread

import dateutil


class Poller():
    pollingFlag = Event()

    def __init__(self, brokers=[]):
        self.brokers = brokers
        self.startPolling()

    def addBroker(self, broker):
        self.brokers.add(broker)

    def startPolling(self):
        self.pollingFlag.set()
        Thread(target=self._poll).start()

    def stopPolling(self):
        self.pollingFlag.clear()

    def _poll(self):
        count = 25
        while self.pollingFlag.isSet():
            count -= 1
            for broker in self.brokers:
                if count <= 0:
                    broker.refreshDeals()
                    currentTime = float(broker.get_time()["epoch"])
                    for deal in broker.brokerDeals["opened"]:
                        creationTime = dateutil.parser.parse(deal["created_at"]).timestamp()
                        timeDiff = currentTime - creationTime
                        if timeDiff >= broker.settings[deal["side"]]["maxLife"]:
                            broker.cancel_order(deal["id"])
                        time.sleep(0.25)

                lastMarketTrade = broker.get_product_trades(product_id=broker.product, limit=1, result=[])[0]
                broker.onRateDiff(lastMarketTrade)
                time.sleep(0.25)

            if count <= 0:
                count = 25
