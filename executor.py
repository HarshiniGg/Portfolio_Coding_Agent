import os
import subprocess
import sys
from pathlib import Path


DEFAULT_TIMEOUT = 30


def run_tests(project_path, timeout=DEFAULT_TIMEOUT):
    """Run the project's pytest tests in a separate subprocess."""

    project_path = Path(project_path).resolve()

    if not project_path.exists():
        return {
            "return_code": -1,
            "stdout": "",
            "stderr": f"Project path does not exist: {project_path}",
            "success": False,
        }

    environment = os.environ.copy()

    # Make the target project importable.
    existing_pythonpath = environment.get("PYTHONPATH", "")

    python_paths = [str(project_path)]

    if existing_pythonpath:
        python_paths.append(existing_pythonpath)

    environment["PYTHONPATH"] = os.pathsep.join(python_paths)

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
            ],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=environment,
        )

        return {
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or ""
        stderr = error.stderr or ""

        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")

        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")

        return {
            "return_code": -1,
            "stdout": stdout,
            "stderr": (
                f"Execution timed out after {timeout} seconds.\n"
                f"{stderr}"
            ),
            "success": False,
        }

    except Exception as error:
        return {
            "return_code": -1,
            "stdout": "",
            "stderr": str(error),
            "success": False,
        }


if __name__ == "__main__":
    result = run_tests("sample_project")

    if result["stdout"]:
        print(result["stdout"])

    if result["stderr"]:
        print(result["stderr"])

    if result["success"]:
        print("Tests passed.")
    else:
        print("Tests failed.")