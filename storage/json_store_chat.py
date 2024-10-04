from storage.json_store import JsonStore
from app_config import JSON_FILES_PATH

class JsonStoreChat(JsonStore):
    def __init__(self):
        super().__init__()
        self._file_name = JSON_FILES_PATH + "messages.json"
        self.load_storage(self._file_name)
        # Hay que ver qué errores queremos poner

    @property
    def data_list(self):
        return self._data_list
