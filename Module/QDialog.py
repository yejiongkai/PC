# coding:utf-8

# 导入matplotlib模块并使用Qt5Agg
import matplotlib

matplotlib.use('Qt5Agg')
# 使用 matplotlib中的FigureCanvas (在使用 Qt5 Backends中 FigureCanvas继承自QtWidgets.QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets, QtGui
import matplotlib.pyplot as plt
import numpy as np
import sys


class My_Main_window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        # 父类初始化方法
        super(My_Main_window, self).__init__(parent)

        # 几个QWidgets
        self.figure = Figure()
        self.ax = self.figure.add_axes([0.1, 0.1, 0.8, 0.8])
        self.canvas = FigureCanvas(self.figure)
        self.button_plot = QtWidgets.QPushButton("绘制")

        # 连接事件
        self.button_plot.clicked.connect(self.plot_)

        # 设置布局
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.button_plot)
        self.setLayout(layout)

    # 连接的绘制的方法
    def plot_(self):
        thread = QtCore.QThread(self)
        thread.run = self.Plot
        thread.start()

    def Plot(self):
        fun = lambda k, a, x, t: (np.power(x, 2)) * np.sin(a * t) + 0.5 * k *x
        while 1:
            for t in np.linspace(0, 2*np.pi, 100):
                x = np.linspace(0, 2*np.pi, 100)
                self.ax.clear()
                self.ax.plot(x, fun(20, 5, x, t))
                self.ax.set_ylim(-50, 50)
                self.ax.set_xlim(0, 2*np.pi + 2)
                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw()
                plt.pause(0.01)


# 运行程序
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = My_Main_window()
    main_window.show()
    app.exec()