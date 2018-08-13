import time
from time import sleep
import Adafruit_BBIO.GPIO as GPIO
#import Adafruit_BBIO.ADC as ADC
from Adafruit_BBIO.Encoder import RotaryEncoder, eQEP2
from mlx90614 import MLX90614

myEncoder = RotaryEncoder(eQEP2)
myEncoder.enable()
sensor = MLX90614(address=0x5a,bus_num=2)

#ADC.setup()
#analogPin="P9_39"
Act = 'P8_7'
#Actt = 'P8_9'
Fan = 'P8_9'
#Fann = 'P8_15'
GPIO.setup(Act, GPIO.OUT)
#GPIO.setup(Actt, GPIO.OUT)
GPIO.setup(Fan, GPIO.OUT)
#GPIO.setup(Fann, GPIO.OUT)
GPIO.output(Act, GPIO.HIGH)
GPIO.output(Fan, GPIO.HIGH)


f = raw_input('file name : ')
filename = f + '.txt'
tdata = open(filename, 'a+')

tdata.write("Test start,start,start,start\n")
a=0
R = 0

while a!=4:
    a= int(input('act=1, cool=2, cycle=3, stop=4, zero=5 '))

    if a==1:
        c = int(input('heating time(s) : '))
        b = c*10+1
        GPIO.output(Act, GPIO.LOW)
        tdata.write("Cal_Disp(mm),Temperature('c),Resistance(ohm),Time(s) \n")
        for count in range(1,b):
            distance = myEncoder.position * 0.02
            temp = sensor.get_obj_temp()
#            Vr=ADC.read(analogPin)
#            R=10000*Vr/(1.8-Vr)
            print("%.2f,%d,%d,%.1f\n" % (distance, temp, R, count * 0.1))
            tdata.write("%.2f,%d,%d,%.1f\n" % (distance, temp, R, count * 0.1))
            time.sleep(0.1)
        GPIO.output(Act, GPIO.HIGH)
        for count in range(b,b+11):
            distance = myEncoder.position * 0.02
            temp = sensor.get_obj_temp()
#            Vr=ADC.read(analogPin)
#            R=10000*Vr/(1.8-Vr)
            print("%.2f,%d,%d,%.1f\n" % (distance, temp, R, count * 0.1))
            tdata.write("%.2f,%d,%d,%.1f\n" % (distance, temp, R, count * 0.1))
            time.sleep(0.1)

    elif a==2:
        c = int(input('cooling time(s) : '))
        b = c*5+1
        GPIO.output(Fan, GPIO.LOW)
        tdata.write("Cal_Disp, mm, Sen_Disp, mm, Temperature, 'c, Time, s \n")
        for count in range(1,b):
            distance = myEncoder.position * 0.02
            temp = sensor.get_obj_temp()
#            Vr=ADC.read(analogPin)
#            R=10000*Vr/(1.8-Vr)
            print("%.2f,%d,%d,%.1f\n" % (distance, temp, R, count * 0.1))
            tdata.write("%.2f,%d,%d,%.1f\n" % (distance, temp, R, count * 0.1))
            time.sleep(0.1)
        GPIO.output(Fan, GPIO.HIGH)

    elif a==3:
        ht = int(input('High temp : '))
        ct = int(input('Low temp : '))
        cy = int(input('cycle number : '))
        tdata.write("Cal_Disp(mm),Temperature('c),Resistance(Ohm),Time(s) \n")
        distance = 0.00
        count = 0.00
        temp = 0.00
        R = 0.00
        for cycle in range(1, cy):
            while temp < ht:
                #GPIO.output(Act, GPIO.LOW)
                distance = -myEncoder.position * 0.02
                temp = sensor.get_obj_temp()
#                Vr = ADC.read(analogPin)
#                R = 99.00 * Vr / (1.80 - Vr)
                count = count+1
                print("%.2f,%.2f,%.2f,%.1f,%d" % (distance, temp, R, count * 2, cycle))
                tdata.write("%.2f,%.2f,%.2f,%.1f,%d\n" % (distance, temp, R, count * 2, cycle))
                time.sleep(2)
            GPIO.output(Act, GPIO.HIGH)
            while temp > ct:
                #GPIO.output(Fan, GPIO.LOW)
                distance = -myEncoder.position * 0.02
                temp = sensor.get_obj_temp()
#                Vr = ADC.read(analogPin)
#                R = 99.00* Vr / (1.8 - Vr)
                count = count+1
                print("%.2f,%.2f,%.2f,%.1f,%d" % (distance, temp, R, count * 2, cycle))
                tdata.write("%.2f,%.2f,%.2f,%.1f,%d\n" % (distance, temp, R, count * 2, cycle))
                time.sleep(2)
            GPIO.output(Fan, GPIO.HIGH)
        GPIO.output(Act, GPIO.HIGH)
        GPIO.output(Fan, GPIO.HIGH)
    elif a==5:
        myEncoder.zero()



tdata.close()
