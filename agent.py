import json
import os
import difflib

from dotenv import load_dotenv
from groq import Groq

from project_scanner import scan_project
from prompts import SYSTEM_PROMPT, build_user_prompt
from editor import read_file, write_file
from executor import run_tests
from corrector import generate_correction
from logger import log_attempt


load_dotenv()


MAX_ATTEMPTS = 3


def get_client():
    """Create the Groq client using the API key from .env."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Check your .env file."
        )

    return Groq(api_key=api_key)


def identify_files(instruction, project_path):
    """Ask the LLM which project-relative files need to be changed."""

    project_context = scan_project(project_path)

    prompt = build_user_prompt(
        instruction,
        project_context
    )

    client = get_client()

    response = client.chat.completions.create(
        model=os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        ),
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)

    except json.JSONDecodeError:
        raise RuntimeError(
            f"The LLM did not return valid JSON:\n{content}"
        )


def generate_file_edit(
    file_path,
    instruction,
    project_path
):
    """Ask the LLM to generate the complete updated file."""

    full_path = os.path.join(
        project_path,
        file_path
    )

    original_content = read_file(full_path)

    edit_prompt = f"""
You are editing a Python project.

User instruction:
{instruction}

File to edit:
{file_path}

Current file contents:
{original_content}

Return ONLY the complete updated contents of this file.

Do not use Markdown code fences.
Do not explain anything.

Preserve all existing functionality unless the instruction
requires a change.
"""

    client = get_client()

    response = client.chat.completions.create(
        model=os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        ),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful Python software engineer. "
                    "Return only the complete updated file contents."
                ),
            },
            {
                "role": "user",
                "content": edit_prompt,
            },
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```python"):
        content = content[len("```python"):].strip()

    if content.startswith("```"):
        content = content[3:].strip()

    if content.endswith("```"):
        content = content[:-3].strip()

    return content


def edit_project(
    instruction,
    project_path,
    dry_run=False
):
    """Identify files, generate edits, and optionally apply them."""

    result = identify_files(
        instruction,
        project_path
    )

    files_to_edit = result.get(
        "files_to_edit",
        []
    )

    if not files_to_edit:
        print("\nNo files need to be changed.")
        return []

    print("\nFiles identified for editing:")
    print("=" * 40)

    changed_files = []

    for file_info in files_to_edit:

        file_path = file_info["file"]
        reason = file_info["reason"]

        print(f"\nFile: {file_path}")
        print(f"Reason: {reason}")

        new_content = generate_file_edit(
            file_path,
            instruction,
            project_path
        )

        full_path = os.path.join(
            project_path,
            file_path
        )

        if dry_run:
            original_content = read_file(
                full_path
            )

            diff = difflib.unified_diff(
                original_content.splitlines(),
                new_content.splitlines(),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm="",
            )

            diff_text = "\n".join(diff)

            print("\n[DRY RUN] Proposed diff:")
            print("-" * 60)

            if diff_text:
                print(diff_text)
            else:
                print("No changes proposed.")

            print("-" * 60)
            print("No changes were written.")

            continue

        backup_path = write_file(
            full_path,
            new_content
        )

        changed_files.append(
            {
                "file": full_path,
                "backup": str(backup_path),
            }
        )

        print(
            f"Backup created: {backup_path}"
        )

        print("File updated successfully.")

    return changed_files


def run_project_tests(project_path):
    """Run the project tests and display the result."""

    print("\nRunning tests...")
    print("=" * 40)

    test_result = run_tests(
        project_path
    )

    if test_result["stdout"]:
        print(test_result["stdout"])

    if test_result["stderr"]:
        print(test_result["stderr"])

    if test_result["success"]:
        print("ALL TESTS PASSED")
    else:
        print("TESTS FAILED")

    return test_result


def correct_changed_files(
    changed_files,
    instruction,
    test_result
):
    """Ask the LLM to correct files after a failed test."""

    test_output = (
        "STDOUT:\n"
        + test_result.get("stdout", "")
        + "\n\nSTDERR:\n"
        + test_result.get("stderr", "")
    )

    corrected_files = []

    for item in changed_files:

        file_path = item["file"]

        print(
            f"\nCorrecting: {file_path}"
        )

        current_content = read_file(
            file_path
        )

        corrected_content = generate_correction(
            file_path=file_path,
            current_content=current_content,
            task=instruction,
            test_output=test_output,
        )

        backup_path = write_file(
            file_path,
            corrected_content
        )

        corrected_files.append(
            {
                "file": file_path,
                "backup": str(backup_path),
            }
        )

        print(
            f"Correction applied. "
            f"Backup created: {backup_path}"
        )

    return corrected_files


def run_agent(
    instruction,
    project_path,
    dry_run=False
):
    """
    Run the complete:

    generate → execute → observe → correct

    loop.
    """

    print("\nPlanning changes...")
    print("=" * 40)

    changed_files = edit_project(
        instruction,
        project_path,
        dry_run=dry_run,
    )

    if dry_run:
        print("\nDry run completed.")
        print("No files were modified.")
        return

    if not changed_files:
        print("\nNo changes were made.")
        return

    for attempt in range(
        1,
        MAX_ATTEMPTS + 1
    ):

        print("\n")
        print("=" * 60)
        print(
            f"ATTEMPT {attempt} "
            f"OF {MAX_ATTEMPTS}"
        )
        print("=" * 60)

        test_result = run_project_tests(
            project_path
        )

        log_attempt(
            attempt_number=attempt,
            task=instruction,
            files_changed=[
                item["file"]
                for item in changed_files
            ],
            test_result=test_result,
            error_message=(
                test_result.get(
                    "stderr",
                    ""
                )
                if not test_result["success"]
                else ""
            ),
        )

        if test_result["success"]:

            print("\nSUCCESS!")

            print(
                f"The project passed after "
                f"{attempt} attempt(s)."
            )

            return

        if attempt == MAX_ATTEMPTS:

            print("\nFAILED.")

            print(
                f"The agent reached the maximum "
                f"of {MAX_ATTEMPTS} attempts."
            )

            return

        print("\nTests failed.")
        print(
            "Sending the failure back to the LLM..."
        )

        print(
            "The agent will attempt a correction."
        )

        changed_files = correct_changed_files(
            changed_files,
            instruction,
            test_result,
        )

    print(
        "\nAgent execution completed."
    )


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Portfolio Coding Agent"
    )

    parser.add_argument(
        "--project",
        required=True,
        help=(
            "Path to the project the agent "
            "should modify"
        ),
    )

    parser.add_argument(
        "--task",
        required=True,
        help="Coding task for the agent",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show the planned changes "
            "without modifying files"
        ),
    )

    args = parser.parse_args()

    print("\nPortfolio Coding Agent")
    print("=" * 40)

    print("\nProject:")
    print(args.project)

    print("\nTask:")
    print(args.task)

    if args.dry_run:
        print("\nMode: DRY RUN")
        print("Files will NOT be modified.")

    run_agent(
        instruction=args.task,
        project_path=args.project,
        dry_run=args.dry_run,
    )

    print("\nAgent execution completed.")