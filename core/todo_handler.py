from core.data_handler import Data_Handler


# Handles the to-do list.
class Todo_Handler(Data_Handler):
    def __init__(self, todo_json_path="data/todo.json"):
        super(Todo_Handler, self).__init__(
            "Todo", json_path=todo_json_path, default_data=[]
        )

    @property
    def todo_list(self):
        return self._data

    @todo_list.setter
    def todo_list(self, value):
        self._data = value

    # Returns an array of all todo items.
    def flat_item_list(self) -> [dict]:
        ret = []
        for item in self.todo_list:
            ret += item_to_list(item)
        return ret


def item_to_list(item: dict) -> [dict]:
    ret = [item]
    if "items" in item:
        for child_item in item["items"]:
            ret += item_to_list(child_item)
    return ret


def todo_item_is_completed(item: dict) -> bool:
    try:
        return item["completed"]
    except KeyError:
        return False


todo_handler = Todo_Handler()