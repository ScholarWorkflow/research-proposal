"""每稿独立的保存、Markdown 交付提交与中断恢复。"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import shutil
import tempfile
from uuid import uuid4

from ._common import hash_file, issue, json_digest, read_json, result, write_json
from ._record_paths import (
    LITERAL_FIELDS, PATH_FIELDS, PATH_LIST_FIELDS, decode_record_paths, encode_record_paths,
    write_record,
)


STATE_NAME = "研究计划状态.json"
BODY_NAME = "正文.json"
REFERENCE_NAME = "引用定位.json"
STAGES = (
    "materials", "question", "scheme", "body", "interview",
    "docx", "md", "script", "qa", "review",
)
FORMAT_NAMES = {
    "docx": "研究计划草稿.docx", "md": "研究计划草稿.md",
    "script": "研究计划讲稿.md", "qa": "研究计划想定问答.md",
}
# 当前交付只要求 Markdown；Word 导出与页图为延期实现，状态结构保留但不参与交付。
DELIVERY_FORMATS = ["md"]
# 讲稿与想定问答按用途加选：inputs.deliverables 含 script 或 qa 时才要求。
INTERVIEW_FORMATS = ("script", "qa")
DEFERRED_FORMATS = ("docx",)
_FORMAT_LABELS = {
    "docx": "Word（.docx）", "md": "Markdown（.md）",
    "script": "发表讲稿（Markdown）", "qa": "想定问答（Markdown）",
}
# 各保存步骤或正文变化时连带失效的步骤。`interview` 是保存讲稿与想定问答内容
# 的步骤，`script`、`qa` 是由它生成的两份交付文件。
_DEPENDENT = {
    "materials": ("interview", "script", "qa", "body", "docx", "md", "review"),
    "question": ("scheme", "interview", "script", "qa", "body", "docx", "md", "review"),
    "scheme": ("interview", "script", "qa", "body", "docx", "md", "review"),
    "interview": ("script", "qa", "review"),
    "body": ("script", "qa", "docx", "md", "review"),
}
STORED_PATH_BASE = "."


def _absolute(value: str | Path) -> str:
    return str(Path(value).expanduser().resolve())


def _deliverables(value) -> list:
    """本稿需要的交付文件；Markdown 正文始终包含。"""
    if value is None:
        return list(DELIVERY_FORMATS)
    if not isinstance(value, list) or not value:
        raise ValueError("deliverables 必须是包含 md 的非空数组")
    names = ["md"]
    for name in value:
        if name == "docx":
            raise ValueError("Word 交付尚未实现，不能列入 deliverables")
        if name not in {"md", *INTERVIEW_FORMATS}:
            raise ValueError(f"deliverables 只能包含 md、script、qa，收到 {name}")
        if name not in names:
            names.append(name)
    return names


def _normal_inputs(value: dict) -> dict:
    inputs = deepcopy(value)
    for name in ("application_id", "purpose", "question_id", "material_paths"):
        if name not in inputs:
            raise ValueError(f"inputs 缺少 {name}")
    # 当前只交付 Markdown，template_path 为可选历史引用。
    inputs.setdefault("template_path", None)
    if not inputs["application_id"] or not inputs["purpose"]:
        raise ValueError("申请项目和用途不能为空")
    if not isinstance(inputs["material_paths"], list):
        raise ValueError("material_paths 必须是路径数组")
    inputs["material_paths"] = [_absolute(path) for path in inputs["material_paths"]]
    if inputs["template_path"] is not None:
        inputs["template_path"] = _absolute(inputs["template_path"])
    if "deliverables" in inputs:
        inputs["deliverables"] = _deliverables(inputs["deliverables"])
    return inputs


@contextmanager
def _locked(proposal_dir: str):
    directory = Path(proposal_dir).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".研究计划.lock").open("a+b") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield directory
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _store_state(directory: Path, state: dict) -> None:
    """所有步骤产物保存后，才替换唯一状态入口。"""
    next_version = state["state_version"] + 1
    saved = {**state, "state_version": next_version}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix=".研究计划状态-", suffix=".json",
            dir=directory, delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(saved, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, directory / STATE_NAME)
        state["state_version"] = next_version
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _response(state: dict | None, status="ready", issues=None, **fields) -> dict:
    if state is not None:
        fields.update(state=deepcopy(state), state_version=state["state_version"])
    return result(status, issues, **fields)


def _preserve_return(directory: Path, state: dict | None, request: dict) -> str | None:
    """过期调用的新内容另存，不能成为任何已采用步骤。"""
    if "data" not in request:
        return None
    work = (state or {}).get("works", {}).get(request.get("revision_id"))
    if work and not work.get("committed") and Path(work["directory"]).is_dir():
        destination = Path(work["directory"]) / "未采用返回"
    else:
        destination = directory / "未采用返回"
    path = destination / f"{uuid4().hex}.json"
    write_json(path, request)
    return str(path)


def _ensure_steps(work: dict) -> dict:
    """补齐本版新增、旧状态里没有的步骤键。

    只补缺失键为未开始，不改已有步骤、确认、条件和用户决定；补进来的步骤没有
    保存件，摘要为 None，不算作内容变化。
    """
    steps = work.setdefault("steps", {})
    for name in STAGES:
        steps.setdefault(name, {"status": "pending", "artifacts": {}, "issues": []})
    return work


def _load(directory: Path, request: dict, *, create=False):
    path = directory / STATE_NAME
    state = read_json(path) if path.is_file() else None
    for work in (state or {}).get("works", {}).values():
        _ensure_steps(work)
    expected = request.get("expected_state_version")
    matches = (
        (state is None and create and "expected_state_version" in request and expected is None)
        or (state is not None and type(expected) is int and expected == state["state_version"])
    )
    if not matches:
        preserved = _preserve_return(directory, state, request)
        return state, _response(state, "conflict", [issue(
            "state_changed", "状态版本已变化，请先读取现存状态；本次内容没有覆盖已有决定。", str(path),
        )], **({"preserved_return": preserved} if preserved else {}))
    return state, None


def _current_id(state: dict) -> str | None:
    return state["current"]["revision_id"] if state["current"] else None


def _work_for_write(directory: Path, state: dict, request: dict):
    revision = request.get("revision_id")
    work = state["works"].get(revision)
    if work is None:
        return None, _response(state, "needs_input", [issue(
            "unknown_revision", "没有找到指定的修订，请使用状态中记录的修订编号。", revision,
        )])
    if work.get("committed"):
        return work, _response(state, "blocked", [issue(
            "committed_read_only", "已提交稿件只供读取；请先建立新的工作版本。", work["directory"],
        )])
    if work["base_revision"] != _current_id(state):
        preserved = _preserve_return(directory, state, request)
        return work, _response(state, "conflict", [issue(
            "base_changed", "另一轮已提交新稿。本轮目录和返回内容已保留，请明确采用的基准。", work["directory"],
        )], **({"preserved_return": preserved} if preserved else {}))
    if work.get("pending_commit") and not work["pending_commit"].get("needs_repair"):
        return work, _response(state, "blocked", [issue(
            "pending_commit", "该修订已有待提交目录，请先恢复这次提交。", work["directory"],
        )])
    return work, None


def _digest_file(path: str | Path | None):
    if path is None or not Path(path).is_file():
        return None
    return hash_file(path)


def _file_paths(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _file_paths(item)
    elif isinstance(value, list):
        for item in value:
            yield from _file_paths(item)
    elif isinstance(value, str):
        yield value


def _artifact_digests(artifacts: dict) -> dict:
    return {path: _digest_file(path) for path in _file_paths(artifacts)}


def _delivery_formats(work: dict) -> list:
    """本版交付要求；历史已提交记录缺该字段时按原双格式只读解释。

    Markdown 正文始终交付；讲稿与想定问答由 `inputs.deliverables` 加选，
    没有该字段的历史稿件不会因为新增文件而失效。
    """
    value = work.get("delivery_formats")
    if isinstance(value, list) and value:
        formats = [name for name in value if name in FORMAT_NAMES]
    elif work.get("committed"):
        return ["docx", "md"]
    else:
        formats = list(DELIVERY_FORMATS)
    requested = (work.get("inputs") or {}).get("deliverables")
    if isinstance(requested, list):
        for name in requested:
            if name in INTERVIEW_FORMATS and name not in formats:
                formats.append(name)
    return formats


def _delivery_artifact_names(formats) -> set:
    names = set(formats)
    if "docx" in names:
        names.update({"preview_pdf", "page_images"})
    return names


def _delivery_artifacts(work: dict, *, valid_only=False) -> dict:
    """只汇总本版交付要求中的实际文件，不把旧 Word 混入当前交付。"""
    allowed = _delivery_artifact_names(_delivery_formats(work))
    return {
        name: value for name, value in _existing_artifacts(work, valid_only=valid_only).items()
        if name in allowed
    }


def _review_artifact_digests(work: dict) -> dict:
    """核对摘要只依赖本版交付要求中的实际产物。"""
    allowed = _delivery_artifact_names(_delivery_formats(work))
    artifacts = {name: value for name, value in work.get("artifacts", {}).items() if name in allowed}
    return _artifact_digests(artifacts)


def _material_source_paths(paths) -> dict:
    """材料读取记录指向的原文；记录变化或原文变化都要让依赖它的工作失效。

    记录按各自 JSON 文件所在目录解释相对引用，其余仍保留绝对路径。
    """
    sources = {}
    for path in paths:
        record_path = Path(path)
        if not record_path.is_file():
            continue
        try:
            value = read_json(record_path)
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(value, dict):
            continue
        # 完整操作返回是 {"material": {...}}；read_material 写出的记录文件是扁平对象。
        material = value.get("material")
        if not isinstance(material, dict):
            material = value
        original = material.get("original_path")
        if not isinstance(original, str) or not original:
            continue
        target = Path(original)
        if not target.is_absolute():
            target = record_path.parent / target
        sources[str(target)] = _digest_file(target)
    return sources


def _material_records(work: dict) -> list:
    """材料步骤保存的已采用材料：原文路径、记录声明的摘要及当前摘要。

    材料步骤记录按该步骤 JSON 文件所在目录解释相对引用，其余保留绝对路径。
    已采用材料不必再重复列入 inputs.material_paths，组件按实际记录登记依赖。
    """
    step = (work.get("steps") or {}).get("materials") or {}
    data_path = (step.get("artifacts") or {}).get("data")
    if not isinstance(data_path, str) or not data_path:
        return []
    record_path = Path(data_path)
    if not record_path.is_file():
        return []
    try:
        value = read_json(record_path)
    except (OSError, ValueError, TypeError):
        return []
    materials = value.get("materials") if isinstance(value, dict) else None
    if not isinstance(materials, list):
        return []
    records = []
    for material in materials:
        original = material.get("original_path") if isinstance(material, dict) else None
        if not isinstance(original, str) or not original:
            continue
        target = Path(original)
        if not target.is_absolute():
            target = record_path.parent / target
        records.append((str(target), material.get("digest"), _digest_file(target)))
    return records


def _material_record_sources(work: dict) -> dict:
    return {path: actual for path, _, actual in _material_records(work)}


def _material_record_drift(work: dict) -> dict:
    """读取记录声明的摘要与原件当前内容不符的材料。

    旧记录没有后加的摘要项时，也能据此发现已采用材料的原文变化。
    """
    return {
        path: actual for path, recorded, actual in _material_records(work)
        if isinstance(recorded, str) and recorded and recorded != actual
    }


def _snapshot(work: dict) -> dict:
    inputs = work["inputs"]
    directory = Path(work["directory"])
    template = work.get("template_path", inputs.get("template_path"))
    stage_files = {}
    for stage in ("materials", "question", "scheme", "interview"):
        data_path = work["steps"][stage].get("artifacts", {}).get("data")
        stage_files[stage] = _digest_file(data_path)
    return {
        "inputs": json_digest(inputs),
        "materials": {path: _digest_file(path) for path in inputs["material_paths"]},
        "material_sources": _material_source_paths(inputs["material_paths"]),
        "adopted_materials": _material_record_sources(work),
        "template": {"path": template, "digest": _digest_file(template)},
        "mapping": json_digest(work.get("mapping")),
        "body": _digest_file(directory / BODY_NAME),
        "references": _digest_file(directory / REFERENCE_NAME),
        "stage_files": stage_files,
        "decisions": json_digest(work["confirmations"]),
        "conditions": json_digest(work["conditions"]),
        **({"delivery_formats": list(work["delivery_formats"])} if work.get("delivery_formats") else {}),
    }


# 后加的摘要项：旧记录没有该键时不作为变化，避免把历史已提交稿判为改动。
LATE_FINGERPRINTS = ("material_sources", "adopted_materials")


def _fingerprints_changed(previous: dict, current: dict, keys=None) -> bool:
    """比较整体摘要；keys 指定时只比这些键，延期项不参与。

    旧状态补齐新增步骤后，这些步骤的保存件摘要仍为 None；它们只是新增的步骤键，
    不构成内容变化，否则每次读取旧稿都会被判成已改动。
    """
    for key, value in current.items():
        if keys is not None and key not in keys:
            continue
        if key in LATE_FINGERPRINTS and key not in previous:
            continue
        if key == "stage_files" and isinstance(value, dict):
            before = previous.get(key)
            before = before if isinstance(before, dict) else {}
            value = {name: digest for name, digest in value.items()
                     if name in before or digest is not None}
        if previous.get(key) != value:
            return True
    return False


def _dependencies(work: dict) -> dict:
    """交付与核对依赖；`stage_files` 已覆盖各步骤保存件本身。"""
    snapshot = _snapshot(work)
    names = [
        "inputs", "materials", "material_sources", "adopted_materials", "template",
        "mapping", "body", "references", "decisions", "conditions",
    ]
    # 仅 Markdown 交付时不把 Word 模板算作 Markdown 的依赖。
    if "docx" not in _delivery_formats(work):
        names.remove("template")
    return {name: snapshot[name] for name in names}


def _delivery_stages(work: dict) -> tuple:
    """本版交付实际要求的导出与核对步骤；延期 Word 不参与 Markdown 的失效判断。"""
    formats = _delivery_formats(work)
    stages = ("docx", "md", "review") if "docx" in formats else ("md", "review")
    stages = (*stages, *(name for name in INTERVIEW_FORMATS if name in formats))
    return tuple(dict.fromkeys(stages))


def _with_delivery(work: dict, *stages) -> tuple:
    return tuple(dict.fromkeys((*stages, *_delivery_stages(work))))


def _pending(stage: dict, reason: dict) -> None:
    stage["status"] = "pending"
    stage["issues"] = [reason]


def _invalidate(work: dict, stages, reason: dict) -> None:
    for name in stages:
        _pending(work["steps"][name], reason)
    # 只有本版交付要求的步骤失效才清空核对；延期 Word 单独失效不影响 Markdown。
    if any(name in stages for name in _delivery_stages(work)):
        work["checks"] = {
            "content_consistent": False, "checked_formats": [], "notes": reason["message"],
        }


def _unconfirm(work: dict, names) -> None:
    for name in names:
        confirmation = deepcopy(work["confirmations"][name])
        confirmation["status"] = "needs_input"
        work["confirmations"][name] = confirmation


def _changed_material_location(current: dict, previous: dict):
    """指出实际变化的材料；没有可指明的具体路径时退回材料输入。"""
    for key in ("materials", "material_sources", "adopted_materials"):
        before = previous.get(key)
        after = current.get(key)
        if not isinstance(after, dict):
            continue
        if not isinstance(before, dict):
            return "steps.materials"
        for path, digest in after.items():
            if before.get(path) != digest:
                return path
        for path in before:
            if path not in after:
                return path
    return "inputs.material_paths"


def _sync_work(work: dict, inputs: dict | None = None) -> bool:
    """只核对实际摘要及已保存状态，不把孤立文件提升为已完成步骤。"""
    before = deepcopy(work)
    previous = work["fingerprints"]
    old_inputs = work["inputs"]
    if inputs is not None:
        work["inputs"] = inputs
        work["template_path"] = inputs.get("template_path")
    current = _snapshot(work)
    changed_question = work["inputs"].get("question_id") != old_inputs.get("question_id")
    if changed_question:
        reason = issue("question_changed", "研究问题选择发生变化，需要处理对应确认并更新方案。", "inputs.question_id")
        _invalidate(work, _with_delivery(work, "question", "scheme", "body"), reason)
        _unconfirm(work, ("question", "scheme"))
        work["conditions"] = {"resolved": False, "notes": "研究问题改变后须核对对应条件。"}
    drift = _material_record_drift(work)
    if current["materials"] != previous.get("materials") or (
        "material_sources" in previous
        and current["material_sources"] != previous["material_sources"]
    ) or (
        "adopted_materials" in previous
        and current["adopted_materials"] != previous["adopted_materials"]
    ) or drift:
        reason = issue(
            "materials_changed", "材料内容或路径变化，须核对受影响的摘录、引用和正文。",
            next(iter(drift), None) or _changed_material_location(current, previous),
        )
        _invalidate(work, _with_delivery(work, "materials", "body"), reason)
    old_other = {key: value for key, value in old_inputs.items() if key not in {"template_path", "material_paths", "question_id"}}
    new_other = {key: value for key, value in work["inputs"].items() if key not in {"template_path", "material_paths", "question_id"}}
    if old_other != new_other:
        _invalidate(work, _with_delivery(work, "body"), issue(
            "requirements_changed", "采用的输入或要求变化，须更新受影响正文。", "inputs",
        ))
    if current["template"] != previous.get("template") or current["mapping"] != previous.get("mapping"):
        # 仅 Markdown 交付时不因 Word 模板或栏目映射变化而使 Markdown 失效。
        _invalidate(work, ("docx", "md", "review") if "docx" in _delivery_formats(work) else ("docx",),
                    issue("template_changed", "模板或栏目映射变化，须重新导出并核对。", "inputs.template_path"))
    for stage in ("materials", "question", "scheme", "interview"):
        if work["steps"][stage]["status"] != "complete":
            continue
        if current["stage_files"][stage] != previous.get("stage_files", {}).get(stage):
            reason = issue("saved_content_changed", "已保存步骤文件变化，请通过保存入口明确采用内容。", stage)
            _invalidate(work, _with_delivery(work, stage, *_DEPENDENT[stage]), reason)
            if stage in {"question", "scheme"}:
                _unconfirm(work, ("question", "scheme") if stage == "question" else ("scheme",))
    if work["steps"]["body"]["status"] == "complete" and any(
        current[name] != previous.get(name) for name in ("body", "references")
    ):
        _invalidate(work, _with_delivery(work, "body", *_DEPENDENT["body"]), issue(
            "body_changed", "工作正文或引用发生变化，请明确采用后重新导出。", str(Path(work["directory"]) / BODY_NAME),
        ))
    dependencies = _dependencies(work)
    for name in ("docx", "md", *INTERVIEW_FORMATS):
        step = work["steps"][name]
        if step["status"] == "complete" and (
            step.get("dependencies") != dependencies
            or step.get("fingerprints") != _artifact_digests(step.get("artifacts", {}))
        ):
            _invalidate(work, (name, "review"), issue(
                "export_changed", "导出文件或其输入改变，先前导出与核对不再适用。", name,
            ))
    review = work["steps"]["review"]
    if review["status"] == "complete" and (
        review.get("dependencies") != dependencies
        or review.get("fingerprints") != _review_artifact_digests(work)
    ):
        _invalidate(work, ("review",), issue("review_changed", "核对所依据的内容已变化。", "review"))
    work["fingerprints"] = _snapshot(work)
    return work != before


def _remap(value, old: Path, new: Path, field=None):
    """只更新位于本轮目录内的记录路径，不改写源材料。"""
    if isinstance(value, dict):
        return {
            _remap(key, old, new, "path"): deepcopy(item) if key in LITERAL_FIELDS else _remap(item, old, new, key)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_remap(item, old, new, field) for item in value]
    state_paths = {
        "directory", "work_directory", "target_directory", "data", "body", "references",
        "docx", "md", "script", "qa", "preview_pdf", "location",
    }
    if field in PATH_FIELDS | PATH_LIST_FIELDS | state_paths and isinstance(value, str) and Path(value).is_absolute():
        try:
            return str(new / Path(value).relative_to(old))
        except ValueError:
            pass
    return value


def _relocate(work: dict, old: Path, new: Path) -> dict:
    relocated = _remap(deepcopy(work), old, new)
    for name, binding in relocated.get("confirmation_bindings", {}).items():
        binding["decision"] = json_digest(relocated["confirmations"][name])
    # 目录移动只改变路径值；保留文件内容摘要，恢复仍能发现真正的文件改动。
    values = {
        "inputs": json_digest(relocated["inputs"]),
        "decisions": json_digest(relocated["confirmations"]),
        "conditions": json_digest(relocated["conditions"]),
        "mapping": json_digest(relocated.get("mapping")),
    }
    relocated["fingerprints"].update(values)
    for name in ("docx", "md", "review"):
        if "dependencies" in relocated["steps"][name]:
            relocated["steps"][name]["dependencies"].update(values)
    return relocated


def _existing_artifacts(work: dict, *, valid_only=False) -> dict:
    artifacts = {}
    for name, value in work.get("artifacts", {}).items():
        owner = "docx" if name in {"preview_pdf", "page_images"} else name
        step = work["steps"].get(owner, {})
        if valid_only and step.get("status") != "complete":
            continue
        if isinstance(value, str) and Path(value).is_file():
            artifacts[name] = value
        elif isinstance(value, list):
            paths = [path for path in value if isinstance(path, str) and Path(path).is_file()]
            if paths:
                artifacts[name] = paths
    return artifacts


def _support_files(work: dict) -> None:
    directory = Path(work["directory"])
    write_record(directory / "研究计划输入.json", work["inputs"], movable_root=directory)
    notes = []
    for name in ("question", "scheme"):
        if work["confirmations"][name]["status"] != "confirmed":
            notes.append("研究问题尚待用户决定。" if name == "question" else "中文研究方案尚待用户决定。")
    if not work["conditions"].get("resolved"):
        notes.append("关键条件尚未解决：" + str(work["conditions"].get("notes", "请核对取得途径和备用办法。")))
    deferred = set(DEFERRED_FORMATS) - set(_delivery_formats(work))
    for name in STAGES:
        if name in deferred:
            # 延期的 Word 状态不作为当前交付的待确认事项。
            continue
        notes.extend(item["message"] for item in work["steps"][name].get("issues", []))
    # 交付要求先写清楚；旧记录里的格式承诺可能已经过期，注明以本版要求为准。
    formats = _delivery_formats(work)
    notes.append("本版交付格式：" + "、".join(_FORMAT_LABELS.get(name, name) for name in formats) + "。")
    deferred = [name for name in DEFERRED_FORMATS if name not in formats]
    if deferred:
        notes.append("以下格式已延期，不是本版的交付要求，也不影响本版提交："
                     + "、".join(_FORMAT_LABELS.get(name, name) for name in deferred) + "。")
    saved = [str(item) for item in work.get("pending_items", [])]
    if saved:
        notes.append("以下为先前记录的待确认事项，其中与上面交付格式不一致的格式承诺以本版要求为准。")
        notes.extend(saved)
    unique = list(dict.fromkeys(notes))
    text = "# 研究计划待确认事项\n\n"
    text += "\n".join(f"- {note}" for note in unique) if unique else "本轮没有保存额外待确认事项。草稿仍可继续讨论。"
    (directory / "研究计划待确认事项.md").write_text(text + "\n", encoding="utf-8")


def _persist_work(directory: Path, state: dict, work: dict) -> None:
    _support_files(work)
    work["fingerprints"] = _snapshot(work)
    _store_state(directory, state)


def _new_work(directory: Path, inputs: dict, base_revision=None) -> dict:
    confirmation = {"revision": None, "status": "needs_input", "decision": None}
    work = {
        "directory": str(directory), "base_revision": base_revision,
        "inputs": inputs, "fingerprints": {},
        "steps": {name: {"status": "pending", "artifacts": {}, "issues": []} for name in STAGES},
        "confirmations": {"question": deepcopy(confirmation), "scheme": deepcopy(confirmation)},
        "confirmation_bindings": {},
        "conditions": {"resolved": False, "notes": "尚未核对关键条件。"},
        "delivery_formats": list(DELIVERY_FORMATS),
        "checks": {"content_consistent": False, "checked_formats": []},
        "pending_commit": None, "committed": False, "artifacts": {},
        "template_path": inputs.get("template_path"), "mapping": None,
        "stored_path_base": STORED_PATH_BASE,
    }
    work["fingerprints"] = _snapshot(work)
    return work


def _binding_error(state: dict, inputs: dict):
    for name in ("application_id", "purpose"):
        if state["binding"][name] != inputs[name]:
            return issue("different_proposal", "申请项目或用途不同，请另建稿件目录；原稿继续保留。", f"inputs.{name}")
    return None


def _confirmation_valid(confirmation) -> bool:
    return (
        isinstance(confirmation, dict)
        and confirmation.get("status") in {"confirmed", "needs_input"}
        and "revision" in confirmation and "decision" in confirmation
        and (confirmation["status"] != "confirmed" or bool(confirmation["revision"]) and bool(confirmation["decision"]))
    )


def _body_prerequisites(work: dict) -> list:
    issues = []
    for stage in ("materials", "question", "scheme"):
        if work["steps"][stage]["status"] != "complete":
            issues.append(issue("incomplete_step", "生成完整正文前须完成对应材料、问题及方案步骤。", stage))
    for name in ("question", "scheme"):
        confirmation = work["confirmations"][name]
        binding = work.get("confirmation_bindings", {}).get(name, {})
        if (
            not _confirmation_valid(confirmation) or confirmation["status"] != "confirmed"
            or binding.get("decision") != json_digest(confirmation)
            or binding.get("content") != work["steps"][name].get("content_digest")
        ):
            issues.append(issue("confirmation_required", "对应内容尚无有效用户决定，不能生成完整正文。", name))
    if work["conditions"].get("resolved") is not True:
        issues.append(issue("conditions_unresolved", "关键条件尚未解决，请先保存取得途径和备用办法。", "conditions"))
    for path, digest in work["fingerprints"].get("materials", {}).items():
        if digest is None:
            issues.append(issue("material_unavailable", "采用的材料不能读取，请补齐或明确调整本稿材料。", path))
    return issues


def _next_steps(work: dict) -> list:
    """当前下一步不把延期的 Word 或未加选的交付文件列为未完成。"""
    formats = _delivery_formats(work)
    deferred = set(DEFERRED_FORMATS) - set(formats)
    optional = set(INTERVIEW_FORMATS) - set(formats)
    if not set(INTERVIEW_FORMATS) & set(formats):
        # 没有加选讲稿或想定问答时，保存这两项内容的步骤也不是必经步骤。
        optional.add("interview")
    return [
        name for name in STAGES
        if name not in deferred and name not in optional
        and work["steps"][name]["status"] != "complete"
    ]


CANDIDATE_GATES = ("pass", "pending", "soft_stop", "hard_stop", "merge")
STOP_REASONS = ("novelty_zero", "gap_zero", "problem_invalid")
NO_TOTAL_GATES = ("pending", "hard_stop", "merge")
# 两道硬门槛项名；判决与分数要对齐，分数与判决也要对齐。
HARD_GATE_ITEMS = ("新意落点", "空白成因")
# 每条停因要求哪道硬门槛恰好是 0：某道门槛记 0 才能用它的停因（`problem_invalid`
# 不在九项里，不要求任何一项为 0）。
STOP_REASON_GATE = {"novelty_zero": "新意落点", "gap_zero": "空白成因"}
CANDIDATE_REQUIRED = (
    "id", "question", "statement_version", "gate",
    "scores", "evidence", "experiment", "missing",
)
# 免评分判决（单候选、无需比较时）的字段与判决取值：没有比较就没有排序，
# 因而不评“备选”与“并入”，也没有 `scores`、`weights` 与总分。
VERDICT_GATES = ("pass", "pending", "hard_stop")
VERDICT_REQUIRED = (
    "id", "statement_version", "gate", "experiment", "missing", "evidence",
)


def _candidate_scores_problems(scores, extra_ids=()) -> list:
    """判决记录的入参检查：一次列出全部问题，由调用方统一报错。

    记录与分数分开：判决词、总分处理、停因与三样内容必须互相对得上，缺证据
    的记「未评」而不是 0 分。这里检查结构、取值与判决对齐，不重算分数，也不
    判断证据本身是否成立。

    两类检查刻意分开：字段自身的错误（类型、取值、键集合）先全部收集，
    与 `gate` 有关的对齐要求只在 `gate` 合法时才查。这样一条记录同时有多处
    独立错误时也能一次报全，而不是遇到非法 `gate` 就返回。
    """
    if not isinstance(scores, dict):
        return ["candidate_scores 须是对象，含 weights、evidence_cutoff 和 items。"]
    problems = []
    for name in ("weights", "evidence_cutoff"):
        if name not in scores:
            problems.append(f"candidate_scores 缺少 {name}。")
    cutoff = scores.get("evidence_cutoff")
    if "evidence_cutoff" in scores and (
        not isinstance(cutoff, str) or not cutoff.strip()
    ):
        problems.append("candidate_scores.evidence_cutoff 须是非空字符串（证据截止日期）。")
    weights = scores.get("weights")
    if "weights" in scores and (
        not isinstance(weights, dict) or not weights
        or any(type(value) not in (int, float) or isinstance(value, bool) or value < 0
               for value in weights.values())
    ):
        problems.append("candidate_scores.weights 须是非空对象，权重为不为负的数字。")
        weights = None
    items = scores.get("items")
    if "items" not in scores or not isinstance(items, list) or not items:
        problems.append("candidate_scores.items 须是非空数组。")
        return problems
    seen = {}
    for index, item in enumerate(items):
        label = f"items[{index}]"
        if not isinstance(item, dict):
            problems.append(f"{label} 须是对象。")
            continue
        identifier = item.get("id")
        version = item.get("statement_version")
        # 先判类型再构造键：畸形输入也按 ValueError 报问题，不能抛 TypeError。
        if not isinstance(identifier, str) or not identifier.strip():
            problems.append(f"{label} 缺少 id。")
            identifier = None
        if not isinstance(version, str) or not version.strip():
            problems.append(f"{label} 的 statement_version 须是非空字符串。")
            version = None
        # id 是候选身份，跨题面版本不变；同一版本只留一条记录。
        key = (identifier, version)
        if identifier is None or version is None:
            pass
        elif key in seen:
            problems.append(
                f"candidate_scores 内 {identifier} 的题面版本 "
                f"{item.get('statement_version')!r} 重复；同一候选同一版本只留一条。"
            )
        else:
            seen[key] = item
        for name in CANDIDATE_REQUIRED:
            if name not in item:
                problems.append(f"{label}（{identifier or '无 id'}）缺少 {name}。")
        if isinstance(identifier, str) and identifier:
            label = f"{label}（{identifier}）"
        problems.extend(_candidate_problems(label, item, weights))
    # 候选身份可以只出现在 `verdicts` 里：`merged_into` 指向的是候选身份，
    # 不是某一版记录，因此身份集合要把本次保存里出现过的 id 都算上。
    identities = {identifier for identifier, _ in seen} | set(extra_ids)
    for (identifier, _), item in seen.items():
        merged = item.get("merged_into")
        if item.get("gate") == "merge" and isinstance(merged, str) and merged not in identities:
            problems.append(f"候选 {identifier} 的 merged_into 指向不存在的候选：{merged}。")
    return problems


def _entries_problems(label: str, item: dict, name: str) -> list:
    """`experiment`、`missing` 两个数组字段的检查：必须是字符串数组。"""
    value = item.get(name)
    if name not in item:
        return []
    if not isinstance(value, list):
        return [f"{label} 的 {name} 须是数组。"]
    if any(not isinstance(entry, str) or not entry.strip() for entry in value):
        return [f"{label} 的 {name} 每项须是非空字符串，不能有 null 或空串。"]
    return []


def _candidate_problems(label: str, item: dict, weights) -> list:
    """单条记录的结构与取值问题；与 `gate` 无关的部分不因 `gate` 非法而跳过。"""
    problems = []
    for name in ("experiment", "missing"):
        problems.extend(_entries_problems(label, item, name))
    problems.extend(_score_problems(label, item, weights))
    gate = item.get("gate")
    if gate not in CANDIDATE_GATES:
        problems.append(
            f"{label} 的 gate 须是 {'、'.join(CANDIDATE_GATES)} 之一，实为 {gate!r}；"
            "以下与 gate 有关的检查因 gate 非法而无法进行。"
        )
        return problems
    problems.extend(_gate_problems(label, item, gate, weights))
    return problems


def _score_problems(label: str, item: dict, weights) -> list:
    """分数与依据的结构检查：键集合、取值、逐项依据。与 `gate` 无关。

    两个字段各自判断类型并累积错误：一方写错不能让另一方的错误不被报出。
    `evidence` 与 `scores` 的键集合必须完全一致——多一个键就是一条与分数无关的
    依据，空白串或非文本不是依据。
    """
    problems = []
    scores = item.get("scores")
    evidence = item.get("evidence")
    has_scores = "scores" in item and isinstance(scores, dict)
    has_evidence = "evidence" in item and isinstance(evidence, dict)
    if not has_scores:
        problems.append(f"{label} 的 scores 须是对象，逐项写分数。")
    if not has_evidence:
        problems.append(f"{label} 的 evidence 须是对象，逐项写依据。")
    if has_scores:
        for name, score in scores.items():
            if score is None:
                continue
            if type(score) not in (int, float) or isinstance(score, bool) or score not in (0, 1, 2):
                problems.append(f"{label} 的 {name} 分数须是 0、1、2 或 null（未评）。")
        if weights is not None:
            # 少评一项不等于「未评」：缺键就是缺项，必须显式写 null。
            missing_keys = sorted(set(weights) - set(scores))
            extra_keys = sorted(set(scores) - set(weights))
            if missing_keys:
                problems.append(
                    f"{label} 的 scores 缺少权重表里的项：{'、'.join(missing_keys)}；"
                    "没判的项要写 null，不能直接删掉。"
                )
            if extra_keys:
                problems.append(
                    f"{label} 的 scores 含有权重表里没有的项：{'、'.join(extra_keys)}。"
                )
    if has_evidence:
        # 依据的取值能独立判断：`scores` 写错形态时也要把空白依据一起报出，
        # 否则用户改完分数还会再被打回一次。
        blank_evidence = sorted(
            name for name, text in evidence.items()
            if not isinstance(text, str) or not text.strip()
        )
        if blank_evidence:
            problems.append(
                f"{label} 的 evidence 这些项不是有效依据：{'、'.join(blank_evidence)}；"
                "每项都要写去掉首尾空白后仍有内容的文字。"
            )
    if has_scores and has_evidence:
        # 键集合要两边都是对象才比较：一方写错形态时缺哪一项无从判定。
        missing_evidence = sorted(set(scores) - set(evidence))
        extra_evidence = sorted(set(evidence) - set(scores))
        if missing_evidence:
            problems.append(
                f"{label} 的 evidence 缺少这些项的依据：{'、'.join(missing_evidence)}；"
                "每一项分数后面都要跟一句依据。"
            )
        if extra_evidence:
            problems.append(
                f"{label} 的 evidence 含有 scores 里没有的项：{'、'.join(extra_evidence)}；"
                "依据要逐项对应分数，不能多写没有对应分数的键。"
            )
    return problems


def _gate_problems(label: str, item: dict, gate: str, weights) -> list:
    """只在 `gate` 合法时检查：总分、停因、并入目标、三样内容与判决的对应。"""
    problems = []
    total = item.get("total")
    if gate in NO_TOTAL_GATES and total is not None:
        problems.append(f"{label} 记 {gate}，不得给总分；结果留在 experiment 里。")
    if gate in ("pass", "soft_stop"):
        if type(total) not in (int, float) or isinstance(total, bool):
            problems.append(f"{label} 记 {gate}，须给数值总分。")
    if gate == "hard_stop":
        reason = item.get("stop_reason")
        if reason not in STOP_REASONS:
            problems.append(
                f"{label} 记 hard_stop，须写 stop_reason 为 {'、'.join(STOP_REASONS)} 之一。"
            )
    elif "stop_reason" in item:
        problems.append(f"{label} 记 {gate}，不得写 stop_reason。")
    if gate == "merge":
        merged = item.get("merged_into")
        if not isinstance(merged, str) or not merged.strip():
            problems.append(f"{label} 记 merge，须写 merged_into 指向被并入的候选 id。")
        elif merged == item.get("id"):
            problems.append(f"{label} 的 merged_into 不能指向自己。")
    elif "merged_into" in item:
        problems.append(f"{label} 记 {gate}，不得写 merged_into。")
    evidence = item.get("evidence")
    if gate in ("hard_stop", "pass", "soft_stop") and isinstance(evidence, dict) and not evidence:
        problems.append(f"{label} 记 {gate}，evidence 不能为空。")
    missing = item.get("missing")
    if gate == "pending" and isinstance(missing, list) and not missing:
        problems.append(f"{label} 记 pending，missing 不能为空；没有待办就不算待补。")
    scores = item.get("scores")
    if isinstance(scores, dict):
        # 门槛没判过就不等于门槛已过：硬门槛项未评时整条只能记 pending。
        # 不只拦 pass/soft_stop——hard_stop 与 merge 同样要求门槛已经判过，
        # 否则「还没查」就能顺着 gap_zero 走入停因，正是本轮要堵的路径。
        if gate != "pending":
            for name in HARD_GATE_ITEMS:
                if name in scores and scores[name] is None:
                    problems.append(
                        f"{label} 的硬门槛项 {name} 记未评，只能记 pending；"
                        f"不能记 {gate}，改记 pending 并写明缺什么。"
                    )
        for name in HARD_GATE_ITEMS:
            if name not in scores:
                problems.append(
                    f"{label} 的 scores 缺少硬门槛项 {name}；两道硬门槛必须逐项记分或记 null。"
                )
        problems.extend(_gate_score_alignment(label, item, gate, scores, weights))
    return problems


def _gate_score_alignment(label: str, item: dict, gate: str, scores: dict,
                         weights) -> list:
    """判决与两项硬门槛分数互相对齐。

    判决词和分数是两件事，但方向必须一致：硬门槛记 0 才允许用它的停因，
    记了 0 就不能记可推进或备选。「判停要有依据、通过要有门槛」在两边都不能
    只说一边：`gate` 写停而分数全过、或分数未过硬门槛却记 `pass`，
    都会让候选被误读成与事实相反的结论，正是本轮要堵的路径。

    `weights` 只用于一条：`pass`、`soft_stop` 要求总分照算，而总分分母是
    “已评项的正权重之和”；一项正权重都不剩时分母为零，这两种判决没有依据。
    """
    problems = []
    unrated = [name for name in HARD_GATE_ITEMS if scores.get(name) is None]
    if unrated:
        # 未评项不做分数对齐：未评本身已由上面的规则限制为 pending。
        return problems
    valued = {name: scores[name] for name in HARD_GATE_ITEMS if name in scores}
    if not valued:
        return problems
    if gate == "hard_stop":
        reason = item.get("stop_reason")
        # 先判类型再查表：停因写成列表或对象时不能在这里抛 TypeError，
        # 否则已经收集到的问题和另一个对象的问题都返回不了。
        required = STOP_REASON_GATE.get(reason) if isinstance(reason, str) else None
        if required is None:
            # `problem_invalid` 不是九项之一，不要求哪一项为 0；
            # 非法停因已在 `_gate_problems` 报过，这里不重复报。
            # `hard_stop` 本来就不给总分，分母与它无关。
            return problems
        if valued.get(required) != 0:
            problems.append(
                f"{label} 记 hard_stop 且停因 {reason}，但 {required} 为 "
                f"{valued.get(required)!r}；这条停因要求 {required} = 0（已证伪）。"
            )
        return problems
    if gate in ("pass", "soft_stop"):
        # 文档定义：pass 是“两条硬门槛都过”，soft_stop 是“硬门槛过了，但有软门槛
        # 为 0”。merge 的判据只说并入另一个候选，没有硬门槛要求，不在此列。
        zeroed = sorted(name for name, score in valued.items() if score == 0)
        if zeroed:
            problems.append(
                f"{label} 记 {gate}，但硬门槛 {'、'.join(zeroed)} 为 0；"
                "硬门槛为 0 的候选不进入排序与推荐，须记 hard_stop 并写对应停因，"
                "或改记 pending 并写明缺什么。"
            )
        problems.extend(_denominator_problems(label, gate, scores, weights))
    return problems


def _denominator_problems(label: str, gate: str, scores: dict, weights) -> list:
    """`pass`、`soft_stop` 要求总分照算，分母不能为零。

    分母是“已评项的正权重之和”：权重可以设为 0，也可以整表只留一项正权重；
    若那一项恰好是「未评」，剔除未评项后分母就是 0，总分没有定义。
    这种记录只能记 `pending` 并写明缺哪项，不能记成可推进或备选。
    """
    if weights is None or not isinstance(weights, dict):
        # 权重表本身已判非法，分母无从计算，不叠加报错。
        return []
    counted = [
        name for name, weight in weights.items()
        if isinstance(weight, (int, float)) and not isinstance(weight, bool)
        and weight > 0 and scores.get(name) is not None
    ]
    if counted:
        return []
    return [
        f"{label} 记 {gate}，但没有可计入总分的正权重项（正权重项都已记未评或不存在）；"
        "剔除未评项后分母为零，总分无法照算。改记 pending 并写明缺哪项，或补齐后重判。"
    ]


def _check_candidate_scores(scores, extra_ids=()) -> None:
    """拒绝不合规的判决记录，一次列出全部问题，避免违规记录静默入库。"""
    problems = _candidate_scores_problems(scores, extra_ids)
    if problems:
        raise ValueError("判决记录不合规：" + "；".join(problems))


def _verdict_problems(label: str, item: dict, seen: dict) -> list:
    """单条免评分判决的问题；与 `candidate_scores` 的分数规则无关。"""
    problems = []
    for name in VERDICT_REQUIRED:
        if name not in item:
            problems.append(f"{label} 缺少 {name}。")
    identifier = item.get("id")
    version = item.get("statement_version")
    if not isinstance(identifier, str) or not identifier.strip():
        problems.append(f"{label} 的 id 须是非空字符串。")
        identifier = None
    if not isinstance(version, str) or not version.strip():
        problems.append(f"{label} 的 statement_version 须是非空字符串。")
        version = None
    if identifier is not None and version is not None:
        key = (identifier, version)
        if key in seen:
            problems.append(
                f"verdicts 内 {identifier} 的题面版本 {version!r} 重复；"
                "同一候选同一版本只留一条。"
            )
        else:
            seen[key] = item
    for name in ("experiment", "missing", "evidence"):
        problems.extend(_entries_problems(label, item, name))
    # 两种形态不混用：免评分记录里出现分数、权重或总分，说明这条本该走
    # `candidate_scores`，或者是在旧形态上打补丁，两种都可能掩盖“没算过总分”。
    for name in ("scores", "weights", "total"):
        if name in item:
            problems.append(
                f"{label} 是免评分判决，不得写 {name}；"
                "要记分数与总分就改走 candidate_scores 并满足它的规则。"
            )
    gate = item.get("gate")
    if gate not in VERDICT_GATES:
        problems.append(
            f"{label} 的 gate 须是 {'、'.join(VERDICT_GATES)} 之一（免评分时不评“备选”与“并入”），"
            f"实为 {gate!r}；以下与 gate 有关的检查因 gate 非法而无法进行。"
        )
        return problems
    evidence = item.get("evidence")
    if gate in ("pass", "hard_stop") and isinstance(evidence, list) and not evidence:
        problems.append(f"{label} 记 {gate}，evidence 不能为空；要写明哪条证据支撑这个判决。")
    missing = item.get("missing")
    if gate == "pending" and isinstance(missing, list) and not missing:
        problems.append(f"{label} 记 pending，missing 不能为空；没有待办就不算待补。")
    if gate == "hard_stop":
        reason = item.get("stop_reason")
        if reason not in STOP_REASONS:
            problems.append(
                f"{label} 记 hard_stop，须写 stop_reason 为 {'、'.join(STOP_REASONS)} 之一。"
            )
    elif "stop_reason" in item:
        problems.append(f"{label} 记 {gate}，不得写 stop_reason。")
    return problems


def _verdicts_problems(verdicts) -> list:
    """免评分判决记录的结构与判决问题；不抛错，交由调用方合并报出。

    这是“没有候选比较、因而不评分”时的保存形态：只记判决、题面版本、实验说明、
    支撑证据与缺项，不记分数与总分。与 `candidate_scores` 各按自己的规则检查。
    """
    if not isinstance(verdicts, dict):
        return ["verdicts 须是对象，含 evidence_cutoff 和 items。"]
    problems = []
    cutoff = verdicts.get("evidence_cutoff")
    if "evidence_cutoff" not in verdicts or not isinstance(cutoff, str) or not cutoff.strip():
        problems.append("verdicts.evidence_cutoff 须是非空字符串（证据截止日期）。")
    items = verdicts.get("items")
    if "items" not in verdicts or not isinstance(items, list) or not items:
        problems.append("verdicts.items 须是非空数组。")
        return problems
    seen = {}
    for index, item in enumerate(items):
        label = f"verdicts.items[{index}]"
        if not isinstance(item, dict):
            problems.append(f"{label} 须是对象。")
            continue
        identifier = item.get("id")
        if isinstance(identifier, str) and identifier.strip():
            label = f"{label}（{identifier}）"
        problems.extend(_verdict_problems(label, item, seen))
    return problems


def _check_verdicts(verdicts) -> None:
    """单独校验免评分判决记录（`verdicts` 一个对象）。"""
    problems = _verdicts_problems(verdicts)
    if problems:
        raise ValueError("免评分判决记录不合规：" + "；".join(problems))


def _verdict_identities(verdicts) -> set:
    """`verdicts` 里出现过的候选 id；供 `merged_into` 的身份判断使用。"""
    if not isinstance(verdicts, dict):
        return set()
    items = verdicts.get("items")
    if not isinstance(items, list):
        return set()
    return {
        item["id"] for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip()
    }


def _cross_object_duplicate_problems(candidate_scores, verdicts) -> list:
    """同一 `(id, statement_version)` 不能同时出现在两个对象里。

    两个对象各自查重只能保证“本对象内不重复”，同一条题面版本仍可能在
    `candidate_scores` 记一个判决、在 `verdicts` 记另一个相反判决，两条都落盘后
    汇总无法确定该采用哪一条。题面版本是判决的身份，整次保存只能有一条。
    """
    seen = {}
    problems = []
    for label, obj in (("candidate_scores", candidate_scores), ("verdicts", verdicts)):
        if not isinstance(obj, dict):
            continue
        items = obj.get("items")
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            identifier = item.get("id")
            version = item.get("statement_version")
            if not isinstance(identifier, str) or not isinstance(version, str):
                continue
            key = (identifier, version)
            if key in seen:
                # 同一对象内的重复已由各自的对象校验报过，这里只报跨对象那一类，
                # 否则错误文本会写成“同时记在 verdicts 与 verdicts”这类废话。
                if seen[key] != label:
                    problems.append(
                        f"{identifier} 的题面版本 {version!r} 同时记在 {seen[key]} 与 {label}；"
                        "同一题面版本的判决只能有一条：保留一条，删掉或移走另一条。"
                    )
            else:
                seen[key] = label
    return problems


def _check_materials_records(data: dict) -> None:
    """校验材料步骤里的判决记录，两个可选对象的问题合并成一次报错。

    两个对象可以同时出现，但一条记录的错不能让另一个对象的问题看不见：
    一次保存只说对了一半的错，执行者补齐后还会再被打回一次。
    """
    problems = []
    # 候选身份可能只记在 `verdicts` 里，`merge` 允许指向这种候选。
    extra_ids = _verdict_identities(data.get("verdicts"))
    if "candidate_scores" in data:
        problems.extend(_candidate_scores_problems(
            data["candidate_scores"], extra_ids,
        ))
    if "verdicts" in data:
        problems.extend(_verdicts_problems(data["verdicts"]))
    problems.extend(_cross_object_duplicate_problems(
        data.get("candidate_scores"), data.get("verdicts"),
    ))
    if problems:
        raise ValueError("判决记录不合规：" + "；".join(problems))


def _check_interview_payload(data: dict) -> None:
    """讲稿步骤的入参检查：不接受的写法直接拒绝，避免静默覆盖已保存内容。

    两项内容都只能整体替换成非空对象；写成 null 或空对象一律报错，而不是当作
    删除或过滤掉，这样误传不会把已写好的讲稿或问答悄悄抹掉。
    """
    from ._interview import FILES

    if not isinstance(data, dict):
        raise ValueError("讲稿步骤的 data 须是对象，含 script 或 qa。")
    given = [name for name in FILES if name in data]
    if not given:
        raise ValueError("讲稿步骤须至少保存 script 或 qa 对象")
    for name in given:
        value = data[name]
        if not isinstance(value, dict) or not value:
            raise ValueError(
                f"讲稿步骤的 {name} 须是非空对象；本步骤不支持删除单项，"
                "写成 null 或空对象会被拒绝。"
            )


def _merged_interview(work: dict, data: dict) -> dict:
    """把本次未提交的讲稿项沿用步骤里已保存的内容。

    讲稿与想定问答共用同一个保存件；只补其中一项时，另一项仍按已有内容参与
    检查与导出。本次显式给出的字段覆盖旧值。
    """
    from ._interview import FILES, step_data

    merged = {name: step_data(work, name) for name in FILES}
    for name in FILES:
        # 入参检查已拒绝 null 与空对象，这里只需覆盖有值的那一项。
        if isinstance(data.get(name), dict) and data[name]:
            merged[name] = data[name]
    kept = {name: value for name, value in merged.items() if value is not None}
    if isinstance(data, dict) and "pending_items" in data:
        kept["pending_items"] = data["pending_items"]
    return kept


def _interview_problems(data: dict, formats) -> list:
    """讲稿步骤的检查问题。

    已提供的内容一律检查，避免未加选的内容带着错误保存；只有已加选的交付文件
    在缺内容时才算问题。
    """
    from ._interview import validate

    problems = []
    for name in INTERVIEW_FORMATS:
        value = data.get(name)
        if value is None:
            if name in formats:
                problems.append(issue(
                    "interview_missing",
                    "本稿已加选这项交付文件，请在讲稿步骤中一并保存它的内容。",
                    name,
                ))
            continue
        problems.extend(validate(name, value))
    return problems


def begin_revision(request: dict) -> dict:
    inputs = _normal_inputs(request["inputs"])
    with _locked(request["proposal_dir"]) as directory:
        state, rejected = _load(directory, request, create=True)
        if rejected:
            return rejected
        if state is None:
            state = {
                "schema_version": 1, "proposal_id": f"proposal-{uuid4().hex}",
                "binding": {name: inputs[name] for name in ("application_id", "purpose", "question_id")},
                "state_version": 0, "current": None, "works": {},
            }
        binding_error = _binding_error(state, inputs)
        if binding_error:
            return _response(state, "needs_input", [binding_error])
        revision = datetime.now(timezone.utc).strftime("r-%Y%m%dT%H%M%S-") + uuid4().hex[:12]
        work_directory = directory / "工作版本" / revision
        current = _current_id(state)
        if current:
            baseline = state["works"][current]
            old_directory = Path(baseline["directory"])
            shutil.copytree(old_directory, work_directory)
            work = _relocate(baseline, old_directory, work_directory)
            work.update(base_revision=current, committed=False, pending_commit=None)
            # 从旧版建立的新工作版同样采用 Markdown；历史双格式只读记录不在此迁移。
            work["delivery_formats"] = list(DELIVERY_FORMATS)
            # 新版的正文可复用，格式导出和核对必须另做。
            for path in _file_paths(work.get("artifacts", {})):
                candidate = Path(path)
                if candidate.is_relative_to(work_directory) and candidate.is_file():
                    candidate.unlink()
            work["artifacts"] = {}
            for stage in ("docx", "md", "script", "qa", "review"):
                work["steps"][stage] = {"status": "pending", "artifacts": {}, "issues": []}
            work["checks"] = {"content_consistent": False, "checked_formats": []}
            _sync_work(work, _remap(inputs, old_directory, work_directory))
        else:
            work_directory.mkdir(parents=True)
            work = _new_work(work_directory, inputs)
        state["works"][revision] = work
        _persist_work(directory, state, work)
        return _response(state, revision_id=revision, directory=str(work_directory))


def _stage_content(stage: str, data):
    if stage == "question":
        return {"question_id": data["question_id"], "text": data["text"]}
    if stage == "scheme":
        return {"scheme": data["scheme"], "conditions": data["conditions"]}
    if stage == "body":
        return {"body": data["body"], "references": data["references"]}
    return {key: value for key, value in data.items() if key != "path_base"} if isinstance(data, dict) else data


def _adopt_input_requirements(inputs: dict, data) -> dict:
    """材料步骤整理出的项目要求随该步骤一并采用，写回本稿输入。

    学校要求与申请者资料通常由材料步骤读取；要求摘要留在这个步骤里时，
    输入记录也要同步，不能继续保留「目标语言待确认」之类的旧值。
    """
    requirements = data.get("input_requirements") if isinstance(data, dict) else None
    if not isinstance(requirements, dict) or not requirements:
        return inputs
    adopted = deepcopy(inputs)
    adopted["requirements"] = deepcopy(requirements)
    return adopted


def save_revision(request: dict) -> dict:
    stage = request["stage"]
    if stage not in {"materials", "question", "scheme", "body", "interview"}:
        raise ValueError("stage 必须是 materials、question、scheme、body 或 interview")
    data = deepcopy(request["data"])
    if stage in {"question", "scheme"} and not _confirmation_valid(data.get("confirmation")):
        raise ValueError("confirmation 必须保存修订编号、有效状态和用户原意及来源")
    if stage == "question" and (not data.get("question_id") or not isinstance(data.get("text"), str) or not data["text"].strip()):
        raise ValueError("问题步骤须包含 question_id 和实际问题 text")
    if stage == "scheme" and (
        "scheme" not in data or not isinstance(data.get("conditions"), dict)
        or type(data["conditions"].get("resolved")) is not bool or "notes" not in data["conditions"]
    ):
        raise ValueError("方案步骤须包含 scheme 与 conditions: {resolved, notes}")
    if stage == "body" and (
        not isinstance(data.get("body"), dict) or not isinstance(data["body"].get("blocks"), list)
        or not isinstance(data["body"].get("meta"), dict) or not isinstance(data["body"].get("pandoc-api-version"), list)
        or not isinstance(data.get("references"), list)
    ):
        raise ValueError("正文步骤须保存 Pandoc JSON 文档及 references 数组")
    if stage == "interview":
        _check_interview_payload(data)
    if stage == "materials" and isinstance(data, dict) and (
        "candidate_scores" in data or "verdicts" in data
    ):
        _check_materials_records(data)
    with _locked(request["proposal_dir"]) as directory:
        state, rejected = _load(directory, request)
        if rejected:
            return rejected
        work, rejected = _work_for_write(directory, state, request)
        if rejected:
            return rejected
        work_directory = Path(work["directory"])
        if isinstance(data, dict) and data.get("path_base") == STORED_PATH_BASE:
            data = decode_record_paths(data, work_directory)
        changed = _sync_work(work)
        if stage == "body":
            problems = _body_prerequisites(work)
            if problems:
                if changed:
                    _persist_work(directory, state, work)
                return _response(state, "needs_input", problems)
        saved_data = encode_record_paths(data, work_directory, movable_root=work_directory)
        if stage == "interview":
            # 一次只交其中一项时，把步骤里已有的另一项带上，补齐缺项不必重写全部内容。
            saved_data = _merged_interview(work, saved_data)
        content_digest = json_digest(_stage_content(stage, saved_data))
        differs = work["steps"][stage].get("content_digest") != content_digest
        if differs:
            _invalidate(work, _DEPENDENT[stage],
                        issue("step_changed", "上游步骤已更新，需要继续对应的后续步骤。", stage))
            if stage == "question":
                _unconfirm(work, ("scheme",))
        # 每次保存件独立命名；状态替换中断也不会覆盖先前保存件。
        # 步骤快照与正文同在修订根，嵌入的 Pandoc 目标使用相同文件基准。
        data_path = work_directory / f"步骤-{stage}-{uuid4().hex}.json"
        write_record(data_path, saved_data, movable_root=work_directory)
        artifacts = {"data": str(data_path)}
        if stage in {"question", "scheme"}:
            work["confirmations"][stage] = deepcopy(data["confirmation"])
            work["confirmation_bindings"][stage] = {
                "content": content_digest, "decision": json_digest(data["confirmation"]),
            }
        if stage == "question":
            work["inputs"]["question_id"] = data["question_id"]
        if stage == "scheme":
            work["conditions"] = deepcopy(data["conditions"])
        if stage == "materials":
            work["inputs"] = _adopt_input_requirements(work["inputs"], saved_data)
        if stage == "body":
            write_record(work_directory / BODY_NAME, saved_data["body"], movable_root=work_directory)
            write_record(work_directory / REFERENCE_NAME, saved_data["references"], movable_root=work_directory)
            artifacts.update(body=str(work_directory / BODY_NAME), references=str(work_directory / REFERENCE_NAME))
        if isinstance(data, dict) and "pending_items" in data:
            work["pending_items"] = deepcopy(data["pending_items"])
        if stage == "interview":
            # 内容先落盘，检查问题作为待办返回；不会因为某项未达标而丢掉已写的话。
            problems = _interview_problems(saved_data, _delivery_formats(work))
            work["steps"][stage] = {
                "status": "pending" if problems else "complete",
                "artifacts": artifacts, "issues": problems,
                "content_digest": content_digest, "fingerprints": _artifact_digests(artifacts),
                "path_base": STORED_PATH_BASE,
            }
            _persist_work(directory, state, work)
            if problems:
                return _response(state, "needs_input", problems,
                                 revision_id=request["revision_id"], directory=work["directory"])
            return _response(state, revision_id=request["revision_id"], directory=work["directory"])
        work["steps"][stage] = {
            "status": "complete", "artifacts": artifacts, "issues": [],
            "content_digest": content_digest, "fingerprints": _artifact_digests(artifacts),
            "path_base": STORED_PATH_BASE,
        }
        _persist_work(directory, state, work)
        return _response(state, revision_id=request["revision_id"], directory=work["directory"])


def _accept_export_result(work: dict, formats: list, exported: dict) -> None:
    # 仅 Markdown 时不接受模板字段，也不改写输入的模板引用。
    word_export = "docx" in formats
    for name in ("mapping", "template_path", "template_mode"):
        if name in exported and (word_export or name == "template_mode"):
            work[name] = deepcopy(exported[name])
    if "template_path" in exported and word_export:
        work["inputs"]["template_path"] = exported["template_path"]
    actual = {}
    for name, value in exported.get("artifacts", {}).items():
        if isinstance(value, str) and Path(value).is_file():
            actual[name] = _absolute(value)
        elif isinstance(value, list):
            paths = [_absolute(path) for path in value if Path(path).is_file()]
            if paths:
                actual[name] = paths
    work["artifacts"].update(actual)
    dependencies = _dependencies(work)
    for name in formats:
        if name == "docx":
            names = ("docx", "preview_pdf", "page_images")
        elif name in INTERVIEW_FORMATS:
            names = (name,)
        else:
            names = ("md",)
        artifacts = {key: actual[key] for key in names if key in actual}
        default_status = "complete" if exported["status"] == "ready" else "failed"
        status = exported.get("format_status", {}).get(name, default_status)
        if any(key not in artifacts for key in names):
            status = "failed"
        work["steps"][name] = {
            "status": status, "artifacts": artifacts,
            "issues": [] if status == "complete" else deepcopy(exported.get("issues", [])),
            "dependencies": dependencies, "fingerprints": _artifact_digests(artifacts),
        }
    _invalidate(work, ("review",), issue("export_updated", "导出已更新，需重新读回核对内容。", "review"))


def _interview_export_problems(work: dict) -> list:
    """讲稿与想定问答要先通过内容检查，才生成交付文件。"""
    if work["steps"]["interview"]["status"] == "complete":
        return []
    return [issue(
        "interview_incomplete",
        "讲稿步骤尚未通过检查，请按返回的问题补齐内容后再导出。",
        "interview",
    )]


def export_revision(request: dict) -> dict:
    # 省略 formats 时交付本稿全部已选加的文件。
    formats = request.get("formats")
    if formats is not None and (
        not isinstance(formats, list) or not formats
        or any(name not in {"docx", "md", *INTERVIEW_FORMATS} for name in formats)
    ):
        raise ValueError("formats 必须是 docx、md、script、qa 的非空子集")
    with _locked(request["proposal_dir"]) as directory:
        state, rejected = _load(directory, request)
        if rejected:
            return rejected
        work, rejected = _work_for_write(directory, state, request)
        if rejected:
            return rejected
        if formats is None:
            formats = _delivery_formats(work)
        else:
            formats = list(dict.fromkeys(formats))
        inputs = deepcopy(work["inputs"])
        # 仅 Markdown 时不接受也不采用 Word 模板参数；旧分支作为延期实现保留。
        if "docx" in formats:
            if "template_path" in request:
                inputs["template_path"] = _absolute(request["template_path"]) if request["template_path"] else None
                if inputs["template_path"] != work.get("template_path") and "mapping" not in request:
                    work["mapping"] = None
            if "mapping" in request:
                work["mapping"] = deepcopy(request["mapping"])
        missing = [name for name in formats
                   if name in INTERVIEW_FORMATS and name not in _delivery_formats(work)]
        if missing:
            return _response(state, "needs_input", [issue(
                "deliverable_not_selected",
                "本稿的 deliverables 未包含这项文件；请先在本稿输入中加选，再生成。",
                name,
            ) for name in missing], artifacts=_delivery_artifacts(work, valid_only=True))
        changed = _sync_work(work, inputs)
        problems = _body_prerequisites(work)
        if work["steps"]["body"]["status"] != "complete":
            problems.append(issue("body_required", "请先保存本轮有效正文，再导出稿件。", "body"))
        if any(name in formats for name in INTERVIEW_FORMATS):
            problems.extend(_interview_export_problems(work))
        if problems:
            if changed:
                _persist_work(directory, state, work)
            return _response(state, "needs_input", problems, artifacts=_delivery_artifacts(work, valid_only=True))
        issues: list[dict] = []
        status = "ready"
        document_formats = [name for name in formats if name in {"docx", "md"}]
        if document_formats:
            from ._documents import export_documents
            try:
                exported = export_documents(
                    work, document_formats,
                    template_path=work.get("template_path") if "docx" in document_formats else None,
                    mapping=work.get("mapping") if "docx" in document_formats else None,
                )
            except Exception as error:
                # 不把异常改成成功；先保留已写出的文件及失败进度。
                partial = {}
                for name in document_formats:
                    path = Path(work["directory"]) / FORMAT_NAMES[name]
                    if path.is_file():
                        partial[name] = str(path)
                _accept_export_result(work, document_formats, {
                    "status": "blocked", "artifacts": partial,
                    "issues": [issue("export_failed", str(error), work["directory"])],
                })
                _persist_work(directory, state, work)
                raise
            _accept_export_result(work, document_formats, exported)
            issues.extend(exported.get("issues", []))
            if exported["status"] != "ready" or any(
                work["steps"][name]["status"] != "complete" for name in document_formats
            ):
                status = "blocked"
        interview_formats = [name for name in formats if name in INTERVIEW_FORMATS]
        if interview_formats:
            from ._interview import export_interview
            exported_interview = export_interview(work, interview_formats)
            _accept_export_result(work, interview_formats, exported_interview)
            issues.extend(exported_interview["issues"])
            if exported_interview["status"] != "ready":
                status = "blocked"
        _persist_work(directory, state, work)
        return _response(state, status, issues, artifacts=_delivery_artifacts(work, valid_only=True))


def review_revision(request: dict) -> dict:
    """当前不需要 page_review：实际读回 Markdown 与正式正文核对。"""
    with _locked(request["proposal_dir"]) as directory:
        state, rejected = _load(directory, request)
        if rejected:
            return rejected
        work, rejected = _work_for_write(directory, state, request)
        if rejected:
            return rejected
        _sync_work(work)
        from ._documents import review_documents
        from ._interview import review_interview
        reviewed = review_documents(work)
        checks = deepcopy(reviewed.get("checks", {}))
        issues = deepcopy(reviewed.get("issues", []))
        formats = _delivery_formats(work)
        interview_formats = [name for name in formats if name in INTERVIEW_FORMATS]
        exported = all(work["steps"][name]["status"] == "complete" for name in formats)
        artifacts = _delivery_artifacts(work)
        checks["content_consistent"] = bool(checks.get("content_consistent")) and exported
        checks["checked_formats"] = list(formats)
        if not exported:
            issues.append(issue(
                "exports_incomplete", "当前交付格式尚未完成或其内容已变化，不能沿用先前核对。", "exports",
            ))
        if interview_formats:
            consistent, details, digests = review_interview(work, interview_formats)
            checks["deliverable_digests"] = digests
            if not consistent:
                checks["content_consistent"] = False
                issues.append(issue(
                    "content_inconsistent", "；".join(details), str(work["directory"]),
                ))
        work["checks"] = checks
        complete = bool(checks["content_consistent"])
        work["steps"]["review"] = {
            "status": "complete" if complete else "failed", "artifacts": {}, "issues": issues,
            "dependencies": _dependencies(work), "fingerprints": _review_artifact_digests(work),
        }
        _persist_work(directory, state, work)
        return _response(state, "ready" if complete else "blocked", issues, checks=checks, artifacts=artifacts)


def _commit_problems(work: dict) -> list:
    issues = _body_prerequisites(work)
    # 延期 Word 的状态不影响 Markdown 提交；讲稿与想定问答只在加选时要求。
    for name in ("body", "md", "interview", "script", "qa", "review"):
        if name in INTERVIEW_FORMATS and name not in _delivery_formats(work):
            continue
        if name == "interview" and not set(INTERVIEW_FORMATS) & set(_delivery_formats(work)):
            continue
        if work["steps"][name]["status"] != "complete":
            issues.append(issue("incomplete_step", "此步骤尚未完成，当前有效稿保持不变。", name))
    checks = work["checks"]
    if not checks.get("content_consistent") or list(checks.get("checked_formats") or []) != _delivery_formats(work):
        issues.append(issue(
            "checks_required", "必须完成交付文件与正式正文的内容核对，才能提交当前交付。", "checks",
        ))
    required = [BODY_NAME, REFERENCE_NAME, "研究计划输入.json", "研究计划待确认事项.md"]
    for name in ("script", "qa"):
        if name in _delivery_formats(work):
            required.append(FORMAT_NAMES[name])
    for filename in required:
        path = Path(work["directory"]) / filename
        if not path.is_file():
            issues.append(issue("missing_artifact", "本轮必要文件缺失。", str(path)))
    artifacts = _delivery_artifacts(work, valid_only=True)
    if any(name not in artifacts for name in _delivery_artifact_names(_delivery_formats(work))):
        issues.append(issue("missing_export", "本轮交付文件缺失。", work["directory"]))
    if "docx" in _delivery_formats(work) and work.get("template_path") \
            and _digest_file(work["template_path"]) is None:
        issues.append(issue("template_unavailable", "本轮采用的学校模板无法读取。", work["template_path"]))
    return issues


def _migrate_delivery(work: dict) -> bool:
    """旧未提交工作版在公开恢复中明确转为 Markdown 交付。

    只补充交付要求并让旧交付核对待重做；材料、问题、方案、正文及仍有效的
    用户决定保留。已有的 Markdown 产物本身不丢弃，由随后的核对确认。
    """
    if isinstance(work.get("delivery_formats"), list) and work["delivery_formats"]:
        return False
    reason = issue(
        "delivery_formats_updated",
        "本版改为只交付 Markdown；请重新读回 Markdown 核对后再提交。",
        work.get("directory"),
    )
    work["delivery_formats"] = list(DELIVERY_FORMATS)
    dependencies = _dependencies(work)
    if work["steps"]["md"].get("status") == "complete":
        # 正文未变时已有 Markdown 仍可用；按当前依赖重新登记，只重做核对。
        work["steps"]["md"]["dependencies"] = dependencies
    _pending(work["steps"]["review"], reason)
    work["checks"] = {"content_consistent": False, "checked_formats": [], "notes": reason["message"]}
    # 不在这里改写 fingerprints：保留迁移前的摘要，让随后的 _sync_work 仍能
    # 发现迁移前就已经变化的正文或材料，迁移本身不掩盖这些改动。
    return True


def _committed_response(state: dict, revision: str) -> dict:
    work = state["works"][revision]
    # 只比对本版交付相关的摘要；延期 Word 的模板等变化不阻塞 Markdown 重报。
    # stage_files 覆盖已保存步骤文件，属交付依据，必须一并比较。
    keys = set(_dependencies(work)) | {"stage_files"}
    changed = _fingerprints_changed(work["fingerprints"], _snapshot(work), keys=keys)
    # 已采用材料的读取记录声明了原文摘要；旧记录没有后加摘要项时也按该摘要核对。
    changed = changed or bool(_material_record_drift(work))
    # 只核对本版交付要求内的步骤；延期 Word 未导出时的空指纹不算改动。
    for name in _delivery_formats(work):
        step = work["steps"][name]
        changed = changed or step.get("fingerprints") != _artifact_digests(step.get("artifacts", {}))
    if changed:
        return _response(state, "needs_input", [issue(
            "committed_content_changed", "已提交稿或采用的材料发生变化；请保留修改原件并建立新修订，不原地覆盖。", work["directory"],
        )], revision_id=revision, artifacts=_delivery_artifacts(work))
    return _response(state, "committed", revision_id=revision,
                     artifacts=_delivery_artifacts(work, valid_only=True), next_steps=[])


def _finish_commit(directory: Path, state: dict, revision: str, work: dict) -> dict:
    pending = work["pending_commit"]
    source = Path(pending["work_directory"])
    target = Path(pending["target_directory"])
    if source.is_dir() and not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        os.rename(source, target)
    elif source.exists() or not target.is_dir():
        return _response(state, "blocked", [issue(
            "commit_directory_conflict", "待提交记录的源目录与目标目录不符合改名状态，请保留并核对。", str(target),
        )])
    moved = _relocate(work, source, target)
    moved.update(directory=str(target), committed=True, pending_commit=None)
    moved["fingerprints"] = _snapshot(moved)
    for name in ("docx", "md", "review"):
        moved["steps"][name]["dependencies"] = _dependencies(moved)
    state["works"][revision] = moved
    state["current"] = {"revision_id": revision, "directory": str(target)}
    state["binding"]["question_id"] = moved["inputs"]["question_id"]
    _store_state(directory, state)
    return _response(state, "committed", revision_id=revision,
                     artifacts=_delivery_artifacts(moved, valid_only=True), next_steps=[])


def commit_revision(request: dict) -> dict:
    with _locked(request["proposal_dir"]) as directory:
        state, rejected = _load(directory, request)
        if rejected:
            return rejected
        revision = request.get("revision_id")
        if revision in state["works"] and state["works"][revision].get("committed"):
            return _committed_response(state, revision)
        work, rejected = _work_for_write(directory, state, request)
        if rejected:
            return rejected
        changed = _sync_work(work)
        problems = _commit_problems(work)
        if problems:
            if changed:
                _persist_work(directory, state, work)
            return _response(state, "blocked", problems, artifacts=_delivery_artifacts(work, valid_only=True))
        existing_pending = work.get("pending_commit")
        target = Path(existing_pending["target_directory"]) if existing_pending else directory / "版本" / revision
        if target.exists() and not existing_pending:
            return _response(state, "conflict", [issue("target_exists", "目标版本目录已存在，未覆盖任何稿件。", str(target))])
        work["pending_commit"] = {
            "revision_id": revision,
            "work_directory": existing_pending["work_directory"] if existing_pending else work["directory"],
            "target_directory": str(target),
            "checks": deepcopy(work["checks"]), "fingerprints": deepcopy(work["fingerprints"]),
        }
        # 即使下一次改名或最终指针替换中断，磁盘也有唯一可恢复记录。
        _store_state(directory, state)
        return _finish_commit(directory, state, revision, work)


def resume_revision(request: dict) -> dict:
    with _locked(request["proposal_dir"]) as directory:
        state, rejected = _load(directory, request)
        if rejected:
            return rejected
        revision = request.get("revision_id")
        if revision is None:
            unfinished = [key for key, work in state["works"].items() if not work.get("committed")]
            if len(unfinished) > 1:
                return _response(state, "needs_input", [issue(
                    "choose_revision", "存在多个工作版本，请明确本轮继续的修订编号。", unfinished,
                )], revisions=unfinished, next_steps=["choose_revision"], artifacts={})
            revision = unfinished[0] if unfinished else _current_id(state)
        if revision not in state["works"]:
            return _response(state, "needs_input", [issue(
                "unknown_revision", "没有找到可恢复的修订，请先建立工作版本。", revision,
            )], next_steps=["begin_revision"], artifacts={})
        work = state["works"][revision]
        inputs = _normal_inputs(request["inputs"]) if "inputs" in request else None
        if inputs is not None:
            binding_error = _binding_error(state, inputs)
            if binding_error:
                return _response(state, "needs_input", [binding_error], next_steps=["begin_revision"], artifacts={})
        if work.get("committed"):
            if inputs is not None and inputs != work["inputs"]:
                return _response(state, "needs_input", [issue(
                    "new_revision_required", "采用的输入已变化，请建立新工作版本；已提交稿保持原样。", work["directory"],
                )], next_steps=["begin_revision"], artifacts=_delivery_artifacts(work))
            return _committed_response(state, revision)
        # 旧未提交工作版没有 delivery_formats 时，在锁内明确转为 Markdown 交付。
        migrated = _migrate_delivery(work)
        if work["base_revision"] != _current_id(state):
            if migrated:
                _persist_work(directory, state, work)
            return _response(state, "conflict", [issue(
                "base_changed", "另一轮已更新当前稿。本轮结果仍保留，请明确要采用的基准。", work["directory"],
            )], next_steps=["choose_revision"], artifacts=_delivery_artifacts(work, valid_only=True))
        pending = deepcopy(work.get("pending_commit"))
        relocated = False
        if pending:
            source = Path(pending["work_directory"])
            target = Path(pending["target_directory"])
            if source.exists() and target.exists() or not source.is_dir() and not target.is_dir():
                return _response(state, "blocked", [issue(
                    "commit_directory_conflict", "待提交记录指向的目录状态有冲突；没有扫描或猜测其他版本。", pending,
                )], next_steps=["resolve_directory"], artifacts={})
            if target.is_dir() and Path(work["directory"]) != target:
                work = _relocate(work, source, target)
                work["directory"] = str(target)
                work["pending_commit"] = pending
                state["works"][revision] = work
                relocated = True
        if not Path(work["directory"]).is_dir():
            return _response(state, "blocked", [issue(
                "missing_work_directory", "状态指明的工作目录不存在，不能从其他目录猜测恢复。", work["directory"],
            )], next_steps=["restore_work_directory"], artifacts={})
        changed = _sync_work(work, inputs) or migrated
        if pending:
            problems = _commit_problems(work)
            if not changed and not problems and not pending.get("needs_repair"):
                return _finish_commit(directory, state, revision, work)
            work["pending_commit"]["needs_repair"] = True
            if changed or relocated or not pending.get("needs_repair"):
                _persist_work(directory, state, work)
            return _response(state, "needs_input", problems or [issue(
                "pending_changed", "待提交内容有变化；保留原当前稿，完成受影响步骤后再次提交。", work["directory"],
            )], revision_id=revision, next_steps=_next_steps(work) or ["commit_revision"],
                artifacts=_delivery_artifacts(work, valid_only=True))
        if changed:
            _persist_work(directory, state, work)
        return _response(state, revision_id=revision, directory=work["directory"],
            next_steps=_next_steps(work) or ["commit_revision"],
            artifacts=_delivery_artifacts(work, valid_only=True))
