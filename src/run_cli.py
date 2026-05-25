import json
import copy
from pathlib import Path
from config.default import DEFAULT_CONFIG

CONFIG_FILE = Path("cli_config.json")

def create_config_file():
    config = copy.deepcopy(DEFAULT_CONFIG)
    try:
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"[SUCCESS] 設定ファイルを生成しました: {CONFIG_FILE}")
        print("[SUCCESS] 内容を確認して再実行してください。")
        return
    except Exception as e:
        print(f"[ERROR] 設定ファイルの生成に失敗しました: {e}")

def main():
    print("---File Organizer---")
    # 設定ファイルが存在するか確認
    if not CONFIG_FILE.exists():
        print(f"設定ファイル ({CONFIG_FILE}) が見つかりません。")
        print("設定ファイルを規定値で生成します")
        create_config_file()
    else:
        print(f"設定ファイル ({CONFIG_FILE}) を読み込みます。")
        # ここで読み込み処理や移動ロジックの呼び出しを今後追加します
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = json.load(f)
            print(f"現在の対象ディレクトリ: {config.get('source_directory')}")

if __name__ == "__main__":
    main()