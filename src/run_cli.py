from config.config_loader import load_config
from actions.move_action import build_move_plan, build_undo_plan, execute_moves, save_latest_change, clear_history, display_plan
from config.errors import ConfigError, MoveError


def user_confirm(prompt="\n実行しますか？ (y,yesで実行): "):
    confirm = input(prompt).lower().strip()
    return confirm in ["y", "yes"]


def main(command="move"):
    print("---File Organizer---")
    
    try:
        config = load_config()
        if config is None:
            # 初回生成時はここで終了
            return
        print("CONFIGファイルの読み込み成功。")

    except ConfigError as e:
        print(f"[Config Error] {e}")
        return
    except Exception as e:
        print(f"[Unexpected Error] {e}")
        return
    if command == "move":
        try:
            planned_moves = build_move_plan(config)
            if not planned_moves:
                print("[INFO] 移動対象ファイルがありません。")
                return
            
            if config.get("dry_run"):
                display_plan(planned_moves)
                if not user_confirm():
                    print("[CANCEL] 移動を中断しました。")
                    return
            
            execute_moves(planned_moves)
            save_latest_change(planned_moves)

        except MoveError as e:
            print(f"[Move Error] {e}")
            return
    elif command == "undo":
        try:
            undo_moves = build_undo_plan()
            if not undo_moves:
                print("[INFO] 復元可能な履歴が見つかりません。")
                return
            
            display_plan(undo_moves, title="Undo Plan")
            if not user_confirm("Undoを実行しますか？ (y/n): "):
                print("[CANCEL] Undoを中断しました。")
                return
            
            execute_moves(undo_moves)
            clear_history()
            print("[INFO] Undoが完了し、履歴をクリアしました。")

        except MoveError as e:
            print(f"[Undo Error] {e}")
            return


if __name__ == "__main__":
    import sys
    command =(sys.argv[1]
                if len(sys.argv) > 1 
                else "move").lower()
    main(command)