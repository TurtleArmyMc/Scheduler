import json
import logging
from pathlib import Path
from copy import deepcopy
from datetime import datetime

from core.helpers import Event


logging.basicConfig()


class Data_Handler():
    def __init__(self, name:str, json_path:str, backup_dir_path:str=None, default_data={},
    logging_level:int=logging.WARN):
        self._json_path = Path(json_path)
        if backup_dir_path is None:
            self._backup_dir_path = self._json_path.parent / "backups"
        else:
            self._backup_dir_path = Path(backup_dir_path)

        self._default_data = default_data
        self.update_event = Event()
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging_level)

        self._load_json()

    def _get_data_json(self):
        return self._data

    def _load_json(self, path=None):
        try:
            if path is None:
                path = self._json_path
            if (path.is_file()):
                with open(path, 'r') as file:
                    self._data = json.loads(file.read())
                    self._logger.info(f"Loaded data from '{path}'.")
            else:
                self._data = deepcopy(self._default_data)
                self.save_json()
        except Exception as e:
            self._logger.error(f"Error loading data from {path}", exc_info=e)
            raise e


    def save_json(self, path=None):
        if path is None:
            path = self._json_path
        try:
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch(exist_ok=True)
                self._logger.info(f"Created path '{path}'.")

            with open(path, 'w') as file:
                serialized_json = json.dumps(self._data, indent=1)
                file.write(serialized_json)
                self._logger.info(f"Saved data to '{path}'.")
            self.update_event.call()
        except Exception as e:
            self._logger.error(f"Error saving data to {path}", exc_info=e)
            raise e

    def _backup_json(self, path=None):
        if path is None:
            now = datetime.now().replace(tzinfo=None, microsecond=0).isoformat().replace(":", ".")
            path = self._backup_dir_path / f"{now}_{self._json_path.name}"
        self.save_json(path)