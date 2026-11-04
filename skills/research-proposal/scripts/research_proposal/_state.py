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
STAGES = ("materials", "question", "scheme", "body", "docx", "md", "review")
FORMAT_NAMES = {"docx": "研究计划草稿.docx", "md": "研究计划草稿.md"}
# 当前交付只要求 Markdown；Word 导出与页图为延期实现，状结构保留但不参与交付。
DELIVERY_FORMATS = ["md"]
DEFERRED_FORMATS = ("docx",)
STORED_PATH_BASE = "."


def _absolute(value: str | Path) -> str:
    return str(Path(value).expanduser().resolve())


def _normal_inputs(value: dict) -> dict:
    inputs = deepcopy(value)
    for name in ("application_id", "purpose", "question_id", "material_paths", "template_path"):
        if name not in inputs:
            raise ValueError(f"inputs 缺少 {name}")
    if not inputs["application_id"] or not inputs["purpose"]:
        raise ValueError("申请项目和用途不能为空")
    if not isinstance(inputs["material_paths"], list):
        raise ValueError("material_paths 必须是路径数组")
    inputs["material_paths"] = [_absolute(path) for path in inputs["material_paths"]]
    if inputs["template_path"] is not None:
        inputs["template_path"] = _absolute(inputs["template_path"])
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


def _load(directory: Path, request: dict, *, create=False):
    path = directory / STATE_NAME
    state = read_json(path) if path.is_file() else None
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
    """本版交付要求；历史已提交记录缺该字段时按原双格式只读解释。"""
    value = work.get("delivery_formats")
    if isinstance(value, list) and value:
        return [name for name in value if name in FORMAT_NAMES]
    if work.get("committed"):
        return ["docx", "md"]
    return list(DELIVERY_FORMATS)


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


def _snapshot(work: dict) -> dict:
    inputs = work["inputs"]
    directory = Path(work["directory"])
    template = work.get("template_path", inputs.get("template_path"))
    stage_files = {}
    for stage in ("materials", "question", "scheme"):
        data_path = work["steps"][stage].get("artifacts", {}).get("data")
        stage_files[stage] = _digest_file(data_path)
    return {
        "inputs": json_digest(inputs),
        "materials": {path: _digest_file(path) for path in inputs["material_paths"]},
        "template": {"path": template, "digest": _digest_file(template)},
        "mapping": json_digest(work.get("mapping")),
        "body": _digest_file(directory / BODY_NAME),
        "references": _digest_file(directory / REFERENCE_NAME),
        "stage_files": stage_files,
        "decisions": json_digest(work["confirmations"]),
        "conditions": json_digest(work["conditions"]),
        **({"delivery_formats": list(work["delivery_formats"])} if work.get("delivery_formats") else {}),
    }


def _dependencies(work: dict) -> dict:
    snapshot = _snapshot(work)
    names = ["inputs", "materials", "template", "mapping", "body", "references", "decisions", "conditions"]
    # 仅 Markdown 交付时不把 Word 模板算作 Markdown 的依赖。
    if "docx" not in _delivery_formats(work):
        names.remove("template")
    return {name: snapshot[name] for name in names}


def _delivery_stages(work: dict) -> tuple:
    """本版交付实际要求的导出与核对步骤；延期 Word 不参与 Markdown 的失效判断。"""
    formats = _delivery_formats(work)
    return ("docx", "md", "review") if "docx" in formats else ("md", "review")


def _with_delivery(work: dict, *stages) -> tuple:
    return tuple(dict.fromkeys((*stages, *_delivery_stages(work))))


def _pending(stage: dict, reason: dict) -> None:
    stage["status"] = "pending"
    stage["issues"] = [reason]


def _invalidate(work: dict, stages, reason: dict) -> None:
    for name in stages:
        _pending(work["steps"][name], reason)
    if any(name in stages for name in ("docx", "md", "review")):
        work["checks"] = {
            "content_consistent": False, "checked_formats": [], "notes": reason["message"],
        }


def _unconfirm(work: dict, names) -> None:
    for name in names:
        confirmation = deepcopy(work["confirmations"][name])
        confirmation["status"] = "needs_input"
        work["confirmations"][name] = confirmation


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
    if current["materials"] != previous.get("materials"):
        reason = issue("materials_changed", "材料内容或路径变化，须核对受影响的摘录、引用和正文。", "inputs.material_paths")
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
    for stage in ("materials", "question", "scheme"):
        if work["steps"][stage]["status"] != "complete":
            continue
        if current["stage_files"][stage] != previous.get("stage_files", {}).get(stage):
            reason = issue("saved_content_changed", "已保存步骤文件变化，请通过保存入口明确采用内容。", stage)
            affected = _with_delivery(work, *{
                "materials": ("materials", "body"),
                "question": ("question", "scheme", "body"),
                "scheme": ("scheme", "body"),
            }[stage])
            _invalidate(work, affected, reason)
            if stage in {"question", "scheme"}:
                _unconfirm(work, ("question", "scheme") if stage == "question" else ("scheme",))
    if work["steps"]["body"]["status"] == "complete" and any(
        current[name] != previous.get(name) for name in ("body", "references")
    ):
        _invalidate(work, _with_delivery(work, "body"), issue(
            "body_changed", "工作正文或引用发生变化，请明确采用后重新导出。", str(Path(work["directory"]) / BODY_NAME),
        ))
    dependencies = _dependencies(work)
    for name in ("docx", "md"):
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
        "docx", "md", "preview_pdf", "location",
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
    notes.extend(str(item) for item in work.get("pending_items", []))
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
    """当前下一步不把延期的 Word 列为未完成。"""
    deferred = set(DEFERRED_FORMATS) - set(_delivery_formats(work))
    return [
        name for name in STAGES
        if name not in deferred and work["steps"][name]["status"] != "complete"
    ]


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
            for stage in ("docx", "md", "review"):
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


def save_revision(request: dict) -> dict:
    stage = request["stage"]
    if stage not in {"materials", "question", "scheme", "body"}:
        raise ValueError("stage 必须是 materials、question、scheme 或 body")
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
        content_digest = json_digest(_stage_content(stage, saved_data))
        differs = work["steps"][stage].get("content_digest") != content_digest
        if differs:
            dependent = {
                "materials": ("body", "docx", "md", "review"),
                "question": ("scheme", "body", "docx", "md", "review"),
                "scheme": ("body", "docx", "md", "review"),
                "body": ("docx", "md", "review"),
            }[stage]
            _invalidate(work, dependent, issue("step_changed", "上游步骤已更新，需要继续对应的后续步骤。", stage))
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
        if stage == "body":
            write_record(work_directory / BODY_NAME, saved_data["body"], movable_root=work_directory)
            write_record(work_directory / REFERENCE_NAME, saved_data["references"], movable_root=work_directory)
            artifacts.update(body=str(work_directory / BODY_NAME), references=str(work_directory / REFERENCE_NAME))
        if isinstance(data, dict) and "pending_items" in data:
            work["pending_items"] = deepcopy(data["pending_items"])
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
        names = ("docx", "preview_pdf", "page_images") if name == "docx" else ("md",)
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


def export_revision(request: dict) -> dict:
    # 当前使用 formats:["md"]；省略时同样采用 Markdown。
    formats = request.get("formats", list(DELIVERY_FORMATS))
    if not isinstance(formats, list) or not formats or any(name not in {"docx", "md"} for name in formats):
        raise ValueError("formats 必须是 docx、md 的非空子集")
    formats = list(dict.fromkeys(formats))
    with _locked(request["proposal_dir"]) as directory:
        state, rejected = _load(directory, request)
        if rejected:
            return rejected
        work, rejected = _work_for_write(directory, state, request)
        if rejected:
            return rejected
        inputs = deepcopy(work["inputs"])
        # 仅 Markdown 时不接受也不采用 Word 模板参数；旧分支作为延期实现保留。
        if "docx" in formats:
            if "template_path" in request:
                inputs["template_path"] = _absolute(request["template_path"]) if request["template_path"] else None
                if inputs["template_path"] != work.get("template_path") and "mapping" not in request:
                    work["mapping"] = None
            if "mapping" in request:
                work["mapping"] = deepcopy(request["mapping"])
        changed = _sync_work(work, inputs)
        problems = _body_prerequisites(work)
        if work["steps"]["body"]["status"] != "complete":
            problems.append(issue("body_required", "请先保存本轮有效正文，再导出稿件。", "body"))
        if problems:
            if changed:
                _persist_work(directory, state, work)
            return _response(state, "needs_input", problems, artifacts=_delivery_artifacts(work, valid_only=True))
        from ._documents import export_documents
        try:
            exported = export_documents(
                work, formats,
                template_path=work.get("template_path") if "docx" in formats else None,
                mapping=work.get("mapping") if "docx" in formats else None,
            )
        except Exception as error:
            # 不把异常改成成功；先保留已写出的文件及失败进度。
            partial = {}
            for name in formats:
                path = Path(work["directory"]) / FORMAT_NAMES[name]
                if path.is_file():
                    partial[name] = str(path)
            _accept_export_result(work, formats, {
                "status": "blocked", "artifacts": partial,
                "issues": [issue("export_failed", str(error), work["directory"])],
            })
            _persist_work(directory, state, work)
            raise
        _accept_export_result(work, formats, exported)
        _persist_work(directory, state, work)
        status = exported["status"]
        if any(work["steps"][name]["status"] != "complete" for name in formats) and status == "ready":
            status = "blocked"
        return _response(state, status, exported.get("issues", []),
                         artifacts=_delivery_artifacts(work, valid_only=True))


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
        reviewed = review_documents(work)
        checks = deepcopy(reviewed.get("checks", {}))
        issues = deepcopy(reviewed.get("issues", []))
        formats = _delivery_formats(work)
        exported = all(work["steps"][name]["status"] == "complete" for name in formats)
        artifacts = _delivery_artifacts(work)
        checks["content_consistent"] = bool(checks.get("content_consistent")) and exported
        checks["checked_formats"] = list(formats)
        if not exported:
            issues.append(issue(
                "exports_incomplete", "当前交付格式尚未完成或其内容已变化，不能沿用先前核对。", "exports",
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
    # 延期 Word 的状态不影响 Markdown 提交。
    for name in ("body", "md", "review"):
        if work["steps"][name]["status"] != "complete":
            issues.append(issue("incomplete_step", "此步骤尚未完成，当前有效稿保持不变。", name))
    checks = work["checks"]
    if not checks.get("content_consistent") or list(checks.get("checked_formats") or []) != _delivery_formats(work):
        issues.append(issue("checks_required", "必须完成 Markdown 与正式正文的内容核对，才能提交当前交付。", "checks"))
    for filename in (BODY_NAME, REFERENCE_NAME, "研究计划输入.json", "研究计划待确认事项.md"):
        path = Path(work["directory"]) / filename
        if not path.is_file():
            issues.append(issue("missing_artifact", "本轮必要文件缺失。", str(path)))
    artifacts = _delivery_artifacts(work, valid_only=True)
    if any(name not in artifacts for name in _delivery_artifact_names(_delivery_formats(work))):
        issues.append(issue("missing_export", "本轮 Markdown 交付文件缺失。", work["directory"]))
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
    work["fingerprints"] = _snapshot(work)
    return True


def _committed_response(state: dict, revision: str) -> dict:
    work = state["works"][revision]
    changed = _snapshot(work) != work["fingerprints"]
    for name in ("docx", "md"):
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
    return _response(state, "committed", revision_id=revision, artifacts=_existing_artifacts(moved, valid_only=True), next_steps=[])


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
