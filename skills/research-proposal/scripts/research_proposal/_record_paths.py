"""产品记录的本地引用；不改写原件、识别原始响应或任意用户文件。"""

from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from ._common import read_json, write_json


PATH_FIELDS = {
    "path", "original_path", "raw_output_path", "input_image", "image", "page_image",
    "material_path", "original_copy", "baseline_body", "body_path", "import_record", "template_path", "diagnostic_path",
}
PATH_LIST_FIELDS = {"material_paths", "page_images"}
LITERAL_FIELDS = {"raw_output", "text", "source", "message", "decision"}


def _movable_root(base: Path, fallback=None) -> Path:
    """只采用状态明确列出的修订目录，不扫描或推测版本。"""
    for parent in (base, *base.parents):
        state_path = parent / "研究计划状态.json"
        if not state_path.is_file():
            continue
        state = read_json(state_path)
        if not isinstance(state, dict) or state.get("schema_version") != 1:
            continue
        candidates = []
        for work in state.get("works", {}).values():
            candidates.append(work.get("directory"))
            pending = work.get("pending_commit") or {}
            candidates.extend((pending.get("work_directory"), pending.get("target_directory")))
        if state.get("current"):
            candidates.append(state["current"].get("directory"))
        roots = [Path(path).resolve() for path in candidates if isinstance(path, str) and Path(path).is_absolute()]
        owned = [root for root in roots if base.is_relative_to(root)]
        if owned:
            return max(owned, key=lambda root: len(root.parts))
    return Path(fallback).resolve() if fallback is not None else base


def _path(value, base: Path, root: Path | None, *, url=False, location=False):
    if not isinstance(value, str) or not value:
        return value
    parts = urlsplit(value)
    if parts.scheme not in {"", "file"} or parts.netloc not in {"", "localhost"}:
        return value
    uri = url or parts.scheme == "file"
    if uri and not parts.path:
        return value
    path = unquote(parts.path) if uri else value
    if location and not Path(path).is_absolute() and not path.startswith(("./", "../")):
        # location 也可以是字段名等标识，不能把它冒充文件路径。
        return value
    suffix = (("?" + parts.query) if parts.query else "") + (("#" + parts.fragment) if parts.fragment else "") if uri else ""
    candidate = Path(path)
    candidate = candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()
    absolute = quote(str(candidate), safe="/@:+-._~") if uri else str(candidate)
    if root is None:
        return absolute + suffix
    if not candidate.is_relative_to(root):
        # 原有外部路径不改写；外部相对媒体必须先成为稳定的绝对引用。
        return value if Path(path).is_absolute() else absolute + suffix
    relative = Path(os.path.relpath(candidate, base)).as_posix()
    if location and not relative.startswith(("./", "../")):
        relative = "./" + relative
    return (quote(relative, safe="/@:+-._~") if uri else relative) + suffix


def _transform(value, base: Path, root: Path | None):
    if isinstance(value, list):
        return [_transform(item, base, root) for item in value]
    if not isinstance(value, dict):
        return value
    transformed = {}
    for key, item in value.items():
        if key in LITERAL_FIELDS:
            transformed[key] = deepcopy(item)
        elif key in PATH_FIELDS and isinstance(item, str):
            transformed[key] = _path(item, base, root)
        elif key in PATH_LIST_FIELDS and isinstance(item, list):
            transformed[key] = [_path(path, base, root) for path in item]
        elif key == "location" and isinstance(item, str):
            transformed[key] = _path(item, base, root, location=True)
        else:
            transformed[key] = _transform(item, base, root)
    if transformed.get("t") in {"Image", "Link"}:
        content = transformed.get("c")
        if isinstance(content, list) and len(content) == 3 and isinstance(content[2], list) and len(content[2]) == 2:
            content[2][0] = _path(content[2][0], base, root, url=True)
    return transformed


def encode_record_paths(value, base, movable_root=None):
    """返回编码副本；base 是记录所在目录，movable_root 是找不到所属修订时的范围。"""
    directory = Path(base).resolve()
    return _transform(value, directory, _movable_root(directory, movable_root))


def decode_record_paths(value, base):
    """返回解码副本；本地路径以记录目录为基准，远程链接和原话不变。"""
    return _transform(value, Path(base).resolve(), None)


def write_record(path, value, movable_root=None) -> None:
    destination = Path(path).resolve()
    stored = encode_record_paths(value, destination.parent, movable_root)
    if isinstance(stored, dict) and "pandoc-api-version" not in stored:
        stored["path_base"] = "."
    write_json(destination, stored)


def read_record(path):
    source = Path(path).resolve()
    stored = read_json(source)
    restored = decode_record_paths(stored, source.parent)
    if isinstance(restored, dict) and restored.get("path_base") == ".":
        restored.pop("path_base")
    return restored
