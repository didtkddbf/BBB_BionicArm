import time
#from Adafruit_AMG88xx import Adafruit_AMG88xx
from time import sleep
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
from Adafruit_BBIO.Encoder import RotaryEncoder, eQEP2
from Adafruit_AMG88xx import Adafruit_AMG88xx

myEncoder = RotaryEncoder(eQEP2)
myEncoder.enable()
sensor = Adafruit_AMG88xx(address=0x69, busnum=2)

ADC.setup()
analogPin="P9_39"
Act = 'P8_7'
Actt = 'P8_9'
Fan = 'P8_11'
Fann = 'P8_15'
GPIO.setup(Act, GPIO.OUT)
GPIO.setup(Actt, GPIO.OUT)
GPIO.setup(Fan, GPIO.OUT)
GPIO.setup(Fann, GPIO.OUT)
GPIO.output(Act, GPIO.HIGH)



f = raw_input('file name : ')
filename = f + '.txt'
tdata = open(filename, 'a+')

tdata.write("Cal_Disp(mm),Temperature('c),Time(s) \n")
a=0

while a!=4:
    a= int(input('act=1, cool=2, cycle=3, stop=4 '))

    if a==1:
        c = int(input('heating time(s) : '))
        b = c*10+1
        GPIO.output(Act, GPIO.LOW)
        tdata.write("Cal_Disp(mm),Temperature('c),Resistance(ohm),Time(s) \n")
        for count in range(1,b):
            distance = myEncoder.position * 0.01
            temp = max(sensor.readPixels())
            Vr=ADC.read(analogPin)
            R=10000*Vr/(1.8-Vr)
            print("%.2f,%d,%d,%.1f" % (distance, temp, R, count*0.1))
            tdata.write("%.2f,%d,%d,%.1f" % (distance, temp, R, count*0.1))
            time.sleep(0.1)
        GPIO.output(Act, GPIO.HIGH)
        for count in range(b,b+11):
            distance = myEncoder.position * 0.01
            temp = max(sensor.readPixels())
            Vr=ADC.read(analogPin)
            R=10000*Vr/(1.8-Vr)
            print("%.2f,%d,%d,%.1f" % (distance, temp, R, count*0.1))
            tdata.write("%.2f,%d,%d,%.1f" % (distance, temp, R, count*0.1))
            time.sleep(0.1)

    elif a==2:
        c = int(input('cooling time(s) : '))
        b = c*5+1
        GPIO.output(Fan, GPIO.LOW)
        tdata.write("Cal_Disp, mm, Sen_Disp, mm, Temperature, 'c, Time, s \n")
        for count in range(1,b):
            distance = myEncoder.position * 0.01
            temp = max(sensor.readPixels())
            Vr=ADC.read(analogPin)
            R=10000*Vr/(1.8-Vr)
            print("%.2f,%d,%d,%.1f" % (distance, temp, R, count*0.1))
            tdata.write("%.2f,%d,%d,%.1f" % (distance, temp, R, count*0.1))
            time.sleep(0.1)
        GPIO.output(Fan, GPIO.HIGH)

    elif a==3:
        ht = int(input('heating time(s) : '))
        ct = int(input('cooling time(s) : '))
        cy = int(input('cycle number : '))
        h = ht*10+1
        c = ct*10+1
        tdata.write("Cal_Disp(mm),Temperature('c),Time(s) \n")
        for cycle in range(1, cy):
            for count in range(1, h):
                GPIO.output(Act, GPIO.LOW)
                distance = myEncoder.position * 0.01
                temp = max(sensor.readPixels())
                Vr = ADC.read(analogPin)
                R = 10000 * Vr / (1.8 - Vr)
                print("%.2f,%d,%d,%.1f" % (distance, temp, R, count * 0.1))
                tdata.write("%.2f,%d,%d,%.1f" % (distance, temp, R, count * 0.1))
                time.sleep(0.1)
            GPIO.output(Act, GPIO.HIGH)
            for count in range(1, c):
                GPIO.output(Fan, GPIO.LOW)
                distance = myEncoder.position * 0.01
                temp = max(sensor.readPixels())
                Vr = ADC.read(analogPin)
                R = 10000 * Vr / (1.8 - Vr)
                print("%.2f,%d,%d,%.1f" % (distance, temp, R, count * 0.1))
                tdata.write("%.2f,%d,%d,%.1f" % (distance, temp, R, count * 0.1))
                time.sleep(0.1)
            GPIO.output(Fan, GPIO.HIGH)
        GPIO.output(Act, GPIO.HIGH)
        GPIO.output(Fan, GPIO.HIGH)
    elif a==5:
        myEncoder.zero()



tdata.close()
