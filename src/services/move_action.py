import shutil
import json
from pathlib import Path
from config.errors import MoveError

LATEST_CHANGE_FILE = Path("data/latest_change.json")

def get_destination(item, rules):
    item_suffix = item.suffix.lower()
    
    for rule in rules or []:
        if item_suffix == str(rule.get("extension", "")).lower():
            return rule.get("destination")
        
    return item_suffix.lstrip(".") or None

def execute_moves(planned_moves):
    for move in planned_moves:
        try:
            move["dst"].parent.mkdir(parents=True, exist_ok=True)
            shutil.move(move["src"], move["dst"])
        except Exception as e:
            raise MoveError("move_failed", src=move["src"], dst=move["dst"]) from e

def commit_move_plan(planned_moves):
    execute_moves(planned_moves)
    save_latest_change(planned_moves)

def commit_undo_plan(undo_moves):
    execute_moves(undo_moves)
    clear_history()

def save_latest_change(planned_moves):
    try:
        save_data = []
        LATEST_CHANGE_FILE.parent.mkdir(parents=True, exist_ok=True)

        for data in planned_moves:
            save_data.append({"src": str(data["src"]), "dst": str(data["dst"])})

        with LATEST_CHANGE_FILE.open("w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise MoveError("save_history_failed", error=e)

def clear_history():
    if not LATEST_CHANGE_FILE.exists():
        return
    try:    
        LATEST_CHANGE_FILE.unlink()
    except Exception as e:
        raise MoveError("delete_history_failed", error=e)

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

    try:
        with LATEST_CHANGE_FILE.open("r", encoding="utf-8") as f:
            history = json.load(f)

        if not history:
            return []

        undo_moves = []

        for move in history:
            undo_moves.append({"src": Path(move["dst"]), "dst": Path(move["src"])})
        
        return undo_moves
    except Exception as e:
        raise MoveError("read_history_failed", error=e)