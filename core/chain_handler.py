import logging
import json
from pathlib import Path

import core.helpers as h


logging.getLogger().setLevel(logging.WARNING)

# Handles loading, saving, and getting chains.
class Chain_Handler():
    def __init__(self, chains_json_path="data/chains.json"):
        self._chains_json_path = Path(chains_json_path)
        self._load_json()

    def _load_json(self):
        if (self._chains_json_path.is_file()):
            with open(self._chains_json_path, 'r') as file:
                self._chains_dict = json.loads(file.read())
                self._chains = self._chains_dict["chains"]
                self._chain_order = self._chains_dict["chain_order"]
                self._chain_comments = self._chains_dict["chain_comments"]
                logging.info(f"Loaded chains data from '{self._chains_json_path}'.")
        else:
            self._chains_json_path.parent.mkdir(parents=True, exist_ok=True)
            self._chains_json_path.touch(exist_ok=True)
            self._chains = {}
            self._chain_order = []
            self._chain_comments = {}
            self._chains_dict = {
                "chain_order": self._chain_order,
                "chains": self._chains,
                "chain_comments": self._chain_comments
            }
            self._save_json()

    def _save_json(self):
        try:
            serialized_json = json.dumps(self._chains_dict, indent=0)
            with open(self._chains_json_path, 'w') as file:
                file.write(serialized_json)
                logging.info(f"Saved chains data to '{self._chains_json_path}'.")
        except:
            raise

    def create_new_chain(self, chain_name):
        self._chains[chain_name] = {}
        self._chain_order.append(chain_name)
        logging.info(f"Created new chain '{chain_name}'.")
        self._save_json()
    
    def rename_chain(self, current_name, new_name):
        if new_name in self._chains:
            raise NameError(f"'{new_name}' already exists in chains.")
        else:
            chain_order_index = self._chain_order.index(current_name)
            self._chain_order[chain_order_index] = new_name

            self._chains[new_name] = self._chains[current_name]
            del self._chains[current_name]
            
            if current_name in self._chain_comments:
                self._chain_comments[new_name] = self._chain_comments[current_name]
                del self._chain_comments[current_name] 
            logging.info(f"Renamed chain '{current_name}' to '{new_name}'.")
            
            self._save_json()

    def get_chain_order(self):
        return self._chain_order.copy()

    def edit_chain_order(self, new_order):
        # Check to see that the new order contains the same chains.
        old_order = self.get_chain_order()
        if new_order.copy().sort() == old_order.sort():
            self._chains_dict["chain_order"] = new_order.copy()
            self._chain_order = self._chains_dict["chain_order"]
            logging.info(f"Reordered chains from to {old_order} to {new_order}.")
            self._save_json()
        else:
            raise SyntaxError("New chain order must contain the same names as the old order.")
    
    # Edits a chain at a given date. chain_name should be a string, new value should be 0 or 1 for incomplete or complete.
    def edit_chain(self, chain_name, new_value: int, year=None, month=None, day=None, date=None):
        year, month, day = h.format_date_ssi(year, month, day, date)
        
        # If missing dictionary keys for year and/or month, add them.
        if (year not in self._chains[chain_name]):
            self._chains[chain_name][year] = {}
        if (month not in self._chains[chain_name][year]):
            days = h.days_in_month(year, month)
            self._chains[chain_name][year][month] = [0] * days
        
        day_index = day - 1
        old_value = self._chains[chain_name][year][month][day_index]
        self._chains[chain_name][year][month][day_index] = new_value
        logging.info(f"Changed chain '{chain_name}' at {year}/{month}/{day} from '{old_value}' to '{new_value}'.")
        self._delete_chain_if_empty(chain_name, year, month)
        self._save_json()

    # Removes chain link lists that are all 0 and any empty year/month dictionaries.
    def _delete_chain_if_empty(self, chain_name, year, month):
        if max(self._chains[chain_name][year][month]) == 0:
            del self._chains[chain_name][year][month]
            if not self._chains[chain_name][year]:
                del self._chains[chain_name][year]

    # Try to check the value of the chain at the date. If it's missing, return 0.
    def get_chain(self, chain, year=None, month=None, day=None, date=None):
        year, month, day = h.format_date_ssi(year, month, day, date)

        try:
            return self._chains[chain][year][month][day-1]
        except (KeyError, IndexError):
            return 0

    # Return a list of all the chain links for a month. If it's not present in the json, return an empty list.
    def get_chain_month(self, chain_name, year, month):
        year = str(year)
        month = str(month)

        try:
            return self._chains[chain_name][year][month].copy()
        except KeyError:
            days = h.days_in_month(year, month)
            return [0] * days

    def delete_chain(self, chain_name):
        if chain_name in self._chain_order:
            self._chain_order.remove(chain_name)
            del self._chains[chain_name]
            self._chain_comments.pop(chain_name, None)
            logging.info(f"Deleted chain '{chain_name}'.")
            self._save_json()
        else:
            raise NameError(f"No chain '{chain_name}'")

    # Edit the comment for a chain at a date. 
    def edit_chain_comment(self, chain_name, new_comment, year=None, month=None, day=None, date=None):
        if new_comment == "" or new_comment.isspace():
            self.delete_chain_comment(self, chain_name, year, month, day, date)
        else:
            year, month, day = h.format_date_ssi(year, month, day, date)
            # Unlike _chains, _chains_comments uses strings for days because [chain_name][year][month] contains a 
            # dictionary instead of a list.
            day = str(day)
            
            if (chain_name not in self._chain_comments):
                self._chain_comments[chain_name] = {}
            if (year not in self._chain_comments[chain_name]):
                self._chain_comments[chain_name][year] = {}
            if (month not in self._chain_comments[chain_name][year]):
                self._chain_comments[chain_name][year][month] = {}
            old_comment = self.get_chain_comment(chain_name, year, month, day)
            self._chain_comments[chain_name][year][month][day] = new_comment
            logging.info(
                f"Changed chain '{chain_name}' comment at {year}/{month}/{day} from '{old_comment}' to '{new_comment}'.")
            self._save_json()
    
    # Delete the comment for a chain at a date. 
    def delete_chain_comment(self, chain_name, year=None, month=None, day=None, date=None):
        year, month, day = h.format_date_sss(year, month, day, date)
        # Unlike _chains, _chains_comments uses strings for days because [chain_name][year][month] contains a dictionary
        # instead of a list.

        try:
            old_comment = self.get_chain_comment(chain_name, year, month, day)
            del self._chain_comments[chain_name][year][month][day]
            logging.info(f"Deleted chain '{chain_name}' comment '{old_comment}' at {year}/{month}/{day}.")
            self._delete_chain_comment_dictionaries_if_empty(chain_name, year, month)
            self._save_json()
        except KeyError:
            logging.info(
                f"Tried to delete chain '{chain_name}' comment at {year}/{month}/{day} but there was no comment.")

    # Removes chain_comments dictionaries that are empty.
    def _delete_chain_comment_dictionaries_if_empty(self, chain_name, year, month):
        if not self._chain_comments[chain_name][year][month]:
            del self._chain_comments[chain_name][year][month]
            if not self._chain_comments[chain_name][year]:
                del self._chain_comments[chain_name][year]
                if not self._chain_comments[chain_name]:
                    del self._chain_comments[chain_name]

    # Return the comment for a chain at a date. If it's not present in the json, return None.
    def get_chain_comment(self, chain_name, year=None, month=None, day=None, date=None):
        year, month, day = h.format_date_sss(year, month, day, date)
        # Unlike _chains, _chains_comments uses strings for days because [chain_name][year][month] contains a dictionary 
        # instead of a list.

        try:
            return self._chain_comments[chain_name][year][month][day]
        except KeyError:
            return None


chain_handler = Chain_Handler()