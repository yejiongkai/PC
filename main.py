from control import LeftTabWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QDockWidget, QToolBar, QMenu, \
                            QAction, QInputDialog
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QPoint
import sys


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.Control = LeftTabWidget()
        self.Show = self.Control.Show
        self.Wave = self.Control.Wave

        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet('font-size: 20px;font-family: "New Roman"')
        self.setGeometry(400, 400, 1000, 700)
        show_item = QDockWidget(self)
        show_item.setContextMenuPolicy(3)
        show_item.customContextMenuRequested[QPoint].connect(lambda: self.showContextMenu(show_item))
        menu = QMenu(self)
        show_item.contextMenu = menu

        wave_item = QDockWidget(self)
        wave_item.setMinimumSize(400, 400)

        clear = QAction('Origin', self)
        clear.triggered.connect(self.Show_Clear)
        alpha = QAction('alpha', self)
        alpha.triggered.connect(self.Change_Alpha)
        beta = QAction('beta', self)
        beta.triggered.connect(self.Change_Beta)

        show_item.contextMenu.addActions([clear, alpha, beta])
        show_item.setStyleSheet('font-size: 12px;font-family: "宋体";background-color:rgba(255, 255, 255, 230)')
        layout = QHBoxLayout()
        show_item.setWidget(self.Show)
        bar = QToolBar()
        bar.setStyleSheet('background-color:rgba(0, 225, 225, 12)')
        show_item.setTitleBarWidget(bar)
        show_item.setFeatures(
            QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

        wave_item.setStyleSheet('font-size: 12px;font-family: "宋体";background-color:rgba(255, 255, 255, 230)')
        wave_item.setWidget(self.Wave)
        w_bar = QToolBar()
        w_bar.setStyleSheet('background-color:rgba(0, 225, 225, 12)')
        wave_item.setTitleBarWidget(w_bar)
        wave_item.setFeatures(
            QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

        show_item.setFloating(False)
        show_item.setMinimumSize(200, 200)

        wave_item.setFloating(False)
        wave_item.setMinimumSize(200, 200)

        self.setCentralWidget(self.Control)
        self.addDockWidget(Qt.RightDockWidgetArea, show_item)
        self.addDockWidget(Qt.RightDockWidgetArea, wave_item)

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

    def Change_Alpha(self):
        value, ok = QInputDialog.getText(self, '改变alpha', 'cur_alpha', text=str(self.Show.alpha))
        if ok:
            self.Show.alpha = eval(value)
            self.Show.Setting_Save()

    def Change_Beta(self):
        value, ok = QInputDialog.getText(self, '改变beta', 'cur_beta', text=str(self.Show.beta))
        if ok:
            self.Show.beta = eval(value)
            self.Show.Setting_Save()

    def closeEvent(self, a0) -> None:
        self.Control.Drawer.is_route = True
        self.Control.Drawer.is_pause = False
        self.Show.Close = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec_())
