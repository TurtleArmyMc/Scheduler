from copy import deepcopy

from core.data_handler import Data_Handler
import core.helpers as h


# Handles loading, saving, and getting chains.
class Chain_Handler(Data_Handler):
    def __init__(self, chains_json_path="data/chains.json"):
        default_data = {
            "chain_order": [],
            "chains": {},
            "chain_comments": {}
        }
        super(Chain_Handler, self).__init__("Chains", json_path=chains_json_path, default_data=default_data)

    @property
    def chain_order(self):
        return self._data["chain_order"].copy()

    @chain_order.setter
    def chain_order(self, new_order):
        old_order = self.chain_order
        old_order_sorted = self.chain_order
        old_order_sorted.sort()
        new_order_sorted = new_order.copy()
        new_order_sorted.sort()
        if  new_order_sorted == old_order_sorted:
            self._data["chain_order"] = new_order.copy()
            self._logger.info(f"Reordered chains from to {old_order} to {new_order}.")
            self.save_json()
        else:
            raise SyntaxError("New chain order must contain the same names as the old order.")

    @property
    def chains(self):
        return h.Indexable_Property(self._chains_getitem, self._chains_setitem)

    @property
    def chain_comments(self):
        return h.Indexable_Property(self._chain_comments_getitem, self._chain_comments_setitem)

    def _chains_getitem(self, index):
        chain_name = index[0]
        self._data["chains"][chain_name] # Raise KeyError if chain_name not in chains.
        if len(index) == 4:
            year, month, day = h.format_date_ssi(*index[1:])
            try:
                day_index = day - 1
                return self._data["chains"][chain_name][year][month][day_index]
            except (KeyError, IndexError):
                return 0
        if len(index) == 3:
            year, month = str(index[1]), str(index[2])
            try:
                return self._data["chains"][chain_name][year][month].copy()
            except KeyError:
                days = h.days_in_month(year, month)
                return [0] * days
        raise IndexError

    def _chains_setitem(self, index:tuple, new_value:bool):
        if not (isinstance(new_value, bool) or new_value in [0, 1]):
            raise ValueError

        chain_name, year, month, day = index[0], None, None, None
        if len(index) == 4:
            year, month, day = h.format_date_ssi(*index[1:])
        elif len(index) == 2:
            year, month, day = h.format_date_ssi(date=index[1])
        else:
            raise IndexError

        # If missing dictionary keys for year and/or month, add them.
        if (year not in self._data["chains"][chain_name]):
            self._data["chains"][chain_name][year] = {}
        if (month not in self._data["chains"][chain_name][year]):
            days = h.days_in_month(year, month)
            self._data["chains"][chain_name][year][month] = [0] * days

        day_index = day - 1
        old_value = self._data["chains"][chain_name][year][month][day_index]
        self._data["chains"][chain_name][year][month][day_index] = int(new_value)
        self._logger.info(f"Changed chain '{chain_name}' at {year}/{month}/{day} from '{old_value}' to '{new_value}'.")
        self._delete_chain_if_empty(chain_name, year, month)
        self.save_json()

    def _chain_comments_getitem(self, index):
        chain_name, year, month, day = index[0], None, None, None
        if len(index) == 4:
            year, month, day = h.format_date_sss(*index[1:])
        elif len(index) == 2:
            year, month, day = h.format_date_sss(date=index[1])
        else:
            raise IndexError

        try:
            return self._data["chain_comments"][chain_name][year][month][day]
        except KeyError:
            return None

    def _chain_comments_setitem(self, index:tuple, new_comment:str):
        chain_name, year, month, day = index[0], None, None, None
        # Unlike _data["chains"], _data["chains_comments"] uses strings for days because [chain_name][year][month]
        # contains a dictionary instead of a list.
        if len(index) == 4:
            year, month, day = h.format_date_sss(*index[1:])
        elif len(index) == 2:
            year, month, day = h.format_date_sss(date=index[1])
        else:
            raise IndexError

        if new_comment == "" or new_comment.isspace():
            self.delete_chain_comment(self, chain_name, year, month, day)
        else:

            if (chain_name not in self._data["chain_comments"]):
                self._data["chain_comments"][chain_name] = {}
            if (year not in self._data["chain_comments"][chain_name]):
                self._data["chain_comments"][chain_name][year] = {}
            if (month not in self._data["chain_comments"][chain_name][year]):
                self._data["chain_comments"][chain_name][year][month] = {}
            old_comment = self.chain_comments[chain_name, year, month, day]
            self._data["chain_comments"][chain_name][year][month][day] = new_comment
            self._logger.info(
                f"Changed chain '{chain_name}' comment at {year}/{month}/{day} from '{old_comment}' to '{new_comment}'.")
            self.save_json()

    def create_new_chain(self, chain_name):
        self._data["chains"][chain_name] = {}
        self._data["chain_order"].append(chain_name)
        self._logger.info(f"Created new chain '{chain_name}'.")
        self.save_json()

    def rename_chain(self, current_name, new_name):
        if new_name in self._data["chains"]:
            raise NameError(f"'{new_name}' already exists in chains.")
        else:
            chain_order_index = self._data["chain_order"].index(current_name)
            self._data["chain_order"][chain_order_index] = new_name

            self._data["chains"][new_name] = self._data["chains"][current_name]
            del self._data["chains"][current_name]

            if current_name in self._data["chain_comments"]:
                self._data["chain_comments"][new_name] = self._data["chain_comments"][current_name]
                del self._data["chain_comments"][current_name]
            self._logger.info(f"Renamed chain '{current_name}' to '{new_name}'.")

            self.save_json()

    # Removes chain link lists that are all 0 and any empty year/month dictionaries.
    def _delete_chain_if_empty(self, chain_name, year, month):
        if max(self._data["chains"][chain_name][year][month]) == 0:
            del self._data["chains"][chain_name][year][month]
            if not self._data["chains"][chain_name][year]:
                del self._data["chains"][chain_name][year]

    def delete_chain(self, chain_name):
        if chain_name in self._data["chain_order"]:
            self._data["chain_order"].remove(chain_name)
            del self._data["chains"][chain_name]
            self._data["chain_comments"].pop(chain_name, None)
            self._logger.info(f"Deleted chain '{chain_name}'.")
            self.save_json()
        else:
            raise NameError(f"No chain '{chain_name}'")

    # Delete the comment for a chain at a date.
    def delete_chain_comment(self, chain_name, year=None, month=None, day=None, date=None):
        year, month, day = h.format_date_sss(year, month, day, date)
        # Unlike _data["chains"], _data["chains_comments"] uses strings for days because [chain_name][year][month]
        # contains a dictionary instead of a list.

        try:
            old_comment = self.chain_comments[chain_name, year, month, day]
            del self._data["chain_comments"][chain_name][year][month][day]
            self._logger.info(f"Deleted chain '{chain_name}' comment '{old_comment}' at {year}/{month}/{day}.")
            self._delete_chain_comment_dictionaries_if_empty(chain_name, year, month)
            self.save_json()
        except KeyError:
            self._logger.info(
                f"Tried to delete chain '{chain_name}' comment at {year}/{month}/{day} but there was no comment.")

    # Removes chain_comments dictionaries that are empty.
    def _delete_chain_comment_dictionaries_if_empty(self, chain_name, year, month):
        if not self._data["chain_comments"][chain_name][year][month]:
            del self._data["chain_comments"][chain_name][year][month]
            if not self._data["chain_comments"][chain_name][year]:
                del self._data["chain_comments"][chain_name][year]
                if not self._data["chain_comments"][chain_name]:
                    del self._data["chain_comments"][chain_name]


chain_handler = Chain_Handler()