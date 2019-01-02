import sys
import time
#from PyQt5.QtWidgets import *
#from PyQt5 import uic
import RPi.GPIO as GPIO
#from PyQt5.QtCore import *
from Adafruit_AMG88xx import Adafruit_AMG88xx

#form_class = uic.loadUiType("ui_sine.ui")[0]


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
FAN_PIN = 23
FAN2_PIN = 24
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(FAN2_PIN, GPIO.OUT)
GPIO.output(FAN_PIN, GPIO.LOW)
GPIO.output(FAN2_PIN, GPIO.LOW)

sensor = Adafruit_AMG88xx(address=0x69, busnum=1)
sensor2 = Adafruit_AMG88xx(address=0x68, busnum=1)

clk = 16
dt =  20

GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clkLastState = GPIO.input(clk)

def my_callback(channel):
    global clkLastState
    global counter
    try:
                clkState = GPIO.input(clk)
                if clkState != clkLastState:
                        dtState = GPIO.input(dt)
                        if dtState != clkState:
                                counter += 1
                        else:
                                counter -= 1
                clkLastState = clkState
                print(counter)
                #sleep(0.0)
    finally:
                print("??")

counter = 0
clkLastState = GPIO.input(clk)
GPIO.add_event_detect(16, GPIO.FALLING  , callback=my_callback, bouncetime=1)
a=0

try:
    while a!=4:
        a = int(input('check=1, zero=2, temp=3, stop=4 '))

        if a==1:
            for i in range(1,10):
           	 print (counter)
           	 time.sleep(0.5)

        elif a==2:
            counter = 0

        elif a==3:
            print(max(sensor.readPixels()))
            print(max(sensor2.readPixels()))

except KeyboardInterrupt:
    print ("ctl+c")

except:
    # this catches ALL other exceptions including errors.
    # You won't get any error messages for debugging
    # so only use it once your code is working
    print ("Other error or exception occurred!")

finally:
    GPIO.cleanup()  # this ensures a clean exit
