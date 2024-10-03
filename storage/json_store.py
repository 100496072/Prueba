import json


from app_errors import AppError


class JsonStore:
    def __init__(self):
        self._data_list = []
        self._file_name = ""
        self.load_storage(self._file_name)

    def load_storage(self, file_store):
        """Método para cargar datos"""
        try:
            with open(file_store, "r", encoding="utf-8", newline="") as file:
                self._data_list = json.load(file)
        except FileNotFoundError:
            self._data_list = []
        except json.decoder.JSONDecodeError as exception:
            raise AppError("JSON Decode Error - Wrong JSON format")
        return self._data_list

    def add_item(self, new_item):
        """Método add_item"""
        self.load_storage(self._file_name)
        self._data_list.append(new_item.__dict__)
        self.save_store()

    def save_store(self):
        try:
            with open(self._file_name, "w", encoding="utf-8", newline="") as file:
                json.dump(self._data_list, file, indent=2)
        except FileNotFoundError as exception:
            raise AppError("File Not Found") from exception


    def find_item(self, wanted_item, key):
        self.load_storage(self._file_name)
        for user_data in self._data_list:
            print(user_data)
            if wanted_item == user_data[key]:
                return "Usuario encontrado"
        return None

    def read_file_store(self):
        try:
            with open(self._file_name, "r", encoding="utf-8", newline="") as file:
                self._data_list = json.load(file)
        except FileNotFoundError as exception:
            raise AppError("File Not Found") from exception
        except json.decoder.JSONDecodeError as exception:
            raise AppError("JSON Decode Error - Wrong JSON format") from exception
        return self._data_list

    def delete_item(self, wanted_user):
        self.load_storage(self._file_name)
        for user_data in self._data_list:
            if wanted_user == user_data["user"]:
                self._data_list.remove(user_data)
                self.save_store()
        return None

    @property
    def data_list(self):
        return self._data_list