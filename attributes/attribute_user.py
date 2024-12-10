from attributes.attribute import Attribute

class AttributeUser(Attribute):
    def __init__(self, attr_value):
        self._validation_pattern = r"^[a-zA-Z0-9]{5,10}$"
        self._error_message = "Usuario no válido"
        self._attr_value = self._validate(attr_value)


class AttributeMensaje(Attribute):
    def __init__(self, attr_value):
        # Actualización de la expresión regular
        self._validation_pattern = r"^[a-zA-Z0-9.,: ]{0,200}$"
        self._error_message = "Mensaje con caracteres no permitidos"
        self._attr_value = self._validate(attr_value)

class AttributeDatos(Attribute):
    def __init__(self, attr_value):
        self._validation_pattern = r"^[a-zA-Z]{2,20}$"
        self._error_message = "Pais o Ciudad no permitido"
        self._attr_value = self._validate(attr_value)

class AttributeCodigo(Attribute):
    def __init__(self, attr_value):
        self._validation_pattern = r"^[0-9]{2,20}$"
        self._error_message = "Codigo no permitido"
        self._attr_value = self._validate(attr_value)