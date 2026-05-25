DEFAULT_CONFIG = {
        "source_directory": "../test_directory",
        "dry_run": True,
        "rules": [
            {"extension": ".jpg", "destination": "images/jpg"},
            {"extension": ".jpeg", "destination": "images/jpg"},
            {"extension": ".png", "destination": "images/png"},
            {"extension": ".mp4", "destination": "videos/mp4"},
            {"extension": ".mp3", "destination": "music/mp3"},
            {"extension": ".txt", "destination": "documents/txt"},
        ]
    }