import sys
from PySide2.QtWidgets import QApplication

from QtMainWindow import MainWindow


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())