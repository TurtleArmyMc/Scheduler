from PySide2 import QtWidgets
from PySide2.QtCore import Qt

from core.todo_handler import todo_handler

import core.helpers as h


# Widget to load and display todo items.
class Q_Todo_Handler_Widget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Q_Todo_Handler_Widget, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout(self)
        
        self.tree_view = Q_Todo_Tree_Widget(self, todo_handler.todo_list)
        layout.addWidget(self.tree_view)

        new_item_button = QtWidgets.QPushButton("Add new todo item.", self)
        new_item_button.clicked.connect(self.tree_view.new_tree_item)
        layout.addWidget(new_item_button)

        self.setLayout(layout)

    def save_tree_to_json(self):
        todo_handler.todo_list = self.tree_view.to_list()
        todo_handler.save_json()


class Q_Todo_Tree_Widget(QtWidgets.QTreeWidget):
    def __init__(self, parent, load_list=[]):
        super(Q_Todo_Tree_Widget, self).__init__(parent)

        todo_tree_stylesheet = """QTreeView { font-size: 40px; }
            QTreeView::indicator { width: 20px; height: 20px; }"""
        self.setStyleSheet(todo_tree_stylesheet)

        self.setDragDropMode(self.InternalMove)
        self.setHeaderLabel("TODO")

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

    def new_tree_item(self):
        new_item = Q_Todo_Item("Unnamed item", parent=self)
        new_item.setSelected(True)

    def clear_checked_items(self):
        items = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]
        for item in items:
            item.clear_checked_children()
            if item.childCount() == 0 and item.checkState(0) == Qt.Checked:
                item.delete()

    def dropEvent(self, event):
        super(Q_Todo_Tree_Widget, self).dropEvent(event)
        self.save_tree_to_json()

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
    def __init__(self, name, completed=False, items=None, parent=None):
        super(Q_Todo_Item, self).__init__(parent)
        
        self.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | 
            Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)

        self.setText(0, name)
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

    def delete(self):
        tree_widget = self.treeWidget()
        parent = self.parent()
        # parent() returns None for top level widgets.
        if parent is not None:
            parent.removeChild(self)
        else:
            i = tree_widget.indexOfTopLevelItem(self)
            tree_widget.takeTopLevelItem(i)
        tree_widget.save_tree_to_json()

    def to_dict(self):
        ret = {
            "name": self.text(0)
        }

        if self.checkState(0) == Qt.CheckState.Checked:
            ret["completed"] = True
        else:
            ret["completed"] = False
        
        if self.childCount() != 0:
            ret["items"] = [self.child(i).to_dict() for i in range(self.childCount())]

        return ret

