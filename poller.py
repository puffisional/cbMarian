import time
from threading import Event, Thread

import dateutil.parser


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

    # def _poll(self):
    #     count = 25
    #     while self.pollingFlag.isSet():
    #         count -= 1
    #         for broker in self.brokers:
    #             if count <= 0:
    #                 broker.refreshDeals()
    #                 currentTime = float(broker.get_time()["epoch"])
    #                 for deal in broker.brokerDeals["opened"]:
    #                     creationTime = dateutil.parser.parse(deal["created_at"]).timestamp()
    #                     timeDiff = currentTime - creationTime
    #                     if timeDiff >= broker.settings[deal["side"]]["maxLife"]:
    #                         broker.cancel_order(deal["id"])
    #                     time.sleep(0.25)
    #
    #             lastMarketTrade = broker.get_product_trades(product_id=broker.product, limit=1, result=[])[0]
    #             broker.onRateDiff(lastMarketTrade)
    #             time.sleep(0.25)
    #
    #         if count <= 0:
    #             count = 25

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

                lastMarketBook = broker.get_product_order_book(broker.product)
                broker.onRateDiff(lastMarketBook)
                time.sleep(0.25)

            if count <= 0:
                count = 25

{'sequence': 329566891, 'bids': [['0.09304', '0.7', 2]], 'asks': [['0.09327', '1.1491243', 1]]}