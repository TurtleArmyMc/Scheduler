import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QScrollArea

from ui.qt_chains_handler import Q_Chain_Handler_Widget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.chain_handler_widget = Q_Chain_Handler_Widget(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.chain_handler_widget)
        self.scroll_area.setWidgetResizable(True) # Allows widget to expand and scroll in the scroll area.
        self.setCentralWidget(self.scroll_area)


class App(QApplication):
    def __init__(self):
        super(App, self).__init__()
        self.window = MainWindow()

    def run(self):
        self.window.showMaximized()
        sys.exit(self.exec_())