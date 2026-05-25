import shutil
from pathlib import Path

def dry_run_prompt():
    pass

def execute_move(config):
    source_directory = config.get("source_directory")
    dry_run = config.get("dry_run")
    rules = config.get("rules")

    source_path = Path(source_directory)

    for item in source_path.iterdir():
        if not item.is_file():
            continue

        for rule in rules:
            if item.suffix != rule.get("extension"):
                continue

            destination_path = (source_path / rule.get("destination"))
            if dry_run:
                print(f"[DRY RUN] {item} -> {destination_path}")
            else:
                destination_path.mkdir(parents=True, exist_ok=True)
                shutil.move(item, destination_path / item.name)
                break

