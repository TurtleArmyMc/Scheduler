from PySide2 import QtWidgets, QtGui
from PySide2.QtCore import Qt

from core.todo_handler import todo_handler
import core.helpers as h

from ui.qt_calendar import Q_Todo_Calendar


# Widget to load and display todo items.
class Q_Todo_Handler_Widget(QtWidgets.QSplitter):
    def __init__(self, *args, **kwargs):
        super(Q_Todo_Handler_Widget, self).__init__(*args, **kwargs)

        todo_tree_wrapper = QtWidgets.QWidget(self)
        todo_tree_wrapper.save_tree_to_json = self.save_tree_to_json
        layout = QtWidgets.QVBoxLayout(self)

        self.tree_widget = Q_Todo_Tree_Widget(self, todo_handler.todo_list)
        layout.addWidget(self.tree_widget)

        new_item_button = QtWidgets.QPushButton("Add new todo item.", self)
        new_item_button.clicked.connect(lambda: self.tree_widget.new_tree_item())
        layout.addWidget(new_item_button)

        todo_tree_wrapper.setLayout(layout)

        self.addWidget(todo_tree_wrapper)

        self.calendar = Q_Todo_Calendar(parent=self)
        self.addWidget(self.calendar)

    def save_tree_to_json(self):
        todo_handler.todo_list = self.tree_widget.to_list()
        todo_handler.save_json()


class Q_Todo_Tree_Widget(QtWidgets.QTreeWidget):
    def __init__(self, parent, load_list=[]):
        super(Q_Todo_Tree_Widget, self).__init__(parent)

        todo_tree_stylesheet = """QTreeView { font-size: 40px; }
            QTreeView::indicator { width: 20px; height: 20px; }"""
        self.setStyleSheet(todo_tree_stylesheet)

        self.setDragDropMode(self.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.setColumnCount(2)

        # Set last column (due_date column) to stretch only as large as it needs to be to fit its contents.
        header = self.header()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        self.setHeaderLabels(["TODO", "Due Date"])

        self.init_context_menu()

        self.load_widgets_from_list(load_list)
        self.itemChanged.connect(self.on_item_changed)

    def load_widgets_from_list(self, load_list, parent=None):
        if parent is None:
            parent = self

        for item in load_list:
            tree_view_item = Q_Todo_Item(**item, parent=parent)
            if "items" in item:
                self.load_widgets_from_list(item["items"], parent=tree_view_item)
            self.expandItem(tree_view_item)

    def save_tree_to_json(self):
        self.parent().save_tree_to_json()

    def to_list(self):
        return [self.topLevelItem(i).to_dict() for i in range(self.topLevelItemCount())]

    def new_tree_item(self, parent=None):
        if parent is None:
            parent = self
        item = Q_Todo_Item("Unnamed item", parent=parent)
        self.deselect_all_items()
        self.scrollToItem(item)
        item.setSelected(True)
        self.setFocus()
        self.setCurrentItem(item)
        self.editItem(item, 0)

    def deselect_all_items(self):
        for item in self.selectedItems():
            item.setSelected(False)

    def clear_checked_items(self):
        items = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]
        for item in items:
            item.clear_checked_children()
            if item.childCount() == 0 and item.checkState(0) == Qt.Checked:
                item.delete()

    def delete_selected_items(self):
        for item in self.selectedItems():
            item.delete()

    def dropEvent(self, event):
        # Save todo list when todo items are reordered.
        selected_items = self.selectedItems()
        super(Q_Todo_Tree_Widget, self).dropEvent(event)
        self.save_tree_to_json()
        for item in selected_items:
            item.setSelected(True)
        self.scrollToItem(selected_items[0])

    def init_context_menu(self):
        self.context_menu = QtWidgets.QMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)

    def load_context_menu(self, point):
        self.context_menu.clear()

        item = self.itemAt(point)

        if item is not None:
            delete_item_action = QtWidgets.QAction("Delete todo item", parent=self.context_menu)
            delete_item_action.triggered.connect(item.delete)
            self.context_menu.addAction(delete_item_action)

        if len(self.selectedItems()) > 1:
            delete_selected_items_action = QtWidgets.QAction("Delete selected todo items", parent=self.context_menu)
            delete_selected_items_action.triggered.connect(self.delete_selected_items)
            self.context_menu.addAction(delete_selected_items_action)

        add_child_action = QtWidgets.QAction("Add todo item", parent=self.context_menu)
        if item is not None:
            add_child_action.triggered.connect(item.add_child_todo_item)
        else:
            add_child_action.triggered.connect(lambda: self.new_tree_item())
        self.context_menu.addAction(add_child_action)

        clear_checked_items_action = QtWidgets.QAction("Clear completed items", parent=self.context_menu)
        clear_checked_items_action.triggered.connect(self.clear_checked_items)
        self.context_menu.addAction(clear_checked_items_action)

    # Opens context menu on right click.
    def on_context_menu(self, point):
        self.load_context_menu(point)
        self.context_menu.exec_(self.mapToGlobal(point))

    def on_item_changed(self):
        self.save_tree_to_json()


class Q_Todo_Item(QtWidgets.QTreeWidgetItem):
    def __init__(self, name, completed=False, due_date=None, items=None, parent=None):
        super(Q_Todo_Item, self).__init__(parent)

        self.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled |
            Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)

        self.setText(0, name)
        if due_date is not None:
            self.setText(1, due_date)

        if completed == True:
            self.setCheckState(0, Qt.CheckState.Checked)
        else:
            self.setCheckState(0, Qt.CheckState.Unchecked)

    def save_tree_to_json(self):
        self.treeWidget().save_tree_to_json()

    def clear_checked_children(self):
        items = [self.child(i) for i in range(self.childCount())]
        for item in items:
            item.clear_checked_children()
            if item.childCount() == 0 and item.checkState(0) == Qt.Checked:
                item.delete()

    def delete(self, delete_children=False):
        tree_widget = self.treeWidget()
        parent = self.parent()
        # parent() returns None for top level widgets.
        if parent is not None:
            if not delete_children:
                index = parent.indexOfChild(self)
                for i in range(self.childCount()):
                    parent.insertChild(index + i, self.takeChild(0))
            parent.removeChild(self)
        else:
            index = tree_widget.indexOfTopLevelItem(self)
            if not delete_children:
                for i in range(self.childCount()):
                    tree_widget.insertTopLevelItem(index + i + 1, self.takeChild(0))
            tree_widget.takeTopLevelItem(index)
        tree_widget.save_tree_to_json()

    def add_child_todo_item(self):
        self.treeWidget().new_tree_item(self)

    def to_dict(self):
        ret = {
            "name": self.text(0)
        }

        if self.checkState(0) == Qt.CheckState.Checked:
            ret["completed"] = True
        else:
            ret["completed"] = False

        if self.text(1) != "" and not self.text(1).isspace():
            ret["due_date"] = self.text(1)

        if self.childCount() != 0:
            ret["items"] = [self.child(i).to_dict() for i in range(self.childCount())]

        return ret
