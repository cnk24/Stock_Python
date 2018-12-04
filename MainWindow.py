from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from time import localtime, strftime
from logger import MyLogger

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


class CWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("ViewMain.ui", self)

        self.logBuySell = MyLogger('buysell')
        self.logBuySell.SetLogView(self.buysellLog)

        self.logDebug = MyLogger('debug')
        self.logDebug.SetLogView(self.debugLog)

    def log_debug(self, msg):
        self.logDebug.debug(msg)

    def log_buysell(self, msg):
        self.logBuySell.info(msg)

        