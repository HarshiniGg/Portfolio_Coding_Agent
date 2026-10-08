SYSTEM_PROMPT = """
You are a coding agent working on a small Python project.

Your job is to analyze the project context and determine which files
need to be changed to satisfy the user's instruction.

Return your response as valid JSON with this structure:

{
    "files_to_edit": [
        {
            "file": "path/to/file.py",
            "reason": "Why this file needs to be changed"
        }
    ]
}

Only include files that actually need modification.
Do not include files that do not need to change.
"""


def build_user_prompt(instruction, project_context):
    """Build the prompt containing the user instruction and project context."""

    context_text = ""

    for file_info in project_context:
        context_text += (
            f"File: {file_info['file']}\n"
            f"Functions: {', '.join(file_info['functions'])}\n\n"
        )

    return f"""
Project context:

{context_text}

User instruction:

{instruction}

Identify all files that need to be changed to complete the instruction.
Return only valid JSON.
"""