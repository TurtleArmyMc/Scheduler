from PySide2 import QtWidgets, QtCore, QtGui
import datetime

from core.chain_handler import chain_handler

from ui.qt_helpers import (
    date_string_to_qdate,
    qdate_is_weekend,
    scroll_area_wrapper,
    date_to_qdate,
    qdate_to_date,
)


class Q_Todo_Month_View(QtWidgets.QSplitter):
    def __init__(self, *args, **kwargs):
        super(Q_Todo_Month_View, self).__init__(*args, **kwargs)

        self.chain_selector = Q_Chain_Selector(self)
        self.chains_calendar = Q_Chains_Calendar(self)

        self.addWidget(self.chain_selector)
        self.addWidget(self.chains_calendar)

    def on_chain_selection_update(self):
        self.chains_calendar.on_chain_selection_update()
        self.chains_calendar.updateCells()

    def get_chains(self):
        chains = []
        for i in range(self.chain_selector.count()):
            item = self.chain_selector.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                chains.append(item.text())
        return chains


class Q_Chain_Selector(QtWidgets.QListWidget):
    def __init__(self, parent: Q_Todo_Month_View, *args, **kwargs):
        super(Q_Chain_Selector, self).__init__(parent, *args, **kwargs)

        chain_selector_stylesheet = """QListView { font-size: 40px; }
            QListView::indicator { width: 20px; height: 20px; }"""
        self.setStyleSheet(chain_selector_stylesheet)

        self.setDragDropMode(self.InternalMove)

        self.generate_items()

        chain_handler.update_chain_order_event.connect(self.generate_items)
        self.itemChanged.connect(parent.on_chain_selection_update)

    def generate_items(self):
        self.clear()

        for index, chain in enumerate(chain_handler.get_chain_order()):
            self.addItem(chain)
            item = self.item(index)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)

    def dropEvent(self, event):
        super(Q_Chain_Selector, self).dropEvent(event)
        self.parent().on_chain_selection_update()


# Calendar to display chains monthly
class Q_Chains_Calendar(QtWidgets.QCalendarWidget):
    class Color:
        # Color enum
        selected_background = QtGui.QColor(0, 120, 215)
        unselected_date_text = QtGui.QColor(0, 0, 0)
        unselected_month_date_text = QtGui.QColor(120, 120, 120)
        unselected_weekend_date_text = QtGui.QColor(255, 0, 0)
        chain_name_color = QtGui.QColor(255, 255, 255)

    chain_colors = [
        QtGui.QColor(220, 20, 60),  # Crimson
        QtGui.QColor(0, 128, 0),  # Green
        QtGui.QColor(0, 0, 139),  # Dark blue
        QtGui.QColor(218, 165, 32),  # Goldenrod
        QtGui.QColor(138, 43, 226),  # Blue violet
        QtGui.QColor(154, 205, 50),  # Yellow green
        QtGui.QColor(255, 99, 71),  # Tomato
        QtGui.QColor(238, 130, 238),  # Violet
        QtGui.QColor(32, 178, 170),  # Light sea green
        QtGui.QColor(106, 90, 205),  # Slate blue
        QtGui.QColor(255, 105, 180),  # Hot pink
    ]

    def __init__(self, parent: Q_Todo_Month_View, *args, **kwargs):
        super(Q_Chains_Calendar, self).__init__(parent=parent, *args, **kwargs)
        self.setFirstDayOfWeek(QtCore.Qt.DayOfWeek.Monday)
        self.setVerticalHeaderFormat(self.VerticalHeaderFormat.NoVerticalHeader)
        self.setSelectionMode(self.NoSelection)

        today = datetime.date.today()

        # Prevent scrolling past the current date
        self.setMaximumDate(date_to_qdate(today))

        # Hides the selected date
        self.setSelectedDate(QtCore.QDate(1, 1, 1))
        self.setCurrentPage(today.year, today.month)

        self.month_chains = {}
        self.set_chain_colors()
        self.currentPageChanged.connect(self.on_chain_selection_update)
        chain_handler.update_chain_val_event.connect(self.on_chain_selection_update)

    def on_chain_selection_update(self):
        self.month_chains = {}
        self.set_chain_colors()
        self.updateCells()

    def set_chain_colors(self):
        self.chain_color_dict = {
            chain_name: self.chain_colors[index % len(self.chain_colors)]
            for index, chain_name in enumerate(self.parent().get_chains())
        }

    def generate_week_info(self, date: datetime.date):
        chains = self.parent().get_chains()

        # Set date to the first day of the week displayed in the calendar
        while date.isoweekday() != self.firstDayOfWeek():
            date -= datetime.timedelta(days=1)

        date_range = (date, date + datetime.timedelta(days=6))

        # Get all of the chains for every week.
        week_chains = [
            chain_name
            for chain_name in chains
            if any(
                chain_handler.get_chain(
                    chain_name, date=date + datetime.timedelta(days=day_offset)
                )
                for day_offset in range(7)
            )
        ]
        self.month_chains[date_range] = week_chains
        return week_chains

    def paintCell(
        self, painter: QtGui.QPainter, rect: QtCore.QRect, qdate: QtCore.QDate
    ):
        date = qdate_to_date(qdate)
        # Paint date text
        if self.monthShown() != qdate.month():
            painter.setPen(self.Color.unselected_month_date_text)
        else:
            painter.setPen(self.Color.unselected_date_text)
        painter.setFont(QtGui.QFont("Helvetica", 20))
        painter.drawText(rect, QtCore.Qt.AlignTop, str(qdate.day()))

        # Get all of the chains for the current week
        for date_range, chains in self.month_chains.items():
            if date_range[0] <= date and date <= date_range[1]:
                display_chains = chains
                break
        else:
            display_chains = self.generate_week_info(qdate_to_date(qdate))

        # Paint completed chains
        completed_chains_num = 0
        x = 5
        y = 32
        width = rect.width() - x
        painter.setFont(QtGui.QFont("Helvetica", 10))
        for chain in display_chains:
            if y > rect.height():
                break

            height = rect.height() - y
            bounding_rect = painter.boundingRect(
                rect.x() + x,
                rect.y() + y,
                width,
                height,
                QtCore.Qt.TextWordWrap,
                chain,
            )
            if chain_handler.get_chain(chain, qdate.year(), qdate.month(), qdate.day()):
                # Draw colored rect
                painter.fillRect(
                    rect.x(),
                    rect.y() + y,
                    rect.width(),
                    min(bounding_rect.height(), rect.height() - y),
                    self.chain_color_dict[chain],
                )

                # Draw text
                painter.setPen(self.Color.chain_name_color)
                completed_chains_num += 1
                painter.drawText(
                    rect.x() + x,
                    rect.y() + y,
                    width,
                    height,
                    QtCore.Qt.TextWordWrap,
                    chain,
                )

            y += bounding_rect.height()

        # Paint number of completed todo items
        if completed_chains_num > 0:
            if self.monthShown() != qdate.month():
                painter.setPen(self.Color.unselected_month_date_text)
            else:
                painter.setPen(self.Color.unselected_date_text)
            x = 40
            y = 5
            width = rect.width() - x
            painter.setFont(QtGui.QFont("Helvetica", 14))
            item_number_str = f"{completed_chains_num}"
            painter.drawText(
                rect.x() + x, rect.y() + y, width, rect.height(), 0, item_number_str
            )

        # Surround current date in a blue border
        if datetime.date.today() == date:
            painter.setPen(self.Color.selected_background)
            painter.drawRect(rect.x(), rect.y(), rect.width(), rect.height())
