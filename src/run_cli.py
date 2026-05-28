from config.config_loader import load_config
from actions.move_action import move_flow
from config.errors import ConfigError

def main():
    print("---File Organizer---")
    
    try:
        config = load_config()
        if config is None:
            # 初回生成時はここで終了
            return
        print("読み込み成功。")

    except ConfigError as e:
        print(f"[Config Error] 設定内容に問題があります: {e}")
        return
    except Exception as e:
        print(f"[Unexpected Error] 予期せぬエラーが発生しました: {e}")
        return
    try:
        move_flow(config)
    except Exception as e:
        print(f"[Unexpected Error] 予期せぬエラーが発生しました: {e}")
        return


if __name__ == "__main__":
    main()