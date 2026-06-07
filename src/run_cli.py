from config.config_loader import load_config, create_config_file
from services.move_action import build_move_plan, build_undo_plan, execute_moves, save_latest_change, clear_history
from config.errors import AppError, ConfigError
from resources.text import TEXT


def user_confirm(prompt="\n実行しますか？ (y,yesで実行): "):
    confirm = input(prompt).lower().strip()
    return confirm in ["y", "yes"]

def display_plan(moves, title="Move Plan"):
    if not moves:
        return
    print(f"\n--- {title} ---")
    for move in moves:
        print(f'{move["src"].name} -> {move["dst"]}')

def startup():
    try:
        config = load_config()
        print(f"[SUCCESS] {TEXT['success']['load_config']}")
        return config
    except ConfigError as e:
        if e.key == "no_config_file":
            print(f"[INFO] {TEXT['error']['no_config_file'].format(**e.kwargs)}")
            print(f"[INFO] {TEXT['info']['create_default_config']}")
            try:
                create_config_file()
                print(f"[SUCCESS] {TEXT['info']['complete_create_config']}")
                print(f"[INFO] {TEXT['info']['check_config_and_rerun']}")
            except ConfigError as err:
                msg = TEXT['error'].get(err.key, err.key).format(**err.kwargs)
                print(f"[ERROR] {msg}")
            return None
        
        msg_template = TEXT['error'].get(e.key, e.key)
        print(f"[ERROR] {msg_template.format(**e.kwargs)}")
        return None


def main(command="move"):
    print(TEXT["title"]["main"])
    try:
        config = startup()
        if config is None:
            return

        if command == "move":
            planned_moves = build_move_plan(config)
            if not planned_moves:
                print(f"[INFO] {TEXT['info']['no_move_file']}")
                return
            
            if config.get("dry_run"):
                display_plan(planned_moves)
                if not user_confirm(TEXT['confirm']['move']):
                    print(f"[CANCEL] {TEXT['cancel']['move']}")
                    return
            
            execute_moves(planned_moves)
            save_latest_change(planned_moves)
            print(f"[SUCCESS] {TEXT['success']['move_complete'].format(count=len(planned_moves))}")

        elif command == "undo":
            undo_moves = build_undo_plan()
            if not undo_moves:
                print(f"[INFO] {TEXT['info']['no_undo_file']}")
                return
            
            display_plan(undo_moves, title="Undo Plan")
            if not user_confirm(TEXT['confirm']['undo']):
                print(f"[CANCEL] {TEXT['cancel']['undo']}")
                return
            
            execute_moves(undo_moves)
            clear_history()
            print(f"[SUCCESS] {TEXT['success']['undo_complete'].format(count=len(undo_moves))}")
        
        else:
            print(f"[ERROR] {TEXT['error']['invalid_command'].format(command=command)}")

    except AppError as e:
        print(f"[ERROR] {TEXT['error'][e.key].format(**e.kwargs)}")

if __name__ == "__main__":
    import sys
    command =(sys.argv[1]
                if len(sys.argv) > 1 
                else "move").lower()
    main(command)