# Multi-File Context Agent

A Python-based coding agent that can understand and modify a small multi-file project using an LLM.

## Week 3 - SkillAudit Internship

This project demonstrates multi-file context handling, coordinated code editing, file backups, and automated test execution.

## Features

- Scans all Python files in a project
- Extracts function names using Python AST
- Builds a project context summary
- Sends project context to an LLM
- Identifies which files need modification
- Reads the selected files
- Generates coordinated edits across multiple files
- Creates backups before modifying files
- Runs tests using a safe subprocess
- Reports whether the tests passed or failed

## Project Structure

```text
Multi_File_Context_Agent/
│
├── agent.py
├── project_scanner.py
├── editor.py
├── executor.py
├── main.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
│
├── backups/
│   └── original file backups
│
└── sample_project/
    ├── calculator.py
    ├── test_calculator.py
    └── main.py