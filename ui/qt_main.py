import sys
from PySide2 import QtWidgets
from PySide2.QtGui import QIcon

from ui.qt_chains_handler import Q_Chain_Handler_Widget


class Main_Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Main_Window, self).__init__()
        self.setWindowTitle("Scheduler")
        self.setWindowIcon(QIcon("resources/Clock.ico"))

        self.chain_handler_widget = Q_Chain_Handler_Widget(self)
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidget(self.chain_handler_widget)
        self.scroll_area.setWidgetResizable(True) # Allows widget to expand and scroll in the scroll area.
        self.setCentralWidget(self.scroll_area)


class System_Tray_Icon(QtWidgets.QSystemTrayIcon):
    def __init__(self, app, parent):
        super(System_Tray_Icon, self).__init__()
        
        self.app = app
        self.parent = parent # Dummy widget to prevent garbage collection from destroying context menu.
        
        self.init_icon()
        self.init_context_menu()
        self.activated.connect(self.on_activated)

        self.main_window = None
        self.open_main_window()

    def init_icon(self):
        self.setIcon(QIcon("resources/clock.ico"))
    
    def init_context_menu(self):
        self.context_menu = QtWidgets.QMenu(parent=self.parent) # Requires parent to not be destroyed right away.

        show_main_window_action = QtWidgets.QAction("Main window", parent=self)
        show_main_window_action.triggered.connect(self.open_main_window)
        self.context_menu.addAction(show_main_window_action)

        quit_app_action = QtWidgets.QAction("Quit", parent=self)
        quit_app_action.triggered.connect(self.quit_app)
        self.context_menu.addAction(quit_app_action)

        self.setContextMenu(self.context_menu)

    def load_main_window(self):
        self.main_window = Main_Window(parent=self)
    
    def open_main_window(self):
        if self.main_window is None:
            self.load_main_window()
        self.main_window.showMaximized()
        self.main_window.activateWindow()

    def quit_app(self):
        self.app.quit()

    def on_activated(self, reason):
        if reason == self.ActivationReason.Trigger or reason == self.ActivationReason.MiddleClick: # Exlude right click.
            self.open_main_window()


class App(QtWidgets.QApplication):
    def run(self, use_system_tray=False):
        if use_system_tray:
            self.setQuitOnLastWindowClosed(False)
            
            w = QtWidgets.QWidget()
            self.system_tray_icon = System_Tray_Icon(self, w)

            self.system_tray_icon.show()
        else:
            self.main_window = Main_Window()
            self.main_window.showMaximized()
        sys.exit(self.exec_())