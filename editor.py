from pathlib import Path
import shutil
from datetime import datetime


BACKUP_DIR = Path("backups")


def backup_file(file_path):
    """Create a timestamped backup outside the target project."""

    file_path = Path(file_path)

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    backup_path = BACKUP_DIR / (
        f"{file_path.stem}_backup_"
        f"{timestamp}{file_path.suffix}"
    )

    shutil.copy2(
        file_path,
        backup_path
    )

    return backup_path


def read_file(file_path):
    """Read the complete contents of a file."""

    return Path(file_path).read_text(
        encoding="utf-8"
    )


def write_file(file_path, new_content):
    """Back up the original file and write the new content."""

    file_path = Path(file_path)

    backup_path = backup_file(
        file_path
    )

    file_path.write_text(
        new_content,
        encoding="utf-8"
    )

    return backup_path