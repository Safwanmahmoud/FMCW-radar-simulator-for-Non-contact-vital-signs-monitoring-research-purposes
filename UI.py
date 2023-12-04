from PyQt5.QtWidgets import *
from PyQt5 import uic
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("UI.ui", self)
        self.show()
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.horizontalLayout.addWidget(self.canvas)
        self.checkBox_2.stateChanged.connect(self.static_or_human)
        self.pushButton.clicked.connect(self.generate)
        self.pushButton_5.clicked.connect(self.set)
        self.pushButton_3.clicked.connect(self.add)
        self.pushButton_4.clicked.connect(self.clear)
        self.pushButton_2.clicked.connect(self.export)
        self.progressBar.setValue(0)
        self.progressBar_2.setValue(0)
        self.C = 2.997e8
        self.A = 5
        self.data = []
        self.human_static = []
        self.heart_rates = []
        self.Resp_rates = []
        self.ranges = []
        self.HRV = []


    def to_csv(t,name, nr_of_decimal = 18):
        t_new = np.matrix(np.zeros((t.shape[0], 2)))
        t_new[:,:] = np.round(np.array(((str(np.array(t[:])[0][0])[1:-2]).split('+')), dtype=float), decimals=nr_of_decimal)
        (pd.DataFrame(t_new)).to_csv(name + ".csv", index = False, header = False)


    def export(self):
        Nc = int(self.lineEdit_6.text())
        counter = 0
        fast_time = np.arange(0, self.Ncs, 1)
        data = []
        t = np.arange(0, (1/self.fps) * Nc, 1 / self.fps)
        I_channel = np.zeros(self.Ncs)
        Q_channel = np.zeros(self.Ncs)
        
        for chirp in range(Nc): 
            I_channel = np.zeros(self.Ncs)
            Q_channel = np.zeros(self.Ncs)
            counter += int(Nc / 100)
            self.progressBar_2.setValue(counter)
            big_noise = np.random.normal(0, self.noise_level_chirps, self.Ncs)
            # The effect of objects and humans on frequency "range profile"
            for object in range(len(self.ranges)):
                if self.human_static[object]:
                    hrv = np.random.normal(0, self.HRV[object], 1)    # Additive white Gaussian noise (AWGN)
                    human_rythm = 0.01 * (np.sin(t * (self.Resp_rates[object] / 60) * 2 * np.pi) + np.sin(t * (self.heart_rates[object] / 60) * 2 * np.pi) + hrv)
                    human_ranged_rythm = human_rythm + self.ranges[object]
                    fn = self.S * 2 * human_ranged_rythm[chirp] * (1/self.C)

                    I_channel += self.A * np.cos(2* np.pi * fast_time * fn * self.Ts + human_rythm[chirp] )
                    Q_channel += self.A * np.sin(2* np.pi * fast_time * fn * self.Ts + human_rythm[chirp] ) #% (360 * self.d_res_angle)
                else:
                    fn = self.S * 2 * self.ranges[object] * (1/self.C)
                    I_channel += self.A * np.cos(2* np.pi * fast_time * fn * self.Ts)
                    Q_channel += self.A * np.sin(2* np.pi * fast_time * fn * self.Ts)

            I_channel += big_noise
            Q_channel += big_noise
            chirp_ = np.vectorize(complex)(I_channel, Q_channel)
            data.append(chirp_.tolist())
        np.savetxt("generated data/" + self.lineEdit_13.text() +".txt", np.array(data).view(float))


    def static_or_human(self):
        if self.checkBox_2.checkState() == 0:
            self.lineEdit_8.setEnabled(True)
            self.lineEdit_9.setEnabled(True)
        else:
            self.lineEdit_8.setEnabled(False)
            self.lineEdit_9.setEnabled(False)


    def set(self):
        self.Ncs = int(self.lineEdit.text())
        self.Nc = self.Ncs
        self.B = float(self.lineEdit_2.text()) * 10**9
        self.Fs = float(self.lineEdit_3.text()) * 10**6
        self.Tc = float(self.lineEdit_4.text()) * 10**(-6)
        self.fps = int(self.lineEdit_5.text())
        self.noise_level_chirps = float(self.lineEdit_10.text())
        self.start_freq = float(self.lineEdit_12.text()) * 10**9
        self.S = self.B / self.Tc
        self.Ts = self.Tc / self.Ncs
        self.Wl = self.C / (self.start_freq  + 0.5 * self.B)
        d_max = (self.Fs * self.C) / (2 * self.S)
        d_res_freq = self.C / (2 * self.B)
        self.d_res_angle = self.Wl / (4 * np.pi)
        self.label_20.setText(str(round(self.d_res_angle * 10**3, 4)))
        self.label_14.setText(str(round(d_res_freq * 10**3, 4)))
        self.label_16.setText(str(d_max))
        self.label_10.setText("(Max " + str(math.ceil(d_max))+")")
        self.fast_time = np.arange(0, self.Ncs, 1)
        self.t = (1/self.fps) 


    def add(self):
        self.ranges.append(float(self.lineEdit_7.text()))
        if self.checkBox_2.checkState() == 0:
            self.textEdit.append("Human - " + self.lineEdit_7.text())
            self.human_static.append(1)
            self.heart_rates.append(float(self.lineEdit_8.text()))
            self.Resp_rates.append(float(self.lineEdit_9.text()))
            self.HRV.append(float(self.lineEdit_11.text()))
        else:
            self.textEdit.append("Object - " + self.lineEdit_7.text())
            self.human_static.append(0)
            self.heart_rates.append(0)
            self.Resp_rates.append(0)


    def clear(self):
        self.human_static = []
        self.heart_rates = []
        self.Resp_rates = []
        self.ranges = []
        self.HRV = []
        self.textEdit.clear()

    
    def generate(self):
        counter = 0
        fast_time = np.arange(0, self.Ncs, 1)
        data = []
        t = np.arange(0, (1/self.fps) * self.Nc, 1 / self.fps)
        I_channel = np.zeros(self.Ncs)
        Q_channel = np.zeros(self.Ncs)
        for chirp in range(self.Nc):
            I_channel = np.zeros(self.Ncs)
            Q_channel = np.zeros(self.Ncs)
            counter += int(self.Nc / 100)
            self.progressBar.setValue(counter)
            big_noise = np.random.normal(0, self.noise_level_chirps, self.Ncs)
            for object in range(len(self.ranges)):
                if self.human_static[object]:
                    hrv = np.random.normal(0, self.HRV[object], 1)
                    human_rythm = 0.01 * (np.sin(t * (self.Resp_rates[object] / 60)) + np.sin(t * (self.heart_rates[object] / 60)) + hrv)
                    human_ranged_rythm = human_rythm + self.ranges[object]
                    fn = self.S * 2 * human_ranged_rythm[chirp] * (1/self.C)
                    I_channel += self.A * np.cos(2* np.pi * fast_time * fn * self.Ts + human_rythm[chirp] % (360 * self.d_res_angle))
                    Q_channel += self.A * np.sin(2* np.pi * fast_time * fn * self.Ts + human_rythm[chirp] % (360 * self.d_res_angle))
                else:
                    fn = self.S * 2 * self.ranges[object] * (1/self.C)
                    I_channel += self.A * np.cos(2* np.pi * fast_time * fn * self.Ts)
                    Q_channel += self.A * np.sin(2* np.pi * fast_time * fn * self.Ts)
            I_channel += big_noise
            Q_channel += big_noise
            chirp_ = np.vectorize(complex)(I_channel, Q_channel)
            data.append(chirp_.tolist())
        self.figure.clear()
        plt.imshow(np.abs(np.fft.fft(data, axis = 1)).transpose())
        self.canvas.draw()

def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()

main()
