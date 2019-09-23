import sys
import time
import serial
import re
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

form_class = uic.loadUiType("Shoulder_UI.ui")[0]

#----------Arduino Serial setting---------------
AD = serial.Serial(
    port='COM3',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0)

#--------------File initialize----------------------

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
    Xaxis = 0
    Yaxis = 0
    Zaxis = 0
    S_speed = 0

    def __init__(self, *args, **kwargs):
        super(MyWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.ShoulderSend.clicked.connect(self.SerialSend)
        self.ShoulderZeroSet.clicked.connect(self.ShoulderZero)
        self.ShoulderFree.clicked.connect(self.ShoulderFreeSet)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    # ---------------PWM_B_setting---------------------
    def SerialSend(self):
        Xaxis = str(self.XaxisValue.value())
        Yaxis = str(self.YaxisValue.value())
        Zaxis  = str(self.ZaxisValue.value())
        S_speed = str(self.ShoulderSpeed.value())
        ShoulderMove = "r \n" + Xaxis + " " + Yaxis + " " + Zaxis + " " + S_speed +"\n"
        print(ShoulderMove)
        AD.write(bytes(ShoulderMove, encoding='ascii'))
        Datalist = []
        print("Sended DATA")
        time.sleep(2)
        if AD.readable():
            serialData = AD.readline()
            print(serialData)
            serialString = serialData.decode()
            serialList = serialString.split()
            Datalist = list(map(float, serialList))

        if Datalist[0] == 1:
            self.CommentLCD.append('Shoulder move')
        else:
            self.CommentLCD.append('Failed')
        self.XaxisLCD.display(Datalist[1])
        self.YaxisLCD.display(Datalist[2])
        self.ZaxisLCD.display(Datalist[3])

    def ShoulderZero(self):
        AD.write(b'z')
        self.CommentLCD.append('Zero Set')

    def ShoulderFreeSet(self):
        AD.write(b'f')
        self.CommentLCD.append('Free move')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()



tdata.close()