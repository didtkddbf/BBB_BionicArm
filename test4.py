import sys
import time
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("uitest1.ui")[0]

class MyWindow(QMainWindow, form_class):
    BHT = 0
    PWM = 50
    P_gain = 10
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        global PWM
        global P_gain
        PWM = self.PWM
        P_gain = self.P_gain
        self.BicepH.clicked.connect(self.BicepH_clicked)
        self.BicepC.clicked.connect(self.BicepC_clicked)
        self.BicepHC.clicked.connect(self.BicepHC_clicked)
        self.TricepH.clicked.connect(self.TricepH_clicked)
        self.TricepC.clicked.connect(self.TricepC_clicked)

        self.PWMsetbtn.clicked.connect(self.PWMset_clicked)
        self.Psetbtn.clicked.connect(self.Pset_clicked)
        self.PWMlcd.display(PWM)
        self.Plcd.display(P_gain)

    def BicepH_clicked(self):
        global PWM
        BHT = self.BHtime.value()
        for i in range(1,BHT):
            print(i)
            print(PWM)
            self.BicepTemp.display(i)
            time.sleep(0.1)

    def BicepC_clicked(self):
        BCT = self.BCtime.value()
        for i in range(1,BCT):
            self.BicepTemp.display(i)
            time.sleep(0.1)


    def BicepHC_clicked(self):
        BHT = self.BHtime.value()
        BCT = self.BCtime.value()
        for i in range(1,BHT):
            print(i)
            self.BicepTemp.display(i)
            time.sleep(0.1)
        for j in range(1,BCT):
            self.BicepTemp.display(j)
            time.sleep(0.1)


    def TricepH_clicked(self):
        THT = self.THtime.value()
        for i in range(1,THT):
            print(i)
            self.TricepTemp.display(i)
            time.sleep(0.1)

    def TricepC_clicked(self):
        TCT = self.TCtime.value()
        for i in range(1,TCT):
            self.TricepTemp.display(i)
            time.sleep(0.1)


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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
