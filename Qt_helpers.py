from PySide2 import QtWidgets
from PySide2.QtCore import Qt


# Dialog to confirm or cancel action.
def Q_Confirmation_Dialog(text, informative_text="", warning=False, parent=None, *args, **kwargs):
    dialog = QtWidgets.QMessageBox(parent=parent, *args, **kwargs)
    if warning:
        dialog.setIcon(QtWidgets.QMessageBox.Warning)
    
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
    def __init__(self, input_list, window_title="Reorder list", add_new_button=None, parent=None, *args, **kwargs):
        super(Q_Reorder_Dialogue, self).__init__(parent=parent, *args, **kwargs)
        
        self.setWindowTitle(window_title)
        
        layout = QtWidgets.QVBoxLayout()
        
        self.reorder_widget = Q_Reorder_Widget(input_list, parent=self)
        layout.addWidget(self.reorder_widget)

        if add_new_button is not None:
            new_item_layout = QtWidgets.QHBoxLayout()

            self.new_item_input_field = QtWidgets.QLineEdit(parent=self)
            new_item_layout.addWidget(self.new_item_input_field)
            
            new_item_button = QtWidgets.QPushButton(parent=self)
            new_item_button.setText(add_new_button)
            new_item_button.clicked.connect(self.append_item)
            
            new_item_layout.addWidget(new_item_button, alignment=Qt.AlignRight)

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
        if not (item == "" or item.isspace()):
            self.reorder_widget.append_item(item)

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