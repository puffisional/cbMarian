import time
from threading import Event, Thread

import dateutil.parser


class Poller():
    pollingFlag = Event()
    dealRefreshCount = 3

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
        count = self.dealRefreshCount
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

                    broker.refreshDeals()
                    broker.refreshWallet()
                        # time.sleep(0.25)

                lastMarketBook = broker.get_product_order_book(broker.product)
                print(lastMarketBook)
                broker.onRateDiff(lastMarketBook)
                time.sleep(0.2)

            if count <= 0:
                count = self.dealRefreshCount