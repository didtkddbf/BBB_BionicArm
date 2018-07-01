import sys
import time
from PyQt5.QtWidgets import *
from PyQt5 import uic
import Adafruit_BBIO.GPIO as GPIO
import can
from PyQt5.QtCore import *

form_class = uic.loadUiType("uitest3.ui")[0]
bus = can.interface.Bus(channel='can0', bustype='socketcan_ctypes', bitrate = 1000000)
FAN_PIN = 'P8_8'
GPIO.setup(FAN_PIN, GPIO.OUT)
FAN2_PIN = 'P8_10'
GPIO.setup(FAN2_PIN, GPIO.OUT)
GPIO.output(FAN_PIN, GPIO.HIGH)
GPIO.output(FAN2_PIN, GPIO.HIGH)

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)

class MyWindow(QMainWindow, form_class):
    BHT = 0
    PWM = 50
    P_gain = 10
    msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, 0x00, 0x00], extended_id=False)
    bus.send(msg)
    def __init__(self, *args, **kwargs):
        super(MyWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        global PWM, P_gain, msg
        global P_gain
        global msg
        PWM = self.PWM
        P_gain = self.P_gain
        msg =self.msg
        self.BicepH.clicked.connect(self.BicepH_clicked)
        self.BicepH_2.clicked.connect(self.BicepH2_clicked)
        self.BicepC.clicked.connect(self.BicepC_clicked)
        self.BicepHC.clicked.connect(self.BicepHC_clicked)
        self.TricepH.clicked.connect(self.TricepH_clicked)
        self.TricepH_2.clicked.connect(self.TricepH2_clicked)
        self.TricepC.clicked.connect(self.TricepC_clicked)
        self.PWMsetbtn.clicked.connect(self.PWMset_clicked)
        self.Psetbtn.clicked.connect(self.Pset_clicked)
        self.PWMlcd.display(PWM)
        self.Plcd.display(P_gain)
        self.Stop.clicked.connect(self.Stop_clicked)
        self.BicepTemp_S.clicked.connect(self.BicepTemp_s_clicked)
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

#    def TempLCD(self):
#        global Stop_push
#        global BT
#        Stop_push = False
#        while Stop_push != True:
#            print(BT)
#            self.BicepTemp.display(BT)
#            time.sleep(0.1)

    def BicepTemp_s_clicked(self):
        print("Start to check Bicep temperature")
        worker = Worker(self.BicepH_clicked)
        self.threadpool.start(worker)
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def BicepH_clicked(self):
        global PWM
        global BT
        BHT = self.BHtime.value()
        for i in range(1,BHT):
            GPIO.output(FAN_PIN, GPIO.HIGH)
            PWM2 = PWM*1023//100
            PWMH = PWM2//256
            PWML = PWM2 - PWMH*256
            msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, PWML, PWMH], extended_id=False)
            bus.send(msg)
            message = bus.recv(1.0)
            Temp = message.data[2] + message.data[3] * 256
            BT = Temp // 50 - 273
            print(i*0.1, BT)
            self.BicepTemp.display(BT)
            time.sleep(0.01)
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        GPIO.output(FAN_PIN, GPIO.LOW)

    def BicepH2_clicked(self):
        global PWM
        BHT = self.BHtime_2.value()
        while BT<80:
            PWM2 = PWM*1023//100
            PWMH = PWM2//256
            PWML = PWM2 - PWMH*256
            msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, PWML, PWMH], extended_id=False)
            bus.send(msg)
            message = bus.recv(1.0)
            Temp = message.data[2] + message.data[3] * 256
            BT = Temp // 50 - 273
            time.sleep(0.1)
            if BT > BHT:
                break
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        message = bus.recv(1.0)
        Temp = message.data[2] + message.data[3] * 256
        BT = Temp // 50 - 273
        self.BicepTemp.display(BT)
        GPIO.output(FAN_PIN, GPIO.LOW)


    def BicepC_clicked(self):
        BCT = self.BCtime.value()
        for i in range(1,BCT):
            GPIO.output(FAN_PIN, GPIO.LOW)
            time.sleep(0.1)
        GPIO.output(FAN_PIN, GPIO.HIGH)

    def BicepHC_clicked(self):
        BHT = self.BHtime.value()
        BCT = self.BCtime.value()
        for i in range(1,BHT):
            print(i)
            time.sleep(0.1)
        for j in range(1,BCT):
            GPIO.output(FAN_PIN, GPIO.LOW)
            time.sleep(0.1)
        GPIO.output(FAN_PIN, GPIO.HIGH)

    def TricepH_clicked(self):
        THT = self.THtime.value()
        for i in range(1,THT):
            print(i)
            time.sleep(0.1)

    def TricepH2_clicked(self):
        THT = self.THtime_2.value()
        for i in range(1,THT):
            print(i)
            time.sleep(0.1)

    def TricepC_clicked(self):
        TCT = self.TCtime.value()
        for i in range(1,TCT):
            GPIO.output(FAN2_PIN, GPIO.LOW)
            time.sleep(0.1)
        GPIO.output(FAN2_PIN, GPIO.HIGH)

    def PWMset_clicked(self):
        global PWM
        PWM = self.PWMset.value()
        self.PWMlcd.display(PWM)
        print(PWM)

    def Pset_clicked(self):
        global P_gain
        P_gain = self.Pset.value()
        self.Plcd.display(P_gain)
        print(P_gain)

    def Stop_clicked(self):
        GPIO.output(FAN_PIN, GPIO.HIGH)
        GPIO.output(FAN2_PIN, GPIO.HIGH)
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        message = bus.recv(1.0)
        Temp = message.data[2] + message.data[3] * 256
        BT = Temp // 50 - 273
        self.BicepTemp.display(BT)
        global Stop_push
        Stop_push = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

