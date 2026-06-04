from typing import Any
from pathlib import Path
from config.errors import ConfigError, RuleError, DestinationError, ExtensionError

def validate_config(config: dict[str, Any]):
    _validate_source_directory(config)
    _validate_dry_run(config)
    _validate_rules_list(config)

def _validate_source_directory(config: dict[str, Any]):
    source_directory = config.get("source_directory")
    if not source_directory:
        raise ConfigError("source_directory_required")

    source_path = Path(source_directory)
    if not source_path.exists():
        raise ConfigError("source_dir_not_exist", source_directory=source_directory)
    if not source_path.is_dir():
        raise ConfigError("source_dir_not_dir", source_directory=source_directory)

def _validate_dry_run(config: dict[str, Any]):
    dry_run = config.get("dry_run")
    if dry_run is not None and not isinstance(dry_run, bool):
        raise ConfigError("dry_run_not_bool")

def _validate_rules_list(config: dict[str, Any]):
    rules = config.get("rules")
    if rules is None:
        raise ConfigError("rules_not_exist")
    if not isinstance(rules, list):
        raise RuleError("rules_not_list")

    for rule in rules:
        _validate_single_rule(rule)

def _validate_single_rule(rule: dict[str, Any]):
    extension = rule.get("extension")
    destination = rule.get("destination")
    
    if not isinstance(extension, str):
        raise ExtensionError("extension_not_str")
    if not extension.startswith("."):
        raise ExtensionError("extension_must_start_with_dot")
    if destination is None:
        raise DestinationError("destination_required")
    if not isinstance(destination, str):
        raise DestinationError("destination_not_str")