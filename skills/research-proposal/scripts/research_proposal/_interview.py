"""研究计划讲稿与想定问答：保存检查、Markdown 生成与读回核对。

两项都是本稿的正式交付文件，只在 `inputs.deliverables` 含 `script` 或 `qa`
时要求。内容以结构化 JSON 保存，Markdown 由该数据重新生成，因此读回核对
比较交付文件与重新生成文本的摘要即可，不需要解析 Markdown。
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile

from ._common import issue, result
from ._record_paths import read_record


FILES = {"script": "研究计划讲稿.md", "qa": "研究计划想定问答.md"}
RATE_RANGE = (100, 700)


def characters(value: str) -> int:
    """口述字数按非空白字符统计，结果与语言空格习惯无关。"""
    return len("".join(str(value).split()))


def text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def format_minutes(value) -> str:
    text = f"{round(float(value), 2):.2f}".rstrip("0").rstrip(".")
    return text if text not in {"", "-0"} else "0"


def _positive(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def _non_negative(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def _filled(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _rate_issue(rate, where="timing.chars_per_minute"):
    if _positive(rate) and RATE_RANGE[0] <= rate <= RATE_RANGE[1]:
        return None
    return issue(
        "interview_rate",
        f"chars_per_minute 须是 {RATE_RANGE[0]} 至 {RATE_RANGE[1]} 之间的正数；"
        "日语口述通常按每分钟 300 至 400 字，中文按 200 至 260 字设定。",
        where,
    )


def validate(name: str, data) -> list[dict]:
    """返回本轮数据尚未满足的检查；空数组表示可以导出。"""
    if name == "script":
        return _validate_script(data)
    if name == "qa":
        return _validate_qa(data)
    raise ValueError(f"未知的交付文件：{name}")


def _validate_script(data) -> list[dict]:
    if not isinstance(data, dict):
        return [issue("script_structure", "讲稿须保存为含 timing 和 sections 的对象。", "timing")]
    issues: list[dict] = []
    timing = data.get("timing")
    if not isinstance(timing, dict):
        return [issue("script_timing", "讲稿须在 timing 中给出目标时长、页数、每分钟口述字数和允许误差。", "timing")]
    target = timing.get("target_minutes")
    slides = timing.get("slides")
    rate = timing.get("chars_per_minute")
    tolerance = timing.get("tolerance_minutes")
    if not _positive(target) or not isinstance(slides, int) or isinstance(slides, bool) or slides <= 0:
        return [issue("script_timing", "timing 须包含正的 target_minutes 和正整数 slides。", "timing")]
    rate_problem = _rate_issue(rate)
    if rate_problem:
        issues.append(rate_problem)
    if not _non_negative(tolerance):
        issues.append(issue("script_timing", "tolerance_minutes 须是不小于 0 的分钟数，例如 1。", "timing.tolerance_minutes"))
        tolerance = 0
    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        issues.append(issue("script_structure", "讲稿须在 sections 中按页保存每页要讲的话。", "sections"))
        return issues
    if len(sections) != slides:
        issues.append(issue(
            "script_structure",
            f"timing.slides 写的是 {slides} 页，sections 实际有 {len(sections)} 页。",
            "sections",
        ))
    seen: list[int] = []
    total_minutes = 0.0
    total_characters = 0
    for position, section in enumerate(sections):
        where = f"sections[{position}]"
        if not isinstance(section, dict):
            issues.append(issue("script_structure", "每一页须是包含 slide、title、minutes、script 的对象。", where))
            continue
        number = section.get("slide")
        if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
            issues.append(issue("script_structure", "slide 须是正整数的页码。", where))
        else:
            if number in seen:
                issues.append(issue("script_structure", f"页码 {number} 重复。", where))
            seen.append(number)
        if not _filled(section.get("title")):
            issues.append(issue("script_structure", "每页须有非空 title。", where))
        if not _positive(section.get("minutes")):
            issues.append(issue("script_structure", "每页须有正数 minutes，表示这一页分到的讲述时间。", where))
        else:
            total_minutes += float(section["minutes"])
        if not _filled(section.get("script")):
            issues.append(issue("script_structure", "每页须有非空 script，表示这一页实际要讲的话。", where))
        else:
            total_characters += characters(section["script"])
        if "visual" in section and not isinstance(section["visual"], str):
            issues.append(issue("script_structure", "visual 只能是字符串。", where))
    if len(seen) == len(sections) and sorted(seen) != list(range(1, slides + 1)):
        issues.append(issue("script_structure", f"页码须从 1 到 {slides} 连续编号且不重复。", "sections"))
    if issues:
        return issues
    tolerance_value = float(tolerance)
    if abs(total_minutes - float(target)) > tolerance_value + 1e-9:
        issues.append(issue(
            "script_timing",
            f"各页 minutes 合计 {format_minutes(total_minutes)} 分钟，与目标 {format_minutes(target)} 分钟"
            f"相差超过允许误差 {format_minutes(tolerance)} 分钟。",
            "timing.target_minutes",
        ))
    estimate = total_characters / float(rate)
    if abs(estimate - float(target)) > tolerance_value + 1e-9:
        issues.append(issue(
            "script_timing",
            f"讲稿正文共 {total_characters} 字，按每分钟 {format_minutes(rate)} 字估算约"
            f"{format_minutes(estimate)} 分钟，与目标 {format_minutes(target)} 分钟"
            f"相差超过允许误差 {format_minutes(tolerance)} 分钟。",
            "sections",
        ))
    return issues


def _validate_qa(data) -> list[dict]:
    if not isinstance(data, dict):
        return [issue("qa_structure", "想定问答须保存为含 items 的对象。", "items")]
    issues: list[dict] = []
    rate = data.get("chars_per_minute")
    limit = data.get("max_answer_minutes", 1.5)
    required = data.get("required_categories")
    items = data.get("items")
    rate_problem = _rate_issue(rate, "chars_per_minute")
    if rate_problem:
        issues.append(rate_problem)
    if not _positive(limit):
        issues.append(issue("qa_structure", "max_answer_minutes 须是正数，表示单条答案能占的分钟数。", "max_answer_minutes"))
    if not isinstance(required, list) or not required or any(not _filled(value) for value in required):
        issues.append(issue("qa_structure", "required_categories 须是非空的类别名数组。", "required_categories"))
        required = []
    elif len(set(required)) != len(required):
        issues.append(issue("qa_structure", "required_categories 不能有重复类别。", "required_categories"))
    if not isinstance(items, list) or not items:
        issues.append(issue("qa_structure", "items 须按条保存问与答。", "items"))
        return issues
    covered: set[str] = set()
    for position, item in enumerate(items):
        where = f"items[{position}]"
        if not isinstance(item, dict):
            issues.append(issue("qa_structure", "每条须是包含 category、question、answer 的对象。", where))
            continue
        category = item.get("category")
        if not _filled(category):
            issues.append(issue("qa_structure", "每条须有非空 category。", where))
        elif required and category not in required:
            issues.append(issue("qa_structure", f"类别 {category} 不在 required_categories 中。", where))
        else:
            covered.add(category)
        if not _filled(item.get("question")):
            issues.append(issue("qa_structure", "每条须有非空 question。", where))
        if not _filled(item.get("answer")):
            issues.append(issue("qa_structure", "每条须有非空 answer。", where))
        if "source" in item and not isinstance(item["source"], str):
            issues.append(issue("qa_structure", "source 只能是字符串。", where))
        if _filled(item.get("answer")) and _positive(rate) and _positive(limit):
            estimate = characters(item["answer"]) / float(rate)
            if estimate > float(limit) + 1e-9:
                issues.append(issue(
                    "qa_answer_length",
                    f"答案共 {characters(item['answer'])} 字，按每分钟 {format_minutes(rate)} 字估算约"
                    f"{format_minutes(estimate)} 分钟，超过单条上限 {format_minutes(limit)} 分钟。",
                    where,
                ))
    missing = [value for value in required if value not in covered]
    if missing:
        issues.append(issue(
            "qa_coverage",
            "以下必备类别还没有问题：" + "、".join(missing) + "。",
            "required_categories",
        ))
    return issues


def render(name: str, data) -> str:
    """由已保存数据生成交付 Markdown；调用方先确认 validate 为空。"""
    problems = validate(name, data)
    if problems:
        raise ValueError("；".join(item["message"] for item in problems))
    if name == "script":
        return _render_script(data)
    if name == "qa":
        return _render_qa(data)
    raise ValueError(f"未知的交付文件：{name}")


def _render_script(data) -> str:
    timing = data["timing"]
    sections = data["sections"]
    rate = float(timing["chars_per_minute"])
    total_characters = sum(characters(section["script"]) for section in sections)
    lines = [
        "# 研究计划发表讲稿",
        "",
        f"- 目标时长：{format_minutes(timing['target_minutes'])} 分钟",
        f"- 幻灯片：{timing['slides']} 页",
        f"- 每分钟口述字数：{format_minutes(rate)}",
        f"- 时长允许误差：±{format_minutes(timing['tolerance_minutes'])} 分钟",
        f"- 讲稿正文总字数（不含空白）：{total_characters}",
        f"- 按字数估算总时长：{format_minutes(total_characters / rate)} 分钟",
        "",
    ]
    for section in sections:
        count = characters(section["script"])
        lines.extend([
            f"## 第 {section['slide']} 页｜{section['title'].strip()}",
            "",
            f"- 分配时长：{format_minutes(section['minutes'])} 分钟",
            f"- 本页讲稿字数：{count}",
            f"- 按字数估算时长：{format_minutes(count / rate)} 分钟",
            "",
            section["script"].strip(),
            "",
        ])
        if _filled(section.get("visual")):
            lines.extend([f"视觉提示：{section['visual'].strip()}", ""])
    return "\n".join(lines).rstrip() + "\n"


def _render_qa(data) -> str:
    rate = float(data["chars_per_minute"])
    limit = float(data.get("max_answer_minutes", 1.5))
    items = data["items"]
    longest = max(characters(item["answer"]) for item in items)
    lines = [
        "# 研究计划想定问答",
        "",
        f"- 条目数：{len(items)}",
        f"- 必备类别：{'、'.join(data['required_categories'])}",
        f"- 每分钟口述字数：{format_minutes(rate)}",
        f"- 单条答案上限：{format_minutes(limit)} 分钟",
        f"- 最长答案字数：{longest}（约 {format_minutes(longest / rate)} 分钟）",
        "",
    ]
    for position, item in enumerate(items, start=1):
        count = characters(item["answer"])
        lines.extend([
            f"## 第 {position} 条｜{item['category'].strip()}",
            "",
            f"- 答案字数：{count}",
            f"- 按字数估算时长：{format_minutes(count / rate)} 分钟",
        ])
        if _filled(item.get("source")):
            lines.append(f"- 出处：{item['source'].strip()}")
        lines.extend([
            "",
            f"问：{item['question'].strip()}",
            "",
            "答：",
            "",
            item["answer"].strip(),
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def step_data(work: dict, name: str):
    """读取讲稿步骤中该项内容；缺失或不可读时返回 None。

    讲稿与想定问答共用 `interview` 步骤，各项分别是该步骤保存件的字段。
    """
    data_path = (work.get("steps", {}).get("interview", {}).get("artifacts") or {}).get("data")
    if not isinstance(data_path, str) or not Path(data_path).is_file():
        return None
    try:
        value = read_record(data_path)
    except (OSError, ValueError, TypeError):
        return None
    if not isinstance(value, dict):
        return None
    return value.get(name) if name in FILES else None


def _write_text(target: Path, text: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", prefix=".deliverable-", dir=target.parent, delete=False,
    ) as stream:
        temporary = Path(stream.name)
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def export_interview(work: dict, names) -> dict:
    """重新生成要求的讲稿或想定问答，并返回实际写入的文件。"""
    directory = Path(work["directory"]).resolve()
    issues: list[dict] = []
    artifacts: dict[str, str] = {}
    digests: dict[str, str] = {}
    statuses: dict[str, str] = {}
    for name in names:
        if name not in FILES:
            raise ValueError(f"未知的交付文件：{name}")
        data = step_data(work, name)
        if data is None:
            issues.append(issue("interview_missing", "没有找到这项交付文件的内容，请先保存对应步骤。", name))
            statuses[name] = "failed"
            continue
        problems = validate(name, data)
        if problems:
            issues.extend(problems)
            statuses[name] = "failed"
            continue
        try:
            text = render(name, data)
        except ValueError as error:
            issues.append(issue("interview_render", str(error), name))
            statuses[name] = "failed"
            continue
        target = directory / FILES[name]
        _write_text(target, text)
        artifacts[name] = str(target)
        digests[name] = text_digest(text)
        statuses[name] = "complete"
    status = "ready" if all(value == "complete" for value in statuses.values()) else "blocked"
    return result(status, issues, artifacts=artifacts, format_status=statuses, digests=digests)


def review_interview(work: dict, names):
    """读回交付文件，与已保存数据重新生成的文本逐字比较。"""
    directory = Path(work["directory"]).resolve()
    details: list[str] = []
    digests: dict[str, str] = {}
    consistent = True
    for name in names:
        if name not in FILES:
            raise ValueError(f"未知的交付文件：{name}")
        data = step_data(work, name)
        if data is None:
            consistent = False
            details.append(f"{FILES[name]}：没有找到对应的保存内容")
            continue
        problems = validate(name, data)
        if problems:
            consistent = False
            details.append("；".join(f"{FILES[name]}：{item['message']}" for item in problems))
            continue
        expected = render(name, data)
        target = directory / FILES[name]
        if not target.is_file():
            consistent = False
            details.append(f"缺少 {FILES[name]}")
            continue
        actual = target.read_text(encoding="utf-8")
        digests[name] = text_digest(actual)
        if text_digest(actual) != text_digest(expected):
            consistent = False
            details.append(
                f"{FILES[name]} 与保存内容不一致；请通过保存入口更新内容后再导出，"
                "不要直接修改交付文件"
            )
    return consistent, details, digests
