from config.config_loader import load_config
from config.errors import ConfigError

def main():
    print("---File Organizer---")
    
    try:
        config = load_config()
        if config is None:
            # 初回生成時はここで終了
            return
        
        print(f"読み込み成功。")
        print(f"現在の対象ディレクトリ: {config.get('source_directory')}")
        # 今後ここに実行ロジックを追加

    except ConfigError as e:
        print(f"[Config Error] 設定内容に問題があります: {e}")
    except Exception as e:
        print(f"[Unexpected Error] 予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    main()