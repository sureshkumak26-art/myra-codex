from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from myra_codex.workspace import Workspace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="myra-codex: a lightweight Codex-inspired coding agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize a workspace")
    init_parser.add_argument("--path", default=".", help="workspace root")

    plan_parser = subparsers.add_parser("plan", help="generate a task plan from a prompt")
    plan_parser.add_argument("prompt", help="task description or goal")
    plan_parser.add_argument("--path", default=".", help="workspace root")

    status_parser = subparsers.add_parser("status", help="show workspace status")
    status_parser.add_argument("--path", default=".", help="workspace root")

    run_parser = subparsers.add_parser("run", help="run a shell command in the workspace")
    run_parser.add_argument("command", help="shell command to execute")
    run_parser.add_argument("--path", default=".", help="workspace root")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    workspace = Workspace(Path(args.path))

    if args.command == "init":
        workspace.init()
        print(f"Workspace initialized at {workspace.root}")
        return

    if args.command == "plan":
        task = workspace.generate_plan(args.prompt)
        print(json.dumps(task, indent=2))
        return

    if args.command == "status":
        print(json.dumps(workspace.status(), indent=2))
        return

    if args.command == "run":
        result = subprocess.run(args.command, shell=True, cwd=str(workspace.root), capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=None)
        print(f"Exit code: {result.returncode}")
        return

    parser.error(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
