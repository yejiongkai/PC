from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class TrayModel(QSystemTrayIcon):
    def __init__(self, Window):
        super(TrayModel, self).__init__()
        self.window = Window
        self.Init_UI()

    def Init_UI(self):
        self.menu = QMenu()

        self.show_action = QAction('打开主面板', self, triggered=self.Show_Window)
        self.quit_action = QAction('退出', self, triggered=self.Quit_Window)
        self.reset_action = QAction('重启', self, triggered=self.Reset_Window)

        self.menu.addActions([self.show_action, self.reset_action, self.quit_action])

        self.setContextMenu(self.menu)

        self.setIcon(QIcon('./win.ico'))
        self.icon = self.MessageIcon()

        self.activated.connect(self.app_click)
        self.show()

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
