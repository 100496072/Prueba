from attributes.attribute import Attribute

class AttributePwd(Attribute):
    def __init__(self, attr_value):
        self._validation_pattern = r"^[a-zA-Z0-9]{5,10}$"
        self._error_message = "Contraseña no válido"
        self._attr_value = self._validate(attr_value)