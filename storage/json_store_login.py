from storage.json_store import JsonStore
from app_config import JSON_FILES_PATH

class JsonStoreLogin(JsonStore):
    def __init__(self):
        super().__init__()
        self._file_name = JSON_FILES_PATH + "users.json"
        # Hay que ver qué errores queremos poner

    @property
    def data_list(self):
        return self._data_list

    def find_item(self, wanted_item, key):
        self.load_storage(self._file_name)
        for user_data in self._data_list:
            print(user_data)
            if wanted_item == user_data[key]:
                return user_data
        return 'Credenciales incorrectas'
