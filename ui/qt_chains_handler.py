from PySide2 import QtWidgets, QtCore
import datetime

from core.chain_handler import chain_handler

from ui.qt_helpers import Q_Confirmation_Dialog, Q_Reorder_Dialogue
import core.helpers as h


# Widget to load and display all chains.
class Q_Chain_Handler_Widget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Q_Chain_Handler_Widget, self).__init__(*args, **kwargs)
        self.init_widget_ui()

    def init_widget_ui(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.chain_layout = QtWidgets.QGridLayout()
        layout.addLayout(self.chain_layout)

        # Create button for loading more chain links.
        load_previous_month_button = QtWidgets.QPushButton("Load more chains.")
        load_previous_month_button.clicked.connect(lambda: self.load_chains(14))
        layout.addWidget(load_previous_month_button)

        # Prevents vertical stretching of layout in scroll area.
        layout.addStretch()

        self.load_chain_layout_ui()

    # Creates widget labels loads first two months of chain links.
    def load_chain_layout_ui(self):
        self.clear_chain_layout_ui()
        self.create_chain_labels()

        # Load chains links for next 2 weeks.
        self.date_iterator = h.date_iterator(datetime.timedelta(days=-1), date=datetime.date.today())
        self.load_chains(14)

    def clear_chain_layout_ui(self):
        for column in range(self.chain_layout.columnCount()):
            self.chain_layout.setColumnStretch(column, 0)
            for row in range(self.chain_layout.rowCount()):
                item = self.chain_layout.itemAtPosition(row, column)
                if item is not None:
                    item.widget().deleteLater()

    # Creates labels for each chain in the chain_layout.
    def create_chain_labels(self):
        label_style_sheet = "font-weight: bold; font-size: 50px; margin-right: 5px"
        row = 0
        for index, chain_name in enumerate(chain_handler.get_chain_order()):
            column = index + 1
            label = QtWidgets.QLabel(parent=self)
            label.setText(chain_name)
            label.setStyleSheet(label_style_sheet)
            self.chain_layout.addWidget(label, row, column)

        # Add button to reorder chains and create new chains.
        edit_chains_button = QtWidgets.QPushButton(parent=self)
        edit_chains_button.setText("Edit chains.")
        edit_chains_button.clicked.connect(self.edit_chain_order)
        self.chain_layout.addWidget(edit_chains_button, row, self.chain_layout.columnCount(), alignment=QtCore.Qt.AlignLeft)

        # Prevents horizontal stretching of layout in scroll_area.
        self.chain_layout.setColumnStretch(self.chain_layout.columnCount(), 1)

    def load_chains(self, days):
        date_label_style_sheet = "font-size: 25px"

        row = self.chain_layout.rowCount()
        date_label_column = 0

        for _ in range(days):
            date = next(self.date_iterator)

            weekday = h.get_weekday(date=date)
            date_label = QtWidgets.QLabel(parent=self)
            date_label.setStyleSheet(date_label_style_sheet)
            date_label.setText(f"{weekday} {date.month}/{date.day}/{str(date.year)[2:]}")

            self.chain_layout.addWidget(date_label, row, date_label_column)

            for index, chain_name in enumerate(chain_handler.get_chain_order()):
                column = index + 1
                chain_link = Q_Chain_Link_Checkbox(self, chain_name, date=date)
                self.chain_layout.addWidget(chain_link, row, column)
            row += 1

    def edit_chain_order(self):
        old_chain_order = chain_handler.get_chain_order()
        new_chain_order, ok = Q_Reorder_Dialogue(self).get_order(
            old_chain_order, "Edit chains", "Add chain", allow_duplicates=False)
        if ok:
            for chain_name in new_chain_order:
                if chain_name not in old_chain_order:
                    chain_handler.create_new_chain(chain_name)
            chain_handler.edit_chain_order(new_chain_order)
            self.load_chain_layout_ui()


# Widget used to represent the chain links for each day in a chain.
class Q_Chain_Link_Checkbox(QtWidgets.QCheckBox):
    def __init__(self, parent:Q_Chain_Handler_Widget,
        chain_name, year=None, month=None, day=None, date=None, state=None, *args, **kwargs):
        super(Q_Chain_Link_Checkbox, self).__init__(parent=parent, *args, **kwargs)

        chain_link_checkbox_stylesheet = """QCheckBox { margin-left: 50px; font-size:80px }
            QCheckBox::indicator { width: 80px; height: 80px }"""
        self.setStyleSheet(chain_link_checkbox_stylesheet)

        self.chain_name = chain_name
        self.year, self.month, self.day = h.format_date_iii(year, month, day, date)

        self.init_checked_state(state)
        self.load_comment()
        self.init_context_menu()

    # Determine whether the checkbox should be checked or not.
    def init_checked_state(self, state):
        if state is None:
            state = chain_handler.get_chain(self.chain_name, self.year, self.month, self.day)

        if state == 1:
            self.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.setCheckState(QtCore.Qt.CheckState.Unchecked)

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

    # Load the context menu for editing the chain link's comment tooltip and deleting the chain.
    def init_context_menu(self):
        self.context_menu = QtWidgets.QMenu(self)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)
        self.load_context_menu()

    # Load items in the context menu for editing the chain link's comment tooltip and deleting the chain.
    def load_context_menu(self):
        self.context_menu.clear()

        if self.comment is None:
            create_comment_action = QtWidgets.QAction("Create new comment", parent=self.context_menu)
            create_comment_action.triggered.connect(self.edit_comment)
            self.context_menu.addAction(create_comment_action)
        else:
            edit_comment_action = QtWidgets.QAction("Edit comment", parent=self.context_menu)
            edit_comment_action.triggered.connect(self.edit_comment)
            self.context_menu.addAction(edit_comment_action)

            delete_comment_action = QtWidgets.QAction("Delete comment", parent=self.context_menu)
            delete_comment_action.triggered.connect(self.delete_comment)
            self.context_menu.addAction(delete_comment_action)
        rename_chain_action = QtWidgets.QAction("Rename chain", parent=self.context_menu)
        rename_chain_action.triggered.connect(self.rename_chain)
        self.context_menu.addAction(rename_chain_action)
        delete_chain_action = QtWidgets.QAction("Delete chain", parent=self.context_menu)
        delete_chain_action.triggered.connect(self.delete_chain)
        self.context_menu.addAction(delete_chain_action)


    def delete_chain(self):
        text = f"Delete chain '{self.chain_name}'?"
        informative_text = "WARNING: This can not be undone."
        ok = Q_Confirmation_Dialog(self).get_ok("Confirm deletion", text, informative_text, warning=True)
        if ok:
            chain_handler.delete_chain(self.chain_name)
            self.parent().load_chain_layout_ui()

    def rename_chain(self):
        new_name, ok = QtWidgets.QInputDialog(self).getText(self, f"Rename '{self.chain_name}'", "New name:")
        if ok:
            if new_name == "" or new_name.isspace():
                error_dialog = QtWidgets.QMessageBox(parent=self)
                error_dialog.setWindowTitle("Rename failed")
                error_dialog.setText("Error")
                error_dialog.setInformativeText("New name can not be empty.")
                error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
                error_dialog.exec_()
            else:
                try:
                    chain_handler.rename_chain(self.chain_name, new_name)
                    self.parent().load_chain_layout_ui()
                except NameError:
                    error_dialog = QtWidgets.QMessageBox(parent=self)
                    error_dialog.setWindowTitle("Rename failed")
                    error_dialog.setText("Error")
                    error_dialog.setInformativeText(f"Error: '{new_name}' is already in use.")
                    error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
                    error_dialog.exec_()
                except:
                    raise

    def edit_comment(self):
        comment, ok = QtWidgets.QInputDialog(self).getText(
            self, "Comment", "Set comment:", QtWidgets.QLineEdit.Normal, self.comment)
        if comment and ok:
            chain_handler.edit_chain_comment(self.chain_name, comment, self.year, self.month, self.day)
            self.load_comment(comment)
            self.load_context_menu()

    def delete_comment(self):
        chain_handler.delete_chain_comment(self.chain_name, self.year, self.month, self.day)
        self.load_comment()
        self.load_context_menu()

    # Update chains json when checkbox state is changed.
    def on_state_change(self):
        new_value = 0
        if self.checkState() == QtCore.Qt.CheckState.Checked:
            new_value = 1
        chain_handler.edit_chain(self.chain_name, new_value, self.year, self.month, self.day)

    # Opens custom context menu for editing the chain link's comment tooltip on right click.
    def on_context_menu(self, point):
        self.context_menu.exec_(self.mapToGlobal(point))