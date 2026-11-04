"""RP-11 的 Markdown 失败与恢复分支；基准来自真实成稿。"""

import copy
import os
from pathlib import Path
from unittest import mock

from support import SavedDraftCase, digest, read_json, required_path, write_json


class Interrupted(BaseException):
    pass


class RecoveryTests(SavedDraftCase):
    def test_first_draft_export_failure_has_no_current(self):
        requests = read_json(required_path("RP_SAVE_REQUESTS"))
        current = self.initial["works"][self.initial["current"]["revision_id"]]
        proposal = self.output / "first-md"
        proposal.mkdir()
        started = self.call("begin_revision", {
            "proposal_dir": str(proposal), "expected_state_version": None,
            "inputs": current["inputs"],
        })
        self.assertEqual(started["status"], "ready")
        revision = started["revision_id"]
        state_path = proposal / "研究计划状态.json"

        def request(**fields):
            return {
                "proposal_dir": str(proposal), "revision_id": revision,
                "expected_state_version": read_json(state_path, ".state_version"),
                **fields,
            }

        for stage in ("materials", "question", "scheme", "body"):
            saved = self.call("save_revision", request(stage=stage, data=requests[stage]["data"]))
            self.assertEqual(saved["status"], "ready")
        work = read_json(state_path)["works"][revision]
        directory = Path(work["directory"])
        body_hash = digest(directory / "正文.json")
        (directory / "研究计划草稿.md").mkdir()
        try:
            result = self.call("export_revision", request(formats=["md"]))
            self.assertIn(result["status"], {"blocked", "needs_input"})
        except OSError:
            pass
        rejected = self.call("commit_revision", request())
        self.assertNotEqual(rejected["status"], "committed")
        self.assertIsNone(read_json(state_path)["current"])
        self.assertEqual(digest(directory / "正文.json"), body_hash)

    def test_markdown_export_fails_then_recovers(self):
        revision = self.begin()
        directory = Path(self.work(revision)["directory"])
        body_hash = digest(directory / "正文.json")
        blocked_path = directory / "研究计划草稿.md"
        blocked_path.mkdir()
        try:
            result = self.export(revision)
            self.assertIn(result["status"], {"blocked", "needs_input"})
        except OSError:
            # 正式文件条件触发的原错误允许直接保留；仍必须保存进度。
            pass
        rejected = self.call("commit_revision", self.request(revision))
        self.assertNotEqual(rejected["status"], "committed")
        self.assert_current_unchanged()
        self.assertEqual(digest(directory / "正文.json"), body_hash)
        self.assertNotEqual(self.work(revision)["steps"]["md"]["status"], "complete")
        blocked_path.rmdir()
        self.assertEqual(self.export(revision)["status"], "ready")
        self.assertEqual(digest(directory / "正文.json"), body_hash)
        review = self.review(revision)
        self.assertTrue(review["checks"]["content_consistent"])
        self.assertEqual(review["checks"]["checked_formats"], ["md"])
        committed = self.call("commit_revision", self.request(revision))
        self.assertEqual(committed["status"], "committed")
        self.assertEqual(committed["state"]["current"]["revision_id"], revision)
        self.assertTrue(Path(committed["artifacts"]["md"]).is_file())

    def test_content_mismatch_does_not_commit(self):
        revision = self.ready_work()
        directory = Path(self.work(revision)["directory"])
        markdown = directory / "研究计划草稿.md"
        markdown.write_text(markdown.read_text(encoding="utf-8") + "\n遗漏检查：与正式正文不一致。\n", encoding="utf-8")
        result = self.review(revision)
        self.assertFalse(result["checks"]["content_consistent"])
        self.assertNotEqual(self.call("commit_revision", self.request(revision))["status"], "committed")
        self.assert_current_unchanged()
        self.assertTrue(markdown.exists())

    def test_saved_stage_survives_interruption(self):
        # 这些 data 来自 RP-08 实际保存件，不编写新的确认记录。
        requests = read_json(required_path("RP_SAVE_REQUESTS"))
        current = self.initial["works"][self.initial["current"]["revision_id"]]
        stages = ("materials", "question", "scheme", "body")
        for stage in ("materials", "scheme", "body"):
            with self.subTest(stage=stage):
                proposal = self.output / f"interrupted-{stage}"
                proposal.mkdir()
                started = self.call("begin_revision", {
                    "proposal_dir": str(proposal), "expected_state_version": None,
                    "inputs": current["inputs"],
                })
                self.assertEqual(started["status"], "ready")
                revision = started["revision_id"]
                state_path = proposal / "研究计划状态.json"

                def request(**fields):
                    return {
                        "proposal_dir": str(proposal), "revision_id": revision,
                        "expected_state_version": read_json(state_path, ".state_version"),
                        **fields,
                    }

                for earlier in stages[:stages.index(stage)]:
                    saved = self.call("save_revision", request(stage=earlier, data=requests[earlier]["data"]))
                    self.assertEqual(saved["status"], "ready")
                previous = read_json(state_path)
                previous_work = previous["works"][revision]
                preserved = {}

                def remember_files(value):
                    if isinstance(value, dict):
                        for item in value.values():
                            remember_files(item)
                    elif isinstance(value, list):
                        for item in value:
                            remember_files(item)
                    elif isinstance(value, str) and value.startswith("/"):
                        path = Path(value)
                        if path.is_file() and path.is_relative_to(Path(previous_work["directory"])):
                            preserved[str(path)] = digest(path)

                for earlier in stages[:stages.index(stage)]:
                    remember_files(previous_work["steps"][earlier])
                real_replace = os.replace
                reached = []

                def interrupt(source, destination, *args, **kwargs):
                    if Path(destination) == state_path:
                        reached.append(True)
                        raise Interrupted("RP-11：步骤保存期间中断")
                    return real_replace(source, destination, *args, **kwargs)

                with mock.patch("os.replace", side_effect=interrupt):
                    with self.assertRaises(Interrupted):
                        self.call("save_revision", request(stage=stage, data=requests[stage]["data"]))
                self.assertTrue(reached, "未到达计划约定的状态替换边界")
                self.assertEqual(read_json(state_path)["current"], previous["current"])
                self.assertEqual(read_json(state_path)["state_version"], previous["state_version"])
                resumed = self.call("resume_revision", request())
                self.assertNotEqual(resumed["status"], "conflict")
                resumed_work = resumed["state"]["works"][revision]
                self.assertNotEqual(resumed_work["steps"][stage]["status"], "complete")
                for earlier in stages[:stages.index(stage)]:
                    self.assertEqual(resumed_work["steps"][earlier], previous_work["steps"][earlier])
                for path, content_hash in preserved.items():
                    self.assertEqual(digest(path), content_hash, "先前保存的步骤内容必须保留")
                if stage == "body":
                    self.assertEqual(resumed_work["confirmations"], previous_work["confirmations"])
                    self.assertEqual(resumed_work["conditions"], previous_work["conditions"])
                # 重做未保存的步骤，已保存的其他步骤不得被删除。
                saved = self.call("save_revision", request(stage=stage, data=requests[stage]["data"]))
                self.assertEqual(saved["status"], "ready")
                self.assertEqual(saved["state"]["works"][revision]["steps"][stage]["status"], "complete")
                self.assert_current_unchanged()

    def test_directory_renamed_before_pointer_recovery(self):
        self.check_commit_interruption(after_replace=False)

    def test_pointer_replaced_before_interruption(self):
        self.check_commit_interruption(after_replace=True)

    def check_commit_interruption(self, after_replace):
        revision = self.ready_work()
        real_replace = os.replace
        reached = []

        def interrupt(source, destination, *args, **kwargs):
            if Path(destination) == self.state_path:
                next_state = read_json(source)
                if next_state.get("current", {}).get("revision_id") == revision:
                    reached.append(True)
                    if after_replace:
                        real_replace(source, destination, *args, **kwargs)
                    raise Interrupted("RP-11：最终当前版本切换边界中断")
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch("os.replace", side_effect=interrupt):
            with self.assertRaises(Interrupted):
                self.call("commit_revision", self.request(revision))
        self.assertTrue(reached, "未到达最终状态替换边界")
        state = self.state()
        if after_replace:
            self.assertEqual(state["current"]["revision_id"], revision)
            directory = Path(state["current"]["directory"])
        else:
            self.assert_current_unchanged()
            pending = state["works"][revision]["pending_commit"]
            self.assertEqual(pending["revision_id"], revision)
            directory = Path(pending["target_directory"])
            self.assertTrue(directory.is_dir())
        before = {name: digest(directory / name) for name in (
            "正文.json", "研究计划草稿.md",
        )}
        resumed = self.call("resume_revision", self.request(revision))
        self.assertEqual(resumed["state"]["current"]["revision_id"], revision)
        self.assertEqual(before, {name: digest(directory / name) for name in before})
        self.assertTrue(Path(self.initial["current"]["directory"]).exists())
        self.assertEqual(Path(resumed["artifacts"]["md"]).parent, directory)

    def test_changed_inputs_invalidate_related_work(self):
        for changed in ("body", "material", "selection"):
            with self.subTest(changed=changed):
                revision = self.ready_work()
                work = self.work(revision)
                directory = Path(work["directory"])
                inputs = copy.deepcopy(work["inputs"])
                material = None
                original_material = None
                if changed == "body":
                    body_path = directory / "正文.json"
                    body = read_json(body_path)
                    body["blocks"].append({"t": "Para", "c": [{"t": "Str", "c": "恢复前正文发生变化。"}]})
                    write_json(body_path, body)
                elif changed == "material":
                    material_record_path = required_path("RP_RELATED_MATERIAL_RECORD")
                    material_record = read_json(material_record_path, ".material")
                    material = Path(material_record["original_path"])
                    if not material.is_absolute():
                        material = material_record_path.parent / material
                    material = material.resolve(strict=True)
                    self.assertTrue(material.is_relative_to(required_path("RP_CONSUMER") / "input"))
                    original_material = material.read_bytes()
                    (self.output / "related-material-before").write_bytes(original_material)
                    # 临时替换可见正文，保证实际引用内容改变；不解码 Shift_JIS 原件。
                    # 执行绑定须选择本稿正文实际引用的原文；不新增无关材料。
                    changed_material = b"RP-11 changed source content.\n"
                    if material.suffix.lower() in {".html", ".htm"}:
                        changed_material = b"<html><body>RP-11 changed source content.</body></html>\n"
                else:
                    inputs["question_id"] = "rp11_changed_question"
                try:
                    if material is not None:
                        material.write_bytes(changed_material)
                    resumed = self.call("resume_revision", self.request(revision, inputs=inputs))
                    self.assertNotEqual(resumed["status"], "committed")
                    updated = resumed["state"]["works"][revision]
                    self.assertFalse(updated["checks"].get("content_consistent", False))
                    self.assertNotEqual(self.call("commit_revision", self.request(revision))["status"], "committed")
                    self.assert_current_unchanged()
                    if changed == "body":
                        self.assertEqual(updated["steps"]["materials"], work["steps"]["materials"])
                        self.assertEqual(updated["confirmations"], work["confirmations"])
                    if changed == "selection":
                        self.assertNotEqual(updated["confirmations"]["question"]["status"], "confirmed")
                finally:
                    if material is not None and original_material is not None:
                        material.write_bytes(original_material)

    def test_newer_commit_preserves_late_work(self):
        late = self.begin()
        late_directory = Path(self.work(late)["directory"])
        winner = self.ready_work()
        committed = self.call("commit_revision", self.request(winner))
        self.assertEqual(committed["status"], "committed")
        winner_directory = Path(committed["state"]["current"]["directory"])
        winner_hash = digest(winner_directory / "正文.json")
        late_body = read_json(late_directory / "正文.json")
        result = self.call("save_revision", self.request(
            late, stage="body", data={"body": late_body, "references": []},
        ))
        self.assertEqual(result["status"], "conflict")
        self.assertTrue(late_directory.exists())
        self.assertEqual(self.state()["current"]["revision_id"], winner)
        self.assertEqual(digest(winner_directory / "正文.json"), winner_hash)
