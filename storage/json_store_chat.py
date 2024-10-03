from json_store import JsonStore
from app_config import JSON_FILES_PATH

class JsonStoreRegister(JsonStore):
    def __init__(self):
        self._file_name = JSON_FILES_PATH + "messages.json"
        # Hay que ver qué errores queremos poner

    @property
    def data_list(self):
        return self._data_list
