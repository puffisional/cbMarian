import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from cbMarian.mainWidget import MainWidget
from poller import Poller
from productBroker import ProductBroker

if __name__ == "__main__":
    app = QApplication(sys.argv)

    myProducts = ["ETH-BTC", "LTC-BTC", "BCH-BTC"]
    brokers = []
    for product in myProducts:
        broker = ProductBroker(product, *ProductBroker.getCredentials())
        brokers.append(broker)

    brokerPoller = Poller(brokers)

    win = QMainWindow()
    widget = MainWidget(brokers)
    win.setCentralWidget(widget)

    win.show()
    app.exec_()

