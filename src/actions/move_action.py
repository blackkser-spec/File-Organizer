import shutil
import json
from pathlib import Path
from config.errors import MoveError

LATEST_CHANGE_FILE = Path("data/latest_change.json")

def get_destination(item, rules):
    item_suffix = item.suffix.lower()
    for rule in rules:
        if item_suffix == str(rule.get("extension", "")).lower():
            return rule.get("destination")
    return None

def display_plan(moves, title="Move Plan"):
    if not moves:
        return
    print(f"\n--- {title} ---")
    for move in moves:
        print(f'{move["src"].name} -> {move["dst"]}')

def execute_moves(planned_moves):
    for move in planned_moves:
        try:
            move["dst"].parent.mkdir(parents=True, exist_ok=True)
            shutil.move(move["src"], move["dst"])
        except Exception as e:
            raise MoveError(f"Failed to move {move['src']} -> {move['dst']}") from e
    print(f"[SUCCESS] Moved {len(planned_moves)} files")

def save_latest_change(planned_moves):
    save_data = []
    LATEST_CHANGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    for data in planned_moves:
        save_data.append({"src": str(data["src"]), "dst": str(data["dst"])})

    with LATEST_CHANGE_FILE.open("w", encoding="utf-8")as f:
        json.dump(save_data, f, indent=4, ensure_ascii=False)

def clear_history():
    try:
        if LATEST_CHANGE_FILE.exists():
            LATEST_CHANGE_FILE.unlink()
    except Exception as e:
        raise MoveError(f"履歴ファイルの削除に失敗しました: {e}")

def build_move_plan(config):
    source_directory = config.get("source_directory")
    rules = config.get("rules")
    planned_moves = []

    source_path = Path(source_directory)

    for item in source_path.iterdir():
        if not item.is_file():
            continue

        destination = get_destination(item, rules)
        if not destination:
            continue

        destination_path = source_path / destination
        move_info = {"src": item, "dst": destination_path / item.name}
        planned_moves.append(move_info)

    return planned_moves
    
def build_undo_plan():
    if not LATEST_CHANGE_FILE.exists():
        return []

    with LATEST_CHANGE_FILE.open("r", encoding="utf-8") as f:
        history = json.load(f)

    if not history:
        return []

    undo_moves = []

    for move in history:
        undo_moves.append({"src": Path(move["dst"]), "dst": Path(move["src"])})
    
    return undo_moves