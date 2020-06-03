from json import loads as json_loads, dumps as json_dumps
from pathlib import Path

from helpers import format_date, days_in_month


class Chain_Handler():
    # Handles loading, saving, getting and saving chains.
    chains_json_path = Path("chains.json")

    def __init__(self):
        self.load_json()

    def load_json(self):
        if (self.chains_json_path.is_file()):
            with open(self.chains_json_path, 'r') as file:
                self.chains_json = json_loads(file.read())
                self.chains = self.chains_json["chains"]
                self.chain_order = self.chains_json["chain_order"]
        else:
            self.chains = {}
            self.chain_order = []
            self.chains_json = {"chain_order": self.chain_order, "chains": self.chains}
            self.save_json()

    def save_json(self):
        try:
            serialized_json = json_dumps(self.chains_json, indent=1)
            with open(self.chains_json_path, 'w') as file:
                file.write(serialized_json)
        except:
            raise

    def new_chain(self, chain_name):
        self.chains[chain_name] = {}
        self.chain_order.append(chain_name)
        self.save_json()
    
    def edit_chain(self, chain_name, new_value: int, year=None, month=None, day=None, date=None):
        # Edits a chain at a given date. Chain should be a string, new value should be 0 or 1 for incomplete or complete.
        year, month, day = format_date(year, month, day, date)
        
        # If missing dictionary keys for year and/or month, add them.
        if (year not in self.chains[chain_name]):
            self.chains[chain_name][year] = {}
        if (month not in self.chains[chain_name][year]):
            days = days_in_month(year, month)
            self.chains[chain_name][year][month] = [0] * days
        
        self.chains[chain_name][year][month][day-1] = new_value
        self.save_json()

    def get_chain(self, chain, year=None, month=None, day=None, date=None):
        # Try to check the value of the chain at the date. If it's missing, return 0.
        year, month, day = format_date(year, month, day, date)

        try:
            return self.chains[chain][year][month][day-1]
        except (KeyError, IndexError):
            return 0

    def get_chain_month(self, chain_name, year, month):
        # Return a list of all the chain links for a month. If it's not present in the json, return an empty list.
        year = str(year)
        month = str(month)

        try:
            return self.chains[chain_name][year][month].copy()
        except (KeyError):
            days = days_in_month(year, month)
            return [0] * days