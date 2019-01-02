import sys
import time
from PyQt5.QtWidgets import *
from PyQt5 import uic
import RPi.GPIO as GPIO
from PyQt5.QtCore import *
from Adafruit_AMG88xx import Adafruit_AMG88xx

form_class = uic.loadUiType("uitest4.ui")[0]


#Motor driver setting
GPIO.setmode(GPIO.BCM)			# GPIO numbering
GPIO.setwarnings(False)			# enable warning from GPIO
AN2 = 13				# set pwm2 pin on MD10-Hat
AN1 = 12				# set pwm1 pin on MD10-hat
DIG2 = 24				# set dir2 pin on MD10-Hat
DIG1 = 26				# set dir1 pin on MD10-Hat
GPIO.setup(AN2, GPIO.OUT)		# set pin as output
GPIO.setup(AN1, GPIO.OUT)		# set pin as output
GPIO.setup(DIG2, GPIO.OUT)		# set pin as output
GPIO.setup(DIG1, GPIO.OUT)		# set pin as output
time.sleep(1)				# delay for 1 seconds
pB = GPIO.PWM(DIG1, 100)		# set pwm for M1
pT = GPIO.PWM(DIG2, 100)		# set pwm for M2
pB.start(0)
pT.start(0)

#Fan setting
FAN_PIN = 16
FAN2_PIN = 18
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(FAN2_PIN, GPIO.OUT)
GPIO.output(FAN_PIN, GPIO.LOW)
GPIO.output(FAN2_PIN, GPIO.LOW)

sensor = Adafruit_AMG88xx(address=0x69, busnum=1)
sensor2 = Adafruit_AMG88xx(address=0x68, busnum=1)

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
    P_gain = 2
    def __init__(self, *args, **kwargs):
        super(MyWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        global PWM
        global P_gain
        global msg
        BT=24
        PWM = self.PWM
        P_gain = self.P_gain
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
        BT = max(sensor.readPixels())
        self.BicepTemp.display(BT)
        time.sleep(0.1)

    def TricepTemp_S_clicked(self):
        TT = max(sensor2.readPixels())
        self.TricepTemp.display(TT)
        time.sleep(0.1)

    def BicepH_clicked(self):
        print("Start to check Bicep temperature")
        worker = Worker(self.B_time_heating)
        self.threadpool.start(worker)

    def TricepH_clicked(self):
        print("Start to check Bicep temperature")
        worker = Worker(self.T_time_heating)
        self.threadpool.start(worker)

    def B_time_heating(self):
        global PWM
        global BT
        BHT = self.BHtime.value()
        GPIO.output(FAN_PIN, GPIO.LOW)
        for i in range(1, BHT):
            pB.ChangeDutyCycle(PWM)
            BT = max(sensor.readPixels())
            print(i * 0.1, BT)
            self.BicepTemp.display(BT)
            time.sleep(0.1)
        GPIO.output(FAN_PIN, GPIO.HIGH)
        pB.ChangeDutyCycle(0)

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
        GPIO.output(FAN2_PIN, GPIO.LOW)
        for i in range(1, THT):
            pT.ChangeDutyCycle(PWM)
            TT = max(sensor2.readPixels())
            print(i * 0.1, TT)
            self.TricepTemp.display(TT)
            time.sleep(0.1)
        GPIO.output(FAN2_PIN, GPIO.HIGH)
        pT.ChangeDutyCycle(0)

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
        global P_gain
        global Stop_push
        Stop_push = True
        time.sleep(0.1)
        Stop_push = False
        DBT = self.DesBT.value()
        BT = max(sensor.readPixels())
        while BT<80:
            PWM = (DBT - BT)*P_gain
            if PWM > 100:
                PWM = 100
            pB.ChangeDutyCycle(PWM)
            BT = max(sensor.readPixels())
            self.BicepTemp.display(BT)
            time.sleep(0.1)
            if BT > DBT:
                break
            if Stop_push == True:
                break
        GPIO.output(FAN_PIN, GPIO.HIGH)
        pB.ChangeDutyCycle(0)

    def TTH_clicked(self):
        print("Start to check Bicep temperature")
        worker = Worker(self.TTControl)
        self.threadpool.start(worker)
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def TTControl(self):
        global PWM
        global Stop_push
        Stop_push = True
        time.sleep(0.1)
        Stop_push = False
        DTT = self.DesTT.value()
        TT = max(sensor2.readPixels())
        while TT<80:
            PWM = (DTT - TT)*P_gain
            if PWM > 100:
                PWM = 100
            pT.ChangeDutyCycle(PWM)
            TT = max(sensor2.readPixels())
            self.TricepTemp.display(TT)
            time.sleep(0.1)
            if TT > DTT:
                break
            if Stop_push == True:
                break
        GPIO.output(FAN2_PIN, GPIO.HIGH)
        pT.ChangeDutyCycle(0)

     def AngZ_clicked(self):
         myEncoder.zero()
         Angle = -myEncoder.position*360//8192
         self.Alcd.display(Angle)

     def AngH_clicked(self):
         print("Start to check Bicep temperature")
         worker = Worker(self.AngControl)
         self.threadpool.start(worker)
         print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def AngControl(self):
        global PWM
        global P_gain
        global Stop_push
        OAA = self.DesA.value()
        Stop_push = True
        Stop_push = False
        count=0
        while Stop_push != True:
            Angle = -myEncoder.position *360 //8192
            OA = OAA - 20 + 20*math.sin(math.pi/4*count)
            DA = OA - Angle
            if DA > 0:
                GPIO.output(FAN2_PIN, GPIO.HIGH)
                GPIO.output(FAN_PIN, GPIO.LOW)
                BT = max(sensor.readPixels())
                PWM = DA * P_gain
                if PWM > 100:
                    PWM = 100
                if BT > 70:
                    PWM = 0
                pB.ChangeDutyCycle(PWM)

            else:
                GPIO.output(FAN_PIN, GPIO.HIGH)
                GPIO.output(FAN2_PIN, GPIO.LOW)
                TT = max(sensor.readPixels())
                PWM = -DA * P_gain
                if PWM > 100:
                    PWM = 100
                if TT > 70:
                    PWM = 0

                pT.ChangeDutyCycle(PWM)

            self.BicepTemp.display(BT)
            self.TricepTemp.display(TT)
            self.PWMlcd.display(PWM)
            self.Alcd.display(Angle)
            self.Alcd_2.display(OA)
            count=count+0.05
            time.sleep(0.05)

            if BT > 70 or TT > 70:
                PWM = 0
                break
        GPIO.output(FAN_PIN, GPIO.HIGH)
        GPIO.output(FAN2_PIN, GPIO.HIGH)

    def Stop_clicked(self):
        global Stop_push
        Stop_push = True
        pB.ChangeDutyCycle(0)
        pT.ChangeDutyCycle(0)
        GPIO.output(FAN_PIN, GPIO.LOW)
        GPIO.output(FAN2_PIN, GPIO.LOW)
        BT = max(sensor.readPixels())
        TT = max(sensor2.readPixels())
        self.BicepTemp.display(BT)
        self.TricepTemp.display(TT)
        # Angle = -myEncoder.position * 360 // 8192
        # self.Alcd.display(Angle)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

