# Portfolio Coding Agent CLI

A Python-based coding-agent CLI that can inspect a real multi-file
project, understand a requested change, generate code edits using an LLM,
execute the project's tests, observe failures, and automatically correct
the implementation.

This project demonstrates an agent workflow similar to modern coding
assistants.

## Week 4 - Portfolio Coding Agent
# Portfolio Coding Agent CLI

A Python-based coding-agent CLI that can inspect a real multi-file project, understand a requested change, generate code edits using an LLM, execute the project's tests, observe failures, and automatically correct the implementation.

This project demonstrates an agent workflow similar to modern coding assistants.

## Week 4 - Portfolio Coding Agent

## Core Workflow

The agent follows this loop:

**Generate → Execute → Observe → Correct**

### 1. Generate

- Scans the target project.
- Identifies relevant files.
- Uses an LLM to generate the requested code changes.

### 2. Execute

- Applies the generated changes.
- Runs the target project's test suite using pytest.

### 3. Observe

- Captures test output, return codes, stdout, and stderr.
- Records each attempt in `logs/attempts.json`.

### 4. Correct

- If tests fail, sends the modified file and test failure output back to the LLM.
- Generates a corrected implementation.
- Runs the tests again.
- Allows up to 3 attempts.

## Features

- Command-line coding agent
- Multi-file project scanning
- LLM-powered code generation
- Automatic test execution
- Failure observation
- Automatic self-correction
- Maximum of 3 correction attempts
- Centralized file backups
- Full attempt logging
- Unified diff output for dry runs
- Project-relative file handling
- Configurable test timeout
- `.env` support for API credentials

## LLM Provider

This project uses **Groq** as the LLM provider.

The Groq Python SDK is used for code generation and correction.

The model can be configured using:

```text
GROQ_MODEL