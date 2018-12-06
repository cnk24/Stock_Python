import uuid
import MsgBus
import json
from common import *

class MsgBusAgent():

    # private object
    # this object defined as class variables to avoid too many message sender or collector are created
    # in case you create many instance of MsgBusAgent
    __dimMsgCollector = MsgBus.MsgCollector("KiwoomWithIPCMsgPump")
    __collectorThread = MsgBus.CollectorThread(__dimMsgCollector)
    __dimMsgSender = MsgBus.MsgSender("KiwoomWithIPCReqHandler")

    def __init__(self):
        MsgBusAgent.__collectorThread.start()

    def SendOutMessage(self, code, price, order_type):
        # code = 종목코드
        # price = 현재가
        # order_type = 1:매수 2:매도
        msgName = OrderTypeList.TYPE[order_type]
        msg = '{0}/{1}'.format(code, price)
        MsgBusAgent.__dimMsgSender.FireMessage(msgName, msg)

    def TestSendOutMessage(self, containter_id):
        MsgBusAgent.__dimMsgSender.FireMessage("PythonMessage_%s" % containter_id, "")

