import sys
from PyQt5 import QtWidgets
from stock import StockInfo
from Init import InitDialog
from MainWindow import CWindow
from Kiwoom import Kiwoom


def main():
    app = QtWidgets.QApplication(sys.argv)
    stockInfo = StockInfo()

    dialog = InitDialog(stockInfo)
    dialog.exec_()
    
    w = CWindow()

    kiwoom = Kiwoom(w)
    kiwoom.commConnect()



    w.show()
    

    app.exec_()


if __name__ == '__main__':
    main()
