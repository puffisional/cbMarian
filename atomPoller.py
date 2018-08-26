import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from atomBroker import AtomBroker
from cbMarian.mainWidget import MainWidget
from cbMarian.poller import Poller
from cbMarian.productBroker import ProductBroker

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # myProducts = [("LTC-EUR", 0.2)]
    # myProducts = [("ETH-BTC", 0.04)]
    myProducts = [("LTC-EUR", "auto")]
    brokers = []
    for product, balance in myProducts:
        broker = AtomBroker(product, balance, *AtomBroker.getCredentials())
        brokers.append(broker)

    brokerPoller = Poller(brokers)
    brokerPoller.dealRefreshCount = 30
    win = QMainWindow()
    widget = MainWidget(brokers)
    win.setCentralWidget(widget)

    win.show()
    app.exec_()

