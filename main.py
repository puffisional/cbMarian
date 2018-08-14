import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from cbMarian.mainWidget import MainWidget
from cbMarian.poller import Poller
from cbMarian.productBroker import ProductBroker

if __name__ == "__main__":
    app = QApplication(sys.argv)

    myProducts = ["ETH-BTC", "LTC-BTC", "BCH-BTC", "ETC-BTC"]
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

