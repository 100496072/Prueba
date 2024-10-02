"""Errores customizados para la app"""
class AppError(Exception):
    def __init__(self, message):
        self._message = message
        super().__init__(self.message)

    @property
    def message(self):
        """Get error message (getter)"""
        return self._message

    @message.setter
    def message(self, message):
        """Set error message (setter)"""
        self._message = message