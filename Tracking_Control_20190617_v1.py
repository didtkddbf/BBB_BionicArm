import sys
import time
from PyQt5.QtWidgets import *
from PyQt5 import uic
import can
from PyQt5.QtCore import *

form_class = uic.loadUiType("Circuit_test_UI.ui")[0]

# bus = can.interface.Bus(bustype = 'kvaser', channel=0, bitrate = 1000000)

class TCA_Controller:
    def __init__(self, can_id=0x7f):
        self._PDO_Tx = 0x03
        self._PDO_Rx = 0x04
        self._tx_id = self._PDO_Tx << 7 | can_id
        self._rx_id = self._PDO_Rx << 7 | can_id
        self.bus = can.interface.Bus(bustype = 'kvaser', channel=0, bitrate = 1000000)

        self._rx_message = None
        self.conf = "None"
        self.temperature = 0.0
        self.displacement = 0
        self.force = 0

    def send(self, conf=None, tca_pwm=0, fan_pwm=0):
        if tca_pwm > 1023 & tca_pwm < 0:
            print("pwm_val is out of range(0 <= pwm_val < 1024)")
            return 0
        else:
            tca_pwm_array = tca_pwm.to_bytes(2, 'little')
            _tca_pwm_low = tca_pwm_array[0]
            _tca_pwm_high = tca_pwm_array[1]

        if fan_pwm > 1023 & fan_pwm < 0:
            print("pwm_val is out of range(0 <= pwm_val < 1024)")
            return 0
        else:
            fan_pwm_array = fan_pwm.to_bytes(2, 'little')
            _fan_pwm_low = fan_pwm_array[0]
            _fan_pwm_high = fan_pwm_array[1]

        if conf == 1:
            tx_message = can.Message(arbitration_id=self._tx_id, is_extended_id=False,
                                     data=[0x50, 0x31, _tca_pwm_low, _tca_pwm_high, _fan_pwm_low, _fan_pwm_high])
            self.bus.send(tx_message, timeout=0.5)

            self._rx_message = self.bus.recv()

        elif conf == 2:
            tx_message = can.Message(arbitration_id=self._tx_id, is_extended_id=False,
                                     data=[0x50, 0x32, _tca_pwm_low, _tca_pwm_high, _fan_pwm_low, _fan_pwm_high])
            self.bus.send(tx_message, timeout=0.5)

            self._rx_message = self.bus.recv()

    def recv(self):
        self._conv(self._rx_message)
        return self._rx_message

    def _conv(self, message):
        if message.data[1] == 0x31:
            self.conf = "P1"
        elif message.data[1] == 0x32:
            self.conf = "P2"
        _temperature = message.data[2] + (message.data[3] << 8)
        self.temperature = _temperature * 0.02 - 273.15
        self.displacement = message.data[4] + (message.data[5] << 8)
        self.force = message.data[6] + (message.data[7] << 8)

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
    PWM_1 = 0
    PWM_2 = 0
    Fan_1 = 0
    Fan_2 = 0
    def __init__(self, *args, **kwargs):
        super(MyWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        global PWM_1
        global PWM_2
        global Fan_1
        global Fan_2
        PWM_1 = self.PWM_1
        PWM_2 = self.PWM_2
        Fan_1 = self.Fan_1
        Fan_2 = self.Fan_2
        self.pushButton.clicked.connect(self.PWM_B_clicked)
        self.pushButton_2.clicked.connect(self.PWM_T_clicked)
        self.pushButton_3.clicked.connect(self.Fan_B_clicked)
        self.pushButton_4.clicked.connect(self.Fan_T_clicked)
        self.Start.clicked.connect(self.Start_clicked)
        self.Stop.clicked.connect(self.Stop_clicked)
        #self.PWM.display(PWM)
        self.threadpool = QThreadPool()
        #print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())



    # ---------------PWM_B_setting---------------------
    def PWM_B_clicked(self):
        worker = Worker(self.PWMB_set)
        self.threadpool.start(worker)

    def PWMB_set(self):
        global PWM_1
        PWM_1 = self.PWM_B.value()
        print(PWM_1)

    # ---------------PWM_T_setting---------------------
    def PWM_T_clicked(self):
        worker = Worker(self.PWMT_set)
        self.threadpool.start(worker)

    def PWMT_set(self):
        global PWM_2
        PWM_2 = self.PWM_T.value()
        print(PWM_2)

    # ---------------Fan_B_setting---------------------
    def Fan_B_clicked(self):
        worker = Worker(self.FanB_set)
        self.threadpool.start(worker)

    def FanB_set(self):
        global Fan_1
        Fan_1 = self.Ban.value()
        print(Fan_1)

    # ---------------Fan_T_setting---------------------
    def Fan_T_clicked(self):
        worker = Worker(self.FanT_set)
        self.threadpool.start(worker)

    def FanT_set(self):
        global Fan_2
        Fan_2 = self.Tan.value()
        print(Fan_2)



    def Start_clicked(self):
        print("Start")
        worker = Worker(self.Loop)
        self.threadpool.start(worker)
        #print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def Loop(self):
        global PWM_1
        global PWM_2
        global Fan_1
        global Fan_2
        global Stop_push
        Stop_push = False
        can_bus = TCA_Controller(0x7f)
        can_bus.send(1, 0, 0)
        can_bus.recv()
        can_bus.send(2, 0, 0)
        can_bus.recv()
        i = 0
        cur_Ang = 0
        cur_Ang = can_bus.displacement
        org_Ang = cur_Ang
        obj_Ang = 0
        C2A=23
        count = 0.0
        error = 0
        P_gain = 10
        PWM_1 = 0
        PWM_2 = 0
        Fan_2 = 1023
        Fan_1 = 1023
        Temp_b = 0
        Temp_t = 0
        Force_b = 0
        Force_t = 0
        while Stop_push != True:
            cur_Ang = can_bus.displacement

            if count<3:                         # Start point
                obj_Ang = int(org_Ang)
                error = int(obj_Ang - cur_Ang)

            elif count >= 3 and count < 8:      # 0 to -10deg
                t = count - 3.0
                obj_Ang = int(org_Ang - 2 * t * C2A)
                error = int(obj_Ang - cur_Ang)

            elif count >= 8 and count < 13:     # -10deg cont
                obj_Ang = int(org_Ang - 10*C2A)
                error = obj_Ang - cur_Ang

            elif count >= 13 and count < 18:    # -10deg to -5deg
                t = count - 13
                obj_Ang = int(org_Ang - 10*C2A + 1*t*C2A)
                error = obj_Ang - cur_Ang

            elif count >= 18 and count < 23:    # -5deg cont
                obj_Ang = int(org_Ang - 5*C2A)
                error = obj_Ang - cur_Ang

            elif count >= 23 and count < 28:    # -5deg to 5
                t = count - 23
                obj_Ang = int(org_Ang - 5*C2A + 2*t*C2A)
                error = obj_Ang - cur_Ang

            elif count >= 28 and count < 40:  # 5deg cont
                obj_Ang = int(org_Ang + 5 * C2A)
                error = obj_Ang - cur_Ang

            else :
                PWM_1=0
                PWM_2=0
                Fan_1=1023
                Fan_2=1023


            if error > 0:
                PWM_1 = error * P_gain
                Fan_1 = 0
                Fan_2 = 1023
                if PWM_1 > 1023:
                    PWM_1 = 1023
            else:
                PWM_2 = - error * P_gain
                Fan_1 = 1023
                Fan_2 = 0
                if PWM_2 > 1023:
                    PWM_2 = 1023

            count = count + 0.1

            can_bus.send(1, PWM_1, Fan_1)
            can_bus.recv()
            Temp_b = can_bus.temperature
            Force_b = can_bus.force
            self.Force_1.display(can_bus.force)
            self.Temp_1.display(can_bus.temperature)
            self.Encoder_1.display(can_bus.displacement)

            can_bus.send(2, PWM_2, Fan_2)
            can_bus.recv()
            Temp_t = can_bus.temperature
            Force_t = can_bus.force
            self.Force_2.display(can_bus.force)
            self.Temp_2.display(can_bus.temperature)

            print('{0} {1} {2} {3} {4} {5} {6} {7} {8}'.format(count,cur_Ang,obj_Ang,PWM_1,PWM_2,Temp_b,Temp_t,Force_b,Force_t))

            time.sleep(0.1)

    def Stop_clicked(self):
        global Stop_push
        Stop_push = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
