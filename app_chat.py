
from storage.json_store_chat import JsonStoreChat
from storage.json_store_login import JsonStoreLogin

class AppChat:
    def __init__(self, message, recipient, sender):
        self._message = message
        self._recipient = recipient
        self._sender = sender
    @property
    def message(self):
        return self._message

    @property
    def recipient(self):
        return self._recipient

    @property
    def sender(self):
        return self._sender

    @classmethod
    def send_message(cls, message, recipient, sender):
        users = JsonStoreLogin()
        checked_recipient = users.find_item(wanted_item=recipient, key= "_username")
        communication = cls(message, checked_recipient["_username"], sender)
        man = JsonStoreChat()
        man.add_item(communication)
        return None