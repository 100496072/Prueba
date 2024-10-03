from attribute import Attribute

class AttributeUser(Attribute):
    def __init__(self, attr_value):
        self._validation_pattern = r""
        self._error_message = "User no válido"
        self._attr_value = self._validate(attr_value)