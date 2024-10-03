from storage.json_store import JsonStore
from app_config import JSON_FILES_PATH

class JsonStoreRegister(JsonStore):
    def __init__(self):
        self._data_list = []
        print(self._data_list)
        self._file_name = JSON_FILES_PATH + "users.json"
        self.load_storage(self._file_name)
        print(self._data_list)
        # Hay que ver qué errores queremos poner

    @property
    def data_list(self):
        return self._data_list
