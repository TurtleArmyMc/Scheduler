from PySide2 import QtWidgets, QtCore, QtGui
import datetime

from core.todo_handler import todo_handler

import core.helpers as h
from ui.qt_helpers import date_string_to_qdate, qdate_is_weekend



# Calendar to display todo items based on their due date.
class Q_Todo_Calendar(QtWidgets.QCalendarWidget):
    class Color():
        # Color enum
        selected_background = QtGui.QColor(0, 120, 215)
        selected_date_text = QtGui.QColor(255, 255, 255)
        unselected_date_text = QtGui.QColor(0, 0, 0)
        unselected_month_date_text = QtGui.QColor(120, 120, 120)
        unselected_weekend_date_text = QtGui.QColor(255, 0, 0)
        completed_todo_item = QtGui.QColor(0, 255, 0)
        uncompleted_todo_item = QtGui.QColor(255, 0, 0)
    
    def __init__(self, *args, **kwargs):
        self.todo_items = todo_handler.flat_item_list()

        super(Q_Todo_Calendar, self).__init__(*args, **kwargs)
        self.setFirstDayOfWeek(QtCore.Qt.DayOfWeek.Monday)
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(self.VerticalHeaderFormat.NoVerticalHeader)

        todo_handler.todolist_update_event.connect(self.on_todolist_update)

    def paintCell(self, painter, rect, date):
        # Paint background
        if self.selectedDate() == date:
            painter.fillRect(rect, self.Color.selected_background)

        # Paint date text
        if self.selectedDate() != date:
            if self.monthShown() != date.month():
                painter.setPen(self.Color.unselected_month_date_text)
            elif qdate_is_weekend(date):
                painter.setPen(self.Color.unselected_weekend_date_text)
            else:
                painter.setPen(self.Color.unselected_date_text)
        else:
            painter.setPen(self.Color.selected_date_text)
        painter.setFont(QtGui.QFont("Helvetica", 20))
        painter.drawText(rect, QtCore.Qt.AlignTop, str(date.day()))

        # Get todo items to paint
        items = []
        completed_items_num = 0
        for item in self.todo_items:
            if "due_date" in item:
                if item["due_date"] is not None:
                    item_due_date = date_string_to_qdate(item["due_date"])
                    if item_due_date is not None:
                        if date == item_due_date:
                            items.append(item)

        if len(items) != 0:
            # Paint number of todo items
            # Text color is same is date
            completed_items_num = len([item for item in items if item["completed"]])
            x = 40
            y = 5
            painter.setFont(QtGui.QFont("Helvetica", 14))
            item_number_str = f"{completed_items_num}/{len(items)} items"
            painter.drawText(rect.x() + x, rect.y() + y, rect.width() - x, rect.height(), 0, item_number_str)

            # Paint todo items
            x = 5
            y = 12
            width = rect.width() - x
            height = 20
            for item in items:
                y += height
                if y + height > rect.height():
                    break
                
                if item["completed"]:
                    painter.setPen(self.Color.completed_todo_item)
                else:
                    painter.setPen(self.Color.uncompleted_todo_item)
                painter.setFont(QtGui.QFont("Helvetica", 10))
                painter.drawText(rect.x() + x, rect.y() + y, width, height, 0, item["name"])

    def on_todolist_update(self):
        self.todo_items = todo_handler.flat_item_list()
        self.update()