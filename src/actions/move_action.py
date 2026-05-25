import shutil
from pathlib import Path

""" 将来的にファイルの移動を行うクラス """

class MoveAction:
    def __init__(self, destination):
        self.destination = Path(destination)

    def move_execute(self, file):
        ext = file.suffix.replace(".", "")
        target_dir = self.destination / ext
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(file, target_dir / file.name)