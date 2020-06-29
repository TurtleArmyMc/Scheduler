import logging
import json
from pathlib import Path

import core.helpers as h
from core.event import Event


logging.getLogger().setLevel(logging.WARNING)

# Handles the to-do list.
class Todo_Handler():
    def __init__(self, todo_json_path="data/todo.json"):
        self.todolist_update_event = Event()
        self._todo_json_path = Path(todo_json_path)
        self._load_json()

    def _load_json(self):
        if (self._todo_json_path.is_file()):
            with open(self._todo_json_path, 'r') as file:
                self.todo_list = json.loads(file.read())
                logging.info(f"Loaded todo data from '{self._todo_json_path}'.")
        else:
            self.todo_list = []
            self.save_json()

    def save_json(self):
        try:
            serialized_json = json.dumps(self.todo_list, indent=1)
            with open(self._todo_json_path, 'w') as file:
                file.write(serialized_json)
                logging.info(f"Saved todo data to '{self._todo_json_path}'.")
            self.todolist_update_event.call()
        except:
            raise

    # Returns an array of all todo items. 
    def flat_item_list(self):
        ret = []
        for item in self.todo_list:
            ret += self._item_to_list(item)
        return ret

    def _item_to_list(self, item):
        ret = [item]
        if "items" in item:
            for child_item in item["items"]:
                ret += self._item_to_list(child_item)
        return ret


todo_handler = Todo_Handler()