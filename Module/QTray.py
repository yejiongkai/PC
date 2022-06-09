from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor


class TrayModel(QSystemTrayIcon):
    def __init__(self, Window):
        super(TrayModel, self).__init__()
        self.window = Window
        self.Init_UI()

    def Init_UI(self):
        with open('./parameter/menu.qss', 'r') as f:  # 导入QListWidget的qss样式
            self.menu_style = f.read()

        self.menu = QMenu()

        self.shadow = QGraphicsDropShadowEffect(self.menu)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor('#444444'))  #
        self.shadow.setBlurRadius(10)

        self.show_action = QAction('打开主面板', self, triggered=self.Show_Window)
        self.quit_action = QAction('退出', self, triggered=self.Quit_Window)
        self.reset_action = QAction('重启', self, triggered=self.Reset_Window)

        self.menu.addActions([self.show_action, self.reset_action, self.quit_action])

        # a = QMenu('hi', self.menu)
        # a.addActions([QAction('h', self.menu), QAction('u', self.menu)])
        #
        # self.menu.addMenu(a)

        self.SetMenuStyle(self.menu)

        self.setContextMenu(self.menu)

        self.setIcon(QIcon('./win.ico'))
        self.icon = self.MessageIcon()

        self.activated.connect(self.app_click)
        self.show()

    def SetMenuStyle(self, menu):
        menu.setStyleSheet(self.menu_style)
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        menu.setGraphicsEffect(self.shadow)
        menu_list = menu.actions()
        for action in menu_list:
            if action.menu():
                self.SetMenuStyle(action.menu())

    def Show_Window(self):
        self.window.showNormal()
        self.window.activateWindow()

    def Quit_Window(self):
        self.window.hide_normal = False
        self.window.close()

    def Reset_Window(self):
        self.window.ResetEvent()

    def app_click(self, reason):
        if reason == 2 or reason == 3:  # double_click or click
            self.Show_Window()
            # self.showMessage("hi", 'hellow')
