import re
from app_errors import AppError

class Attribute:
    def __init__(self):
        self._validation_pattern = r""
        self._error_message = ""
        self._attr_value = ""

    def _validate(self, attr_value):
        if not re.match(self._validation_pattern, attr_value):
            print(self._error_message)
            return False
        return attr_value

    @property
    def value(self):
        return self._attr_value

    @value.setter
    def value(self, attr_value):
        self._attr_value = self._validate(attr_value)