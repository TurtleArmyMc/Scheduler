from json import loads as json_loads, dumps as json_dumps
from pathlib import Path

from helpers import format_date, days_in_month


# Handles loading, saving, and getting chains.
class Chain_Handler():
    _chains_json_path = Path("chains.json")

    def __init__(self):
        self._load_json()

    def _get_chains_dict(self):
        return {
                "chain_order": self._chain_order, 
                "chains": self._chains, 
                "chain_comments": self._chain_comments
                }
    
    def _load_json(self):
        if (self._chains_json_path.is_file()):
            with open(self._chains_json_path, 'r') as file:
                chains_dict = json_loads(file.read())
                self._chains = chains_dict["chains"]
                self._chain_order = chains_dict["chain_order"]
                self._chain_comments = chains_dict["chain_comments"]
        else:
            self._chains = {}
            self._chain_order = []
            self._chain_comments = {}
            self._save_json()

    def _save_json(self):
        try:
            chains_dict = self._get_chains_dict()
            serialized_json = json_dumps(chains_dict, indent=1)
            with open(self._chains_json_path, 'w') as file:
                file.write(serialized_json)
        except:
            raise

    def create_new_chain(self, chain_name):
        self._chains[chain_name] = {}
        self._chain_order.append(chain_name)
        self._save_json()
    
    def get_chain_order(self):
        return self._chain_order.copy()

    def edit_chain_order(self, new_order):
        # Check to see that the new order contains the same chains.
        if new_order.copy().sort() == self.get_chain_order().sort():
            self._chain_order = new_order.copy()
            self._save_json()
        else:
            raise SyntaxError("New chain order must contain the same names as the old order.")
    
    # Edits a chain at a given date. chain_name should be a string, new value should be 0 or 1 for incomplete or complete.
    def edit_chain(self, chain_name, new_value: int, year=None, month=None, day=None, date=None):
        year, month, day = format_date(year, month, day, date)
        
        # If missing dictionary keys for year and/or month, add them.
        if (year not in self._chains[chain_name]):
            self._chains[chain_name][year] = {}
        if (month not in self._chains[chain_name][year]):
            days = days_in_month(year, month)
            self._chains[chain_name][year][month] = [0] * days
        
        self._chains[chain_name][year][month][day-1] = new_value
        self._save_json()

    # Try to check the value of the chain at the date. If it's missing, return 0.
    def get_chain(self, chain, year=None, month=None, day=None, date=None):
        year, month, day = format_date(year, month, day, date)

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
            days = days_in_month(year, month)
            return [0] * days

    def delete_chain(self, chain_name):
        if chain_name in self._chain_order:
            self._chain_order.remove(chain_name)
            self._chains.pop(chain_name)
            self._chain_comments.pop(chain_name, None)
            self._save_json()
        else:
            raise NameError(f"No chain '{chain_name}'")

    # Edit the comment for a chain at a date. 
    def edit_chain_comment(self, chain_name, new_comment, year=None, month=None, day=None, date=None):
        if new_comment == "" or new_comment.isspace():
            self.delete_chain_comment(self, chain_name, year, month, day, date)
        else:
            year, month, day = format_date(year, month, day, date)
            # Unlike chains, chains_comments uses strings for days because [chain_name][year][month] contains a 
            # dictionary instead of a list.
            day = str(day)
            
            if (chain_name not in self._chain_comments):
                self._chain_comments[chain_name] = {}
            if (year not in self._chain_comments[chain_name]):
                self._chain_comments[chain_name][year] = {}
            if (month not in self._chain_comments[chain_name][year]):
                self._chain_comments[chain_name][year][month] = {}
            self._chain_comments[chain_name][year][month][day] = new_comment
            self._save_json()
    
    # Delete the comment for a chain at a date. 
    def delete_chain_comment(self, chain_name, year=None, month=None, day=None, date=None):
        year, month, day = format_date(year, month, day, date)
        # Unlike chains, chains_comments uses strings for days because [chain_name][year][month] contains a dictionary
        # instead of a list.
        day = str(day)

        try:
            del self._chain_comments[chain_name][year][month][day]
            self._save_json()
        except KeyError:
            pass

    # Return the comment for a chain at a date. If it's not present in the json, return None.
    def get_chain_comment(self, chain_name, year=None, month=None, day=None, date=None):
        year, month, day = format_date(year, month, day, date)
        # Unlike chains,chains_comments uses strings for days because [chain_name][year][month] contains a dictionary 
        # instead of a list.
        day = str(day)

        try:
            return self._chain_comments[chain_name][year][month][day]
        except KeyError:
            return None