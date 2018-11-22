import sys
from PyQt5 import QtWidgets
from stock import StockInfo


def main():

    #app = QtWidgets.QApplication(sys.argv)


    stockInfo = StockInfo()
    #stockInfo.getAllItem()
    stockInfo.getDayData('011150')


    #app.exec_()


if __name__ == '__main__':
    main()
