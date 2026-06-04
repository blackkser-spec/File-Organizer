TEXT = {
    "title": {
        "main": "--- File Organizer ---"
    },
    "info": {
        "no_move_file": "移動対象のファイルが見つかりません。",
        "no_undo_file": "復元可能な履歴が見つかりません。",
        "create_default_config": "デフォルト設定でファイルを生成します。",
        "complete_create_config": "設定ファイルの生成が完了しました。",
        "check_config_and_rerun": "設定ファイルを確認し、再度実行してください。",
    },
    "success": {
        "load_config": "設定ファイルの読み込みに成功しました。",
        "move_complete": "{count} 個のファイルを移動しました。",
        "undo_complete": "{count} 個のファイルをUndoし、履歴をクリアしました。",
    },
    "confirm": {
        "move": "実行しますか？ (y,yesで実行): ",
        "undo": "Undoを実行しますか？ (y,yesで実行): ",
    },
    "cancel": {
        "move": "移動を中断しました。",
        "undo": "Undoを中断しました。",
    },
    "error": {
        "invalid_command": "{command} は無効なコマンドです。",
        "no_config_file": "設定ファイル ({CONFIG_FILE}) が見つかりません。",
        "move_failed": "{src} から {dst} への移動に失敗しました。",
        "read_history_failed": "履歴ファイルの読み込みに失敗しました: {error}",
        "save_history_failed": "履歴の保存に失敗しました: {error}",
        "delete_history_failed": "履歴ファイルの削除に失敗しました: {error}",
        "invalid_config": "設定ファイルのJSON形式が正しくありません: {error}",
        "generate_config_failed": "設定ファイルの生成に失敗しました: {error}",
        "read_config_failed": "設定ファイルの読み込みに失敗しました: {error}",
        "source_directory_required": "source_directory が指定されていません。",
        "dry_run_not_bool": "dry_run は boolean (true/false) である必要があります。",
        "source_dir_not_exist": "{source_directory} が存在しません。",
        "source_dir_not_dir": "{source_directory} がディレクトリではありません。",
        "rules_not_exist": "rules が存在しません。",
        "rules_not_list": "rules がリストではありません。",
        "extension_not_str": "extension が str ではありません。",
        "extension_must_start_with_dot": "extension が . で始まっていません。",
        "destination_required": "destination が存在しません。",
        "destination_not_str": "destination が str ではありません。",
    }
}