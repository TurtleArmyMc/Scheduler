from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QCheckBox, QScrollArea, QGridLayout, QVBoxLayout
from PySide2.QtCore import Qt

from chain_handler import Chain_Handler
from helpers import format_date, days_in_month, get_current_month, get_current_year, get_current_day


chain_handler = Chain_Handler()

class Ui_ChainHandlerWidget(QWidget):
    def __init__(self):
        super(Ui_ChainHandlerWidget, self).__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.chain_layout = QGridLayout()
        layout.addLayout(self.chain_layout)

        self.load_previous_month_button = QPushButton("Load previous month's chains.")
        self.load_previous_month_button.clicked.connect(self.load_chain_links_previous_month)
        layout.addWidget(self.load_previous_month_button)

        # Prevent vertical stretching of layout in scroll area.
        layout.addStretch()
        
        self.create_chain_labels()

        self.load_month = get_current_month()
        self.load_year = get_current_year()
        self.load_chain_links_previous_month()
        self.load_chain_links_previous_month()

    def create_chain_labels(self):
        # Creates labels for each chain in the chain_layout.
        row = 0
        for index, chain_name in enumerate(chain_handler.chain_order):
            column = index + 1
            label = QLabel()
            label.setText(chain_name)
            self.chain_layout.addWidget(label, row, column)

        # Prevents horizontal stretching of layout in scroll_area.
        self.chain_layout.setColumnStretch(self.chain_layout.columnCount(), 1)
        
    def load_chains_month(self, year, month):
        # Loads all the chains for a month.
        # Add labels.

        if not (month == get_current_month() and year == get_current_year()):
            start_day = days_in_month(year, month)
        else:
            start_day = get_current_day()
        
        row = self.chain_layout.rowCount()
        for day in range(start_day, 0, -1):
            date_label = QLabel()
            date_label.setText(f"{year}-{month}-{day}")
            self.chain_layout.addWidget(date_label, row, 0)

            for index, chain_name in enumerate(chain_handler.chain_order):
                column = index + 1 
                chain_link = Ui_ChainWidgetCheckbox(chain_name, year, month, day)
                self.chain_layout.addWidget(chain_link, row, column)
            row += 1

    def load_chain_links_previous_month(self):
        self.load_chains_month(self.load_year, self.load_month)
        
        if (self.load_month != 1):
            self.load_month -= 1
        else:
            self.load_month = 12 
            self.load_year -= 1


class Ui_ChainWidgetCheckbox(QCheckBox):
    def __init__(self, chain_name, year=None, month=None, day=None, date=None, state=None):
        self.chain_name = chain_name
        self.year, self.month, self.day = format_date(year, month, day, date)
        
        # checkbox_label = f"{self.year}-{self.month}-{self.day}"
        # super(Ui_ChainWidgetCheckbox, self).__init__(checkbox_label)
        super(Ui_ChainWidgetCheckbox, self).__init__()


        if state is None:
            state = chain_handler.get_chain(chain_name, year, month, day, date)
            
        if state == 1:
            self.setCheckState(Qt.CheckState.Checked)
        else:
            self.setCheckState(Qt.CheckState.Unchecked)

        self.stateChanged.connect(self.on_state_change)

    def on_state_change(self):
        new_value = 0
        if self.checkState() == Qt.CheckState.Checked:
            new_value = 1
        chain_handler.edit_chain(self.chain_name, new_value, self.year, self.month, self.day)
        print(f"Changed chain '{self.chain_name}' on {self.year}-{self.month}-{self.day} to {new_value}")
