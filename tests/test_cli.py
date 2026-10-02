from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class Workspace:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.config_path = self.root / ".myra_codex" / "config.json"
        self.tasks_dir = self.root / ".myra_codex" / "tasks"

    def init(self) -> Dict[str, Any]:
        self.root.mkdir(parents=True, exist_ok=True)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        content = {
            "name": self.root.name,
            "initialized": True,
            "tasks_dir": str(self.tasks_dir),
        }
        self.config_path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
        return content

    def status(self) -> Dict[str, Any]:
        exists = self.config_path.exists()
        return {
            "root": str(self.root),
            "initialized": exists,
            "tasks_dir": str(self.tasks_dir),
            "config_path": str(self.config_path),
        }

    def generate_plan(self, prompt: str) -> Dict[str, Any]:
        normalized = prompt.strip()
        if not normalized:
            raise ValueError("Prompt cannot be empty")

        raw = normalized.lower()
        steps = [
            "inspect the current workspace and project context",
            "break the request into concrete implementation steps",
            "make the required code or file changes",
            "verify the result with a targeted check",
        ]

        if "login" in raw or "auth" in raw:
            steps = [
                "inspect existing auth and app structure",
                "create the login flow and validation logic",
                "connect UI and backend behavior",
                "verify form validation and success/error states",
            ]
        elif "landing" in raw or "marketing" in raw or "homepage" in raw:
            steps = [
                "review the current app structure and design system",
                "create the landing page layout and content sections",
                "style the components for responsiveness",
                "check the page renders correctly",
            ]
        elif "api" in raw or "backend" in raw:
            steps = [
                "inspect service and route structure",
                "add or update API endpoints and validation",
                "connect data handling and error responses",
                "verify route behavior with a focused test",
            ]

        plan = {
            "goal": normalized,
            "summary": f"Plan to complete: {normalized}",
            "steps": steps,
            "workspace": str(self.root),
        }

        task_file = self.tasks_dir / "latest_task.json"
        task_file.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        return plan


__all__ = ["Workspace"]
