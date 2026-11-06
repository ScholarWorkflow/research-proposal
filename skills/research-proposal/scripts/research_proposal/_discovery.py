"""Discover input scope and route through the installed upstream checks.

The upstream ``resolve`` and ``verify`` commands may legitimately refresh a
target's display projection. They run on the original application directory;
this module never writes an upstream state, copies its validators, or launches
an agent. Material/candidate completion is not inferred from Markdown files.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

from ._common import issue, read_json, result, run_tool


_MARKERS = (
    "papers.json", "方向预筛.json", "套磁目标.json", "套磁阶段1候选.json",
    "套磁候选输入.json", "套磁候选状态.json",
)
_UPSTREAM_FILES = {*_MARKERS, "套磁候选分析.md", "套磁想法候选.md", "套磁选择.json", "方向素材.json"}
_APPLICATION_FILES = {"info.json", "boshu_analysis.json"}
_CARRIERS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".txt", ".md", ".epub", ".html", ".htm", ".docx"}
_OMIT = {".git", ".agents", ".codex", ".venv", "__pycache__", "node_modules"}


def _check(name: str, arguments: list[str]) -> dict:
    """Consume the original structured response, including business exits."""
    try:
        process = run_tool(name, arguments)
        output = process.stdout
        error = process.stderr
        code = process.returncode
    except subprocess.CalledProcessError as exception:
        output, error, code = exception.stdout, exception.stderr, exception.returncode
    except (OSError, subprocess.TimeoutExpired) as exception:
        return {"status": "blocked", "reason_code": "upstream_unavailable", "message": str(exception)}
    try:
        response = json.loads(output or b"")
    except (ValueError, UnicodeError):
        diagnostic = (error or output or b"").decode("utf-8", errors="replace")
        return {"status": "blocked", "reason_code": "upstream_check_failed", "message": diagnostic.strip(), "exit_code": code}
    if not isinstance(response, dict):
        return {"status": "blocked", "reason_code": "upstream_response_invalid", "message": "原检查未返回 JSON 对象。", "exit_code": code}
    if code and response.get("status") == "ok":
        return {"status": "blocked", "reason_code": "upstream_check_failed", "message": "原检查非零退出，不能采用成功状态。", "exit_code": code}
    return response


def _problem(response: dict, path: Path) -> dict:
    return issue(
        str(response.get("reason_code") or "upstream_check_failed"),
        str(response.get("message") or response.get("notes") or response.get("error") or response.get("status") or "原检查未通过。"),
        str(path),
    )


def _read(path: Path, issues: list) -> dict | None:
    try:
        value = read_json(path)
    except (OSError, ValueError, UnicodeError) as error:
        issues.append(issue("unreadable_input", str(error), str(path)))
        return None
    if not isinstance(value, dict):
        issues.append(issue("invalid_input", "此输入应为 JSON 对象。", str(path)))
        return None
    return value


def _files(directory: Path) -> list[Path]:
    """Inventory only the explicitly supplied scope, without following links."""
    if directory.is_file():
        return [directory]
    found = []
    if directory.is_dir():
        for entry in directory.iterdir():
            if entry.name in _OMIT or entry.name.startswith("."):
                continue
            if entry.is_file():
                found.append(entry)
            elif entry.is_dir() and not entry.is_symlink():
                found.extend(_files(entry))
    return sorted(found)


def _root(path: Path) -> Path | None:
    directory = path if path.is_dir() else path.parent
    for candidate in (directory, *directory.parents):
        if (candidate / "info.json").is_file():
            return candidate.resolve()
    return None


def _analysis_directory(path: Path, root: Path | None) -> Path | None:
    directory = path if path.is_dir() else path.parent
    research = root / "教授研究" if root else None
    for candidate in (directory, *directory.parents):
        if candidate.name == "论文分析" and (
            research is None or candidate.parent != research and candidate.is_relative_to(research)
        ):
            return candidate
    return None


def _analysis_locations(path: Path) -> list[Path]:
    """Locate analysis clues in the given scope without assigning an owner."""
    directories = set()
    current = _analysis_directory(path, None)
    if current is not None:
        directories.add(current)
    if path.is_dir():
        for entry in _files(path):
            if entry.suffix.lower() != ".md" and entry.name != "_index.json" and not entry.name.endswith((".facts.json", ".future_work.json")):
                continue
            directory = _analysis_directory(entry, None)
            if directory is not None:
                directories.add(directory)
    return sorted(directories)


def _linked_analysis_owner(path: Path, root: Path) -> Path | None:
    """Resolve a routing association, not the validity of an analysis.

    The installed analyzer records an absolute path in
    ``论文分析/_index.json`` -> ``papers[item_key].file``. Its original Stage-2
    checks remain responsible for identity, successful level and cache reuse.
    A report can identify that workflow while targets/snapshots/packs are absent.
    """
    directory = _analysis_directory(path, root)
    if directory is None:
        return None
    if path.is_file() and (path.name == "_index.json" or path.name.endswith((".facts.json", ".future_work.json"))):
        return directory.parent
    try:
        index = read_json(directory / "_index.json")
    except (OSError, ValueError, UnicodeError):
        return None
    papers = index.get("papers") if isinstance(index, dict) else None
    if not isinstance(papers, dict):
        return None
    for entry in papers.values():
        recorded = entry.get("file") if isinstance(entry, dict) else None
        if not isinstance(recorded, str) or not recorded.strip():
            continue
        report = Path(recorded.strip()).expanduser()
        # The source contract stores absolute paths. An unresolved relative or
        # stale association needs clarification, never a guessed base directory.
        if not report.is_absolute():
            continue
        report = report.resolve()
        if not report.is_relative_to(directory) or not report.is_file():
            continue
        if report == path or path.is_dir() and report.is_relative_to(path):
            return directory.parent
    return None


def _professors(path: Path, root: Path) -> list[Path]:
    research = root / "教授研究"
    if not research.is_dir():
        return []
    analysis_owner = _linked_analysis_owner(path, root)
    if analysis_owner is not None:
        return [analysis_owner]
    if path.is_file():
        # A supplied source document is its own scope, even when kept beside
        # upstream artifacts. Only a recognized workflow artifact may resolve
        # its owning professor and the owner's required supporting state.
        if not path.is_relative_to(research) or path.name not in _UPSTREAM_FILES:
            return []
        directory = path.parent
        for candidate in (directory, *directory.parents):
            if candidate == research:
                break
            if any((candidate / name).is_file() for name in _MARKERS):
                return [candidate]
        return []
    if path == root:
        scope = research
    elif path.is_relative_to(research):
        scope = path
    else:
        # Application ownership does not widen an explicit material subfolder
        # to every professor in that application.
        return []
    professors = set()
    for entry in _files(scope):
        if entry.name in _MARKERS and entry.parent != research:
            professors.add(entry.parent)
        elif entry.name == "_index.json" and entry.parent.name == "论文分析":
            # A container may hold only associated reports, before any target,
            # snapshot or pack exists. Resolve the directory rather than the
            # index file so the recorded report association is still required.
            owner = _linked_analysis_owner(entry.parent, root)
            if owner is not None:
                professors.add(owner)
    return sorted(professors)


def _materials(path: Path) -> list[str]:
    materials = []
    for entry in _files(path):
        analysis_record = (
            (entry.name == "_index.json" or entry.name.endswith((".facts.json", ".future_work.json")))
            and _analysis_directory(entry, None) is not None
        )
        if entry.suffix.lower() in _CARRIERS or entry.name in _MARKERS or entry.name in _APPLICATION_FILES or analysis_record:
            materials.append(str(entry.resolve()))
    return materials


def _material_scope(path: Path, root: Path | None, selection: dict) -> dict:
    materials = _materials(path)
    if path.is_file() and not materials:
        # The reader must see an explicitly supplied unsupported carrier too.
        materials = [str(path)]
    if not materials:
        return result("needs_input", [issue("application_materials_required", "给定范围内缺少可读取材料；请补充实际研究材料或合格招生项目路径。", str(path))], objects=[], selected=None)
    directory = path if path.is_dir() else path.parent
    analysis_locations = _analysis_locations(path)
    ambiguous = (
        bool(selection)
        or bool(analysis_locations)
        or path.is_file() and path.name in _UPSTREAM_FILES | _APPLICATION_FILES
        or path.is_dir() and any((path / name).is_file() for name in _MARKERS + ("boshu_analysis.json",))
    )
    problems = []
    if ambiguous:
        if analysis_locations:
            for analysis_location in analysis_locations:
                problems.append(issue("input_role_required", "该论文分析目录中的报告或事实文件尚未确认与教授的关联；请明确这是哪位教授的既有分析，还是独立研究材料。给定范围与文件位置已保留，不默认转入非论文路线。", str(analysis_location)))
        else:
            problems.append(issue("input_role_required", "该范围含项目或上游材料线索，但尚不能确定本次要读取研究材料还是继续某位教授的流程；请明确用途或给出对应项目/教授目录。当前保留给定范围，不扩大到其他教授。", str(path)))
    item = {
        "application_root": str(root or directory), "professor_path": None,
        "materials": materials, "valid_artifacts": {},
        "next_step": "needs_input" if ambiguous else "read_materials",
    }
    return result("needs_input" if ambiguous else "ready", problems, objects=[item], selected=None if ambiguous else str(path))


def _profile(root: Path) -> Path | None:
    # Exact default candidates from the installed Stage-3 agent input contract.
    for directory in (Path.cwd(), root.parent, root.parent.parent):
        candidate = directory / "套磁邮件" / "套磁信息.md"
        if candidate.is_file():
            return candidate.resolve()
    return None


def _recorded_terminal(state: dict, directions: list[str]) -> bool:
    """Read the owner's recorded terminal outcomes; do not revalidate prose."""
    validator = state.get("validator")
    if not isinstance(validator, dict) or not directions:
        return False
    records = validator.get("results")
    if not isinstance(records, dict):
        return False
    terminal = {"pass", "fail_after_2_rounds", "fail_after_max_rounds"}
    return all(
        isinstance(records.get(direction), dict)
        and records[direction].get("result") in terminal
        for direction in directions
    )


def _paper_object(root: Path, professor: Path, direction: str | None) -> dict:
    problems: list[dict] = []
    available: dict[str, str] = {}
    item = {
        "application_root": str(root), "professor_path": str(professor),
        "materials": _materials(professor), "valid_artifacts": available,
        "next_step": "collect", "directions": [], "issues": problems,
    }
    pack = professor / "套磁候选输入.json"
    candidates = professor / "套磁候选状态.json"
    if pack.is_file():
        arguments = ["stage3-plan", "--program-root", str(root), "--professor-dir", str(professor), "--refresh-scope", "all"]
        if direction:
            arguments.extend(["--direction-id", direction])
        profile = _profile(root)
        if profile:
            arguments.extend(["--profile", str(profile)])
        planned = _check("contact_state", arguments)
        if planned.get("status") == "blocked":
            problems.append(_problem(planned, pack))
            item["next_step"] = "needs_input"
            item["blocked"] = True
            return item
        if planned.get("status") == "ok":
            available[pack.name] = str(pack)
            raw_pack = _read(pack, problems)
            details = {row.get("direction_id"): row for row in (raw_pack or {}).get("directions", []) if isinstance(row, dict)}
            directions = planned.get("directions") or []
            item["directions"] = [
                {"direction_id": row.get("direction_id"), "name_zh": details.get(row.get("direction_id"), {}).get("name_zh"), "name_ja": details.get(row.get("direction_id"), {}).get("name_ja"), "action": row.get("action")}
                for row in directions
            ]
            identifiers = [row["direction_id"] for row in directions if row.get("direction_id")]
            state = _read(candidates, problems) if candidates.is_file() else None
            reusable = bool(directions) and all(row.get("action") == "reuse" for row in directions)
            if state and reusable and _recorded_terminal(state, identifiers):
                available[candidates.name] = str(candidates)
                item["next_step"] = "proposal"
                outcomes = state["validator"]["results"]
                if any(outcomes[identifier].get("result") != "pass" for identifier in identifiers):
                    problems.append(issue("candidate_validation_failed", "原流程已达到校验终态，但仍有未通过项；选题时须呈现风险，不能宣称校验通过。", str(candidates)))
            elif planned.get("profile_changed_reason") and not profile:
                item["next_step"] = "needs_input"
                problems.append(issue("profile_source_required", "候选使用过个人资料，但原默认位置未找到该资料；请提供原资料供上游核对，不能假定候选已经失效。", str(candidates)))
            else:
                item["next_step"] = "stage3"
                if state and reusable:
                    problems.append(issue("candidate_validation_pending", "候选已有，但尚无适用方向的原校验终态；继续第三阶段原收尾。", str(candidates)))
            return item
        # These original reasons follow a successful pack load. A broken
        # candidate state does not turn an accepted pack into loose analysis.
        if planned.get("reason_code") in {"invalid_candidate_state", "legacy_direction_identity"}:
            available[pack.name] = str(pack)
            item["next_step"] = "stage3"
            problems.append(_problem(planned, candidates))
            return item
        problems.append(_problem(planned, pack))

    preview = professor / "方向预筛.json"
    if not preview.is_file():
        item["next_step"] = "preview" if (professor / "papers.json").is_file() else "collect"
        return item
    checked_preview = _check("contact_targets", ["preview", "--preview", str(preview)])
    if checked_preview.get("status") != "ok":
        problems.append(_problem(checked_preview, preview))
        item["next_step"] = "needs_input" if checked_preview.get("status") == "blocked" else "preview"
        item["blocked"] = checked_preview.get("status") == "blocked"
        return item
    available[preview.name] = str(preview)
    item["directions"] = checked_preview.get("options") or []
    target = professor / "套磁目标.json"
    checked_target = _check("contact_targets", ["resolve", "--program-root", str(root), "--target-file", str(target)])
    if checked_target.get("status") != "ok":
        problems.append(_problem(checked_target, target))
        item["next_step"] = "needs_input" if checked_target.get("status") == "blocked" else "stage0"
        item["blocked"] = checked_target.get("status") == "blocked"
        return item
    available[target.name] = str(target)
    selected_ids = [identifier for selected in checked_target.get("targets", []) for identifier in selected.get("selected_direction_ids", [])]
    item["upstream_selected_direction_ids"] = selected_ids
    if direction and direction not in selected_ids:
        item["next_step"] = "stage0"
        problems.append(issue("direction_selection_required", "请求的方向尚未成为该教授的有效上游目标；交阶段 0 处理真实选择。", str(target)))
        return item
    checked_snapshot = _check("contact_stage1", ["verify", "--program-root", str(root), "--target-file", str(target)])
    if checked_snapshot.get("status") != "ok":
        problems.append(_problem(checked_snapshot, professor / "套磁阶段1候选.json"))
        item["next_step"] = "needs_input" if checked_snapshot.get("status") == "blocked" else "stage1"
        item["blocked"] = checked_snapshot.get("status") == "blocked"
        return item
    available["套磁阶段1候选.json"] = str(Path(checked_snapshot["snapshot_path"]).resolve())
    item["next_step"] = "stage2"
    return item


def discover(request: dict) -> dict:
    supplied = request.get("path")
    if not isinstance(supplied, str) or not supplied.strip():
        return result("needs_input", [issue("path_required", "请提供招生项目、既有教授资料或研究材料的实际路径。", "path")], objects=[], selected=None)
    path = Path(supplied).expanduser().resolve()
    if not path.exists():
        return result("needs_input", [issue("path_missing", "给定路径不存在，请补充实际资料路径。", str(path))], objects=[], selected=None)
    selection = request.get("selection") or {}
    if not isinstance(selection, dict):
        raise ValueError("selection 必须是包含已有选择的对象")
    selected_path = selection.get("professor_path")
    selected_path = Path(selected_path).expanduser().resolve() if selected_path else None
    direction = selection.get("direction_id")
    if direction is not None and (not isinstance(direction, str) or not direction):
        raise ValueError("direction_id 必须是非空字符串")
    root = _root(path)
    if root is None:
        return _material_scope(path, None, selection)
    # These explicit project artifacts identify the application itself. Other
    # files and subfolders keep their supplied scope, even beside project data.
    scope = root if path.is_file() and path.name in _APPLICATION_FILES else path
    professors = _professors(scope, root)
    if not professors and (scope not in {root, root / "教授研究"} or _analysis_locations(scope)):
        return _material_scope(scope, root, selection)
    if selected_path is not None and professors:
        if selected_path not in professors:
            inventory = [{"application_root": str(root), "professor_path": str(professor), "materials": [], "valid_artifacts": {}, "next_step": "needs_input"} for professor in professors]
            return result("needs_input", [issue("selection_outside_scope", "已有教授选择不在给定路径范围内，请核对路径或选择。", str(selected_path))], objects=inventory, selected=None)
        # An explicit professor scope must not refresh another professor's
        # projection as a side effect of checking the chosen one.
        professors = [selected_path]
    objects = [_paper_object(root, professor, direction if selected_path == professor or selected_path is None and len(professors) == 1 else None) for professor in professors]
    if not objects:
        problems: list[dict] = []
        metadata = _read(root / "info.json", problems)
        materials = _materials(scope if scope.is_dir() else root)
        source_files = [value for value in materials if Path(value).suffix.lower() in _CARRIERS]
        eligible = bool(metadata and metadata.get("university") and metadata.get("department") and source_files)
        step = "collect" if eligible else "needs_input"
        if not eligible:
            problems.append(issue("application_materials_required", "需补齐具体学校、研究科/专攻和招生资料；不能只凭学校名称建立完整上游输入。", str(root)))
        item = {"application_root": str(root), "professor_path": None, "materials": materials, "valid_artifacts": {}, "next_step": step}
        return result("ready" if eligible else "needs_input", problems, objects=[item], selected=str(root) if eligible else None)
    if selected_path is not None:
        chosen = [item for item in objects if item["professor_path"] == str(selected_path)]
        if not chosen:
            return result("needs_input", [issue("selection_outside_scope", "已有教授选择不在给定路径范围内，请核对路径或选择。", str(selected_path))], objects=objects, selected=None)
    elif len(objects) == 1:
        chosen = objects
    else:
        return result("needs_input", [issue("professor_selection_required", "存在多个教授，请根据展示材料选择本稿对象。", str(path))], objects=objects, selected=None)
    item = chosen[0]
    problems = list(item.get("issues") or [])
    directions = item.get("directions") or []
    if not direction and len(directions) > 1 and len(item.get("upstream_selected_direction_ids") or []) != 1:
        problems.append(issue("direction_selection_required", "存在多个可选方向，请取得本稿适用方向的真实选择。", item["professor_path"]))
        return result("needs_input", problems, objects=objects, selected=None)
    status = "blocked" if item.get("blocked") else "needs_input" if item["next_step"] == "needs_input" else "ready"
    return result(status, problems, objects=objects, selected=item["professor_path"])
