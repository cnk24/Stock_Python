import sys
from PyQt5 import QtWidgets
from stock import StockInfo
from Init import InitDialog
from MainWindow import CWindow


def main():

    app = QtWidgets.QApplication(sys.argv)

    stockInfo = StockInfo()

    stockInfo.get_daily_price('215600')

    dialog = InitDialog(stockInfo)
    dialog.exec_()
    
    w = CWindow()
    w.show()


    app.exec_()


if __name__ == '__main__':
    main()
