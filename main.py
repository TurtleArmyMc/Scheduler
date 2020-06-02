# from chain_handler import Chain_Handler
from datetime import date as datetime_date
from pprint import pprint

import sys
from PySide2.QtWidgets import QApplication

from QtMainWindow import MainWindow


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())

# 5/26 left for bread but not exercise 
# 5/31 7 lakes
# 6/1 Woke up 11am
# 6/1 Went to sleep 3:30am
# 6/2 Woke up 10:30