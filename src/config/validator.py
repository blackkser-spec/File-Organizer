from typing import Any
from config.errors import ConfigError, RuleError, DestinationError, ExtensionError

def validate_config(config: dict[str, Any]):
    if "source_directory" not in config:
        raise ConfigError("source_directory is required")

    if "rules" not in config:
        raise ConfigError("rules is required")
    
    rules = config.get("rules")
    
    if not isinstance(rules, list):
        raise RuleError("rules must be a list")
    
    for rule in rules:
        validate_rule(rule)

def validate_rule(rule: dict[str, Any]):
    extension = rule.get("extension")
    destination = rule.get("destination")
    if not isinstance(extension, str):
        raise ExtensionError("extension must be str")
    if not extension.startswith("."):
        raise ExtensionError("extension must start with a dot")
    if not destination:
        raise DestinationError("destination is required")