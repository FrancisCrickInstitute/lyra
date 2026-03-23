#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


PATH_KEYS = {
    "path",
    "paths",
    "filePath",
    "filePaths",
    "target_file",
    "target_files",
    "source_file",
    "source_files",
}
RELEVANT_SUFFIXES = (".py", ".pyi")
CONFIG_FILES = {"pyproject.toml"}
IGNORED_PREFIXES = {
    ".github/hooks",
    ".claude",
    ".cursor",
    ".venv",
    "apm_modules",
    "build",
    "dist",
}


def load_payload() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}

    return data if isinstance(data, dict) else {}


def collect_paths(value: object, *, parent_key: str | None = None) -> set[str]:
    paths: set[str] = set()

    if isinstance(value, dict):
        for key, nested_value in value.items():
            paths.update(collect_paths(nested_value, parent_key=key))
        return paths

    if isinstance(value, list):
        for item in value:
            paths.update(collect_paths(item, parent_key=parent_key))
        return paths

    if isinstance(value, str) and parent_key in PATH_KEYS:
        paths.add(value)

    return paths


def normalize_path(raw_path: str, project_root: Path) -> Path | None:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(project_root)
        except ValueError:
            return None

    resolved = (project_root / candidate).resolve()
    try:
        return resolved.relative_to(project_root)
    except ValueError:
        return None


def is_relevant_path(path: Path) -> bool:
    posix_path = path.as_posix()
    if any(posix_path == prefix or posix_path.startswith(f"{prefix}/") for prefix in IGNORED_PREFIXES):
        return False

    if path.name in CONFIG_FILES:
        return True

    return path.suffix in RELEVANT_SUFFIXES


def discover_changed_files(payload: dict, project_root: Path) -> list[Path]:
    tool_args = payload.get("toolArgs", {})
    raw_paths = collect_paths(tool_args)

    changed_files = []
    for raw_path in sorted(raw_paths):
        normalized = normalize_path(raw_path, project_root)
        if normalized is None or not is_relevant_path(normalized):
            continue
        if normalized not in changed_files:
            changed_files.append(normalized)

    return changed_files


def has_python_project_files(project_root: Path) -> bool:
    return any((project_root / marker).exists() for marker in ("pyproject.toml", "setup.py", "setup.cfg", "tox.ini"))


def is_available(command: list[str], project_root: Path) -> bool:
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return False

    return result.returncode == 0


def pick_uv_tool_command(project_root: Path, tool_name: str, tool_args: list[str], groups: list[str]) -> list[str] | None:
    if not shutil.which("uv") or not (project_root / "pyproject.toml").exists():
        return None

    no_group_probe = ["uv", "run", tool_name, "--version"]
    if is_available(no_group_probe, project_root):
        return ["uv", "run", tool_name, *tool_args]

    for group in groups:
        grouped_probe = ["uv", "run", "--group", group, tool_name, "--version"]
        if is_available(grouped_probe, project_root):
            return ["uv", "run", "--group", group, tool_name, *tool_args]

    return None


def pick_lint_command(project_root: Path, changed_files: list[Path]) -> list[str] | None:
    lint_targets = [path.as_posix() for path in changed_files if path.suffix in RELEVANT_SUFFIXES]
    if not lint_targets:
        return None

    venv_ruff = project_root / ".venv" / "bin" / "ruff"
    if venv_ruff.exists():
        return [venv_ruff.as_posix(), "check", *lint_targets]

    uv_lint_command = pick_uv_tool_command(project_root, "ruff", ["check", *lint_targets], ["lint", "dev", "test"])
    if uv_lint_command is not None:
        return uv_lint_command

    if shutil.which("ruff"):
        return ["ruff", "check", *lint_targets]

    return None


def pick_pytest_command(project_root: Path) -> list[str] | None:
    venv_pytest = project_root / ".venv" / "bin" / "pytest"
    if venv_pytest.exists():
        return [venv_pytest.as_posix()]

    uv_pytest_command = pick_uv_tool_command(project_root, "pytest", [], ["test", "dev", "lint"])
    if uv_pytest_command is not None:
        return uv_pytest_command

    if shutil.which("pytest"):
        return ["pytest"]

    return None


def run_command(command: list[str], project_root: Path, label: str) -> int:
    print(f"[python-quality-gate] Running {label}: {' '.join(command)}", file=sys.stderr)
    completed = subprocess.run(command, cwd=project_root, check=False)
    return completed.returncode


def main() -> int:
    project_root = Path(os.environ.get("CWD") or os.getcwd()).resolve()
    payload = load_payload()
    if not payload or not has_python_project_files(project_root):
        return 0

    changed_files = discover_changed_files(payload, project_root)
    if not changed_files:
        return 0

    lint_command = pick_lint_command(project_root, changed_files)
    pytest_command = pick_pytest_command(project_root)

    if lint_command is None and pytest_command is None:
        print("[python-quality-gate] Skipping: neither ruff nor pytest is available.", file=sys.stderr)
        return 0

    exit_code = 0

    if lint_command is not None:
        lint_exit_code = run_command(lint_command, project_root, "lint")
        if lint_exit_code != 0:
            exit_code = lint_exit_code
    else:
        print("[python-quality-gate] Skipping lint: ruff is not available.", file=sys.stderr)

    if pytest_command is not None:
        pytest_exit_code = run_command(pytest_command, project_root, "pytest")
        if pytest_exit_code not in (0, 5) and exit_code == 0:
            exit_code = pytest_exit_code
    else:
        print("[python-quality-gate] Skipping pytest: pytest is not available.", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())