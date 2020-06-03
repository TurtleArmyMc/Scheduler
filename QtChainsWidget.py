from PySide2.QtWidgets import (QWidget, QLabel, QMenu, QAction, QPushButton, QCheckBox, QScrollArea, QGridLayout,
    QVBoxLayout, QInputDialog)
from PySide2.QtCore import Qt

from chain_handler import Chain_Handler
from helpers import format_date, days_in_month, get_current_month, get_current_year, get_current_day


chain_handler = Chain_Handler()

class Ui_ChainHandlerWidget(QWidget):
    def __init__(self, parent=None):
        super(Ui_ChainHandlerWidget, self).__init__(parent=parent)
        self.load_widget_ui()

    # Creates widget layouts and loads first two months of chain links.
    def load_widget_ui(self):  
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create layout for holding chain links and labels. 
        self.chain_layout = QGridLayout()
        layout.addLayout(self.chain_layout)

        # Create button for loading more chain links.
        load_previous_month_button = QPushButton("Load previous month's chains.")
        load_previous_month_button.clicked.connect(self.load_chain_links_previous_month)
        layout.addWidget(load_previous_month_button)

        # Prevents vertical stretching of layout in scroll area.
        layout.addStretch()
        
        self.create_chain_labels()

        # Load chains links for current month and previous month. 
        self.load_month = get_current_month()
        self.load_year = get_current_year()
        self.load_chain_links_previous_month()
        self.load_chain_links_previous_month()

    # Creates labels for each chain in the chain_layout.
    def create_chain_labels(self):
        row = 0
        for index, chain_name in enumerate(chain_handler.chain_order):
            column = index + 1
            label = QLabel(parent=self)
            label.setText(chain_name)
            self.chain_layout.addWidget(label, row, column)

        # Prevents horizontal stretching of layout in scroll_area.
        self.chain_layout.setColumnStretch(self.chain_layout.columnCount(), 1)
        
    # Loads all the chains links for a month.
    def load_chains_month(self, year, month):
        if not (month == get_current_month() and year == get_current_year()):
            start_day = days_in_month(year, month)
        else:
            start_day = get_current_day()
        
        row = self.chain_layout.rowCount()
        date_label_column = 0
        for day in range(start_day, 0, -1):
            date_label = QLabel(parent=self)
            date_label.setText(f"{year}-{month}-{day}")
            self.chain_layout.addWidget(date_label, row, date_label_column)

            for index, chain_name in enumerate(chain_handler.chain_order):
                column = index + 1 
                chain_link = Ui_ChainWidgetCheckbox(chain_name, year, month, day, parent=self)
                self.chain_layout.addWidget(chain_link, row, column)
            row += 1

    # Loads all chain links for the next unloaded month.
    def load_chain_links_previous_month(self):
        self.load_chains_month(self.load_year, self.load_month)
        
        if (self.load_month != 1):
            self.load_month -= 1
        else:
            self.load_month = 12 
            self.load_year -= 1


# Widget used to represent the chain links for each day in a chain.
class Ui_ChainWidgetCheckbox(QCheckBox):
    def __init__(self, chain_name, year=None, month=None, day=None, date=None, state=None, parent=None):
        super(Ui_ChainWidgetCheckbox, self).__init__(parent=parent)
        
        self.chain_name = chain_name
        self.year, self.month, self.day = format_date(year, month, day, date)
        
        self.init_checked_state(state)
        self.load_comment()
        self.init_context_menu()

    # Determine whether the checkbox should be checked or not.
    def init_checked_state(self, state):
        if state is None:
            state = chain_handler.get_chain(self.chain_name, self.year, self.month, self.day)
            
        if state == 1:
            self.setCheckState(Qt.CheckState.Checked)
        else:
            self.setCheckState(Qt.CheckState.Unchecked)

        self.stateChanged.connect(self.on_state_change)

    # Load the comment tooltip for the chain link.
    def load_comment(self, comment=None):
        if comment is None:
            self.comment = chain_handler.get_chain_comment(self.chain_name, self.year, self.month, self.day)
        else:
            self.comment = comment

        # Adds an asterik next to chain links with a comment tootltip. 
        self.checkbox_label = ""
        if self.comment is not None:
            self.checkbox_label = "*"
            self.setToolTip(self.comment)
        else:
            self.setToolTip("")

        self.setText(self.checkbox_label)

    # Load the context menu for editing the chain link's comment tooltip.
    def init_context_menu(self):
        self.context_menu = QMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)
        self.load_context_menu()

    # Load items in the context menu for editing the chain link's comment tooltip.
    def load_context_menu(self):
        self.context_menu.clear()

        if self.comment is None:
            create_comment_action = QAction("Create new comment.", parent=self)
            create_comment_action.triggered.connect(self.edit_comment)
            self.context_menu.addAction(create_comment_action)
        else:
            edit_comment_action = QAction("Edit comment.", parent=self)
            edit_comment_action.triggered.connect(self.edit_comment)
            self.context_menu.addAction(edit_comment_action)
            
            delete_comment_action = QAction("Delete comment.", parent=self)
            delete_comment_action.triggered.connect(self.delete_comment)
            self.context_menu.addAction(delete_comment_action)

    # Edit comment on chain link and update chain_comments json.
    def edit_comment(self):
        comment, ok = QInputDialog(self).getText(self, "Comment", "Set comment:")
        if comment and ok:
            chain_handler.edit_chain_comment(self.chain_name, comment, self.year, self.month, self.day)
            self.load_comment(comment)
            self.load_context_menu()

    # Remove comment from chain link and update chain_comments json.
    def delete_comment(self):
        chain_handler.delete_chain_comment(self.chain_name, self.year, self.month, self.day)
        self.load_comment()
        self.load_context_menu()

    # Update chains json when checkbox state is changed.
    def on_state_change(self):
        new_value = 0
        if self.checkState() == Qt.CheckState.Checked:
            new_value = 1
        chain_handler.edit_chain(self.chain_name, new_value, self.year, self.month, self.day)

    # Opens custom context menu for editing the chain link's comment tooltip on right click.
    def on_context_menu(self, point):
        self.context_menu.exec_(self.mapToGlobal(point))