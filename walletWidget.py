import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow

from cbMarian.productBroker import ProductBroker
from cbMarian.ui.walletWidget import Ui_Form


class WalletWidget(QWidget, Ui_Form):

    def __init__(self, broker, currency, parent=None):
        QWidget.__init__(self, parent)
        self.broker = broker
        self.currency = currency
        self.setupUi(self)
        self.refreshWallet(self.broker.wallet)
        self.broker.sigWalletRefresh.connect(self.refreshWallet)

    @pyqtSlot(object)
    def refreshWallet(self, wallet):
        cw = wallet[self.currency]
        self.currencyLabel.setText("{}".format(cw["currency"]))
        self.holdLabel.setText("{}".format(cw["hold"]))
        self.balanceLabel.setText("{}".format(cw["balance"]))
        self.availableLabel.setText("{}".format(cw["available"]))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    broker = ProductBroker("LTC-BTC", *ProductBroker.getCredentials())

    win = QMainWindow()

    widget = WalletWidget(broker, "BTC")
    win.setCentralWidget(widget)

    win.show()
    app.exec_()
