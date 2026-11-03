"""准备 RP-03 至 RP-05、论文路线的合成外部输入；不调用待测 API。"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
FIXTURES = Path(__file__).resolve().parent / "fixtures"
STAMP = "2026-11-03T00:00:00Z"
NOTICE = "人工合成的接口测试输入；不是本轮采集、分析或校验代理的执行成果。"
DIRECTIONS = (
    ("dir_fixture_voice", "語りの評価主体", "叙述评价的归属", "比较人物评价与叙述者评价"),
    ("dir_fixture_record", "記録と未完了の行為", "记录与未完成动作", "比较记录空白和动作是否完成"),
)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def load_helper(path):
    spec = importlib.util.spec_from_file_location("fixture_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_professor(root, name, stage, helpers, profile_digest, loose=False):
    stage1, targets = helpers
    professor = root / "教授研究" / "叙事研究" / name
    originals = professor / "原文"
    originals.mkdir(parents=True)
    for filename in ("story.md", "professor-study.md", "outside-study.md"):
        shutil.copyfile(FIXTURES / "upstream" / filename, originals / filename)
    papers = [
        {"item_key": "FIXTURE_A", "title": "〈门灯〉中的秩序叙述", "year": 2024,
         "authors": ["林安（合成）"], "authorship": "first", "pdf_status": "not_provided",
         "source_path": str(originals / "professor-study.md"), "test_fixture": NOTICE},
        {"item_key": "FIXTURE_B", "title": "〈门灯〉的焦点转移与未完成动作", "year": 2025,
         "authors": ["周岚（合成）"], "authorship": "other", "pdf_status": "not_provided",
         "source_path": str(originals / "outside-study.md"), "test_fixture": NOTICE},
    ]
    if name == "周岚（合成）":
        papers[0]["authorship"], papers[1]["authorship"] = "other", "first"
    write_json(professor / "papers.json", {"professor": name, "test_fixture": NOTICE, "papers": papers})
    directions = []
    for identifier, japanese, chinese, summary in DIRECTIONS:
        members = [{"item_key": row["item_key"], "preview_confidence": "high"} for row in papers]
        directions.append({
            "direction_id": identifier, "name_ja": japanese, "name_zh": chinese,
            "summary_zh": summary, "members": members,
            "member_fingerprint": fingerprint({"version": "1", "members": members}),
            "representatives": [{"item_key": row["item_key"], "title": row["title"], "year": row["year"]} for row in papers],
            "low_confidence_count": 0, "coverage_share": 1,
        })
    preview = {
        "schema_version": 1, "professor": name, "direction_id_version": "members-v1",
        "membership_mode": "overlap_allowed", "preview_fingerprint_version": "preview-v1",
        "preview_fingerprint": fingerprint(directions), "directions": directions,
        "test_fixture": NOTICE,
    }
    if stage >= 0:
        write_json(professor / "方向预筛.json", preview)
    target = targets._target_from_selection(
        preview, str((professor / "方向预筛.json").relative_to(root)),
        [DIRECTIONS[0][0]], lambda _: "合成外部输入中已给定的上游方向，非研究计划确认。", [], STAMP,
    )
    if stage >= 1:
        write_json(professor / "套磁目标.json", {**target, "test_fixture": NOTICE})
    if stage >= 2:
        # 固定上游的本地字典构造助手；不调用 build/verify CLI 或网络业务。
        entry, _, _ = stage1.build_professor_entry(root, target, {})
        write_json(professor / "套磁阶段1候选.json", {**stage1._state_root(entry), "test_fixture": NOTICE})
    reports = professor / "论文分析"
    reports.mkdir()
    paper_map = {}
    index = {}
    for paper in papers:
        key = paper["item_key"]
        section = "A2—A4" if key == "FIXTURE_A" else "B2—B4"
        claim = ("规则优先的解释依赖将人物评价当作叙述者评价。" if key == "FIXTURE_A"
                 else "门闩未落下不能证明帮助已经发生，也不能证明叙述者认可排斥。")
        report = reports / (key + ".md")
        report.write_text(f"# 合成分析输入：{paper['title']}\n\n{NOTICE}\n\n"
                          f"原文：{paper['source_path']}，{section}。\n\n{claim}\n")
        facts = {
            "facts_file": str(reports / (key + ".md.facts.json")),
            "evidence_level": "fulltext", "input_fingerprint": hashlib.sha256(Path(paper["source_path"]).read_bytes()).hexdigest(),
            "research_problem": "《门灯》中话语归属与推断强度", "research_object": "合成原文 P1—P6",
            "approach": "段落对照与反例核对", "findings": [claim],
            "contributions": ["区分观察句与评价句"], "topic_terms": ["叙述", "话语归属"],
            "limitations": ["不证明作者意图，不证明私人手稿存在"],
            "source_anchors": {"findings": [f"{paper['source_path']}#{section}"]},
            "confidence": 0.8, "future_work_ids": [], "test_fixture": NOTICE,
        }
        write_json(reports / (key + ".md.facts.json"), facts)
        index[key] = {"file": str(report), "facts_file": facts["facts_file"], "test_fixture": NOTICE}
        paper_map[key] = {**paper, "analysis_file": str(report), "analysis_level": "fulltext",
                          "pdf_available": False, "facts_state": "valid", "facts_error": None, "paper_facts": facts}
    write_json(reports / "_index.json", {"papers": index, "test_fixture": NOTICE})
    gap_quote = "后续可比较不同段落中的话语归属，检验秩序解释是否成立。"
    gap_id = hashlib.sha256(gap_quote.encode()).hexdigest()
    pack_directions, candidate_directions = [], []
    for identifier, japanese, chinese, summary in DIRECTIONS:
        gap = {"gap_id": gap_id, "item_key": "FIXTURE_A", "quote": gap_quote,
               "translation_zh": gap_quote, "status": "open", "evidence": "professor-study.md A4",
               "paper_title": papers[0]["title"], "paper_year": 2024, "authorship": "first"}
        direction = {"direction_id": identifier, "name_ja": japanese, "name_zh": chinese,
                     "status": "active", "supporting_item_keys": list(paper_map), "gap_shortlist": [gap],
                     "gaps_excluded": [], "completed_gap_blacklist": [], "user_note": "",
                     "red_lines": ["合成测试材料不当成现实发表；不预设解释已成立。"]}
        direction["input_fingerprint"] = fingerprint({"direction": direction, "papers": paper_map})
        pack_directions.append(direction)
        questions = ("人物评价能否直接推出叙述者立场？", "未完成动作如何限制秩序解释？", "记录空白能支持哪些推断，又不能支持哪些推断？")
        candidates = []
        for number, question in enumerate(questions, 1):
            candidates.append({
                "id": f"{identifier}_q{number}", "kind": "direction", "direction_ids": [identifier],
                "origin": "generated", "title": question, "one_liner": summary,
                "research_question": question, "points": ["逐段区分感知与评价", "对照两篇解释并记录反例"],
                "gap_refs": [{"direction_id": identifier, "item_key": "FIXTURE_A", "gap_id": gap_id, "done_by_self": False}],
                "anchor_type": "author_future_work", "anchor_notes": {},
                "papers": [{"item_key": key, "direction_ids": [identifier], "title": row["title"],
                            "year": row["year"], "authorship": row["authorship"],
                            "role": "主张及反证比较", "fit_note": "提供可回到原段落的解释依据"} for key, row in paper_map.items()],
                "fit": "high", "fit_note": "与合成教授的叙述研究相关", "red_lines": direction["red_lines"],
                "why_recommended": "资料已提供，结论仍须比较，不预写申请者发现。",
                "tension_points": ["人物态度与叙述者立场不能直接等同"], "test_fixture": NOTICE,
            })
        candidate_directions.append({"direction_id": identifier, "name_ja": japanese, "name_zh": chinese,
                                     "stage3_status": "ready", "mode": "generated",
                                     "generator_contract_version": "stage3-ideas-v3", "candidates": candidates})
    pack = {"schema": 2, "kind": "professor-contact-stage2-input", "identity_version": "direction-id-v1",
            "professor": name, "professor_dir": str(professor), "papers": paper_map,
            "directions": pack_directions, "cross_direction_groups": [], "test_fixture": NOTICE}
    if stage >= 3:
        write_json(professor / "套磁候选输入.json", pack)
    if stage >= 4:
        write_json(professor / "套磁候选状态.json", {
            "schema": 2, "kind": "professor-contact-stage3-state", "identity_version": "direction-id-v1",
            "professor": name, "professor_dir": str(professor), "generator_contract_version": "stage3-ideas-v3",
            "profile_fingerprint": profile_digest,
            "input_fingerprints": {row["direction_id"]: row["input_fingerprint"] for row in pack_directions},
            "directions": candidate_directions, "cross_direction_groups": [],
            "validator": {"results": {row[0]: {"result": "pass", "test_fixture": NOTICE} for row in DIRECTIONS},
                          "test_fixture": "合成接口的给定终态，不记录或声称真实校验代理历史。"},
            "test_fixture": NOTICE,
        })
    if not loose:
        # 完整包仍引用这些报告；其他前置场景无需多余分析线索。
        if stage < 3:
            shutil.rmtree(reports)
    return {
        "path": str(reports / "FIXTURE_A.md") if loose else str(professor),
        "application_root": str(root), "professor_path": str(professor),
        "selection": {"professor_path": str(professor), "direction_id": DIRECTIONS[0][0]},
        "input_file": str(professor / "套磁候选输入.json"),
        "candidate_file": str(professor / "套磁候选状态.json"),
        "analysis_file": str(reports / "FIXTURE_A.md"),
        "facts_file": str(reports / "FIXTURE_A.md.facts.json"),
    }


def prepare(output, scripts):
    output.mkdir(parents=True, exist_ok=False)
    stage1 = load_helper(scripts / "contact_stage1.py")
    targets = stage1.contact_targets
    profile = output / "套磁邮件" / "套磁信息.md"
    profile.parent.mkdir()
    shutil.copyfile(FIXTURES / "applications" / "applicant.md", profile)
    profile_digest = hashlib.sha256(profile.read_bytes()).hexdigest()
    operator_inputs = output / "operator-inputs"
    operator_inputs.mkdir()
    supplement = operator_inputs / "access-supplement.md"
    shutil.copyfile(FIXTURES / "upstream" / supplement.name, supplement)
    cases = {}
    specifications = [("complete", 4, False), ("without_candidates", 3, False),
                      ("preview", -1, False), ("stage0", 0, False), ("stage1", 1, False), ("stage2", 2, False),
                      ("analysis_stage0", 0, True), ("analysis_stage1", 1, True), ("analysis_stage2", 2, True),
                      ("multiple", 4, False), ("writing", 4, False)]
    for name, stage, loose in specifications:
        root = output / name
        root.mkdir()
        write_json(root / "info.json", {"university": "松川大学（合成）", "department": "叙事研究（合成）", "major": "文学", "test_fixture": NOTICE})
        shutil.copyfile(FIXTURES / "upstream" / "admissions.md", root / "招生资料.md")
        case = make_professor(root, "林安（合成）", stage, (stage1, targets), profile_digest, loose)
        cases[name] = case
        if name == "multiple":
            second = make_professor(root, "周岚（合成）", -1, (stage1, targets), profile_digest)
            case["other_professor_path"] = second["professor_path"]
        if name == "writing":
            shutil.copyfile(FIXTURES / "upstream" / "access-initial.md", root / "access-initial.md")
            case["access_supplement"] = str(supplement)
            for filename in ("applicant.md", "program-a.md"):
                shutil.copyfile(FIXTURES / "applications" / filename, root / filename)
    collect = output / "collect"
    collect.mkdir()
    write_json(collect / "info.json", {"university": "松川大学（合成）", "department": "叙事研究（合成）", "test_fixture": NOTICE})
    shutil.copyfile(FIXTURES / "upstream" / "admissions.md", collect / "招生资料.md")
    cases["collect"] = {"path": str(collect), "application_root": str(collect)}
    complete = cases["complete"]
    complete["paths"] = [complete["application_root"], str(Path(complete["application_root"]) / "教授研究"),
                         complete["professor_path"], complete["input_file"]]
    write_json(output / "cases.json", {"test_fixture": NOTICE, **cases})
    (output / "输入说明.md").write_text(NOTICE + "\n未调用 research-proposal 或任何模型、网络业务。\n"
                                          "validator.results 是测试输入的给定终态，不是本轮真实校验。\n"
                                          "research-proposal 的确认、正文及当前版本均未准备。\n")
    print(f"输入已生成：{output / 'cases.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--contact-scripts", required=True, type=Path)
    args = parser.parse_args()
    prepare(args.output.resolve(), args.contact_scripts.resolve())
