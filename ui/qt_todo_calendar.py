from PySide2 import QtWidgets, QtCore, QtGui
import datetime

from core.todo_handler import todo_handler, todo_item_is_completed

import core.helpers as h
from ui.qt_helpers import date_string_to_qdate, qdate_is_weekend


# Calendar to display todo items based on their due date.
class Q_Todo_Calendar(QtWidgets.QCalendarWidget):
    class Color:
        # Color enum
        selected_background = QtGui.QColor(0, 120, 215)
        selected_date_text = QtGui.QColor(255, 255, 255)
        unselected_date_text = QtGui.QColor(0, 0, 0)
        unselected_month_date_text = QtGui.QColor(120, 120, 120)
        unselected_weekend_date_text = QtGui.QColor(255, 0, 0)
        completed_todo_item = QtGui.QColor(0, 255, 0)
        uncompleted_todo_item = QtGui.QColor(255, 0, 0)

    def __init__(self, *args, **kwargs):
        self.update_items_dict()

        super(Q_Todo_Calendar, self).__init__(*args, **kwargs)
        self.setFirstDayOfWeek(QtCore.Qt.DayOfWeek.Monday)
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(self.VerticalHeaderFormat.NoVerticalHeader)

        todo_handler.update_event.connect(self.on_todolist_update)

    def paintCell(
        self, painter: QtGui.QPainter, rect: QtCore.QRect, date: QtCore.QDate
    ):
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
        try:
            items = self.todo_item_dict[date.year()][date.month()][date.day()]
        except KeyError:
            pass

        if len(items) != 0:
            # Paint number of todo items
            # Text color is same is date's
            completed_items_num = len([item for item in items if item["completed"]])
            x = 40
            y = 5
            width = rect.width() - x
            painter.setFont(QtGui.QFont("Helvetica", 14))
            item_number_str = f"{completed_items_num}/{len(items)} items"
            painter.drawText(
                rect.x() + x, rect.y() + y, width, rect.height(), 0, item_number_str
            )

            # Paint todo items
            x = 5
            y = 32
            width = rect.width() - x
            painter.setFont(QtGui.QFont("Helvetica", 10))
            for item in items:
                if y > rect.height():
                    break

                if item["completed"]:
                    painter.setPen(self.Color.completed_todo_item)
                else:
                    painter.setPen(self.Color.uncompleted_todo_item)

                height = rect.height() - y
                bounding_rect = painter.boundingRect(
                    rect.x() + x,
                    rect.y() + y,
                    width,
                    height,
                    QtCore.Qt.TextWordWrap,
                    item["name"],
                )
                painter.drawText(
                    rect.x() + x,
                    rect.y() + y,
                    width,
                    height,
                    QtCore.Qt.TextWordWrap,
                    item["name"],
                )
                y += bounding_rect.height()

    def update_items_dict(self):
        # Accessing items: self.todo_item_dict[year: int][month: int][day: int] -> list
        self.todo_item_dict = {}
        for item in todo_handler.flat_item_list():
            if "due_date" in item:
                date = date_string_to_qdate(item["due_date"])
                if date is not None:
                    year, month, day = date.year(), date.month(), date.day()

                    if year not in self.todo_item_dict:
                        self.todo_item_dict[year] = {}
                    if month not in self.todo_item_dict[year]:
                        self.todo_item_dict[year][month] = {}
                    if day not in self.todo_item_dict[year][month]:
                        self.todo_item_dict[year][month][day] = []

                    # If item is complete, append to the end of the list. If it is incomplete, append after the last
                    # incomplete item in the list.
                    if todo_item_is_completed(item):
                        self.todo_item_dict[year][month][day].append(item)
                    else:
                        insert_index = 0
                        for index, check_item in enumerate(
                            self.todo_item_dict[year][month][day]
                        ):
                            if todo_item_is_completed(check_item):
                                break
                            else:
                                insert_index = index + 1
                        self.todo_item_dict[year][month][day].insert(insert_index, item)

    def on_todolist_update(self):
        self.update_items_dict()
        self.updateCells()