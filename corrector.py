import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


def get_client():
    """Create the Groq client using the API key from .env."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Check your .env file."
        )

    return Groq(api_key=api_key)


def generate_correction(
    file_path,
    current_content,
    task,
    test_output,
):
    """Ask the LLM to correct a file after a failed test."""

    prompt = f"""
You are debugging a Python project.

Original user task:
{task}

The following file was modified by the coding agent:

File:
{file_path}

Current file contents:
{current_content}

The project tests failed.

Test output:
{test_output}

Analyze the failure and correct the code.

Return ONLY the complete corrected contents of this file.

Do not use Markdown code fences.
Do not explain anything.

Preserve all existing functionality unless the task
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
                    "You are an expert Python debugging engineer. "
                    "Return only complete corrected file contents."
                ),
            },
            {
                "role": "user",
                "content": prompt,
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