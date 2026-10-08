import ast
from pathlib import Path


def summarize_file(file_path, project_path=None):
    """Create a simple summary of a Python file."""

    file_path = Path(file_path)

    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

    if project_path:
        try:
            display_path = file_path.relative_to(project_path)
        except ValueError:
            display_path = file_path
    else:
        display_path = file_path

    return {
        "file": str(display_path),
        "functions": functions,
    }


def scan_project(project_path):
    """Recursively scan all Python files in the project."""

    project_path = Path(project_path).resolve()

    summaries = []

    for file_path in sorted(project_path.rglob("*.py")):

        # Ignore common generated/cache directories.
        if any(
            part in {
                ".git",
                ".venv",
                "venv",
                "__pycache__",
                ".pytest_cache",
            }
            for part in file_path.parts
        ):
            continue

        summaries.append(
            summarize_file(
                file_path,
                project_path
            )
        )

    return summaries


if __name__ == "__main__":
    summaries = scan_project("sample_project")

    for summary in summaries:
        print(f"\nFile: {summary['file']}")
        print(
            f"Functions: "
            f"{', '.join(summary['functions'])}"
        )