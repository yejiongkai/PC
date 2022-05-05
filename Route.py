import os.path
import sys
import time
import numpy as np

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize, QThread, QTimer
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QFont, QCursor, QPalette, QPainterPathStroker
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QFileDialog


class Drawer(QDialog):
    Order = pyqtSignal(str)

    def __init__(self, parent=None):
        super(QWidget, self).__init__()
        self.setMouseTracking(True)
        self.font = QFont('New Roman', 15)
        self.setFont(self.font)
        self.time = QTimer(self)
        self.time.timeout.connect(self.Straight_Line)
        self.A_k = []
        self.value_range = [10, 20, 30, 40, 50, 60, 70, 80]
        self.press = False
        self.press_pos = None
        self.press_begin = None
        self.press_Straight = False
        self.is_route = False  # 是否进入路径行驶模式
        self.is_pause = False
        self.thread = QThread(self)
        self.thread.run = self.Start
        # self.Order.connect(self.Send)  # 测试
        self.A_k_Init()
        self.UI_Init()

        self.stroker = QPainterPathStroker()
        self.stroker.setCapStyle(Qt.RoundCap)
        self.stroker.setJoinStyle(Qt.RoundJoin)
        self.stroker.setDashPattern(Qt.DashLine)
        self.stroker.setWidth(3)

    def A_k_Init(self):
        if os.path.exists('./A_k.txt'):
            with open('./A_k.txt', 'r+') as f:
                self.A_k = [eval(i[:-1]) for i in f.readlines()]
        else:
            with open('./A_k.txt', 'w') as f:
                self.A_k = [(3, 0), (2, 5), (2, 7), (3, 5), (3, 7), (3, 9), (4, 7), (4, 9), (5, 7)]
                f.writelines([str(i)+'\n' for i in self.A_k])

    def UI_Init(self):

        # palette = QtGui.QPalette()
        # # palette.setBrush(w.backgroundRole(), QtGui.QBrush(image)) #背景图片
        # palette.setColor(self.backgroundRole(), QColor(255, 255, 255))  # 背景颜色
        # self.setPalette(palette)
        # self.setAutoFillBackground(True)

        self.setGeometry(400, 400, 600, 400)

        self.cur_position_label = QLabel('Coordinates:', self)

        self.start_route = QPushButton('开始', self)
        self.start_route.clicked.connect(self.Thread_Start)

        self.end_route = QPushButton('结束', self)
        self.end_route.clicked.connect(self.End)

        self.save = QPushButton('保存', self)
        self.save.clicked.connect(self.Save)

        self.load = QPushButton('加载', self)
        self.load.clicked.connect(self.Load)

        self.plan_path = QPainterPath()
        self.actual_path = QPainterPath()

        h = QHBoxLayout()
        h.addWidget(self.cur_position_label, 5)
        h.addWidget(self.save, 1)
        h.addWidget(self.load, 1)
        h.addWidget(self.start_route, 1)
        h.addWidget(self.end_route, 1)

        v = QVBoxLayout()
        v.addLayout(h, 1)
        v.addStretch(9)
        self.setLayout(v)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(True)

        painter.setPen(QPen(QColor(0, 0, 0, 80), 5, Qt.SolidLine))
        painter.drawPath(self.plan_path)

        if self.is_route:
            painter.setPen(QPen(QColor(255, 0, 0, 255), 7, Qt.SolidLine))
            painter.drawPath(self.actual_path)

    def mousePressEvent(self, event):
        if not self.is_route:
            self.press = True
            self.press_pos = event.pos()
            self.press_begin = event.pos()
            self.plan_path.clear()
            self.plan_path.moveTo(event.pos())
            self.update()

    def Straight_Line(self):
        if self.press_pos == self.mapFromGlobal(QCursor.pos()) and self.press_Straight is False and self.press:
            self.press_Straight = True
            self.plan_path.clear()
            self.plan_path.moveTo(self.press_begin)
            self.plan_path.lineTo(self.press_pos)
            self.update()

    def mouseMoveEvent(self, event):
        if self.press:
            self.press_pos = event.pos()
            if not self.is_route:
                if self.press_Straight:
                    self.plan_path.clear()
                    self.plan_path.moveTo(self.press_begin)
                    self.plan_path.lineTo(self.press_pos)
                    self.update()
                else:
                    self.plan_path.lineTo(event.pos())
                    self.update()

                    self.time.start(1000)

        self.cur_position_label.setText('Coordinates: {}, {}'.format(event.pos().x(), event.pos().y()))

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self.is_route:
            self.press = False
            self.press_Straight = False
            self.press_begin = None
            self.press_pos = None
            self.plan_path = self.stroker.createStroke(self.plan_path)
            self.update()

    def Save(self):
        import pickle
        file, s = QFileDialog.getSaveFileName(self, 'Save Route', '.', '*.route')
        if file and not self.plan_path.isEmpty():
            route = []
            for i in range(self.plan_path.elementCount()):
                element = self.plan_path.elementAt(i)
                route.append((element.x, element.y))
            with open(file, 'wb') as f:
                pickle.dump(route, f)

    def Load(self):
        if not self.is_route:
            import pickle
            file, s = QFileDialog.getOpenFileName(self, 'Load Route', '.', '*.route')
            if file:
                with open(file, 'rb') as f:
                    route = pickle.load(f)
                self.press = False
                self.plan_path.clear()
                self.plan_path.moveTo(*route[0])
                for i in range(1, len(route)):
                    self.plan_path.lineTo(*route[i])
                self.update()

    def MeanPath(self, path, sep):
        cur_x, cur_y, result = path[0][0], path[0][1], [path[0]]
        for x, y in path[1:]:
            x_d, y_d = abs(cur_x - x), abs(cur_y - y)
            if x_d > sep or y_d > sep:
                if x_d > 2 * sep or y_d > 2 * sep:
                    max_sep = max(int(abs(x_d / sep)), int(abs(y_d / sep)))
                    for i in range(1, max_sep):
                        result.append((cur_x + i * (x - cur_x) // max_sep, cur_y + i * (y - cur_y) // max_sep))
                result.append((x, y))
                cur_x, cur_y = x, y
        return result

    def Start(self, speed=0.1):
        self.A_k_Init()
        path = [(self.plan_path.elementAt(i).x, self.plan_path.elementAt(i).y)
                for i in range(self.plan_path.elementCount())]
        path = self.MeanPath(path, 60)
        actions = np.array(path)
        actions = actions[1:] - actions[:-1]
        x, y = actions[:, 0].copy(), actions[:, 1].copy()
        actions = y / x
        actions[actions == np.inf] = 99999
        actions[actions == -np.inf] = -99999
        actions = np.arctan(actions)
        actions[np.logical_and(actions > 0, y < 0)] = np.pi + actions[np.logical_and(actions > 0, y < 0)]
        actions[np.logical_and(actions < 0, y > 0)] = np.pi + actions[np.logical_and(actions < 0, y > 0)]
        actions[np.logical_and(actions < 0, y < 0)] = 2 * np.pi + actions[np.logical_and(actions < 0, y < 0)]
        actions = actions * 180 / np.pi
        actions = actions[:-1] - actions[1:]
        actions[actions >= 180] = actions[actions >= 180] - 360
        actions[actions <= -180] = 360 + actions[actions <= -180]
        # actions[np.logical_or(np.logical_or(actions == np.inf, actions == -np.inf), np.isnan(actions))] = 0
        print(actions)
        '_________________________________________________________________________________'
        j = 0
        lis = [[] for i in range(len(path))]
        a = np.zeros(shape=(len(path),))
        k = np.zeros(shape=(len(path),))
        lis[0] = [a[0], k[0]]
        lis[len(path) - 1] = [a[len(path) - 1], k[len(path) - 1]]
        while j < len(path) - 2:
            # 前进
            if -self.value_range[0] <= actions[j] <= self.value_range[0]:
                a[j + 1] = self.A_k[0][0]
                k[j + 1] = self.A_k[0][1]
            # 第一档
            elif self.value_range[0] < actions[j] <= self.value_range[1] or\
                    -self.value_range[1] < actions[j] <= -self.value_range[0]:
                a[j + 1] = self.A_k[1][0]
                k[j + 1] = self.A_k[1][1] * (abs(actions[j]) / actions[j])
            elif self.value_range[1] < actions[j] <= self.value_range[2] or\
                    -self.value_range[2] < actions[j] <= self.value_range[1]:
                a[j + 1] = self.A_k[2][0]
                k[j + 1] = self.A_k[2][1] * (abs(actions[j]) / actions[j])
            elif self.value_range[2] < actions[j] <= self.value_range[3] or\
                    -self.value_range[3] < actions[j] <= -self.value_range[2]:
                a[j + 1] = self.A_k[3][0]
                k[j + 1] = self.A_k[3][1] * (abs(actions[j]) / actions[j])
            elif self.value_range[3] < actions[j] <= self.value_range[4] or\
                    -self.value_range[4] < actions[j] <= -self.value_range[3]:
                a[j + 1] = self.A_k[4][0]
                k[j + 1] = self.A_k[4][1] * (abs(actions[j]) / actions[j])
            elif self.value_range[4] < actions[j] <= self.value_range[5] or\
                    -self.value_range[5] < actions[j] <= -self.value_range[4]:
                a[j + 1] = self.A_k[5][0]
                k[j + 1] = self.A_k[5][1] * (abs(actions[j]) / actions[j])
            elif self.value_range[5] < actions[j] <= self.value_range[6] or\
                    -self.value_range[6] < actions[j] <= -self.value_range[5]:
                a[j + 1] = self.A_k[6][0]
                k[j + 1] = self.A_k[6][1] * (abs(actions[j]) / actions[j])
            elif self.value_range[6] < actions[j] <= self.value_range[7] or -self.value_range[7] < actions[j] <= -self.value_range[6]:
                a[j + 1] = self.A_k[7][0]
                k[j + 1] = self.A_k[7][1] * (abs(actions[j]) / actions[j])
            elif self.value_range[7] < actions[j] or actions[j] < -self.value_range[7]:
                a[j + 1] = self.A_k[8][0]
                k[j + 1] = self.A_k[8][1] * (abs(actions[j]) / actions[j])
            lis[j + 1] = [a[j + 1], k[j + 1]]
            j += 1
        print(lis)
        '_________________________________________________________________________________'
        self.Order.emit(str((1 << 1, lis)) + '\n')
        actions = np.insert(actions, 0, 0)
        self.actual_path.moveTo(*path[0])
        i = 1
        while i < len(path) and self.is_route:
            if not self.is_pause:
                self.actual_path.lineTo(*path[i])
                # self.Order.emit(actions[i - 1])
                self.update()
                i += 1
            time.sleep(0.1)

        # self.End()

    def Thread_Start(self):
        if self.plan_path.elementCount():
            if self.is_route:
                if self.is_pause:
                    self.start_route.setText('暂停')
                    self.Order.emit(str((1 << 1, True))+'\n')
                else:
                    self.start_route.setText('启动')
                    self.Order.emit(str((1 << 1, False))+'\n')
                self.is_pause ^= 1
            else:
                self.is_route = True
                self.is_pause = False
                self.start_route.setText('暂停')
                self.thread.start()

    def End(self):
        self.is_route = False
        self.Order.emit(str((1 << 1, False))+'\n')
        self.actual_path.clear()
        self.update()
        self.start_route.setText('开始')

    def Send(self, value):
        print(value)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.is_route = True
        self.is_pause = False
        self.thread.wait()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Drawer()
    w.show()
    sys.exit(app.exec_())
