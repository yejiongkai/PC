# coding:utf-8

import serial
import serial.tools.list_ports
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QFont
import sys
import time


class Serial(QtWidgets.QDialog):
    def __init__(self, parent=None):
        # 父类初始化方法
        super(Serial, self).__init__(parent)
        self.font = QFont('New Roman', 15)
        self.setFont(self.font)
        self.COMS = []
        self.Choose_COM = None
        self.text = []
        self.UI_Init()
        self.COMS_Refresh()
        self.recvable = True
        self.sendable = True
        self.thread_send = QtCore.QThread(self)
        self.thread_send.run = self.Uart_Send
        self.thread_send.start()
        self.thread_recv = QtCore.QThread(self)
        self.thread_recv.run = self.Uart_Recv
        self.thread_recv.start()

    def Uart_Init(self):
        if self.Choose_COM and self.Choose_COM.is_open:
            self.Choose_COM.close()
            self.Choose_COM = None
            self.Connect.setText('连接')
            self.combobox.setEnabled(True)
            self.COMS_Refresh()
        else:
            try:
                self.Choose_COM = serial.Serial(self.combobox.currentText().split()[0], 115200, 8, 'N', 1)
            except Exception as e:
                QtWidgets.QMessageBox.information(self, '警告', str(e))
                return

            if self.Choose_COM.is_open:
                # QtWidgets.QMessageBox.information(self, '提示', '连接成功')
                self.Connect.setText('断开')
                self.combobox.setEnabled(False)
            else:
                QtWidgets.QMessageBox.information(self, '提示', '连接失败')
                self.Choose_COM = None

    def UI_Init(self):
        self.setGeometry(400, 400, 400, 400)
        # 几个QWidgets
        self.forward = QtWidgets.QPushButton('↑', self)
        self.forward.setFixedSize(100, 100)
        self.left = QtWidgets.QPushButton('←', self)
        self.left.setFixedSize(100, 100)
        self.right = QtWidgets.QPushButton('→', self)
        self.right.setFixedSize(100, 100)

        self.combobox = QtWidgets.QComboBox(self)
        self.combobox.setFixedHeight(30)
        self.combobox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.combobox.setEditable(False)

        self.TextEdit = QtWidgets.QTextEdit(self)
        self.TextEdit.setReadOnly(True)

        self.Connect = QtWidgets.QPushButton('连接', self)
        self.Connect.setGeometry(90, 300, 50, 20)
        self.Connect.setFixedHeight(30)
        self.Connect.clicked.connect(self.Uart_Init)

        # 设置布局
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(100, 0, 100, 0)
        layout.addStretch(1)
        h1 = QtWidgets.QHBoxLayout()
        h2 = QtWidgets.QHBoxLayout()
        h1.addWidget(self.left)
        h1.addWidget(self.forward)
        h1.addWidget(self.right)
        h2.addWidget(self.Connect, 2)
        h2.addWidget(self.combobox, 8)
        layout.addWidget(self.TextEdit, 4)
        layout.addLayout(h1, 1)
        layout.addLayout(h2, 1)
        layout.addStretch(1)
        self.setLayout(layout)

        self.forward.clicked.connect(self.Forward)
        self.left.clicked.connect(self.Left)
        self.right.clicked.connect(self.Right)

        self.clearFocus()

    def COMS_Refresh(self):
        port_list = list(serial.tools.list_ports.comports())
        self.combobox.clear()
        for i in range(len(port_list)):
            self.combobox.addItem(str(port_list[i]))

    def Forward(self):
        if 'red' not in self.text:
            self.text.append(str((1 << 0, (0.5, 0))).encode('utf-8'))
        else:
            self.text.remove('red')
        # self.Uart_Send()

    def Left(self):
        if 'blue' not in self.text:
            self.text.append('blue')
        else:
            self.text.remove('blue')
        # self.Uart_Send()

    def Right(self):
        if 'green' not in self.text:
            self.text.append('green')
        else:
            self.text.remove('green')
        # self.Uart_Send()

    def Uart_Send(self):
        while self.sendable:
            if self.Choose_COM:
                if self.Choose_COM.writable() and self.text:
                    t = ' '.join(self.text).encode('utf-8')
                    self.Choose_COM.write(t)  # 因为发送速度太快, 单片机端可能收到多次
            time.sleep(0.01)

    def Uart_Recv(self):
        while self.recvable:
            if self.Choose_COM and self.Choose_COM.readable():
                t = self.Choose_COM.readline()[:-1].decode('utf-8')
                self.TextEdit.append(t)
            time.sleep(0.01)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.sendable = False
        self.recvable = False
        self.thread_send.wait()
        self.thread_recv.wait()


# 运行程序
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = Serial()
    main_window.show()
    sys.exit(app.exec_())
