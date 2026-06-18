import os
from services.move_action import build_move_plan, commit_move_plan, build_undo_plan, commit_undo_plan
from resources.texts.text import TEXT

class OrganizerController:
    def __init__(self, view, config_data):
        self.view = view
        self.config_data = config_data
        self.planned_moves = []

    def select_source_directory(self):
        new_dir = self.view.ask_directory()
        if new_dir:
            self.config_data["source_directory"] = new_dir
            self.scan()

    def scan(self):
        if not self.config_data:
            return
        
        self.view.clear_preview()
        self.view.update_path_label(self.config_data.get("source_directory", "Not Selected"))
        self.planned_moves = build_move_plan(self.config_data)
        
        if not self.planned_moves:
            self.view.update_status("Status: No files found")
            return
            
        # 拡張子ごとの出現件数を集計
        extension_counts = {}
        for move in self.planned_moves:
            extension_key = move["src"].suffix.lower() or "(no ext)"
            extension_counts[extension_key] = extension_counts.get(extension_key, 0) + 1
        
        # UIのチェックボックスを更新
        self.view.update_extension_filters(extension_counts)
        self.view.update_preview_table(self.planned_moves)
        self.view.update_status(f"Status: {len(self.planned_moves)} files found.")

    def execute_move(self):
        if not self.planned_moves:
            self.view.update_status("Status: Nothing to move")
            return
        
        # チェックされている拡張子のみをフィルタリング
        selected_extensions = self.view.get_active_extensions()
        filtered_moves = [
            move_plan for move_plan in self.planned_moves 
            if (move_plan["src"].suffix.lower() or "(no ext)") in selected_extensions
        ]

        if not filtered_moves:
            self.view.update_status("Status: No files selected by filter")
            return

        if not self.view.ask_yes_no("確認", f"{len(filtered_moves)} 件のファイルの移動を実行しますか？"):
            return

        commit_move_plan(filtered_moves)
        self.scan()
        self.view.update_status("Status: Move Completed")

    def open_config_editor(self):
        # 設定ファイルのパス（config/config.yaml）を特定してOS標準のエディタで開く
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_path, "config", "config.yaml")
        if os.path.exists(config_path):
            os.startfile(config_path) # Windows環境で既定のアプリで開く
        else:
            self.view.update_status("Status: Config file not found")

    def undo(self):
        undo_moves = build_undo_plan()
        if not undo_moves:
            self.view.update_status("Status: No undo history found")
            return
        
        if not self.view.ask_yes_no("Undo確認", "前回の移動操作を元に戻しますか？"):
            return

        commit_undo_plan(undo_moves)
        self.scan()
        self.view.update_status("Status: Undo Completed")