import logging
import json
from pathlib import Path

import core.helpers as h


logging.getLogger().setLevel(logging.WARNING)

# Handles the to-do list.
class Todo_Handler():
    def __init__(self, todo_json_path="data/todo.json"):
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
        except:
            raise


todo_handler = Todo_Handler()