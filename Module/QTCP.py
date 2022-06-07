# coding:utf-8

import serial
import serial.tools.list_ports
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize, QThread, QTimer
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QFont, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,\
    QInputDialog, QMessageBox, QMenu, QAction, QSlider
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtNetwork import QTcpSocket
import sys
import time


class MyPushButton(QPushButton):
    def __init__(self, name, parent):
        super(MyPushButton, self).__init__(parent)
        self.setFont(QFont('宋体', 12))
        self.name = name
        self.A = 2
        self.k = 0 if self.name == '↑' else 5 if self.name == '←' else -5 if self.name == '→' else None
        if self.k is not None:
            self.setText('{}({},{})'.format(self.name, self.A, self.k))
        else:
            self.setText(self.name)
        self.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.sizePolicy.setWidthForHeight(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSizePolicy(self.sizePolicy)
        # self.setMaximumSize(100, 100)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.buttons() == QtCore.Qt.RightButton:
            text, ok = QInputDialog.getText(self, '修改A和k', '请输入A和k：', text=self.text()[1:])
            if ok:
                try:
                    A, k = eval(text)
                except Exception as e:
                    QMessageBox.information(self, '提示', str(e))
                    return
                self.A, self.k = A, k
                self.setText('{}({},{})'.format(self.name, self.A, self.k))
            return

        if e.buttons() == QtCore.Qt.LeftButton:
            self.clicked.emit()

    def Update(self):
        self.setText('{}({},{})'.format(self.name, self.A, self.k))


class Socket(QtWidgets.QDialog):
    Socket_Connect = pyqtSignal()
    Socket_Disconnect = pyqtSignal()
    Socket_Send = pyqtSignal(str)

    def __init__(self, parent=None):
        # 父类初始化方法
        super(Socket, self).__init__(parent)
        self.font = QFont('New Roman', 15)
        self.setFont(self.font)
        self.Socket = QTcpSocket(self)
        self.Socket.disconnected.connect(self.Server_Disconnect)
        self.A, self.k, self.c = 0, 0, 0
        self.UI_Init()
        self.recvable = True
        self.sendable = True

    def UI_Init(self):
        self.setGeometry(400, 400, 400, 400)
        # 几个QWidgets
        self.forward = MyPushButton('↑', self)
        self.left = MyPushButton('←', self)
        self.right = MyPushButton('→', self)
        self.stop = MyPushButton('⏹', self)
        # self.up_left = QPushButton('Up_L', self)
        # self.down_left = QPushButton('Down_L', self)
        # self.up_right = QPushButton('Up_R', self)
        # self.down_right = QPushButton('Down_R', self)
        self.bionic_on = MyPushButton('B_On', self)
        self.bionic_off = MyPushButton('B_Off', self)

        self.splider = QSlider(Qt.Vertical, self)
        self.splider.setPageStep(1)
        self.splider.setRange(6, 12)
        self.splider.setValue(12)
        self.splider.setTickInterval(1)
        self.splider.setTickPosition(QSlider.TicksRight)
        self.splider.setTickInterval(1)
        self.splider.valueChanged.connect(self.Splider_Change)

        self.combobox = QtWidgets.QComboBox(self)
        self.combobox.setFixedHeight(30)
        self.combobox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.combobox.setEditable(True)
        self.combobox.lineEdit().setFont(self.font)
        self.combobox.lineEdit().setAlignment(Qt.AlignCenter)
        self.combobox.lineEdit().setClearButtonEnabled(True)
        self.combotext = ['192.168.43.64:3411', '127.0.0.1:3411']
        self.combobox.addItems(self.combotext)

        self.TextEdit = QtWidgets.QTextEdit(self)
        self.TextEdit.setReadOnly(True)
        self.TextEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TextEdit.customContextMenuRequested[QPoint].connect(self.showContextMenu)
        menu = QMenu(self)
        self.TextEdit.contextMenu = menu
        clear = QAction('Clear', self)
        clear.triggered.connect(self.Line_Clear)
        self.TextEdit.contextMenu.addAction(clear)
        self.TextEdit.setTextInteractionFlags(Qt.NoTextInteraction)
        # self.TextEdit.setFocusPolicy(Qt.NoFocus)

        self.Connect = QtWidgets.QPushButton('连接', self)
        self.Connect.setFixedHeight(30)
        self.Connect.clicked.connect(self.Socket_Init)
        self.Connect.setFocusPolicy(Qt.NoFocus)

        seq = 4
        # 设置布局
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addStretch(seq//4)
        h1 = QtWidgets.QHBoxLayout()
        h2 = QtWidgets.QHBoxLayout()
        h1.addWidget(self.left, seq)
        h1.addWidget(self.forward, seq)
        h1.addWidget(self.right, seq)
        h1.addWidget(self.stop, seq)
        b_layout = QVBoxLayout()
        b_layout.addWidget(self.bionic_on)
        b_layout.addWidget(self.bionic_off)
        h1.addLayout(b_layout, seq)
        # u_d_l = QVBoxLayout()
        # u_d_l.addWidget(self.up_left)
        # u_d_l.addWidget(self.down_left)
        # h1.addLayout(u_d_l)
        # u_d_r = QVBoxLayout()
        # u_d_r.addWidget(self.up_right)
        # u_d_r.addWidget(self.down_right)
        # h1.addLayout(u_d_r)
        h1.addWidget(self.splider, seq)
        h2.addWidget(self.Connect, seq)
        h2.addWidget(self.combobox, 8*seq)
        layout.addWidget(self.TextEdit, 5*seq)
        layout.addLayout(h1, seq)
        layout.addLayout(h2, seq)
        layout.addStretch(seq//4)
        self.setLayout(layout)

        self.forward.clicked.connect(self.Forward)
        self.left.clicked.connect(self.Left)
        self.right.clicked.connect(self.Right)
        self.stop.clicked.connect(self.Stop)
        self.bionic_on.clicked.connect(self.Bionic_On)
        self.bionic_off.clicked.connect(self.Bionic_Off)
        # self.up_left.clicked.connect(lambda: self.Up(0))
        # self.down_left.clicked.connect(lambda: self.Down(0))
        # self.up_right.clicked.connect(lambda: self.Up(1))
        # self.down_right.clicked.connect(lambda: self.Down(1))

        self.clearFocus()

    def showContextMenu(self, point):
        '''''
        右键点击显示控件右键菜单
        '''
        # 菜单定位
        self.TextEdit.contextMenu.exec_(QCursor.pos())

    def Socket_Init(self):
        if self.Socket.state() == 3:
            self.Socket.disconnectFromHost()
            self.Socket.waitForDisconnected(3000)
            self.Socket.close()
            self.Connect.setText('连接')
            self.combobox.setEnabled(True)
        elif self.Socket.state() == 0:
            try:
                host, port = self.combobox.currentText().split(':')
                self.Socket.connectToHost(host, int(port))
            except Exception as e:
                QtWidgets.QMessageBox.information(self, '警告', str(e))
                return

            if self.Socket.waitForConnected(3000):
                self.Socket_Connect.emit()
                QtWidgets.QMessageBox.information(self, '提示', '连接成功')
                self.Connect.setText('断开')
                self.combobox.setEnabled(False)
            else:
                QtWidgets.QMessageBox.information(self, '提示', '连接失败')

    def Server_Disconnect(self):
        self.Socket.disconnectFromHost()
        self.Socket.close()
        self.Socket_Disconnect.emit()
        self.Connect.setText('连接')
        self.combobox.setEnabled(True)
        QtWidgets.QMessageBox.information(self, '提示', '服务器断开')

    def Forward(self):
        self.Socket_Send.emit((str((1 << 0, (self.forward.A, self.forward.k, self.splider.value()))) + '\n'))
        # if self.Socket.state() == 3:
        #     self.Socket.write((str((1 << 0, (self.forward.A, self.forward.k))) + '\n').encode('utf-8'))

    def Left(self):
        self.Socket_Send.emit((str((1 << 0, (self.left.A, self.left.k, self.splider.value()))) + '\n'))
        # if self.Socket.state() == 3:
        #     self.Socket.write((str((1 << 0, (self.left.A, self.left.k))) + '\n').encode('utf-8'))

    def Right(self):
        self.Socket_Send.emit((str((1 << 0, (self.right.A, self.right.k, self.splider.value()))) + '\n'))
        # if self.Socket.state() == 3:
        #     self.Socket.write((str((1 << 0, (self.right.A, self.right.k))) + '\n').encode('utf-8'))

    def Stop(self):
        self.Socket_Send.emit((str((1 << 0, (0, 0, self.splider.value()))) + '\n'))
        # if self.Socket.state() == 3:
        #     self.Socket.write((str((1 << 0, (0, 0))) + '\n').encode('utf-8'))

    def Up(self, n):
        self.Socket_Send.emit((str((1 << 0, 'Up_{}'.format(n))) + '\n'))
        # if self.Socket.state() == 3:
        #     self.Socket.write((str((1 << 0, 'Up_{}'.format(n))) + '\n').encode('utf-8'))

    def Down(self, n):
        self.Socket_Send.emit((str((1 << 0, 'Down_{}'.format(n))) + '\n'))
        # if self.Socket.state() == 3:
        #     self.Socket.write((str((1 << 0, 'Down_{}'.format(n))) + '\n').encode('utf-8'))

    def Splider_Change(self):
        self.Socket_Send.emit((str((1 << 0, (self.A, self.k, self.splider.value()))) + '\n'))

    def Bionic_On(self):
        self.Socket_Send.emit((str((1 << 8, True)) + '\n'))

    def Bionic_Off(self):
        self.Socket_Send.emit((str((1 << 8, False)) + '\n'))


    def Line_Clear(self):
        self.TextEdit.clear()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        pass

    def keyPressEvent(self, event) -> None:
        if str(event.key()) == '16777220':
            self.Socket_Init()

    def keyReleaseEvent(self, event):
        # ctrl + 单键 优先级高
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_W:
                if self.forward.A < 5:
                    self.forward.A += 1
                if self.left.A < 5:
                    self.left.A += 1
                if self.right.A < 5:
                    self.right.A += 1
            elif event.key() == Qt.Key_S:
                if self.forward.A > 0:
                    self.forward.A -= 1
                if self.left.A > 0:
                    self.left.A -= 1
                if self.right.A > 0:
                    self.right.A -= 1
            elif event.key() == Qt.Key_A:
                if self.left.k < 9:
                    self.left.k += 1
                else:
                    self.left.k = 5
            elif event.key() == Qt.Key_D:
                if self.right.k > -9:
                    self.right.k -= 1
                else:
                    self.right.k = -5
            self.forward.Update()
            self.left.Update()
            self.right.Update()

        else:
            if str(event.key()) == '87':
                self.Forward()
            elif str(event.key()) == '65' or str(event.key()) == '16777234':
                self.Left()
            elif str(event.key()) == '68' or str(event.key()) == '16777236':
                self.Right()
            elif str(event.key()) == '32':
                self.Stop()
            elif str(event.key()) == '16777235':
                value = self.splider.value()
                if value < self.splider.maximum():
                    self.splider.setValue(value + 1)
            elif str(event.key()) == '16777237':
                if self.Socket.state() == 0:
                    self.combobox.showPopup()
                else:
                    value = self.splider.value()
                    if value > self.splider.minimum():
                        self.splider.setValue(value - 1)


# 运行程序
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = Socket()
    main_window.show()
    sys.exit(app.exec_())
