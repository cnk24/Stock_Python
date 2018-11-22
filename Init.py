from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtCore


class Worker(QtCore.QThread):
    # 사용자 정의 시그널 선언
    finished = QtCore.pyqtSignal()
    change_value = QtCore.pyqtSignal(int)

    def __init__(self, stockInfo):
        super().__init__()
        self.stockInfo = stockInfo

    def run(self):
        while True:
            cnt = 0
            codes = self.stockInfo.getCodes()
            for code in codes:
                self.stockInfo.getDayData(code)

                cnt += 1
                pos = (cnt / len(codes)) * 100
                self.change_value.emit(pos)

            self.finished.emit()
            break


class InitDialog(QtWidgets.QDialog):

    def __init__(self, stockInfo):
        super().__init__()
        uic.loadUi("InitDialog.ui", self)

        worker = Worker(stockInfo)
        worker.change_value.connect(self.progressBar.setValue)
        worker.finished.connect(self.Finish)
        worker.start()


    @QtCore.pyqtSlot()
    def Finish(self):
        self.close()
        

        