# coding:utf-8

import serial
import serial.tools.list_ports
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize, QThread, QTimer
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QFont
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtNetwork import QTcpSocket
import sys
import time
import numpy as np


class Track(QtWidgets.QDialog):
    position = pyqtSignal(tuple)
    vision = pyqtSignal(str)

    def __init__(self, parent=None):
        # 父类初始化方法
        super(Track, self).__init__(parent)
        self.font = QFont('New Roman', 15)
        self.X = 0
        self.Y = 0
        self.Width = None
        self.Height = None
        self.setFont(self.font)
        self.position.connect(self.Position_Show)
        self.UI_Init()

    def UI_Init(self):
        self.setGeometry(400, 400, 400, 400)
        # 几个QWidgets
        self.track_open = QPushButton('开启', self)
        self.track_open.setFixedHeight(30)
        self.track_open.clicked.connect(self.Vision_Open)
        self.track_close = QPushButton('关闭', self)
        self.track_close.setFixedHeight(30)
        self.track_close.clicked.connect(self.Vision_Close)

        self.Screen = QLabel(self)
        self.Screen.setFixedSize(320, 240)
        self.Screen.setStyleSheet('border-width: 6px;border-style: solid;\
                border-color: rgb(0, 0, 0);background-color: rgb(255,255,255, 120);')

        # 设置布局
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(100, 0, 100, 0)
        layout.addStretch(1)
        h1 = QtWidgets.QHBoxLayout()
        h2 = QtWidgets.QHBoxLayout()
        h1.addWidget(self.track_open)
        h1.addWidget(self.track_close)
        layout.addWidget(self.Screen, 5)
        layout.addLayout(h1, 1)
        layout.addStretch(1)
        self.setLayout(layout)

        self.clearFocus()

    def Position_Show(self, position):
        x, y, width, height = position
        point = self.Screen.mapToParent(QPoint(x, y))
        self.X = point.x()
        self.Y = point.y()
        self.Width = width
        self.Height = height
        self.update()

    def paintEvent(self, event):
        if self.X and self.Y and self.Width and self.Height:
            painter = QPainter(self)
            painter.setRenderHint(True)
            painter.setPen(QPen(QColor(255, 0, 0), 3, Qt.SolidLine))
            painter.drawRect(self.X, self.Y, self.Width, self.Height)

    def S(self):
        x = np.random.randint(0, 220)
        y = np.random.randint(0, 140)
        width = np.random.randint(10, 100)
        height = np.random.randint(10, 100)
        self.Position_Show(x, y, width, height)

    def Vision_Open(self):
        self.vision.emit(str((1 << 2, True))+'\n')

    def Vision_Close(self):
        self.vision.emit(str((1 << 2, False))+'\n')

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        pass


# 运行程序
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = Track()
    main_window.show()
    sys.exit(app.exec_())
