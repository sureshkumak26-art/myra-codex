"""Run project checks and extract actionable compiler/linter errors."""
from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Diagnostic:
    command: str
    exit_code: int
    output: str
    errors: list[str]

    def to_dict(self):
        return asdict(self)


_ERROR_PATTERNS = [
    re.compile(r"^.*(?:error|Error|ERROR|failed|Failed|FAILED|Exception|Traceback).*$", re.MULTILINE),
]


def detect_errors(output: str, limit: int = 80) -> list[str]:
    found: list[str] = []
    for pattern in _ERROR_PATTERNS:
        found.extend(line.strip() for line in pattern.findall(output) if line.strip())
    # Keep order while removing duplicates.
    return list(dict.fromkeys(found))[:limit]


def run_check(command: str, workspace: str | Path = ".", timeout: int = 180) -> Diagnostic:
    if not command.strip():
        raise ValueError("A check command is required.")
    root = Path(workspace).resolve()
    result = subprocess.run(
        shlex.split(command), cwd=root, capture_output=True, text=True,
        timeout=timeout, check=False,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    return Diagnostic(command, result.returncode, output, detect_errors(output))


def common_checks(root: str | Path = ".") -> list[str]:
    path = Path(root)
    checks = []
    if (path / "package.json").exists():
        checks.append("npm run build")
        checks.append("npm run lint")
    if (path / "pyproject.toml").exists() or (path / "pytest.ini").exists() or (path / "tests").exists():
        checks.append("python -m pytest -q")
    return checks
