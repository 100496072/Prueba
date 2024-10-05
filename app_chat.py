
from storage.json_store_chat import JsonStoreChat
from storage.json_store_relaciones import JsonStoreRelaciones
from storage.json_store_login import JsonStoreLogin
from app_relacion import AppRelacion


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
        man = JsonStoreChat()
        rel = JsonStoreRelaciones()
        users = JsonStoreLogin()
        checked_recipient = users.find_item(wanted_item=recipient, key="_username")

        relacionexiste = None
        for relacion in rel.data_list:
            if ((relacion["_username1"] == sender and relacion["_username2"] == checked_recipient) or
                    (relacion["_username1"] == checked_recipient and relacion["_username2"] == sender)):
                communication = cls(message, checked_recipient["_username"], sender)
                man.add_item(communication)
                relacionexiste = True


        if relacionexiste is False:
            AppRelacion.reg_relacion(sender, recipient)
            communication = cls(message, checked_recipient["_username"], sender)
            man.add_item(communication)
        return None