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
        stopped = record(
            id="C2", gate="hard_stop", total=None, stop_reason="gap_zero",
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
