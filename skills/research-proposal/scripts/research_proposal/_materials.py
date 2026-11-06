"""Public material reading and revision import operations.

These operations retain evidence and a pending body. They do not adopt a body,
accept review markup, or change proposal/user-confirmation state.
"""

from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
import shutil
import subprocess
from uuid import uuid4
from zipfile import BadZipFile

from lxml import etree

from ._common import hash_file, issue, json_digest, result
from ._material_readers import (
    ast_text, decode_text, pandoc_body, read_docx, read_epub, read_html,
    read_image, read_pdf, read_text,
)
from ._material_word import read_word_structure, without_comments
from ._record_paths import decode_record_paths, read_record, write_record


def _path(request: dict, field: str) -> Path:
    value = request.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"需要提供 {field} 路径。")
    return Path(value).expanduser().resolve()


def _preserve(path: Path, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / path.name
    if target.exists() and hash_file(target) != hash_file(path):
        target = directory / f"{path.stem}-{uuid4().hex[:12]}{path.suffix}"
    if target.resolve() != path and not target.exists():
        shutil.copy2(path, target)
    return target.resolve()


_READ_FAILURES = (OSError, ValueError, ImportError, KeyError, BadZipFile, etree.LxmlError, subprocess.SubprocessError)


def read_material(request: dict) -> dict:
    try:
        path = _path(request, "path")
        output = _path(request, "output_dir")
        if not path.is_file():
            return result("needs_input", [issue("missing_material", "材料文件不存在或不是文件。", str(path))])
        for field in ("material_type", "source"):
            if not isinstance(request.get(field), str) or not request[field].strip():
                return result("needs_input", [issue("missing_attribution", f"请补充材料的 {field}。", str(path))])
        digest = hash_file(path)
        material_id = "material-" + digest[:24]
        directory = output / material_id
        directory.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError) as error:
        return result("needs_input", [issue("material_input", str(error), request.get("path", "path"))])
    material = {
        "material_id": material_id, "material_type": request["material_type"],
        "source": request["source"], "original_path": str(path), "digest": digest,
        "reader": "尚未读取", "blocks": [], "issues": [],
    }
    extension = path.suffix.lower()
    readers = {
        ".txt": lambda: read_text(path, directory, False, movable_root=output),
        ".md": lambda: read_text(path, directory, True, movable_root=output),
        ".markdown": lambda: read_text(path, directory, True, movable_root=output),
        ".html": lambda: read_html(path, directory, movable_root=output),
        ".htm": lambda: read_html(path, directory, movable_root=output),
        ".xhtml": lambda: read_html(path, directory, movable_root=output),
        ".epub": lambda: read_epub(path, directory, movable_root=output),
        ".docx": lambda: read_docx(path, directory, movable_root=output),
        ".pdf": lambda: read_pdf(path, directory, movable_root=output),
    }
    if extension in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff", ".bmp"}:
        readers[extension] = lambda: read_image(path, directory, movable_root=output)
    record_path = directory / "材料.json"
    if extension not in readers:
        material["issues"] = [issue("conversion_required", f"尚不支持 {extension or '无扩展名'} 载体，请转换为 PDF、图片、TXT、Markdown、HTML、EPUB 或 DOCX；原文件保留。", str(path))]
        status = "needs_input"
    else:
        try:
            reading = readers[extension]()
            blocks, issues, reader = reading[:3]
            if len(reading) > 3:
                for field in ("interpretation", "ocr_outputs"):
                    if field in reading[3]:
                        material[field] = reading[3][field]
            for position, block in enumerate(blocks, 1):
                block["block_id"] = f"{material_id}-{position}"
            material.update(blocks=blocks, issues=issues, reader=reader)
            if not blocks and not issues:
                material["issues"].append(issue("no_readable_content", "未提取到可读内容，需检查原件或提供转换副本；不能将其当作空材料。", str(path)))
            status = "ready" if not material["issues"] else ("needs_input" if blocks else "blocked")
        except _READ_FAILURES as error:
            material["issues"] = [issue("material_read_failed", f"材料未能读完：{type(error).__name__}: {error}", str(path))]
            # A failed retry must not erase a previously readable extraction of these bytes.
            if record_path.is_file():
                previous = read_record(record_path)
                if previous.get("digest") == digest:
                    material["blocks"] = previous.get("blocks", [])
                    material["reader"] = previous.get("reader", material["reader"])
                    material["issues"] = previous.get("issues", []) + material["issues"]
                    for field in ("interpretation", "ocr_outputs"):
                        if field in previous:
                            material[field] = previous[field]
            status = "blocked"
    write_record(record_path, material, movable_root=output)
    return result(status, material["issues"], material=material, material_path=str(record_path))


def _differences(baseline: dict, body: dict, baseline_path: Path, source: Path) -> list:
    old, new = baseline["blocks"], body["blocks"]
    old_keys, new_keys = [json_digest(block) for block in old], [json_digest(block) for block in new]
    changes = []
    for operation, old_start, old_end, new_start, new_end in SequenceMatcher(None, old_keys, new_keys, autojunk=False).get_opcodes():
        if operation == "equal":
            continue
        for side, blocks, start, end, path in (
            ("baseline", old, old_start, old_end, baseline_path),
            ("import", new, new_start, new_end, source),
        ):
            for index in range(start, end):
                changes.append({"kind": "content_delete" if side == "baseline" else "content_insert",
                                "text": ast_text(blocks[index]).strip() or "正文结构或非文字对象发生变化。",
                                "location": {"path": str(path), "body_block": index, "side": side, "operation": operation}})
    if baseline.get("meta", {}) != body.get("meta", {}):
        changes.append({"kind": "metadata", "text": "标题或其他正文元数据有变化。",
                        "location": {"path": str(source), "field": "meta"}})
    return changes


def import_revision(request: dict) -> dict:
    issues, changes, comments, unsupported = [], [], [], []
    body = None
    try:
        path = _path(request, "path")
        baseline_path = _path(request, "baseline_body")
        output = _path(request, "output_dir")
        if not path.is_file():
            return result("needs_input", [issue("missing_revision", "修改稿不存在或不是文件。", str(path))])
        source_digest = hash_file(path)
        baseline_digest = hash_file(baseline_path) if baseline_path.is_file() else "missing"
        directory = output / f"import-{source_digest[:16]}-{baseline_digest[:16]}"
        original = _preserve(path, directory / "原件")
    except (OSError, ValueError) as error:
        return result("needs_input", [issue("revision_input", str(error), request.get("path", "path"))])

    baseline = None
    try:
        baseline = read_record(baseline_path)
        if not isinstance(baseline, dict) or not isinstance(baseline.get("blocks"), list) or not baseline.get("pandoc-api-version"):
            raise ValueError("基准不是 Pandoc 正文结构。")
        _preserve(baseline_path, directory / "基准")
    except (OSError, ValueError) as error:
        issues.append(issue("baseline_unavailable", f"不能与基准正文比较：{error}", str(baseline_path)))
        baseline = None

    try:
        if path.suffix.lower() == ".docx":
            # XML is inspected first so a converter failure cannot discard the review markup.
            structure = read_word_structure(original)
            changes.extend(structure["changes"])
            comments.extend(structure["comments"])
            unsupported.extend(structure["unsupported"])
            body = without_comments(pandoc_body(original, "docx+styles", media_dir=directory / "media", track_changes=True))
            body = decode_record_paths(body, path.parent)
            if structure["changes"]:
                issues.append(issue("unresolved_changes", "已保留插入、删除及其他未决修订；需按用户已有决定处理，导入没有接受或拒绝它们。", str(original)))
            for item in unsupported:
                issues.append(issue("unsupported_word_object", item["text"], item["location"]))
        elif path.suffix.lower() in {".md", ".markdown"}:
            body = pandoc_body(None, "markdown", data=decode_text(original).encode("utf-8"))
            # Relative media belong to the submitted source, not its archived copy or the process cwd.
            body = decode_record_paths(body, path.parent)
        else:
            issues.append(issue("conversion_required", "修改稿需为 DOCX 或 Markdown；请转换后重新导入，原件已保留。", str(original)))
        if body is not None and baseline is not None:
            changes.extend(_differences(baseline, body, baseline_path, original))
    except _READ_FAILURES as error:
        issues.append(issue("revision_read_failed", f"修改稿未能完整导入：{type(error).__name__}: {error}；原件及已读标记保留。", str(original)))

    status = "ready" if body is not None and not issues else ("needs_input" if body is not None else "blocked")
    imported = result(status, issues, body=body, original_copy=str(original), changes=changes,
                      comments=comments, unsupported=unsupported, baseline_body=str(baseline_path),
                      source_digest=source_digest, baseline_digest=baseline_digest)
    if body is not None:
        body_path = directory / "待处理正文.json"
        write_record(body_path, body, movable_root=output)
        imported["body_path"] = str(body_path)
    record_path = directory / "导入记录.json"
    imported["import_record"] = str(record_path)
    write_record(record_path, imported, movable_root=output)
    return imported
