from typing import Any
from pathlib import Path
from config.errors import ConfigError, RuleError, DestinationError, ExtensionError

def validate_config(config: dict[str, Any]):
    source_directory = config.get("source_directory")
    if not source_directory:
        raise ConfigError("source_directory is required")
    
    source_path = Path(source_directory)
    if not source_path.exists():
        raise ConfigError(f"source_directory {source_directory} does not exist")
    if not source_path.is_dir():
        raise ConfigError(f"source_directory {source_directory} is not a directory")
    
    rules = config.get("rules")
    if not rules:
        raise ConfigError("rules is required")
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
    if not isinstance(destination, str):
        raise DestinationError("destination must be str")