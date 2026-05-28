import shutil
from pathlib import Path

def check_destination(item, rules):
    item_suffix = item.suffix.lower()
    for rule in rules:
        if item_suffix == rule.get("extension", "").lower():
            return rule.get("destination")
    return None

def execute_move(item, destination_path):
    destination_path.mkdir(parents=True, exist_ok=True)
    shutil.move(item, destination_path / item.name) 

def move_flow(config):
    source_directory = config.get("source_directory")
    dry_run = config.get("dry_run")
    rules = config.get("rules")
    planned_moves = []

    source_path = Path(source_directory)

    for item in source_path.iterdir():
        if not item.is_file():
            continue

        destination = check_destination(item, rules)
        if not destination:
            continue

        destination_path = source_path / destination
        
        if dry_run:
            planned_moves.append((item, destination_path))
        else:
            execute_move(item, destination_path)

    if dry_run:
        if not planned_moves:
            print("[INFO] 移動対象ファイルがありません。")
            return
        else:
            print("\n--- Move Plan (Dry Run) ---")
            for src, dst in planned_moves:
                print(f"{src.name} -> {dst}")
            
            confirm = input("\n上記の内容で実行しますか？ (y, yesで実行): ").lower().strip()
            if confirm in ["y", "yes"]:
                for src, dst in planned_moves:
                    execute_move(src, dst)
                print("[SUCCESS] ファイルの移動が完了しました。")
            else:
                print("[CANCEL] 移動をキャンセルしました。")
