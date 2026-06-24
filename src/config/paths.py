from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

DATA_DIR = PROJECT_ROOT / "data"
RESOURCES_DIR = SRC_DIR / "resources"
IMAGES_DIR = RESOURCES_DIR / "images"

CONFIG_FILE = DATA_DIR / "config.json"
LATEST_CHANGE_FILE = DATA_DIR / "latest_change.json"