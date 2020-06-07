from PySide2.QtWidgets import QMainWindow, QScrollArea

from QtChainsWidget import Q_Chain_Handler_Widget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.chain_handler_widget = Q_Chain_Handler_Widget(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.chain_handler_widget)
        self.scroll_area.setWidgetResizable(True) # Allows widget to expand and scroll in the scroll area.
        self.setCentralWidget(self.scroll_area)