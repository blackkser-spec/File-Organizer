from pathlib import Path
import json
import copy
from config.default import DEFAULT_CONFIG
from config.validator import validate_config
from config.errors import ConfigError
from typing import Any

CONFIG_FILE = Path("config/config.json")

def create_config_file():
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    config = copy.deepcopy(DEFAULT_CONFIG)
    try:
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        source_directory = Path(config["source_directory"])
        source_directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise ConfigError("generate_config_failed", error=str(e))

def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        raise ConfigError("no_config_file", CONFIG_FILE=CONFIG_FILE)
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError("invalid_config", error=str(e))
    except OSError as e:
        raise ConfigError("read_config_failed", error=str(e))

    validate_config(data)
    return data
