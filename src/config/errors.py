class ConfigError(Exception):
    pass

class RuleError(ConfigError):
    pass

class ExtensionError(RuleError):
    pass

class DestinationError(RuleError):
    pass

class MoveError(Exception):
    pass