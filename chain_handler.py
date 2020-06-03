from json import loads as json_loads, dumps as json_dumps
from pathlib import Path

from helpers import format_date, days_in_month


class Chain_Handler():
    # Handles loading, saving, and getting chains.
    chains_json_path = Path("chains.json")

    def __init__(self):
        self.load_json()

    def load_json(self):
        if (self.chains_json_path.is_file()):
            with open(self.chains_json_path, 'r') as file:
                self.chains_json = json_loads(file.read())
                self.chains = self.chains_json["chains"]
                self.chain_order = self.chains_json["chain_order"]
                self.chain_comments = self.chains_json["chain_comments"]
        else:
            self.chains = {}
            self.chain_order = []
            self.chains_json = {
                "chain_order": self.chain_order, 
                "chains": self.chains, 
                "chain_comments": self.chain_comments}
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
    
    # Edits a chain at a given date. chain_name should be a string, new value should be 0 or 1 for incomplete or complete.
    def edit_chain(self, chain_name, new_value: int, year=None, month=None, day=None, date=None):
        year, month, day = format_date(year, month, day, date)
        
        # If missing dictionary keys for year and/or month, add them.
        if (year not in self.chains[chain_name]):
            self.chains[chain_name][year] = {}
        if (month not in self.chains[chain_name][year]):
            days = days_in_month(year, month)
            self.chains[chain_name][year][month] = [0] * days
        
        self.chains[chain_name][year][month][day-1] = new_value
        self.save_json()

    # Try to check the value of the chain at the date. If it's missing, return 0.
    def get_chain(self, chain, year=None, month=None, day=None, date=None):
        year, month, day = format_date(year, month, day, date)

        try:
            return self.chains[chain][year][month][day-1]
        except (KeyError, IndexError):
            return 0

    # Return a list of all the chain links for a month. If it's not present in the json, return an empty list.
    def get_chain_month(self, chain_name, year, month):
        year = str(year)
        month = str(month)

        try:
            return self.chains[chain_name][year][month].copy()
        except KeyError:
            days = days_in_month(year, month)
            return [0] * days

    # Edit the comment for a chain at a date. 
    def edit_chain_comment(self, chain_name, new_comment, year=None, month=None, day=None, date=None):
        if new_comment == "" or new_comment.isspace():
            self.delete_chain_comment(self, chain_name, year, month, day, date)
        else:
            year, month, day = format_date(year, month, day, date)
            # Unlike chains, chains_comments uses strings for days because [chain_name][year][month] contains a 
            # dictionary instead of a list.
            day = str(day)
            
            if (chain_name not in self.chain_comments):
                self.chain_comments[chain_name] = {}
            if (year not in self.chain_comments[chain_name]):
                self.chain_comments[chain_name][year] = {}
            if (month not in self.chain_comments[chain_name][year]):
                self.chain_comments[chain_name][year][month] = {}
            self.chain_comments[chain_name][year][month][day] = new_comment
            self.save_json()
    
    # Delete the comment for a chain at a date. 
    def delete_chain_comment(self, chain_name, year=None, month=None, day=None, date=None):
        year, month, day = format_date(year, month, day, date)
        # Unlike chains, chains_comments uses strings for days because [chain_name][year][month] contains a dictionary
        # instead of a list.
        day = str(day)

        try:
            del self.chain_comments[chain_name][year][month][day]
            self.save_json()
        except KeyError:
            pass

    # Return the comment for a chain at a date. If it's not present in the json, return None.
    def get_chain_comment(self, chain_name, year=None, month=None, day=None, date=None):
        year, month, day = format_date(year, month, day, date)
        # Unlike chains,chains_comments uses strings for days because [chain_name][year][month] contains a dictionary 
        # instead of a list.
        day = str(day)

        try:
            return self.chain_comments[chain_name][year][month][day]
        except KeyError:
            return None