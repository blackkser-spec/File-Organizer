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
        
        self.view.clear_log()
        self.view.update_path_label(self.config_data.get("source_directory", "Not Selected"))
        self.planned_moves = build_move_plan(self.config_data)
        
        if not self.planned_moves:
            self.view.update_status("Status: No files found")
            return
            
        self.view.update_preview_table(self.planned_moves)
        
        self.view.update_status(f"Status: {len(self.planned_moves)} files found.")

    def execute_move(self):
        if not self.planned_moves:
            self.view.update_status("Status: Nothing to move")
            return
        
        if not self.view.ask_yes_no("確認", "ファイルの移動を実行しますか？"):
            return

        commit_move_plan(self.planned_moves)
        self.scan()
        self.view.update_status("Status: Move Completed")

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