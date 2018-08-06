import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from cbMarian.broker import Broker
from cbMarian.mainWidget import MainWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    broker = Broker(*Broker.getCredentials())
    broker.startPolling()

    win = QMainWindow()
    widget = MainWidget(broker)
    win.setCentralWidget(widget)

    win.show()
    app.exec_()

