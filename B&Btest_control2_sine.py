import sys
import time
from PyQt5.QtWidgets import *
from PyQt5 import uic
import can
from PyQt5.QtCore import *
import math

form_class = uic.loadUiType("Circuit_test_UI2.ui")[0]

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
    Time_inval = 10
    Ki = 0
    Kd = 10
    Kp = 10
    def __init__(self, *args, **kwargs):
        global Ki, Kd, Kp
        Ki = self.Ki
        Kd = self.Kd
        Kp = self.Kp
        super(MyWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.PWM_B_clicked)
        self.pushButton_2.clicked.connect(self.PWM_T_clicked)
        self.pushButton_3.clicked.connect(self.Fan_B_clicked)
        self.pushButton_4.clicked.connect(self.Fan_T_clicked)
        self.Start.clicked.connect(self.Start_clicked)
        self.Cool.clicked.connect(self.Cool_clicked)
        self.Stop.clicked.connect(self.Stop_clicked)
        #self.PWM.display(PWM)
        self.threadpool = QThreadPool()
        #print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    # ---------------PWM_B_setting---------------------
    def PWM_B_clicked(self):
        worker = Worker(self.PWMB_set)
        self.threadpool.start(worker)

    def PWMB_set(self):
        global Time_inval
        Time_inval = self.PWM_B.value()
        print("Time interval = ",Time_inval)

    # ---------------Kp_setting---------------------
    def PWM_T_clicked(self):
        worker = Worker(self.PWMT_set)
        self.threadpool.start(worker)

    def PWMT_set(self):
        global Kp
        Kp = self.PWM_T.value()

    # ---------------Fan_B_setting---------------------
    def Fan_B_clicked(self):
        worker = Worker(self.FanB_set)
        self.threadpool.start(worker)

    def FanB_set(self):
        global Ki
        Ki = self.Ban.value()

    # ---------------Fan_T_setting---------------------
    def Fan_T_clicked(self):
        worker = Worker(self.FanT_set)
        self.threadpool.start(worker)

    def FanT_set(self):
        global Kd
        Kd = self.Tan.value()

    def Cool_clicked(self):
        worker = Worker(self.Cooling)
        self.threadpool.start(worker)

    def Cooling(self):

        global Stop_push
        Stop_push = False
        can_bus = TCA_Controller(0x7f)
        while Stop_push != True:
            can_bus.send(1, 0, 1000)
            can_bus.recv()
            Temp_b = can_bus.temperature
            Force_b = can_bus.force
            R_angle = (can_bus.displacement - 4096)/22.7
            self.Force_1.display(Force_b)
            self.Temp_1.display(Temp_b)
            self.Encoder_1.display(R_angle)
            can_bus.send(2, 0, 1000)
            can_bus.recv()
            Temp_t = can_bus.temperature
            Force_t = can_bus.force
            self.Force_2.display(Force_t)
            self.Temp_2.display(Temp_t)



    def Start_clicked(self):
        print("Time(s) Cur_Ang Obj_Ang Force_t Temp_b Temp_t PWM_b PWM_t")
        worker = Worker(self.Loop)
        self.threadpool.start(worker)
        #print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def Loop(self):

        global Time_inval
        global Kp
        global Ki
        global Kd
        global Stop_push
        Stop_push = False
        #-------------Varaibles Initialization-----------
        PWM_1 = 0
        PWM_2 = 0
        Fan_1 = 0
        Fan_2 = 0
        Temp_b = 0
        Temp_t = 0
        Force_b = 0
        Force_t = 0

        #----------------Control setting-------------------
        #-----PID value------------
        Ki = 0
        Kd = 0
        Kp = 30
        Time_inval = self.Time_inval
        Kpp = 20
        Kdd = 10

        #-----Angle value-----------
        cur_Ang = 0
        obj_Ang = 0
        C2A=22.7
        error = 0
        error_prev = 0

        #-----------CAN Initializtion---------------------
        can_bus = TCA_Controller(0x7f)
        can_bus.send(1, 0, 0)
        can_bus.recv()
        can_bus.send(2, 0, 0)
        can_bus.recv()
        org_Ang = can_bus.displacement

        #--------Time Initializtion---------------------
        dt = 0
        dt_sleep = 0.1
        Tolerance = 0.2
        count = 0.0
        start_time = time.time()
        time_prev = 0


        while Stop_push != True:
            cur_Ang = (can_bus.displacement-4096)/22.7
            cur_time = time.time()-start_time
        #-----------Object Angle-----------------
            # if count<3:                         # Start point
            #     obj_Ang = org_Ang
            #
            # elif count >= 3 and count < Time_inval+3:      # 0 to 45deg
            #     obj_Ang = org_Ang + 45*C2A
            #
            # else :
            #     obj_Ang = org_Ang

            if cur_time < 30:                         # Start point
                obj_Ang = 20

            elif cur_time < 230:
                obj_Ang = 10*math.sin(math.pi/50*(cur_time-30+75)) + 30

            else :    # 45deg to 5
                obj_Ang = 20

        # ----------Error Calculation-----------
            error = obj_Ang - cur_Ang
            de = error - error_prev
            dt = time.time() - time_prev
            control = int(Kp*error)
            control2 =int(Kpp * error)

            if abs(error) <= Tolerance:
                PWM_1 = int(0 + 12.45*obj_Ang - 121.76 - 0.14*obj_Ang*obj_Ang)
                # if obj_Ang < 20:
                #     PWM_2 = abs(int(control2 -0.8936*obj_Ang + 21.089))
                # else :
                #     PWM_2 = 0
                Fan_1 = 0
                Fan_2 = 0

            elif error > Tolerance:
                PWM_1 = int(abs(control) + 12.45*obj_Ang - 121.76 - 0.14*obj_Ang*obj_Ang)
                PWM_2 = 0
                Fan_1 = 0
                Fan_2 = 1023
                if PWM_1 > 1023:
                    PWM_1 = 1023

            else:
                PWM_1 = 0
                if obj_Ang < 10:
                    PWM_2 = abs(int(control2 -0.8936*obj_Ang + 21.089))
                else :
                    PWM_2 = abs(control2)
                Fan_1 = 1023
                Fan_2 = 0
                if PWM_2 > 1023:
                    PWM_2 = 1023

            # if obj_Ang < 20:
            #     PWM_1 = 0

            if Temp_b > 60:
                PWM_1 = 0

            if Temp_t > 60:
                PWM_2 = 0



            can_bus.send(1, PWM_1, Fan_1)
            can_bus.recv()
            Temp_b = can_bus.temperature
            Force_b = can_bus.force
            self.ADC_1.display(PWM_1)
            # self.Force_1.display(Force_b)
            self.Temp_1.display(Temp_b)
            self.Encoder_1.display(cur_Ang)

            can_bus.send(2, PWM_2, Fan_2)
            can_bus.recv()
            Temp_t = can_bus.temperature
            Force_t = can_bus.force
            # self.Force_2.display(Force_t)
            self.ADC_2.display(PWM_2)
            self.Temp_2.display(Temp_t)

            print('{0} {1} {2} {3} {4} {5} {6} {7}'.format((time.time()-start_time), cur_Ang, obj_Ang, Force_t, Temp_b, Temp_t, PWM_1, PWM_2))
            #------------Previous DATA---------------
            error_prev = error
            time_prev = time.time()
            count = count + 0.1
            time.sleep(0.02)

    def Stop_clicked(self):
        global Stop_push
        Stop_push = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()