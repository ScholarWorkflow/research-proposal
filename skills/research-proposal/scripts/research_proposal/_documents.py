"""Export and read back the delivered formats of a single adopted manuscript.

当前只交付 Markdown；Word 导出、模板填写与页图核对属延期实现，代码保留但
不参与当前交付要求，也不由 Markdown 导出或核对调用。
"""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unicodedata

import pymupdf

from ._common import hash_file, issue, json_digest, read_json, result, run_tool, write_json
from ._export_docx import TemplateFallback, fill_template, inspect_template


FILENAMES = {"docx": "研究计划草稿.docx", "md": "研究计划草稿.md"}
RECORD = "导出记录.json"
DISPLAY_META = ("title", "subtitle", "author", "date", "abstract")


def _text(value):
    # Curly quote glyphs are a writer's typographic choice, not a new citation.
    normalized = unicodedata.normalize("NFC", value).translate(str.maketrans({
        "“": '"', "”": '"', "‘": "'", "’": "'",
    }))
    return " ".join(normalized.split())


def _inlines(values):
    text, objects = [], []
    for value in values:
        kind, content = value.get("t"), value.get("c")
        if kind == "Str":
            text.append(content)
        elif kind in {"Space", "SoftBreak", "LineBreak"}:
            text.append(" ")
        elif kind in {"Emph", "Strong", "Underline", "Strikeout", "SmallCaps", "Superscript", "Subscript"}:
            child = _inlines(content)
            text.append(child["text"])
            objects.extend(child["objects"])
        elif kind == "Span":
            child = _inlines(content[1])
            text.append(child["text"])
            objects.extend(child["objects"])
        elif kind == "Quoted":
            child = _inlines(content[1])
            quote = '"' if content[0]["t"] == "DoubleQuote" else "'"
            text.extend([quote, child["text"], quote])
            objects.extend(child["objects"])
        elif kind in {"Code", "Math"}:
            text.append(content[1])
            if kind == "Math":
                objects.append({"math": "".join(content[1].split())})
        elif kind == "Cite":
            if not content[1]:
                raise ValueError("引文缺少可显示的引用文字；请先补齐正文中的引用标记")
            child = _inlines(content[1])
            text.append(child["text"])
            objects.extend(child["objects"])
        elif kind in {"Link", "Image"}:
            child = _inlines(content[1])
            text.append(child["text"])
            if kind == "Link":
                # Word changes an internal anchor's generated identifier; visible
                # linked text is still checked, external destinations stay exact.
                target = content[2][0]
                objects.append({"link": "#" if target.startswith("#") else target})
                objects.extend(child["objects"])
            else:
                objects.append({"image": child["text"]})
        elif kind == "Note":
            objects.append({"note": _blocks(content)})
        else:
            raise ValueError(f"正文含尚不能可靠导出和核对的行内对象：{kind}")
    return {"text": _text("".join(text)), "objects": objects}


def _caption(value):
    # Pandoc Caption is [optional short inlines, long blocks].
    if value[1]:
        return _blocks(value[1])
    return [{"kind": "paragraph", **_inlines(value[0])}] if value[0] else []


def _blocks(values):
    output = []
    for value in values:
        kind, content = value.get("t"), value.get("c")
        if kind in {"Para", "Plain", "Header"}:
            inline = content[2] if kind == "Header" else content
            semantic = _inlines(inline)
            if semantic["text"] or semantic["objects"]:
                output.append({"kind": "paragraph", **semantic})
        elif kind in {"Div", "BlockQuote"}:
            output.extend(_blocks(content[1] if kind == "Div" else content))
        elif kind in {"BulletList", "OrderedList"}:
            items = content[1] if kind == "OrderedList" else content
            entry = {"kind": "list", "ordered": kind == "OrderedList", "items": [_blocks(item) for item in items]}
            if kind == "OrderedList":
                entry["start"] = content[0][0]
            output.append(entry)
        elif kind == "Table":
            if len(content) != 6:
                raise ValueError("正文表格不是当前 Pandoc 表格结构")
            rows = list(content[3][1])
            for table_body in content[4]:
                rows.extend(table_body[2])
                rows.extend(table_body[3])
            rows.extend(content[5][1])
            output.append({"kind": "table", "caption": _caption(content[1]), "rows": [
                [{"rowspan": cell[2], "colspan": cell[3], "blocks": _blocks(cell[4])}
                 for cell in row[1]] for row in rows
            ]})
        elif kind == "CodeBlock":
            output.append({"kind": "paragraph", "text": _text(content[1]), "objects": []})
        elif kind == "LineBlock":
            joined = []
            for index, line in enumerate(content):
                if index:
                    joined.append({"t": "LineBreak"})
                joined.extend(line)
            output.append({"kind": "paragraph", **_inlines(joined)})
        elif kind == "HorizontalRule":
            continue
        elif kind == "Figure":
            output.extend(_blocks(content[2]))
            output.extend(_caption(content[1]))
        else:
            raise ValueError(f"正文含尚不能可靠导出和核对的正文对象：{kind}")
    return output


def _metadata(value):
    kind, content = value.get("t"), value.get("c")
    if kind == "MetaInlines":
        return _inlines(content)
    if kind == "MetaBlocks":
        return _blocks(content)
    if kind == "MetaString":
        return {"text": _text(content), "objects": []}
    if kind == "MetaList":
        return [_metadata(item) for item in content]
    raise ValueError(f"不支持的可见文档元数据：{kind}")


def _semantic(body):
    return {"meta": {key: _metadata(body["meta"][key]) for key in DISPLAY_META
                     if key in body.get("meta", {})}, "blocks": _blocks(body["blocks"])}


def _mapping(body, mapping):
    if mapping is None:
        return None
    if not isinstance(mapping, list) or not mapping:
        raise ValueError("学校栏目映射必须是非空数组")
    indices = []
    for entry in mapping:
        if not isinstance(entry, dict) or not isinstance(entry.get("field"), str) or not entry["field"].strip():
            raise ValueError("每项学校栏目映射须有栏目名称")
        blocks = entry.get("body_blocks")
        if not isinstance(blocks, list) or not blocks:
            raise ValueError(f"栏目 {entry['field']} 尚未对应正文块")
        if any(type(index) is not int or index < 0 or index >= len(body["blocks"]) for index in blocks):
            raise ValueError(f"栏目 {entry['field']} 的正文块索引不在正文内")
        target = entry.get("target")
        if target is not None and (not isinstance(target, dict) or
                set(target) not in ({"paragraph"}, {"table", "row", "column"}) or
                any(type(index) is not int or index < 0 for index in target.values())):
            raise ValueError(f"栏目 {entry['field']} 的模板位置无效")
        indices.extend(blocks)
    if sorted(indices) != list(range(len(body["blocks"]))):
        raise ValueError("学校栏目映射须完整且不重复地覆盖采用的全部正文块")
    return deepcopy(mapping)


def _ordered_body(body, mapping, mode):
    ordered = deepcopy(body)
    if mapping is not None:
        ordered["blocks"] = []
        for index, entry in enumerate(mapping):
            if mode == "transfer":
                ordered["blocks"].append({"t": "Header", "c": [1, [f"school-field-{index}", [], []],
                    [{"t": "Str", "c": entry["field"]}]]})
            ordered["blocks"].extend(deepcopy(body["blocks"][position]) for position in entry["body_blocks"])
    return ordered


def _error(error):
    if isinstance(error, subprocess.CalledProcessError):
        detail = (error.stderr or b"").decode("utf-8", errors="replace").strip()
        return f"转换程序退出 {error.returncode}：{detail[-2000:]}"
    if isinstance(error, subprocess.TimeoutExpired):
        return f"转换程序在 {error.timeout} 秒内未完成"
    return str(error)


def _renderable(value):
    """Use the adopted visible citation, identically in both output formats.

    Pandoc's Markdown writer otherwise replaces a Cite's display text with a
    citeproc key, while its Word writer keeps the display text.  The citation
    key remains in the structured body and in a span attribute in Markdown.
    """
    if isinstance(value, list):
        return [_renderable(child) for child in value]
    if isinstance(value, dict):
        if value.get("t") == "Cite":
            citations, visible = value["c"]
            keys = " ".join(citation["citationId"] for citation in citations)
            return {"t": "Span", "c": [["", ["citation"], [["data-cites", keys]]], _renderable(visible)]}
        return {key: _renderable(child) for key, child in value.items()}
    return value


def _pandoc_write(body, destination, kind, directory, reference=None):
    arguments = ["-f", "json", "-t", kind, "--standalone", "-o", str(destination)]
    if kind == "markdown":
        arguments.extend(["--wrap=none", "--markdown-headings=atx"])
    if reference is not None:
        arguments.extend(["--reference-doc", str(reference)])
    run_tool("pandoc", arguments, input=json.dumps(_renderable(body), ensure_ascii=False), cwd=directory)
    if not destination.is_file() or destination.stat().st_size == 0:
        raise OSError(f"转换程序未生成有效文件：{destination.name}")


def _pandoc_read(path, kind, directory):
    completed = run_tool("pandoc", [str(path), "-f", kind, "-t", "json"], cwd=directory)
    return json.loads(completed.stdout)


def _dependency(kind, body_digest, mapping, mode, template_digest):
    value = {"body": body_digest, "mapping": mapping, "mode": mode}
    if kind == "docx":
        value["template"] = template_digest
    return json_digest(value)


def _read_record(directory):
    path = directory / RECORD
    if not path.is_file():
        return {"schema_version": 1, "formats": {}}
    try:
        value = read_json(path)
        if value.get("schema_version") == 1 and isinstance(value.get("formats"), dict):
            return value
    except (OSError, ValueError, TypeError):
        pass
    return {"schema_version": 1, "formats": {}}


def _save_record(directory, record):
    with tempfile.NamedTemporaryFile(prefix=".export-record-", dir=directory, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        write_json(temporary, record)
        os.replace(temporary, directory / RECORD)
    finally:
        temporary.unlink(missing_ok=True)


def _preview(directory, docx):
    document_digest = hash_file(docx)
    with tempfile.TemporaryDirectory(prefix=".preview-", dir=directory) as temporary:
        temporary = Path(temporary)
        profile = temporary / "profile"
        profile.mkdir()
        run_tool("soffice", [f"-env:UserInstallation={profile.as_uri()}", "--headless",
                             "--convert-to", "pdf", "--outdir", str(temporary), str(docx)],
                 cwd=directory, timeout=180)
        pdf = temporary / (docx.stem + ".pdf")
        if not pdf.is_file() or not pdf.stat().st_size:
            raise OSError("Word 转换程序未生成预览 PDF")
        image_directory = temporary / "pages"
        image_directory.mkdir()
        with pymupdf.open(pdf) as document:
            if document.page_count == 0:
                raise OSError("Word 预览 PDF 没有页面")
            for index, page in enumerate(document):
                page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).save(
                    image_directory / f"page-{index + 1:03d}.png")
            page_count = document.page_count
        final_pdf = directory / "研究计划草稿预览.pdf"
        final_images = directory / ("页面预览-" + document_digest[:16])
        if final_images.exists():
            shutil.rmtree(final_images)
        os.replace(image_directory, final_images)
        os.replace(pdf, final_pdf)
        return {"docx_digest": document_digest,
                "pdf": {"path": final_pdf.name, "digest": hash_file(final_pdf)},
                "page_count": page_count,
                "images": [{"path": str(path.relative_to(directory)), "digest": hash_file(path)}
                           for path in sorted(final_images.glob("page-*.png"))]}


def _preview_valid(directory, preview, docx_digest):
    if not isinstance(preview, dict) or preview.get("docx_digest") != docx_digest:
        return False
    records = [preview.get("pdf", {}), *preview.get("images", [])]
    if not preview.get("images") or len(preview["images"]) != preview.get("page_count"):
        return False
    for entry in records:
        path = directory / entry.get("path", "")
        if not path.is_file() or hash_file(path) != entry.get("digest"):
            return False
    try:
        with pymupdf.open(directory / preview["pdf"]["path"]) as document:
            return document.page_count == preview["page_count"] and document.page_count > 0
    except (OSError, ValueError, RuntimeError):
        return False


def _artifacts(directory, record, dependencies, kinds=None):
    """只汇总本版交付要求中的实际产物；旧 Word 预览不混入当前交付。"""
    artifacts = {}
    for kind, entry in record["formats"].items():
        if kinds is not None and kind not in kinds:
            continue
        path = directory / entry.get("path", "")
        if kind in FILENAMES and entry.get("dependency") == dependencies.get(kind) and path.is_file():
            if hash_file(path) == entry.get("digest"):
                artifacts[kind] = str(path.resolve())
    if "docx" in artifacts and _preview_valid(directory, record.get("preview"), hash_file(artifacts["docx"])):
        artifacts["preview_pdf"] = str((directory / record["preview"]["pdf"]["path"]).resolve())
        artifacts["page_images"] = [str((directory / entry["path"]).resolve()) for entry in record["preview"]["images"]]
    return artifacts


def export_documents(work, formats, *, template_path=None, mapping=None):
    directory = Path(work["directory"]).resolve()
    record = _read_record(directory)
    issues, format_status = [], {}
    if not isinstance(formats, list) or not formats or any(kind not in FILENAMES for kind in formats):
        return result("blocked", [issue("formats", "导出格式须为 docx、md 的非空子集", "formats")], artifacts={}, format_status={})
    formats = list(dict.fromkeys(formats))
    # 仅 Markdown 时不读取、不复制 Word 模板，模板参数作为延期实现保留。
    word_export = "docx" in formats
    template_path = template_path or work.get("template_path") or work.get("inputs", {}).get("template_path")
    if not word_export:
        template_path = None
    if mapping is None:
        mapping = work.get("mapping") if word_export else None
    try:
        body_path = directory / "正文.json"
        body = read_json(body_path)
        if not isinstance(body, dict) or not isinstance(body.get("blocks"), list) or not body["blocks"]:
            raise ValueError("本轮没有可导出的结构化正文")
        _semantic(body)  # Unsupported content is never silently dropped by a writer.
        mapping = _mapping(body, mapping) if word_export else None
        template = Path(template_path).resolve(strict=True) if template_path else None
        if template and (template in [directory / value for value in FILENAMES.values()] or template == body_path):
            raise ValueError("模板原件不能同时作为本轮正文或导出目标")
        if template and mapping is None:
            return result("needs_input", [issue("template_mapping", "请先建立学校栏目与全部正文块的对应关系", str(template))],
                          artifacts={}, format_status={}, mapping=None, template_path=str(template), template_mode=None)
        mode = "plain"
        if template or mapping:
            mode = "editable"
            try:
                if template is None or any(entry.get("target") is None for entry in mapping):
                    raise TemplateFallback("栏目尚无可直接填写的 Word 位置")
                if any(key in body.get("meta", {}) for key in DISPLAY_META):
                    raise TemplateFallback("正文包含未映射的标题等可见元数据")
                inspect_template(template, mapping, body)
            except TemplateFallback as error:
                mode = "transfer"
                issues.append(issue("template_transfer", f"{error}；已按学校栏目顺序生成普通草稿，需要转填到学校原表。", str(template) if template else "mapping"))
        ordered = _ordered_body(body, mapping, mode)
        _semantic(ordered)
        body_digest = hash_file(body_path)
        template_digest = hash_file(template) if template else None
        dependencies = {kind: _dependency(kind, body_digest, mapping, mode, template_digest) for kind in formats}
        record.update({"body_digest": body_digest, "mapping": mapping, "template_mode": mode,
                       "template_digest": template_digest,
                       "template_notice": next((entry["message"] for entry in issues if entry["kind"] == "template_transfer"), None)})
        if template is not None:
            copied_template = directory / ("学校模板副本" + template.suffix.lower())
            if copied_template != template:
                shutil.copyfile(template, copied_template)
            record["template_copy"] = copied_template.name
        else:
            copied_template = None
            record.pop("template_copy", None)
    except (OSError, ValueError, TypeError, KeyError) as error:
        return result("blocked", [issue("export_input", _error(error), str(directory / "正文.json"))],
                      artifacts={}, format_status={kind: "failed" for kind in formats}, mapping=mapping,
                      template_path=str(template_path) if template_path else None, template_mode=None)

    with tempfile.TemporaryDirectory(prefix=".export-", dir=directory) as temporary:
        temporary = Path(temporary)
        for kind in formats:
            target = directory / FILENAMES[kind]
            old = record["formats"].get(kind, {})
            reusable = (old.get("dependency") == dependencies[kind] and target.is_file()
                        and hash_file(target) == old.get("digest"))
            try:
                if not reusable:
                    output = temporary / FILENAMES[kind]
                    if kind == "docx" and mode == "editable":
                        fragments = []
                        for index, entry in enumerate(mapping):
                            fragment_body = {**body, "meta": {}, "blocks": [body["blocks"][position] for position in entry["body_blocks"]]}
                            fragment_path = temporary / f"field-{index}.docx"
                            _pandoc_write(fragment_body, fragment_path, "docx", directory, reference=copied_template)
                            fragments.append(fragment_path)
                        regions = fill_template(copied_template, mapping, body, fragments, output)
                    else:
                        _pandoc_write(ordered, output, "docx" if kind == "docx" else "markdown", directory)
                        regions = None
                    os.replace(output, target)
                    record["formats"][kind] = {"path": target.name, "digest": hash_file(target),
                                                "dependency": dependencies[kind], "complete": False}
                    if kind == "docx":
                        record["regions"] = regions
                        record.pop("preview", None)
                    # Save the completed conversion even if the preview later fails.
                    _save_record(directory, record)
                if kind == "docx" and not _preview_valid(directory, record.get("preview"), hash_file(target)):
                    record["preview"] = _preview(directory, target)
                record["formats"][kind]["complete"] = True
                format_status[kind] = "complete"
                _save_record(directory, record)
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
                format_status[kind] = "failed"
                if kind in record["formats"]:
                    record["formats"][kind]["complete"] = False
                issues.append(issue("export_" + kind, _error(error), str(target)))
                _save_record(directory, record)
    return result("ready" if all(value == "complete" for value in format_status.values()) else "blocked", issues,
                  artifacts=_artifacts(directory, record, dependencies), format_status=format_status,
                  mapping=mapping, template_path=str(template) if template else None, template_mode=mode)


def review_documents(work):
    """当前交付只核对 Markdown 与正式正文；不读 Word、不查页面。"""
    directory = Path(work["directory"]).resolve()
    record = _read_record(directory)
    issues, content_details = [], []
    content_consistent = True
    dependencies, digests = {}, {}
    try:
        body_path = directory / "正文.json"
        body = read_json(body_path)
        body_digest = hash_file(body_path)
        references_path = directory / "引用定位.json"
        digests["body"] = body_digest
        digests["references"] = hash_file(references_path) if references_path.is_file() else None
        mapping = record.get("mapping")
        mode = record.get("template_mode", "plain")
        ordered = _ordered_body(body, mapping, mode)
        expected = _semantic(ordered)
        dependencies = {"md": _dependency("md", body_digest, mapping, mode, record.get("template_digest"))}
        entry = record["formats"].get("md", {})
        path = directory / FILENAMES["md"]
        if not path.is_file():
            raise ValueError("缺少本轮实际 md 文件")
        if entry.get("dependency") != dependencies["md"] or not entry.get("complete"):
            raise ValueError("本轮 md 尚未完成或对应的正文已改变")
        digests["md"] = hash_file(path)
        if digests["md"] != entry.get("digest"):
            content_consistent = False
            content_details.append("Markdown 文件在导出后被修改，请先按修改稿流程采用正文")
        markdown_body = _pandoc_read(path, "markdown", directory)
        markdown_content = _semantic(markdown_body)
        if markdown_content != expected:
            content_consistent = False
            content_details.append("Markdown 的段落、列表、表格、引用或链接与采用正文不一致")
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        content_consistent = False
        content_details.append(_error(error))
    if not content_consistent:
        issues.append(issue("content_inconsistent", "；".join(content_details), str(directory)))
    checks = {
        "content_consistent": content_consistent,
        "checked_formats": ["md"],
        "content_details": content_details,
        "digests": digests,
    }
    artifacts = _artifacts(directory, record, dependencies, kinds={"md"}) if dependencies else {}
    return result("ready" if content_consistent else "blocked", issues, checks=checks, artifacts=artifacts)
