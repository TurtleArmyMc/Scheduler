from PySide2.QtWidgets import QLabel, QWidget, QCheckBox, QHBoxLayout, QVBoxLayout
from PySide2.QtCore import Qt

from chain_handler import Chain_Handler
from helpers import format_date, days_in_month


chain_handler = Chain_Handler()

class Ui_ChainHandlerWidget(QWidget):
    def __init__(self):
        super(Ui_ChainHandlerWidget, self).__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        
        self.date_labels = QVBoxLayout()
        self.layout.addLayout(self.date_labels)
        
        self.chains = []
        self.create_all_chains()
        self.load_chain_links_month("2020", "6")

    def create_new_chain(self, chain_name):
        new_chain = Ui_ChainWidget(chain_name)
        self.chains.append(new_chain)
        self.layout.addWidget(new_chain)

    def create_all_chains(self):
        for chain_name in chain_handler.chain_order:
            self.create_new_chain(chain_name)

    def load_chain_links_month(self, year, month):
        # Loads all the chains for a month.
        # Add labels.
        for day in range(days_in_month(year, month), 0, -1):
            date_label = QLabel()
            date_label.setText(f"{year}-{month}-{day}")
            self.date_labels.addWidget(date_label)

        for chain in self.chains:
            chain.load_chain_links_month(year, month)


class Ui_ChainWidget(QWidget):
    def __init__(self, chain_name):
        super(Ui_ChainWidget, self).__init__()
        self.chain_name = chain_name
        self.layout = QVBoxLayout()
        label = QLabel()
        label.setText(chain_name)
        self.layout.addWidget(label)
        self.setLayout(self.layout)

    def load_chain_links_month(self, year, month):
        chain_links = chain_handler.check_chain_month(self.chain_name, year, month)
        
        chain_links.reverse() # Reverse to append the end of the month to the layout first.
        day = len(chain_links)
        for link in chain_links:
            chain_link = Ui_ChainWidgetCheckbox(self.chain_name, year, month, day, state=link)
            self.layout.addWidget(chain_link)
            day -= 1 


class Ui_ChainWidgetCheckbox(QCheckBox):
    def __init__(self, chain_name, year=None, month=None, day=None, date=None, state=None):
        self.chain_name = chain_name
        self.year, self.month, self.day = format_date(year, month, day, date)
        
        checkbox_label = f"{self.year}-{self.month}-{self.day}"
        super(Ui_ChainWidgetCheckbox, self).__init__(checkbox_label)

        if state is None:
            state = chain_handler.check_chain(chain_name, year, month, day, date)
            
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
