from services.move_action import build_move_plan, commit_move_plan, build_undo_plan, commit_undo_plan
from config.config_loader import save_config
from resources.texts.text import TEXT
from gui.config_window import ConfigWindow
import logging

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
        self.view.update_path_label(self.config_data.get("source_directory", TEXT["gui"]["path_label_default"]))
        self.planned_moves = build_move_plan(self.config_data)
        
        if not self.planned_moves:
            self.view.update_move_item_count(0, 0)
            self.view.update_status(TEXT["gui"]["footer_status_nothing_scaned_file"])
            return
            
        # 拡張子ごとの出現件数を集計
        extension_counts = {}
        for move in self.planned_moves:
            extension_key = move["src"].suffix.lower() or "(no ext)"
            extension_counts[extension_key] = extension_counts.get(extension_key, 0) + 1
        
        # UIのチェックボックスを更新
        self.view.update_extension_filters(extension_counts)
        self.refresh_preview()

    def execute_move(self):
        if not self.planned_moves:
            return
        
        filtered_moves = self.get_filtered_moves()

        if not filtered_moves:
            self.view.update_status(TEXT["gui"]["footer_status_no_files_selected"])
            return

        if not self.view.ask_yes_no(TEXT["gui"]["dialog_title_confirm"],
                                    TEXT["gui"]["dialog_move_confirm"].format(count=len(filtered_moves))):
            return

        commit_move_plan(filtered_moves)
        self.scan()
        self.view.update_status(TEXT["gui"]["footer_status_move_complate"])

    def get_filtered_moves(self):
        selected_extensions = self.view.get_active_extensions()
        return [
            move
            for move in self.planned_moves
            if (move["src"].suffix.lower() or "(no ext)") in selected_extensions
        ]
    
    def refresh_preview(self):
        filtered_moves = self.get_filtered_moves()
        # プレビュー一覧を更新
        self.view.update_preview_table(self.planned_moves)
        # フッターの件数表示を更新
        self.view.update_move_item_count(
            len(filtered_moves),
            len(self.planned_moves),
        )

    def open_config_editor(self):
        ConfigWindow(self.view, self.config_data, self._save_config_to_file)

    def _save_config_to_file(self, updated_config):
        try:
            # 元のデータの参照を維持したまま中身を置き換える
            self.config_data.clear()
            self.config_data.update(updated_config)
            save_config(self.config_data)
            self.view.update_status(TEXT["gui"]["footer_status_config_saved"])
            self.scan()  # 新しいルールに基づいてプレビューを更新
        except Exception as e:
            logging.exception(f"設定保存に失敗しました- {str(e)}")
            self.view.update_status(TEXT["gui"]["footer_status_config_save_failed"])

    def execute_undo(self):
        undo_moves = build_undo_plan()
        if not undo_moves:
            self.view.update_status(TEXT["gui"]["footer_status_nothing_undo_file"])
            return
        
        if not self.view.ask_yes_no(TEXT["gui"]["dialog_title_confirm"], TEXT["gui"]["dialog_undo_confirm"]):
            return

        commit_undo_plan(undo_moves)
        self.scan()
        self.view.update_status(TEXT["gui"]["footer_status_undo_complete"])

    def execute_refresh(self):
        self.scan()
        self.view.update_status(TEXT["gui"]["footer_status_refresh_complete"])