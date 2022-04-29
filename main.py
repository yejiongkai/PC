from control import LeftTabWidget
from QShow import Show
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QDockWidget, QTextEdit, QToolBar, QMenu, QAction
from PyQt5.QtGui import QPixmap, QFont, QCursor
from PyQt5.QtCore import Qt, QPoint
import sys
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.Control = LeftTabWidget()
        self.Show = self.Control.Show

        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet('font-size: 20px;font-family: "New Roman"')
        items = QDockWidget(self)
        items.setContextMenuPolicy(3)
        items.customContextMenuRequested[QPoint].connect(lambda: self.showContextMenu(items))
        menu = QMenu(self)
        items.contextMenu = menu
        clear = QAction('Origin', self)
        clear.triggered.connect(self.Show_Clear)
        items.contextMenu.addAction(clear)

        items.setStyleSheet('font-size: 12px;font-family: "宋体";background-color:rgba(255, 255, 255, 230)')
        layout = QHBoxLayout()
        items.setWidget(self.Show)
        bar = QToolBar()
        items.setTitleBarWidget(bar)
        items.setFeatures(
            QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

        items.setFloating(False)
        self.setCentralWidget(self.Control)
        self.addDockWidget(Qt.RightDockWidgetArea, items)

        self.setLayout(layout)
        self.setWindowTitle('主界面')

    def showContextMenu(self, cls):
        '''''
        右键点击显示控件右键菜单
        '''
        # 菜单定位
        cls.contextMenu.exec_(QCursor.pos())

    def Show_Clear(self):
        self.Show.Clear()

    def closeEvent(self, a0) -> None:
        self.Control.Drawer.is_route = True
        self.Control.Drawer.is_pause = False
        self.Show.Close = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec_())
