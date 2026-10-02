# myra-codex

myra-codex is a lightweight, Codex-inspired local coding agent starter. It gives you a sane project structure for prompting, planning, and executing small engineering tasks in a workspace.

## What it includes

- a Python CLI with `init`, `plan`, `status`, and `run` commands
- workspace scaffolding for tasks and config
- a simple planning engine that turns a prompt into a structured action plan
- a clean starting point for extending into a more advanced agent workflow

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
myra-codex init
myra-codex plan "Build a landing page for a SaaS product"
myra-codex status
```

## Example

```bash
myra-codex plan "Add a login page with email and password form"
```

This produces a structured task plan such as:

- define the goal
- inspect the app structure
- create the login page
authentication flow
- validate behavior

## Project structure

```text
myra-codex/
├── README.md
├── pyproject.toml
├── .gitignore
├── myra_codex/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   └── workspace.py
├── tests/
│   └── test_cli.py
└── .myra_codex/
    ├── config.json
    └── tasks/
```

## Why this is "Codex-like"

The project is intentionally shaped like a compact coding-agent workflow:

- prompt-driven task creation
- lightweight planning
- workspace state tracking
- command execution hooks for real coding tasks

This gives you a solid starting foundation to evolve into a more complete local AI coding assistant.
