from attributes.attribute import Attribute

class AttributeUser(Attribute):
    def __init__(self, attr_value):
        self._validation_pattern = r"^[a-zA-Z]{5,10}$"
        self._error_message = "User no válido"
        self._attr_value = self._validate(attr_value)