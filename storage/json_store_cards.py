from json_store import JsonStore
from app_config import JSON_FILES_PATH

class JsonStoreRegister(JsonStore):
    def __init__(self):
        super().__init__()