import json
from datetime import datetime
from pathlib import Path


LOG_FILE = Path("logs/attempts.json")


def log_attempt(
    attempt_number,
    task,
    files_changed,
    test_result,
    error_message="",
):
    """Save one agent attempt to the JSON log."""

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if LOG_FILE.exists():
        try:
            attempts = json.loads(
                LOG_FILE.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError:
            attempts = []
    else:
        attempts = []

    attempt = {
        "timestamp": datetime.now().isoformat(),
        "attempt": attempt_number,
        "task": task,
        "files_changed": files_changed,
        "test_passed": test_result.get("success", False),
        "return_code": test_result.get("return_code"),
        "stdout": test_result.get("stdout", ""),
        "stderr": test_result.get("stderr", ""),
        "error_message": error_message,
    }

    attempts.append(attempt)

    LOG_FILE.write_text(
        json.dumps(attempts, indent=2),
        encoding="utf-8",
    )