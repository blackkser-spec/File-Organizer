DEFAULT_CONFIG = {
        "source_directory": "Desktop",
        "dry_run": True,
        "split_by_extension": True,
        "rules": [
            {"extension": ".jpg", "destination": "images"},
            {"extension": ".jpeg", "destination": "images"},
            {"extension": ".png", "destination": "images"},
            {"extension": ".mp4", "destination": "videos"},
            {"extension": ".mp3", "destination": "music/mp3"},
            {"extension": ".txt", "destination": "documents/txt"},
        ]
    }