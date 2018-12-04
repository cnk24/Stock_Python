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

        self.logDebug = MyLogger('debugLog')
        self.logDebug.SetLogView(self.debugLog)

        self.logSocket = MyLogger('socketLog')
        self.logSocket.SetLogView(self.socketLog)

    def log_debug(self, msg):
        self.logDebug.debug(msg)

    def log_socket(self, msg):
        self.logSocket.info(msg)

    def add_target(self, code, price, _type):
        if _type not in TypeList.TYPE:
            return

        # Socket Send

        rowPosition = 0 #self.table.rowCount()
        self.targetList.insertRow(rowPosition)
        self.targetList.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(code)) # code
        self.targetList.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(price)) # price
        self.targetList.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(_type)) # type





class TypeList(object):
    TYPE = {
        1: '매수',
        2: '매도'
    }

        