class AppError(Exception):
    def __init__(self, key, **kwargs):
        super().__init__(key)
        self.key = key
        self.kwargs = kwargs

class ConfigError(AppError):
    pass

class RuleError(ConfigError):
    pass

class ExtensionError(RuleError):
    pass

class DestinationError(RuleError):
    pass

class MoveError(AppError):
    pass