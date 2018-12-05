from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from time import localtime, strftime
from logger import MyLogger
from common import *

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

    def add_target(self, code, price, order_type):
        if order_type not in OrderTypeList.TYPE:
            return

        # Socket Send

        rowPosition = 0 #self.table.rowCount()
        self.targetList.insertRow(rowPosition)
        self.targetList.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(code)) # 종목코드
        self.targetList.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(price)) # 현재가
        self.targetList.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(order_type)) # 주문타입

