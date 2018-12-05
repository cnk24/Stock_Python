import sys
from PyQt5 import QtWidgets
from stock import StockInfo
from Init import InitDialog
from MainWindow import CWindow

from MsgBusAgent import MsgBusAgent
from common import *


def main():
    app = QtWidgets.QApplication(sys.argv)
    stockInfo = StockInfo()

    #dialog = InitDialog(stockInfo)
    #dialog.exec_()
    
    w = CWindow()
    w.show()


    agent = MsgBusAgent()
    agent.SendOutMessage('001040', '2500', 1)
    #for containter_id in range(100):
        #agent.TestSendOutMessage(containter_id)
        #time.sleep(1)
        #agent.SendOutMessage('001040', '2500', 1)        

    app.exec_()


if __name__ == '__main__':
    main()
