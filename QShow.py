import sys
import time
import random
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
# from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QThread
from PyQt5 import QtWidgets
from streamDetectionPlot import streamDetectionPlot


class Show(QtWidgets.QDialog):
    def __init__(self, parent=None):
        # 父类初始化方法
        super(Show, self).__init__(parent)
        self.period = 1
        self.num = 20
        self.X, self.Y, self.Z, self.R, self.V = [0], [0], [0], [90], [np.zeros((3,))]
        self.A, self.k, self.theta, self.alpha = 0, 0, 0, 0.05 * np.pi
        self.vx, self.vy, self.vz = 0, 0, 0
        self.Close = False
        self.clear = False

        # 几个QWidgets
        self.Stream = streamDetectionPlot(self.X, self.Y, self.Z, self.R, self.V)

        # 设置布局
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.Stream)
        self.setLayout(layout)

        thread = QThread(self)
        thread.run = self.Handle_Data
        thread.start()

    def Handle_Data(self):
        while 1:
            if self.Close:
                break
            if self.A == 0:
                self.vx, self.vy, self.vz = 0, 0, 0
            else:
                self.theta -= self.k * self.alpha
                self.vx = self.A * np.cos(self.theta)
                self.vy = self.A * np.sin(self.theta)
                self.vz = 0
            v, r = np.array([self.vx, self.vy, self.vz]), 0
            if (v == 0).all():
                plt.pause(0.01)
                continue
            t = self.period / self.num
            coef = 2
            last_v = self.V[-1]
            v_distance = v - last_v
            coefs = np.zeros_like(v_distance)
            coefs[:] = coef
            bias_t = 0
            flag = False  # 用于计算时间偏差, 2个来回一次循环
            for i in range(1, self.num + 1):
                cur_t = time.time()
                weight = (i / self.num) ** coefs
                cur_v = (weight * v_distance + last_v)
                self.V.append(cur_v)
                self.X.append(self.X[-1] + cur_v[0] * t)
                self.Y.append(self.Y[-1] + cur_v[1] * t)
                self.Z.append(self.Z[-1] + cur_v[2] * t)
                self.R.append(r)
                time.sleep(t - bias_t)
                flag = not flag
                if flag:
                    temp_t = time.time() - cur_t - t
                    bias_t = temp_t if temp_t < t else t
                else:
                    bias_t = 0
                if not self.Stream.pause:
                    if not self.clear:
                        self.Stream.DetectionPlot(self.X, self.Y, self.Z, self.R, self.V)
                        self.Stream.draw()
                    else:
                        self.X, self.Y, self.Z, self.R, self.V = [0], [0], [0], [90], [np.zeros((3,))]
                        self.Stream.DetectionPlot(self.X, self.Y, self.Z, self.R, self.V)
                        self.Stream.DetectionPlot(self.X, self.Y, self.Z, self.R, self.V)
                        self.Stream.draw()
                        self.clear = False

    def Clear(self):
        if self.A == 0:
            self.X, self.Y, self.Z, self.R, self.V = [0], [0], [0], [90], [np.zeros((3,))]
            self.Stream.DetectionPlot(self.X, self.Y, self.Z, self.R, self.V)
            self.Stream.DetectionPlot(self.X, self.Y, self.Z, self.R, self.V)
            self.Stream.draw()
        else:
            self.clear = True


# 运行程序
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = Show()
    main_window.show()
    sys.exit(app.exec())
