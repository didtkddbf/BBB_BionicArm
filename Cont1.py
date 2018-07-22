import sys
import time
from PyQt5.QtWidgets import *
from PyQt5 import uic
import Adafruit_BBIO.GPIO as GPIO
import can
from PyQt5.QtCore import *
from Adafruit_BBIO.Encoder import RotaryEncoder, eQEP2

form_class = uic.loadUiType("uitest4.ui")[0]
bus = can.interface.Bus(channel='can0', bustype='socketcan_ctypes', bitrate = 1000000)
myEncoder = RotaryEncoder(eQEP2)
myEncoder.enable()
FAN_PIN = 'P8_8'
GPIO.setup(FAN_PIN, GPIO.OUT)
FAN2_PIN = 'P8_10'
GPIO.setup(FAN2_PIN, GPIO.OUT)
GPIO.output(FAN_PIN, GPIO.LOW)
GPIO.output(FAN2_PIN, GPIO.LOW)

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
        global PWM
        global P_gain
        global msg
        BT=24
        PWM = self.PWM
        P_gain = self.P_gain
        msg =self.msg
        self.BicepTemp_S.clicked.connect(self.BicepTemp_S_clicked)
        self.TricepTemp_S.clicked.connect(self.TricepTemp_S_clicked)
        self.BicepH.clicked.connect(self.BicepH_clicked)
        self.BicepC.clicked.connect(self.BicepC_clicked)
        self.BicepHC.clicked.connect(self.BicepHC_clicked)
        self.TricepH.clicked.connect(self.TricepH_clicked)
        self.TricepC.clicked.connect(self.TricepC_clicked)
        self.TricepHC.clicked.connect(self.TricepHC_clicked)
        self.PWMsetbtn.clicked.connect(self.PWMset_clicked)
        self.Psetbtn.clicked.connect(self.Pset_clicked)
        self.BTH.clicked.connect(self.BTH_clicked)
        self.TTH.clicked.connect(self.TTH_clicked)
        self.AngZ.clicked.connect(self.AngZ_clicked)
        self.AngH.clicked.connect(self.AngH_clicked)
        self.PWMlcd.display(PWM)
        self.Plcd.display(P_gain)
        self.Stop.clicked.connect(self.Stop_clicked)
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def BicepTemp_S_clicked(self):
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        message = bus.recv(1.0)
        Temp = message.data[2] + message.data[3] * 256
        BT = Temp // 50 - 273
        self.BicepTemp.display(BT)
        time.sleep(0.1)

    def TricepTemp_S_clicked(self):
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x32, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        message = bus.recv(1.0)
        Temp = message.data[2] + message.data[3] * 256
        TT = Temp // 50 - 273
        self.TricepTemp.display(TT)
        time.sleep(0.1)

    def BicepH_clicked(self):
        print("Start to check Bicep temperature")
        worker = Worker(self.B_time_heating)
        self.threadpool.start(worker)
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def TricepH_clicked(self):
        print("Start to check Bicep temperature")
        worker = Worker(self.T_time_heating)
        self.threadpool.start(worker)
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def B_time_heating(self):
        global PWM
        global BT
        BHT = self.BHtime.value()
        for i in range(1, BHT):
            GPIO.output(FAN_PIN, GPIO.LOW)
            PWM2 = PWM * 1023 // 100
            PWMH = PWM2 // 256
            PWML = PWM2 - PWMH * 256
            msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, PWML, PWMH], extended_id=False)
            bus.send(msg)
            message = bus.recv(1.0)
            Temp = message.data[2] + message.data[3] * 256
            BT = Temp // 50 - 273
            print(i * 0.1, BT)
            self.BicepTemp.display(BT)
            time.sleep(0.1)
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        GPIO.output(FAN_PIN, GPIO.HIGH)

    def BicepC_clicked(self):
        BCT = self.BCtime.value()
        for i in range(1,BCT):
            GPIO.output(FAN_PIN, GPIO.HIGH)
            time.sleep(0.1)
        GPIO.output(FAN_PIN, GPIO.LOW)

    def BicepHC_clicked(self):
        self.BicepH_clicked()
        self.BicepC_clicked()

    def T_time_heating(self):
        global PWM
        global BT
        THT = self.THtime.value()
        for i in range(1, THT):
            GPIO.output(FAN2_PIN, GPIO.LOW)
            PWM2 = PWM * 1023 // 100
            PWMH = PWM2 // 256
            PWML = PWM2 - PWMH * 256
            msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x32, PWML, PWMH], extended_id=False)
            bus.send(msg)
            message = bus.recv(1.0)
            Temp = message.data[2] + message.data[3] * 256
            TT = Temp // 50 - 273
            print(i * 0.1, TT)
            self.TricepTemp.display(TT)
            time.sleep(0.1)
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x32, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        GPIO.output(FAN2_PIN, GPIO.HIGH)

    def TricepC_clicked(self):
        TCT = self.TCtime.value()
        for i in range(1,TCT):
            GPIO.output(FAN2_PIN, GPIO.HIGH)
            time.sleep(0.1)
        GPIO.output(FAN2_PIN, GPIO.LOW)

    def TricepHC_clicked(self):
        self.TricepH_clicked()
        self.TricepC_clicked()

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

    def BTH_clicked(self):
        print("Start to check Bicep temperature")
        worker = Worker(self.BTControl)
        self.threadpool.start(worker)
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def BTControl(self):
        global PWM
        global Stop_push
        Stop_push = True
        Stop_push = False
        DBT = self.DesBT.value()
        BT = 0
        while BT<80:
            PWM2 = PWM*1023//100
            PWMH = PWM2//256
            PWML = PWM2 - PWMH*256
            msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, PWML, PWMH], extended_id=False)
            bus.send(msg)
            message = bus.recv(1.0)
            Temp = message.data[2] + message.data[3] * 256
            BT = Temp // 50 - 273
            self.BicepTemp.display(BT)
            time.sleep(0.1)
            if BT > DBT:
                break
            if Stop_push == True:
                break
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        GPIO.output(FAN_PIN, GPIO.HIGH)

    def TTH_clicked(self):
        print("Start to check Bicep temperature")
        worker = Worker(self.TTControl)
        self.threadpool.start(worker)
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def TTControl(self):
        global PWM
        global Stop_push
        Stop_push = True
        Stop_push = False
        DTT = self.DesTT.value()
        TT = 0
        while TT < 80:
            PWM2 = PWM*1023//100
            PWMH = PWM2//256
            PWML = PWM2 - PWMH*256
            msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x32, PWML, PWMH], extended_id=False)
            bus.send(msg)
            message = bus.recv(1.0)
            Temp = message.data[2] + message.data[3] * 256
            TT = Temp // 50 - 273
            self.TricepTemp.display(TT)
            time.sleep(0.1)
            if TT > DTT:
                break
            if Stop_push == True:
                break
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x32, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        GPIO.output(FAN2_PIN, GPIO.HIGH)

    def AngZ_clicked(self):
        myEncoder.zero()
        Angle = -myEncoder.position*360//8192
        self.Alcd.display(Angle)

    def AngH_clicked(self):
        print("Start to check Bicep temperature")
        worker = Worker(self.AngContol)
        self.threadpool.start(worker)
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def AngControl(self):
        global PWM
        global P_gain
        global Stop_push
        OA = self.DesA.value()
        Stop_push = True
        Stop_push = False
        while Stop_push != True:
            Angle = -myEncoder.position *360 //8192
            PWM2 = PWM * 1023 // 100
            PWMH = PWM2 // 256
            PWML = PWM2 - PWMH * 256
            msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, PWML, PWMH], extended_id=False)
            bus.send(msg)
            message = bus.recv(1.0)
            Temp = message.data[2] + message.data[3] * 256
            BT = Temp // 50 - 273
            DA = OA - Angle

            if DA < 0:
                GPIO.output(FAN_PIN, GPIO.GIGH)
                PWM = 0
            else:
                GPIO.output(FAN_PIN, GPIO.LOW)
                PWM = DA * P_gain

            self.BicepTemp.display(BT)
            self.PWMlcd.display(PWM)
            self.Alcd.display(Angle)
            time.sleep(0.05)

            if BT > 80:
                PWM = 0
                break

        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        message = bus.recv(1.0)
        Temp = message.data[2] + message.data[3] * 256
        BT = Temp // 50 - 273
        self.BicepTemp.display(BT)
        GPIO.output(FAN_PIN, GPIO.HIGH)

    def Stop_clicked(self):
        global Stop_push
        Stop_push = True
        GPIO.output(FAN_PIN, GPIO.LOW)
        GPIO.output(FAN2_PIN, GPIO.LOW)
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x31, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        message = bus.recv(1.0)
        Temp = message.data[2] + message.data[3] * 256
        BT = Temp // 50 - 273
        self.BicepTemp.display(BT)
        msg = can.Message(arbitration_id=0x27F, data=[0x50, 0x57, 0x4D, 0x32, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        message = bus.recv(1.0)
        TTemp = message.data[2] + message.data[3] * 256
        TT = TTemp // 50 - 273
        self.TricepTemp.display(TT)
        Angle = -myEncoder.position * 360 // 8192
        self.Alcd.display(Angle)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

