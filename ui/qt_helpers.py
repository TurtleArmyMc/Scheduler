from PySide2 import QtWidgets
from PySide2 import QtCore, QtGui
import datetime


def scroll_area_wrapper(widget:QtWidgets.QWidget) -> QtWidgets.QScrollArea:
    widget_scroll_area = QtWidgets.QScrollArea()
    widget_scroll_area.setWidget(widget)
    widget_scroll_area.setWidgetResizable(True) # Allows widget to expand and scroll in the scroll area.
    return widget_scroll_area


# Dialog to confirm or cancel action.
def Q_Confirmation_Dialog(window_title, text, informative_text="", warning=False, parent=None, *args, **kwargs):
    dialog = QtWidgets.QMessageBox(parent=parent, *args, **kwargs)
    if warning:
        dialog.setIcon(QtWidgets.QMessageBox.Warning)
    
    dialog.setWindowTitle(window_title)
    dialog.setText(text)
    if informative_text:
        dialog.setInformativeText(informative_text)

    dialog.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
    dialog.setDefaultButton(QtWidgets.QMessageBox.Cancel)

    button_press = dialog.exec_()
    if button_press == QtWidgets.QMessageBox.Ok:
        return True
    elif button_press == QtWidgets.QMessageBox.Cancel:
        return False
    else:
        # This should never be reached.
        raise Exception()


# Dialogue to reorder a list of strings.
class Q_Reorder_Dialogue(QtWidgets.QDialog):
    # Passing a string to add_new_button will allow for new items to be added to the list.
    def __init__(self, input_list, window_title="Reorder list", add_new_button=None, allow_duplicates=True, 
        parent=None, *args, **kwargs):

        self.allow_duplicates = allow_duplicates
        
        super(Q_Reorder_Dialogue, self).__init__(parent=parent, *args, **kwargs)
        
        self.setWindowTitle(window_title)
        
        layout = QtWidgets.QVBoxLayout()
        
        self.reorder_widget = Q_Reorder_Widget(input_list, parent=self)
        layout.addWidget(self.reorder_widget)

        if add_new_button is not None:
            new_item_layout = QtWidgets.QHBoxLayout()

            self.new_item_input_field = QtWidgets.QLineEdit(parent=self)
            self.new_item_input_field.textChanged.connect(self.on_text_changed)
            new_item_layout.addWidget(self.new_item_input_field)
            
            self.new_item_button = QtWidgets.QPushButton(parent=self)
            self.new_item_button.setText(add_new_button)
            self.new_item_button.setEnabled(False)
            self.new_item_button.clicked.connect(self.append_item)
            
            new_item_layout.addWidget(self.new_item_button, alignment=QtCore.Qt.AlignRight)

            layout.addLayout(new_item_layout)
        
        buttons = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(buttons, parent=self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)
        
        self.setLayout(layout)

        self.ok = self.exec_()
        self.return_list = self.reorder_widget.get_items()

    def append_item(self):
        item = self.new_item_input_field.text()
        self.reorder_widget.append_item(item)
        self.new_item_input_field.clear()

    def on_text_changed(self):
        if self.new_item_input_field.text() == "" or self.new_item_input_field.text().isspace():
            self.new_item_button.setEnabled(False)
        elif not self.allow_duplicates:
            if self.new_item_input_field.text() in self.reorder_widget.get_items():
                self.new_item_button.setEnabled(False)
            else:
                self.new_item_button.setEnabled(True)
        else:
            self.new_item_button.setEnabled(True)

    # Allows for unpacking of return_list and ok in single line.
    def __iter__(self):
        yield self.return_list 
        yield self.ok


# Widget with a rearangable list of strings.
class Q_Reorder_Widget(QtWidgets.QListWidget):
    def __init__(self, input_list: list, parent=None, *args, **kwargs):
        super(Q_Reorder_Widget, self).__init__(parent=parent, *args, **kwargs)

        self.setDragDropMode(self.InternalMove)

        for item in input_list:
            self.append_item(item)

    def append_item(self, item):
        drag_item = QtWidgets.QListWidgetItem(parent=self)
        drag_item.setText(str(item))
        self.addItem(drag_item)

    def get_items(self):
        return [self.item(i).text() for i in range(self.count())]


def date_string_to_qdate(string:str) -> QtCore.QDate:
    # Assumes mm/dd/yy date format
    try:
        _date = datetime.date.today()
        year, month, day = _date.year, _date.month, _date.day

        split_string = string.split("/")
        if len(split_string) == 3:
            month, day, year = split_string
            month, day, year = int(month), int(day), int(year) 
        elif len(split_string) == 2:
            month, day = split_string
            month, day = int(month), int(day) 
        else:
            return None

        qdate = QtCore.QDate()
        qdate.setDate(year, month, day)

        return qdate
    except:
        return None


def qdate_is_weekend(qdate:QtCore.QDate) -> bool:
    day_of_week = qdate.dayOfWeek()
    return day_of_week == 6 or day_of_week == 7