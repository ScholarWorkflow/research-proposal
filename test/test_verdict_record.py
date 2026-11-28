"""RP-18 的判决记录校验；在独占目录中建立合成稿件，不读取用户真实资料。

只调用本地组件，不安装产品、不启动会话、不调用上游。对应 plan/test-plan.md 的 RP-18。
"""

import copy
import json
from pathlib import Path

from support import ComponentCase, read_json


WEIGHTS = {
    "问题成形": 15, "价值": 15, "新意落点": 15, "先行核对": 10, "空白成因": 15,
    "方法落地": 15, "准备档位": 5, "两种结果": 5, "两个弱点": 5,
}

SCORES = {
    "问题成形": 2, "价值": 2, "新意落点": 1, "先行核对": 1, "空白成因": 1,
    "方法落地": 2, "准备档位": 1, "两种结果": 2, "两个弱点": 2,
}

EVIDENCE = {name: "事实：合成依据" for name in WEIGHTS}


def record(**overrides):
    """一条合规记录，按需覆盖单个字段构造违规情形。"""
    item = {
        "id": "C1",
        "question": "合成候选问题",
        "statement_version": "q1",
        "scores": dict(SCORES),
        "evidence": dict(EVIDENCE),
        "experiment": [],
        "missing": ["还缺最接近三篇的全文"],
        "total": 70.0,
        "gate": "pass",
    }
    item.update(overrides)
    return item


def payload(*items):
    return {
        "weights": dict(WEIGHTS),
        "evidence_cutoff": "2026-11-28",
        "items": list(items),
    }


class VerdictRecordTests(ComponentCase):
    """保存入口对 candidate_scores 的拒绝与放行。"""

    def setUp(self):
        super().setUp()
        self.proposal = self.output / "proposal"
        self.proposal.mkdir()
        started = self.call("begin_revision", {
            "proposal_dir": str(self.proposal), "expected_state_version": None,
            "inputs": {
                "application_id": "合成项目-判决记录", "purpose": "联系教授",
                "question_id": "q1", "material_paths": [],
            },
        })
        self.assertEqual(started["status"], "ready")
        self.revision = started["revision_id"]

    def save(self, data):
        state = read_json(self.proposal / "研究计划状态.json")
        return self.call("save_revision", {
            "proposal_dir": str(self.proposal), "revision_id": self.revision,
            "expected_state_version": state["state_version"],
            "stage": "materials", "data": data,
        })

    def materials(self, **fields):
        return {"materials": [], "candidates": [], **fields}

    def test_compliant_record_is_saved(self):
        gap_scores = dict(SCORES)
        gap_scores["空白成因"] = 0
        stopped = record(
            id="C2", gate="hard_stop", total=None, stop_reason="gap_zero",
            scores=gap_scores,
            missing=["反例还待核"], experiment=["参数网格换过一档后仍然更低"],
        )
        result = self.save(self.materials(candidate_scores=payload(record(), stopped)))
        self.assertEqual(result["status"], "ready")
        state = read_json(self.proposal / "研究计划状态.json")
        saved = read_json(
            state["works"][self.revision]["steps"]["materials"]["artifacts"]["data"]
        )
        self.assertEqual([item["id"] for item in saved["candidate_scores"]["items"]], ["C1", "C2"])
        self.assertEqual(saved["candidate_scores"]["items"][1]["stop_reason"], "gap_zero")

    def test_pending_with_total_is_rejected(self):
        item = record(gate="pending", total=88.0, missing=["还缺三篇"])
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("pending", str(caught.exception))
        self.assertIn("不得给总分", str(caught.exception))

    def test_hard_stop_without_reason_is_rejected(self):
        item = record(gate="hard_stop", total=None)
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("stop_reason", str(caught.exception))

    def test_hard_stop_with_unknown_reason_is_rejected(self):
        item = record(gate="hard_stop", total=None, stop_reason="too_low")
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("stop_reason", str(caught.exception))

    def test_merge_without_target_is_rejected(self):
        item = record(gate="merge", total=None, merged_into=None)
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("merged_into", str(caught.exception))

    def test_merge_target_must_exist(self):
        item = record(id="C2", gate="merge", total=None, merged_into="C9")
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(record(id="C1"), item)))
        self.assertIn("不存在的候选", str(caught.exception))

    def test_pass_needs_numeric_total(self):
        for total in (None, "70"):
            with self.subTest(total=total):
                item = record(total=total)
                with self.assertRaises(ValueError):
                    self.save(self.materials(candidate_scores=payload(item)))

    def test_pending_needs_missing(self):
        item = record(gate="pending", total=None, missing=[])
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("missing", str(caught.exception))

    def test_pass_needs_evidence(self):
        item = record(evidence={})
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("evidence", str(caught.exception))

    def test_rejected_save_keeps_previous_state_version(self):
        self.assertEqual(self.save(self.materials())["status"], "ready")
        before = read_json(self.proposal / "研究计划状态.json")["state_version"]
        with self.assertRaises(ValueError):
            self.save(self.materials(candidate_scores=payload(record(gate="pending", total=88.0))))
        self.assertEqual(read_json(self.proposal / "研究计划状态.json")["state_version"], before)

    def test_rejected_save_leaves_previous_materials_record_untouched(self):
        """被拒时不落盘：上一份材料记录逐字节不变，新内容不写入。"""
        self.assertEqual(
            self.save(self.materials(candidate_scores=payload(record())))["status"], "ready"
        )
        state = read_json(self.proposal / "研究计划状态.json")
        data_path = state["works"][self.revision]["steps"]["materials"]["artifacts"]["data"]
        before = Path(data_path).read_bytes()
        version_before = state["state_version"]
        with self.assertRaises(ValueError):
            self.save(self.materials(
                candidates=[{"id": "C9", "question": "本轮新加但会被拒"}],
                candidate_scores=payload(record(gate="hard_stop", total=None)),
            ))
        self.assertEqual(Path(data_path).read_bytes(), before, "上一份材料记录不能被改写")
        after = read_json(self.proposal / "研究计划状态.json")
        self.assertEqual(after["state_version"], version_before)
        self.assertNotIn("C9", json.dumps(
            read_json(after["works"][self.revision]["steps"]["materials"]["artifacts"]["data"]),
            ensure_ascii=False,
        ))

    def test_unrated_item_needs_evidence(self):
        # 用非硬门槛项验证未评：硬门槛项未评有单独规则（见下一条用例）。
        scores = copy.deepcopy(SCORES)
        scores["两种结果"] = None
        missing_evidence = record(scores=scores, evidence={
            name: "事实：合成依据" for name in WEIGHTS if name != "两种结果"
        })
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(missing_evidence)))
        self.assertIn("evidence 缺少这些项的依据", str(caught.exception))

        rated = record(scores=scores, evidence={
            **{name: "事实：合成依据" for name in WEIGHTS if name != "两种结果"},
            "两种结果": "推演：还没跑到第二种结果，待补一次复测",
        })
        result = self.save(self.materials(candidate_scores=payload(rated)))
        self.assertEqual(result["status"], "ready")

    def test_scores_must_match_weights(self):
        scores = dict(SCORES)
        scores.pop("准备档位")
        item = record(scores=scores, evidence={
            name: "事实：合成依据" for name in WEIGHTS if name != "准备档位"
        })
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("缺少权重表里的项", str(caught.exception))

    def test_hard_gate_unrated_cannot_pass(self):
        scores = copy.deepcopy(SCORES)
        scores["空白成因"] = None
        evidence = {name: "事实：合成依据" for name in WEIGHTS if name != "空白成因"}
        evidence["空白成因"] = "全文：还没拿到，待补最接近的三篇"
        for gate in ("pass", "soft_stop"):
            with self.subTest(gate=gate):
                item = record(gate=gate, scores=scores, evidence=evidence, missing=[])
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=payload(item)))
                self.assertIn("硬门槛项", str(caught.exception))

        # hard_stop 与 merge 同样要先判过门槛，否则「还没查」会顺着 gap_zero 入库。
        for gate, extra in (("hard_stop", {"stop_reason": "gap_zero"}),
                            ("merge", {"merged_into": "C2"})):
            with self.subTest(gate=gate):
                item = record(gate=gate, total=None, scores=scores, evidence=evidence,
                              missing=["空白成因还缺最接近三篇的全文"], **extra)
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=payload(record(id="C2"), item)))
                self.assertIn("只能记 pending", str(caught.exception))

        pending = record(gate="pending", total=None, scores=scores, evidence=evidence,
                         missing=["空白成因还缺最接近三篇的全文"])
        self.assertEqual(self.save(self.materials(candidate_scores=payload(pending)))["status"], "ready")

    def test_same_candidate_may_keep_other_statement_version(self):
        first = record(id="C1", statement_version="q1")
        second = record(id="C1", statement_version="q2", gate="pending", total=None,
                        missing=["新题面下还缺三篇"])
        result = self.save(self.materials(candidate_scores=payload(first, second)))
        self.assertEqual(result["status"], "ready")

    def test_same_candidate_same_version_is_rejected(self):
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(record(id="C1", statement_version="q1"),
                                                              record(id="C1", statement_version="q1"))))
        self.assertIn("题面版本", str(caught.exception))

    def test_merge_target_uses_candidate_identity(self):
        merged = record(id="C2", statement_version="q2", gate="merge", total=None, merged_into="C1")
        result = self.save(self.materials(candidate_scores=payload(record(id="C1"), merged)))
        self.assertEqual(result["status"], "ready")

    def test_record_fields_are_required(self):
        item = record()
        for name in ("statement_version", "experiment", "missing"):
            with self.subTest(field=name):
                broken = copy.deepcopy(item)
                broken.pop(name)
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=payload(broken)))
                self.assertIn(name, str(caught.exception))

    def test_all_problems_are_reported_at_once(self):
        broken = record(gate="pending", total=88.0, missing=[])
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(broken)))
        message = str(caught.exception)
        self.assertIn("不得给总分", message)
        self.assertIn("missing", message)

    def test_evidence_keys_must_match_scores(self):
        """pass 的 evidence 不能是与 scores 无关的一堆键。"""
        for case, evidence in (
            ("完全不对应", {"别的项": "事实：x"}),
            ("缺一项", {k: "事实：x" for k in list(WEIGHTS)[:8]}),
            ("空对象", {}),
        ):
            with self.subTest(case=case):
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=payload(record(evidence=evidence))))
                self.assertIn("evidence", str(caught.exception))

    def test_missing_entries_must_be_non_empty_strings(self):
        for bad in ([None], [""], ["   "], ["待补", None]):
            with self.subTest(missing=bad):
                item = record(gate="pending", total=None, missing=bad)
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=payload(item)))
                self.assertIn("missing", str(caught.exception))

    def test_experiment_entries_must_be_non_empty_strings(self):
        item = record(experiment=["有内容", None])
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("experiment", str(caught.exception))

    def test_evidence_cutoff_must_be_non_empty_string(self):
        for bad in ("", "   ", None, 20261128):
            with self.subTest(cutoff=bad):
                broken = payload(record())
                broken["evidence_cutoff"] = bad
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=broken))
                self.assertIn("evidence_cutoff", str(caught.exception))

    def test_hard_gates_must_be_present_in_scores(self):
        """从权重、分数、依据里删掉一道硬门槛不能变成合规记录。"""
        for name in ("新意落点", "空白成因"):
            with self.subTest(gate_item=name):
                weights = {k: v for k, v in WEIGHTS.items() if k != name}
                scores = {k: 2 for k in weights}
                evidence = {k: "事实：x" for k in weights}
                broken = payload(record(scores=scores, evidence=evidence, total=100.0))
                broken["weights"] = weights
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=broken))
                self.assertIn("硬门槛项", str(caught.exception))

    def test_weights_must_not_be_negative(self):
        broken = payload(record())
        broken["weights"] = {**WEIGHTS, "价值": -1}
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=broken))
        self.assertIn("不为负", str(caught.exception))

    def test_independent_errors_are_reported_together(self):
        """gate 非法时，与该 gate 无关的结构错误仍要一起列出。"""
        item = record(gate="keep", experiment="文字", missing={"a": 1})
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        message = str(caught.exception)
        self.assertIn("experiment 须是数组", message)
        self.assertIn("missing 须是数组", message)
        self.assertIn("gate 须是", message)

    def test_illegal_gate_does_not_hide_score_errors(self):
        scores = dict(SCORES)
        scores["价值"] = 9
        evidence = dict(EVIDENCE)
        item = record(gate="keep", scores=scores, evidence=evidence)
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        message = str(caught.exception)
        self.assertIn("分数须是", message)
        self.assertIn("gate 须是", message)

    def test_materials_without_scores_still_save(self):
        result = self.save(self.materials())
        self.assertEqual(result["status"], "ready")

    def test_materials_without_object_saves_as_before(self):
        """不带 candidate_scores 时按原行为保存；其他阶段由 test_interview 回归覆盖。"""
        result = self.save(self.materials())
        self.assertEqual(result["status"], "ready")
        state = read_json(self.proposal / "研究计划状态.json")
        work = state["works"][self.revision]
        self.assertEqual(work["steps"]["materials"]["status"], "complete")

    def test_scores_shape_is_required(self):
        for name, value in (
            ("不是对象", "candidate_scores 须是对象"),
            ("缺 weights", "缺少 weights"),
            ("缺 evidence_cutoff", "缺少 evidence_cutoff"),
            ("权重为空", "weights 须是非空对象"),
            ("权重非数字", "权重为不为负的数字"),
            ("items 为空", "items 须是非空数组"),
            ("items 不是数组", "items 须是非空数组"),
        ):
            with self.subTest(case=name):
                broken = payload(record())
                if name == "不是对象":
                    broken = ["not", "an", "object"]
                elif name == "缺 weights":
                    broken.pop("weights")
                elif name == "缺 evidence_cutoff":
                    broken.pop("evidence_cutoff")
                elif name == "权重为空":
                    broken["weights"] = {}
                elif name == "权重非数字":
                    broken["weights"] = {**WEIGHTS, "问题成形": "15"}
                elif name == "items 为空":
                    broken["items"] = []
                else:
                    broken["items"] = "not-a-list"
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=broken))
                self.assertIn(value, str(caught.exception))

    def test_gate_must_be_known_value(self):
        item = record(gate="keep")
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("gate 须是", str(caught.exception))

    def test_non_stop_gates_must_not_carry_stop_fields(self):
        for gate, field, value in (
            ("pass", "stop_reason", "gap_zero"),
            ("pass", "merged_into", "C2"),
            ("soft_stop", "stop_reason", "novelty_zero"),
            ("pending", "stop_reason", "gap_zero"),
            ("pending", "merged_into", "C2"),
            ("merge", "stop_reason", "gap_zero"),
        ):
            with self.subTest(gate=gate, field=field):
                item = record(
                    gate=gate, total=None if gate in ("pending", "merge") else 70.0,
                    missing=["待办"], **{field: value},
                )
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=payload(record(id="C2"), item)))
                self.assertIn(field, str(caught.exception))

    def test_merge_cannot_point_to_itself(self):
        item = record(id="C1", gate="merge", total=None, merged_into="C1")
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("不能指向自己", str(caught.exception))

    def test_score_values_are_limited(self):
        for bad in (3, -1, 1.5, "2"):
            with self.subTest(score=bad):
                scores = dict(SCORES)
                scores["价值"] = bad
                item = record(scores=scores)
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=payload(item)))
                self.assertIn("分数须是", str(caught.exception))

    def test_experiment_and_missing_must_be_arrays(self):
        for field in ("experiment", "missing"):
            for bad in ("文字", {"a": 1}):
                with self.subTest(field=field, value=type(bad).__name__):
                    item = record(**{field: bad})
                    with self.assertRaises(ValueError) as caught:
                        self.save(self.materials(candidate_scores=payload(item)))
                    self.assertIn(f"{field} 须是数组", str(caught.exception))

    def test_evidence_must_be_object(self):
        item = record(evidence=["事实：数组写法不被接受"])
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(item)))
        self.assertIn("evidence 须是对象", str(caught.exception))

    def test_soft_stop_with_evidence_is_accepted(self):
        item = record(gate="soft_stop", total=70.0, missing=["软门槛补法：先找使用者"])
        result = self.save(self.materials(candidate_scores=payload(item)))
        self.assertEqual(result["status"], "ready")

    def test_malformed_id_types_raise_value_error(self):
        """畸形 id 或题面版本按 ValueError 报问题，不抛 TypeError。"""
        for field, bad in (("id", ["C1"]), ("id", {"a": 1}), ("id", ""), ("id", "   "),
                           ("statement_version", ["q1"]), ("statement_version", {"a": 1}),
                           ("statement_version", ""), ("statement_version", "   ")):
            with self.subTest(field=field):
                item = record(**{field: bad})
                with self.assertRaises(ValueError):
                    self.save(self.materials(candidate_scores=payload(item)))

    def test_hard_gate_score_must_match_stop_reason(self):
        """停因要求对应硬门槛恰好为 0：分数全过却记停，是把候选误记为停。"""
        for reason, gate_item in (("gap_zero", "空白成因"), ("novelty_zero", "新意落点")):
            with self.subTest(reason=reason):
                item = record(gate="hard_stop", total=None, stop_reason=reason)
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=payload(item)))
                message = str(caught.exception)
                self.assertIn(reason, message)
                self.assertIn(gate_item, message)
                self.assertIn("= 0", message)

        # 停因与那一道门槛对得上才是合规的。
        for reason, gate_item in (("gap_zero", "空白成因"), ("novelty_zero", "新意落点")):
            with self.subTest(reason=reason, accepted=True):
                scores = dict(SCORES)
                scores[gate_item] = 0
                item = record(gate="hard_stop", total=None, stop_reason=reason,
                              scores=scores, missing=["反例还待核"])
                self.assertEqual(
                    self.save(self.materials(candidate_scores=payload(item)))["status"], "ready"
                )

    def test_problem_invalid_needs_no_zero_gate(self):
        """`problem_invalid` 不在九项里，不要求哪一项为 0。"""
        item = record(gate="hard_stop", total=None, stop_reason="problem_invalid",
                      missing=["反例还待核"])
        self.assertEqual(self.save(self.materials(candidate_scores=payload(item)))["status"], "ready")

    def test_zero_hard_gate_cannot_pass_or_soft_stop(self):
        """硬门槛记 0 却记可推进或备选，会让未过门槛的候选进入推荐。"""
        for gate, gate_item in (("pass", "空白成因"), ("pass", "新意落点"),
                                ("soft_stop", "空白成因"), ("soft_stop", "新意落点")):
            with self.subTest(gate=gate, gate_item=gate_item):
                scores = dict(SCORES)
                scores[gate_item] = 0
                item = record(scores=scores, gate=gate, missing=["软门槛补法：先找使用者"])
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=payload(item)))
                message = str(caught.exception)
                self.assertIn(gate_item, message)
                self.assertIn("硬门槛", message)

        # 记 0 又记 pending 是合规的：还没判完就该停在待补。
        scores = dict(SCORES)
        scores["空白成因"] = 0
        stopped = record(scores=scores, gate="pending", total=None,
                         missing=["已证伪后还要确认是否换切口"])
        self.assertEqual(self.save(self.materials(candidate_scores=payload(stopped)))["status"], "ready")

    def test_merge_does_not_require_zero_gate(self):
        """`merge` 的判据只有并入目标，文档没有硬门槛要求，不扩大到它。"""
        scores = dict(SCORES)
        scores["空白成因"] = 0
        merged = record(id="C2", scores=scores, gate="merge", total=None, merged_into="C1")
        self.assertEqual(
            self.save(self.materials(candidate_scores=payload(record(id="C1"), merged)))["status"],
            "ready",
        )

    def test_blank_evidence_is_rejected(self):
        """依据是空白串或非文本时，不能当成已有依据。"""
        for bad in ("   ", "", True, 1, None):
            with self.subTest(evidence_value=bad):
                evidence = {name: "事实：合成依据" for name in WEIGHTS}
                evidence["价值"] = bad
                with self.assertRaises(ValueError) as caught:
                    self.save(self.materials(candidate_scores=payload(record(evidence=evidence))))
                self.assertIn("evidence", str(caught.exception))

    def test_extra_evidence_key_is_rejected(self):
        """多出一个没有对应分数的依据键，说明依据与分数对不上。"""
        evidence = dict(EVIDENCE)
        evidence["无对应评分项"] = "事实：x"
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(record(evidence=evidence))))
        self.assertIn("evidence 含有 scores 里没有的项", str(caught.exception))
        self.assertIn("无对应评分项", str(caught.exception))

    def test_scores_and_evidence_errors_are_reported_together(self):
        """一方类型写错不能让另一方的错误消失。"""
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(
                record(scores=[], evidence=[], gate="keep"))))
        message = str(caught.exception)
        self.assertIn("scores 须是对象", message)
        self.assertIn("evidence 须是对象", message)
        self.assertIn("gate 须是", message)

    def test_out_of_range_score_survives_evidence_error(self):
        """`evidence` 不是对象时，越界分数仍要一起报出。"""
        scores = dict(SCORES)
        scores["价值"] = 9
        with self.assertRaises(ValueError) as caught:
            self.save(self.materials(candidate_scores=payload(record(scores=scores, evidence=[]))))
        message = str(caught.exception)
        self.assertIn("evidence 须是对象", message)
        self.assertIn("分数须是", message)


class VerdictWithoutScoresTests(ComponentCase):
    """单候选、不评分时的判决记录：只记判决与三样内容，不记分数与总分。"""

    def setUp(self):
        super().setUp()
        self.proposal = self.output / "proposal"
        self.proposal.mkdir()
        started = self.call("begin_revision", {
            "proposal_dir": str(self.proposal), "expected_state_version": None,
            "inputs": {
                "application_id": "合成项目-免评分判决", "purpose": "联系教授",
                "question_id": "q1", "material_paths": [],
            },
        })
        self.assertEqual(started["status"], "ready")
        self.revision = started["revision_id"]

    def save(self, data):
        state = read_json(self.proposal / "研究计划状态.json")
        return self.call("save_revision", {
            "proposal_dir": str(self.proposal), "revision_id": self.revision,
            "expected_state_version": state["state_version"],
            "stage": "materials", "data": data,
        })

    def verdict(self, **overrides):
        item = {
            "id": "C1",
            "statement_version": "q1",
            "gate": "pass",
            "experiment": ["初测高于预注册判据线"],
            "missing": [],
            "evidence": ["全文：最接近的三篇都只回答相邻问题"],
        }
        item.update(overrides)
        return item

    def verdicts(self, *items):
        return {"evidence_cutoff": "2026-11-28", "items": list(items)}

    def test_single_candidate_verdict_is_saved(self):
        """单候选、可以推进、没有总分：按题面版本读回判决。"""
        result = self.save({
            "materials": [], "candidates": [{"id": "C1", "question": "唯一候选"}],
            "verdicts": self.verdicts(self.verdict()),
        })
        self.assertEqual(result["status"], "ready")
        state = read_json(self.proposal / "研究计划状态.json")
        saved = read_json(
            state["works"][self.revision]["steps"]["materials"]["artifacts"]["data"]
        )
        saved_item = saved["verdicts"]["items"][0]
        self.assertEqual(saved_item["statement_version"], "q1")
        self.assertEqual(saved_item["gate"], "pass")
        self.assertNotIn("total", saved_item)
        self.assertNotIn("scores", saved_item)

    def test_verdict_must_not_carry_scores_or_total(self):
        """免评分形态不写 scores、weights、total；写了说明该走 candidate_scores。"""
        for extra in ({"scores": {}}, {"scores": None}, {"weights": {}},
                      {"total": 70.0}, {"total": None}):
            with self.subTest(extra=list(extra)):
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "verdicts": self.verdicts(
                        self.verdict(**extra))})
                message = str(caught.exception)
                self.assertIn("免评分判决", message)
                self.assertIn(list(extra)[0], message)

    def test_verdict_gate_limited_to_three(self):
        """没有比较就没有排序：备选与并入不能用在这条路径。"""
        for gate in ("soft_stop", "merge"):
            with self.subTest(gate=gate):
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "verdicts": self.verdicts(
                        self.verdict(gate=gate))})
                self.assertIn("verdicts.items[0]", str(caught.exception))

    def test_verdict_hard_stop_needs_reason(self):
        with self.assertRaises(ValueError) as caught:
            self.save({"materials": [], "verdicts": self.verdicts(
                self.verdict(gate="hard_stop"))})
        self.assertIn("stop_reason", str(caught.exception))

        for bad_reason in ("too_low", "gap_zero_typo", "", None, ["gap_zero"]):
            with self.subTest(stop_reason=bad_reason):
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "verdicts": self.verdicts(
                        self.verdict(gate="hard_stop", stop_reason=bad_reason))})
                self.assertIn("stop_reason", str(caught.exception))

        result = self.save({"materials": [], "verdicts": self.verdicts(
            self.verdict(gate="hard_stop", stop_reason="problem_invalid"))})
        self.assertEqual(result["status"], "ready")

    def test_verdict_pending_needs_missing(self):
        with self.assertRaises(ValueError) as caught:
            self.save({"materials": [], "verdicts": self.verdicts(
                self.verdict(gate="pending", missing=[]))})
        self.assertIn("missing", str(caught.exception))

        result = self.save({"materials": [], "verdicts": self.verdicts(
            self.verdict(gate="pending", missing=["还缺关键数据"]) )})
        self.assertEqual(result["status"], "ready")

    def test_verdict_pass_and_hard_stop_need_evidence(self):
        for gate, extra in (("pass", {}),
                            ("hard_stop", {"stop_reason": "problem_invalid"})):
            with self.subTest(gate=gate):
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "verdicts": self.verdicts(
                        self.verdict(gate=gate, evidence=[], **extra))})
                self.assertIn("evidence", str(caught.exception))

    def test_verdict_entries_must_be_non_empty_strings(self):
        """数组项要是去掉首尾空白后仍有内容的字符串；空白串与非文本都不算。"""
        for name in ("experiment", "missing", "evidence"):
            for bad in ([None], [""], ["   "], [True], [1], ["有内容", None]):
                with self.subTest(field=name, value=bad):
                    with self.assertRaises(ValueError) as caught:
                        self.save({"materials": [], "verdicts": self.verdicts(
                            self.verdict(gate="pending", **{name: bad}))})
                    self.assertIn(name, str(caught.exception))

    def test_verdict_needs_cutoff_and_items(self):
        for broken in ({}, {"items": [self.verdict()]},
                       {"evidence_cutoff": "", "items": [self.verdict()]},
                       {"evidence_cutoff": "   ", "items": [self.verdict()]},
                       {"evidence_cutoff": 20261128, "items": [self.verdict()]},
                       {"evidence_cutoff": None, "items": [self.verdict()]},
                       {"evidence_cutoff": "2026-11-28", "items": []},
                       {"evidence_cutoff": "2026-11-28", "items": {}}):
            with self.subTest(keys=sorted(broken, key=str)):
                with self.assertRaises(ValueError):
                    self.save({"materials": [], "verdicts": broken})

    def test_verdict_statement_version_unique(self):
        with self.assertRaises(ValueError) as caught:
            self.save({"materials": [], "verdicts": self.verdicts(
                self.verdict(), self.verdict())})
        self.assertIn("题面版本", str(caught.exception))

    def test_verdict_and_candidate_scores_coexist(self):
        """一次保存里既有比较过的候选、又有单候选判决，各按自己的规则校验。"""
        result = self.save({
            "materials": [],
            "candidate_scores": payload(record(id="C1")),
            "verdicts": self.verdicts(self.verdict(id="C9", statement_version="q9")),
        })
        self.assertEqual(result["status"], "ready")

    def test_verdict_rejection_writes_nothing(self):
        self.assertEqual(self.save({"materials": []})["status"], "ready")
        before = read_json(self.proposal / "研究计划状态.json")["state_version"]
        with self.assertRaises(ValueError):
            self.save({"materials": [], "verdicts": self.verdicts(self.verdict(gate="merge"))})
        self.assertEqual(read_json(self.proposal / "研究计划状态.json")["state_version"], before)

    def test_one_compliant_one_invalid_split(self):
        """一合规一违规时，判定的方向必须落在出错的那一侧。"""
        # 只有 candidate_scores 违规
        with self.assertRaises(ValueError) as caught:
            self.save({"materials": [],
                       "candidate_scores": payload(record(gate="pending", total=88.0, missing=[])),
                       "verdicts": self.verdicts(self.verdict(id="C9", statement_version="q9"))})
        message = str(caught.exception)
        self.assertIn("不得给总分", message)
        self.assertNotIn("verdicts.items", message)

        # 只有 verdicts 违规（用不同题面版本，避免同时命中跨对象重复）
        with self.assertRaises(ValueError) as caught:
            self.save({"materials": [],
                       "candidate_scores": payload(record()),
                       "verdicts": self.verdicts(self.verdict(id="C9", statement_version="q9",
                                                              gate="merge"))})
        message = str(caught.exception)
        self.assertIn("verdicts.items", message)
        self.assertNotIn("不得给总分", message)

    def test_compliant_scores_and_verdicts_are_saved_verbatim(self):
        """两个对象都合规时原样落盘，不补字段、不改写。

        两条记录必须属于不同题面版本：同一 `(id, statement_version)` 只能有一条判决。
        """
        scores_payload = payload(record(id="C1", statement_version="q1"))
        verdicts_payload = self.verdicts(self.verdict(id="C2", statement_version="q2"))
        self.assertEqual(
            self.save({"materials": [], "candidate_scores": scores_payload,
                       "verdicts": verdicts_payload})["status"],
            "ready",
        )
        state = read_json(self.proposal / "研究计划状态.json")
        saved = read_json(
            state["works"][self.revision]["steps"]["materials"]["artifacts"]["data"]
        )
        self.assertEqual(saved["candidate_scores"], scores_payload)
        self.assertEqual(saved["verdicts"], verdicts_payload)

    def test_verdict_required_fields_must_be_present(self):
        """六个必填字段逐个删除都要被拒，并指名字段。"""
        for name in ("id", "statement_version", "gate", "experiment", "missing", "evidence"):
            with self.subTest(field=name):
                item = self.verdict()
                item.pop(name)
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "verdicts": self.verdicts(item)})
                self.assertIn(name, str(caught.exception))

    def test_verdicts_top_level_and_items_shapes(self):
        """`verdicts` 须是对象、`items` 须是非空数组、每个条目须是对象。"""
        for label, broken in (
            ("顶层是数组", []),
            ("顶层是 null", None),
            ("顶层是字符串", "verdicts"),
            ("items 含 null", {"evidence_cutoff": "2026-11-28", "items": [None]}),
            ("items 含数字", {"evidence_cutoff": "2026-11-28", "items": [1]}),
        ):
            with self.subTest(case=label):
                with self.assertRaises(ValueError):
                    self.save({"materials": [], "verdicts": broken})

    def test_verdict_gate_unknown_value_is_rejected(self):
        """除 `soft_stop`、`merge` 外，未知值同样要被拒。"""
        for bad in ("keep", "", None, 1, ["pass"]):
            with self.subTest(gate=bad):
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "verdicts": self.verdicts(
                        self.verdict(gate=bad, missing=["还缺数据"]))})
                self.assertIn("gate", str(caught.exception))

    def test_verdict_id_and_version_must_be_non_empty_strings(self):
        for field in ("id", "statement_version"):
            for bad in ("", "   ", ["C1"], {"a": 1}, 1, None):
                with self.subTest(field=field, value=bad):
                    with self.assertRaises(ValueError):
                        self.save({"materials": [], "verdicts": self.verdicts(
                            self.verdict(**{field: bad}))})

    def test_verdict_array_fields_must_be_arrays(self):
        """三个内容字段传非数组时按“须是数组”拒绝，不抛 TypeError。"""
        for field in ("experiment", "missing", "evidence"):
            for bad in ("文字", {"a": 1}, None, 1):
                with self.subTest(field=field, value=bad):
                    with self.assertRaises(ValueError) as caught:
                        self.save({"materials": [], "verdicts": self.verdicts(
                            self.verdict(**{field: bad}))})
                    self.assertIn(field, str(caught.exception))

    def test_verdict_does_not_use_score_rules(self):
        """免评分形态不走 candidate_scores 的分数规则：没有 weighted 项也能存。"""
        result = self.save({"materials": [], "verdicts": self.verdicts(self.verdict())})
        self.assertEqual(result["status"], "ready")

    def test_verdict_non_stop_gate_must_not_carry_reason(self):
        """只有 `hard_stop` 写停因；`pass`、`pending` 带 `stop_reason` 是缺口。"""
        for gate, extra in (("pass", {}), ("pending", {"missing": ["还缺数据"]})):
            with self.subTest(gate=gate):
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "verdicts": self.verdicts(
                        self.verdict(gate=gate, stop_reason="gap_zero", **extra))})
                self.assertIn("stop_reason", str(caught.exception))

    def test_verdict_all_problems_reported_at_once(self):
        """一条记录内多处独立错误要一次报全。"""
        broken = self.verdict(gate="pending", missing=[], evidence=["   "],
                              experiment="文字")
        with self.assertRaises(ValueError) as caught:
            self.save({"materials": [], "verdicts": self.verdicts(broken)})
        message = str(caught.exception)
        for expected in ("experiment", "missing", "evidence"):
            self.assertIn(expected, message)

    def test_both_objects_report_problems_together(self):
        """两个对象同时有错时一次列全，不先报一个、补完再报另一个。"""
        bad_scores = record(gate="pending", total=88.0, missing=[])
        bad_verdict = self.verdict(gate="pending", missing=[])
        with self.assertRaises(ValueError) as caught:
            self.save({"materials": [],
                       "candidate_scores": payload(bad_scores),
                       "verdicts": self.verdicts(bad_verdict)})
        message = str(caught.exception)
        # candidate_scores 的问题
        self.assertIn("不得给总分", message)
        # verdicts 的问题
        self.assertIn("verdicts.items[0]", message)

    def test_both_objects_valid_still_save(self):
        result = self.save({
            "materials": [],
            "candidate_scores": payload(record(id="C1")),
            "verdicts": self.verdicts(self.verdict(id="C9", statement_version="q9")),
        })
        self.assertEqual(result["status"], "ready")

    def test_cross_object_statement_version_must_be_unique(self):
        """同一 (id, statement_version) 不能同时记在两个对象里，否则两份判决互相矛盾。"""
        cases = {
            "同版本相反判决": (payload(record(id="C1", statement_version="q1", gate="pass")),
                              self.verdicts(self.verdict(id="C1", statement_version="q1",
                                                         gate="hard_stop",
                                                         stop_reason="problem_invalid"))),
            "同版本同判决": (payload(record(id="C1", statement_version="q1", gate="pass")),
                            self.verdicts(self.verdict(id="C1", statement_version="q1",
                                                       gate="pass"))),
        }
        for label, (scores_payload, verdicts_payload) in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "candidate_scores": scores_payload,
                               "verdicts": verdicts_payload})
                message = str(caught.exception)
                self.assertIn("题面版本", message)
                self.assertIn("candidate_scores", message)
                self.assertIn("verdicts", message)

        # 不同版本或不同候选可以并存。
        ok = self.save({
            "materials": [],
            "candidate_scores": payload(record(id="C1", statement_version="q1")),
            "verdicts": self.verdicts(self.verdict(id="C1", statement_version="q2")),
        })
        self.assertEqual(ok["status"], "ready")

    def test_verdict_bad_reason_type_does_not_raise_type_error(self):
        """停因写成列表或对象时按 ValueError 报问题，不能抛 TypeError 打断整份报错。"""
        for bad in ([], {}, ["gap_zero"], {"gap_zero": 1}):
            with self.subTest(stop_reason=bad):
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "verdicts": self.verdicts(
                        self.verdict(gate="hard_stop", stop_reason=bad, missing=["x"]))})
                self.assertIn("stop_reason", str(caught.exception))

    def test_bad_stop_reason_keeps_other_errors_visible(self):
        """`candidate_scores` 的停因形态非法时不抛 TypeError，且另一对象的独立错误仍要一起报出。

        真正会走到停因表字典查找的是候选侧（两道硬门槛已评分）；这里覆盖列表与对象
        两种形态，保留 `verdicts` 一侧 `pending` 缺 `missing` 的独立错误。
        """
        for bad_reason in ([], {}):
            with self.subTest(stop_reason=bad_reason):
                with self.assertRaises(ValueError) as caught:
                    self.save({
                        "materials": [],
                        "candidate_scores": payload(record(gate="hard_stop", total=None,
                                                           stop_reason=bad_reason,
                                                           missing=["x"])),
                        "verdicts": self.verdicts(self.verdict(id="C9", statement_version="q9",
                                                               gate="pending", missing=[])),
                    })
                message = str(caught.exception)
                self.assertIn("stop_reason", message)
                self.assertIn("verdicts.items", message)

    def test_blank_evidence_reported_even_when_scores_malformed(self):
        """依据取值能独立判断：scores 形态写错时也要一并报出空白依据。"""
        evidence = {name: "事实：合成依据" for name in WEIGHTS}
        evidence["价值"] = "   "
        for bad_scores in ([], "70", None):
            with self.subTest(scores_type=type(bad_scores).__name__):
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "candidate_scores": payload(
                        record(scores=bad_scores, evidence=evidence))})
                message = str(caught.exception)
                self.assertIn("scores 须是对象", message)
                self.assertIn("不是有效依据", message)

    def test_zero_denominator_cannot_pass(self):
        """只留一项正权重而该项未评时分母为零，两种判决都不能记。"""
        weights = {name: 0 for name in WEIGHTS}
        weights["价值"] = 15
        scores = {name: 2 for name in WEIGHTS}
        scores["价值"] = None
        evidence = {name: "事实：合成依据" for name in WEIGHTS}
        for gate in ("pass", "soft_stop"):
            with self.subTest(gate=gate):
                broken = {"weights": weights, "evidence_cutoff": "2026-11-28",
                          "items": [record(gate=gate, scores=scores, evidence=evidence,
                                           total=100.0, missing=["软门槛补法：先找使用者"])]}
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "candidate_scores": broken})
                message = str(caught.exception)
                self.assertIn("正权重", message)
                self.assertIn("分母", message)

        # 改记 pending 并写明缺项即可保存。
        pending = {"weights": weights, "evidence_cutoff": "2026-11-28",
                   "items": [record(gate="pending", total=None, scores=scores,
                                    evidence=evidence, missing=["价值还缺使用者访谈"])]}
        self.assertEqual(
            self.save({"materials": [], "candidate_scores": pending})["status"], "ready"
        )

    def test_zero_weights_still_need_one_positive(self):
        """整表权重为 0 时没有可计入的项，两种判决都无从计算。"""
        weights = {name: 0 for name in WEIGHTS}
        for gate in ("pass", "soft_stop"):
            with self.subTest(gate=gate):
                broken = {"weights": weights, "evidence_cutoff": "2026-11-28",
                          "items": [record(gate=gate, total=100.0,
                                           missing=["软门槛补法：先找使用者"])]}
                with self.assertRaises(ValueError) as caught:
                    self.save({"materials": [], "candidate_scores": broken})
                self.assertIn("正权重", str(caught.exception))

    def test_merge_may_target_candidate_only_in_verdicts(self):
        """`merged_into` 指向候选身份；候选只记在 `verdicts` 里也应算存在。"""
        merged = record(id="C2", gate="merge", total=None, merged_into="C9")
        result = self.save({
            "materials": [],
            "candidate_scores": payload(merged),
            "verdicts": self.verdicts(self.verdict(id="C9", statement_version="q9")),
        })
        self.assertEqual(result["status"], "ready")

    def test_same_object_duplicate_not_reported_as_cross_object(self):
        """同对象内重复由各自校验报出，错误文本不写成“同时记在两个同一对象里”。"""
        cases = {
            "candidate_scores": payload(
                record(id="C1", statement_version="q1"),
                record(id="C1", statement_version="q1"),
            ),
            "verdicts": None,  # 下面单独构造
        }
        verdicts_dup = self.verdicts(
            self.verdict(id="C1", statement_version="q1"),
            self.verdict(id="C1", statement_version="q1"),
        )
        for label, payload_value in cases.items():
            with self.subTest(obj=label):
                data = {"materials": []}
                if label == "verdicts":
                    data["verdicts"] = verdicts_dup
                else:
                    data["candidate_scores"] = payload_value
                with self.assertRaises(ValueError) as caught:
                    self.save(data)
                message = str(caught.exception)
                self.assertIn("重复", message)
                self.assertNotIn(f"同时记在 {label} 与 {label}", message)

    def test_cross_object_error_points_to_remedy(self):
        """跨对象重复的报错要给出补救办法，与文档保存节第 5 条同一句。"""
        with self.assertRaises(ValueError) as caught:
            self.save({"materials": [],
                       "candidate_scores": payload(record(id="C1", statement_version="q1")),
                       "verdicts": self.verdicts(self.verdict(id="C1", statement_version="q1",
                                                              gate="pass"))})
        message = str(caught.exception)
        self.assertIn("保留一条", message)
        self.assertIn("删掉或移走另一条", message)

    def test_same_version_different_candidates_can_coexist(self):
        """唯一键是 `(id, statement_version)`：同一题面文字下不同候选可以各有一条。"""
        result = self.save({
            "materials": [],
            "candidate_scores": payload(record(id="C1", statement_version="q1")),
            "verdicts": self.verdicts(self.verdict(id="C2", statement_version="q1")),
        })
        self.assertEqual(result["status"], "ready")
