"""Generate and safely apply AI-proposed unified diffs."""
from __future__ import annotations

import subprocess
from pathlib import Path

from myra_codex.ai_providers import MultiAI
from myra_codex.diagnostics import Diagnostic


SYSTEM = """You are an expert coding agent. Fix only the reported issue.
Return ONLY a valid unified diff (git diff format), with paths relative to the
workspace root. Do not use markdown fences. Do not change unrelated files.
If there is not enough context, explain briefly instead of inventing a patch."""


def propose_fix(diagnostic: Diagnostic, workspace: str | Path = ".", ai: MultiAI | None = None) -> str:
    root = Path(workspace).resolve()
    prompt = (
        f"Workspace: {root}\nCommand: {diagnostic.command}\nExit code: {diagnostic.exit_code}\n"
        f"Detected errors:\n{chr(10).join(diagnostic.errors)}\n\n"
        f"Full output:\n{diagnostic.output[:18000]}\n\n"
        "Inspect the relevant project files conceptually from the supplied diagnostics. "
        "Return a unified diff only."
    )
    return (ai or MultiAI()).chat(prompt, SYSTEM).strip()


def apply_fix(diff: str, workspace: str | Path = ".", *, approve: bool = False) -> str:
    """Validate and apply a patch only after explicit approval.

    A backup is not made automatically: commit/stash your work before applying.
    """
    if not approve:
        raise PermissionError("Patch not applied. Review it, then call apply_fix(..., approve=True).")
    if not diff.startswith("diff --git "):
        raise ValueError("AI response is not a git unified diff; refusing to apply.")
    root = Path(workspace).resolve()
    check = subprocess.run(["git", "apply", "--check", "-"], cwd=root, input=diff, text=True, capture_output=True)
    if check.returncode:
        raise RuntimeError(f"Patch validation failed: {check.stderr.strip()}")
    applied = subprocess.run(["git", "apply", "-"], cwd=root, input=diff, text=True, capture_output=True)
    if applied.returncode:
        raise RuntimeError(f"Patch application failed: {applied.stderr.strip()}")
    return "Patch applied. Run your project checks again."
