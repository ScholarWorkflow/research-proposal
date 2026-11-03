"""Small shared helpers; manuscript state writes live in the state module."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any


def issue(kind: str, message: str, location: Any) -> dict:
    return {"kind": kind, "message": message, "location": location}


def result(status: str = "ready", issues: list | None = None, **fields: Any) -> dict:
    return {"status": status, "issues": issues if issues is not None else [], **fields}


def read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path: str | Path, value: Any) -> None:
    """Persist a normal artifact; do not use this for the current-state pointer."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def hash_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_digest(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def tool(name: str) -> str:
    """Use the installed fixed runtime; PATH is for explicit non-Nix installs."""
    try:
        from ._runtime import TOOLS
    except ModuleNotFoundError as error:
        if error.name != f"{__package__}._runtime":
            raise
        fixed = None
    else:
        if name not in TOOLS:
            raise FileNotFoundError(f"固定运行环境未声明程序：{name}")
        fixed = TOOLS[name]
    if fixed:
        candidate = Path(fixed)
        if not candidate.is_absolute() or not candidate.is_file() or not os.access(candidate, os.X_OK):
            raise FileNotFoundError(f"固定运行程序不可执行：{name}: {fixed}")
        return str(candidate)
    executable = shutil.which(name)
    if not executable:
        raise FileNotFoundError(f"缺少运行程序 {name}；请安装 README 声明的运行依赖。")
    return str(Path(executable).absolute())


def run_tool(
    name: str,
    args: list,
    input: bytes | str | None = None,
    cwd: str | Path | None = None,
    timeout: int | float = 180,
) -> subprocess.CompletedProcess:
    if isinstance(input, str):
        input = input.encode("utf-8")
    return subprocess.run(
        [tool(name), *(str(argument) for argument in args)],
        input=input,
        cwd=cwd,
        timeout=timeout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
