from copy import deepcopy

from core.data_handler import Data_Handler
import core.helpers as h


# Handles loading, saving, and getting chains.
class Chain_Handler(Data_Handler):
    def __init__(self, chains_json_path="data/chains.json"):
        default_data = {"chain_order": [], "chains": {}, "chain_comments": {}}
        super(Chain_Handler, self).__init__(
            "Chains", json_path=chains_json_path, default_data=default_data
        )

    def get_chain_order(self):
        return self._data["chain_order"].copy()

    def edit_chain_order(self, new_order):
        old_order = self.get_chain_order()
        old_order_sorted = self.get_chain_order()
        old_order_sorted.sort()
        new_order_sorted = new_order.copy()
        new_order_sorted.sort()
        if new_order_sorted == old_order_sorted:
            self._data["chain_order"] = new_order.copy()
            self._logger.info(f"Reordered chains from to {old_order} to {new_order}.")
            self.save_json()
        else:
            raise SyntaxError(
                "New chain order must contain the same names as the old order."
            )

    # Try to check the value of the chain at the date. If it's not set, return 0.
    def get_chain(self, chain, year=None, month=None, day=None, date=None):
        year, month, day = h.format_date_ssi(year, month, day, date)

        try:
            return self._data["chains"][chain][year][month][day - 1]
        except (KeyError, IndexError):
            return 0

    # Return a list of all the chain links for a month. If it's not present in the json, return an empty list.
    def get_chain_month(self, chain_name, year, month):
        year = str(year)
        month = str(month)

        try:
            return self._data["chains"][chain_name][year][month].copy()
        except KeyError:
            days = h.days_in_month(year, month)
            return [0] * days

    def edit_chain(
        self, chain_name, new_value: int, year=None, month=None, day=None, date=None
    ):
        year, month, day = h.format_date_ssi(year, month, day, date)

        # If missing dictionary keys for year and/or month, add them.
        if year not in self._data["chains"][chain_name]:
            self._data["chains"][chain_name][year] = {}
        if month not in self._data["chains"][chain_name][year]:
            days = h.days_in_month(year, month)
            self._data["chains"][chain_name][year][month] = [0] * days

        day_index = day - 1
        old_value = self._data["chains"][chain_name][year][month][day_index]
        self._data["chains"][chain_name][year][month][day_index] = int(new_value)
        self._logger.info(
            f"Changed chain '{chain_name}' at {year}/{month}/{day} from '{old_value}' to '{new_value}'."
        )
        self._delete_chain_if_empty(chain_name, year, month)
        self.save_json()

    # Return the comment for a chain at a date. If it's not present in the json, return None.
    def get_chain_comment(self, chain_name, year=None, month=None, day=None, date=None):
        year, month, day = h.format_date_sss(year, month, day, date)
        # Unlike _chains, _chains_comments uses strings for days because [chain_name][year][month] contains a dictionary
        # instead of a list.

        try:
            return self._data["chain_comments"][chain_name][year][month][day]
        except KeyError:
            return None

    # Edit the comment for a chain at a date.
    def edit_chain_comment(
        self, chain_name, new_comment, year=None, month=None, day=None, date=None
    ):
        if new_comment == "" or new_comment.isspace():
            self.delete_chain_comment(self, chain_name, year, month, day)
        else:
            year, month, day = h.format_date_ssi(year, month, day, date)
            # Unlike _chains, _chains_comments uses strings for days because [chain_name][year][month] contains a
            # dictionary instead of a list.
            day = str(day)

            if chain_name not in self._data["chain_comments"]:
                self._data["chain_comments"][chain_name] = {}
            if year not in self._data["chain_comments"][chain_name]:
                self._data["chain_comments"][chain_name][year] = {}
            if month not in self._data["chain_comments"][chain_name][year]:
                self._data["chain_comments"][chain_name][year][month] = {}
            old_comment = self.get_chain_comment(chain_name, year, month, day)
            self._data["chain_comments"][chain_name][year][month][day] = new_comment
            self._logger.info(
                f"Changed chain '{chain_name}' comment at {year}/{month}/{day} from '{old_comment}' to '{new_comment}'."
            )
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
                self._data["chain_comments"][new_name] = self._data["chain_comments"][
                    current_name
                ]
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
    def delete_chain_comment(
        self, chain_name, year=None, month=None, day=None, date=None
    ):
        year, month, day = h.format_date_sss(year, month, day, date)
        # Unlike _data["chains"], _data["chains_comments"] uses strings for days because [chain_name][year][month]
        # contains a dictionary instead of a list.

        try:
            old_comment = self.get_chain_comment(chain_name, year, month, day)
            del self._data["chain_comments"][chain_name][year][month][day]
            self._logger.info(
                f"Deleted chain '{chain_name}' comment '{old_comment}' at {year}/{month}/{day}."
            )
            self._delete_chain_comment_dictionaries_if_empty(chain_name, year, month)
            self.save_json()
        except KeyError:
            self._logger.info(
                f"Tried to delete chain '{chain_name}' comment at {year}/{month}/{day} but there was no comment."
            )

    # Removes chain_comments dictionaries that are empty.
    def _delete_chain_comment_dictionaries_if_empty(self, chain_name, year, month):
        if not self._data["chain_comments"][chain_name][year][month]:
            del self._data["chain_comments"][chain_name][year][month]
            if not self._data["chain_comments"][chain_name][year]:
                del self._data["chain_comments"][chain_name][year]
                if not self._data["chain_comments"][chain_name]:
                    del self._data["chain_comments"][chain_name]


chain_handler = Chain_Handler()