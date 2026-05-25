from pathlib import Path
from config.default import DEFAULT_CONFIG
from config.validator import validate_config
import json
import copy
from typing import Any, Optional

CONFIG_FILE = Path("config/cli_config.json")

def create_config_file():
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    config = copy.deepcopy(DEFAULT_CONFIG)
    try:
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        source_directory = Path(config["source_directory"])
        source_directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise IOError(f"設定ファイルの生成に失敗しました: {e}")

def load_config() -> Optional[dict[str, Any]]:
    if not CONFIG_FILE.exists():
        print(f"設定ファイル ({CONFIG_FILE}) が見つかりません。")
        print("デフォルト設定でファイルを生成します...")
        create_config_file()
        print(f"[SUCCESS] 生成完了: {CONFIG_FILE}")
        print("内容を確認・編集してから再実行してください。")
        return None

    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            from config.errors import ConfigError
            raise ConfigError(f"JSON形式が正しくありません: {e}")

    validate_config(data)
    return data
