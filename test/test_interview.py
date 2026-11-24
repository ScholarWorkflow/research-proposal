"""讲稿与想定问答的组件检查；只调用本地组件，不调用上游代理或模型服务。

这些用例尚未进入 plan/test-plan.md 的必测清单，属于本次交付的组件证据。
"""

from pathlib import Path

from support import ComponentCase, read_json, write_json
from research_proposal import _interview


SCRIPT = {
    "timing": {"target_minutes": 10, "slides": 3, "chars_per_minute": 300,
               "tolerance_minutes": 1},
    "sections": [
        {"slide": 1, "title": "问题与背景", "minutes": 3,
         "script": "合" * 900, "visual": "背景页只留一句话"},
        {"slide": 2, "title": "方法与判断", "minutes": 4, "script": "研" * 1200},
        {"slide": 3, "title": "进度与备用", "minutes": 3, "script": "备" * 900},
    ],
}

QA = {
    "chars_per_minute": 300, "max_answer_minutes": 1.5,
    "required_categories": ["方法与依据", "可行性", "研究不足"],
    "items": [
        {"category": "方法与依据", "question": "为什么用这个方法？",
         "answer": "因为" * 80, "source": "材料块 3"},
        {"category": "可行性", "question": "两年做得完吗？", "answer": "按" * 100},
        {"category": "研究不足", "question": "这个方案最大的不足是什么？", "answer": "限" * 90},
    ],
}


def kinds(problems):
    return {item["kind"] for item in problems}


class InterviewRenderTests(ComponentCase):
    def test_counts_characters_without_whitespace(self):
        self.assertEqual(_interview.characters(" 一二 三\n四 "), 4)
        self.assertEqual(_interview.characters(""), 0)

    def test_valid_script_and_questions_render(self):
        self.assertEqual(_interview.validate("script", SCRIPT), [])
        text = _interview.render("script", SCRIPT)
        self.assertIn("# 研究计划发表讲稿", text)
        self.assertIn("- 目标时长：10 分钟", text)
        self.assertIn("## 第 2 页｜方法与判断", text)
        self.assertIn("- 讲稿正文总字数（不含空白）：3000", text)
        self.assertIn("视觉提示：背景页只留一句话", text)
        self.assertNotIn("视觉提示", text.split("## 第 2 页")[1])
        self.assertTrue(text.endswith("\n"))

        self.assertEqual(_interview.validate("qa", QA), [])
        answers = _interview.render("qa", QA)
        self.assertIn("## 第 3 条｜研究不足", answers)
        self.assertIn("出处：材料块 3", answers)
        self.assertIn("问：为什么用这个方法？", answers)

    def test_refuses_to_render_invalid_content(self):
        broken = {**SCRIPT, "timing": {**SCRIPT["timing"], "slides": 2}}
        with self.assertRaises(ValueError):
            _interview.render("script", broken)

    def test_script_structure_checks(self):
        broken = {
            "timing": {"target_minutes": 10, "slides": 2, "chars_per_minute": 300,
                       "tolerance_minutes": 1},
            "sections": [
                {"slide": 1, "title": "", "minutes": 0, "script": ""},
                {"slide": 1, "title": "重复页码", "minutes": 5, "script": "字" * 10},
            ],
        }
        seen = kinds(_interview.validate("script", broken))
        self.assertIn("script_structure", seen)
        missing = {"timing": {"slides": 1}}
        self.assertIn("script_timing", kinds(_interview.validate("script", missing)))

    def test_script_time_and_rate_checks(self):
        wrong_rate = {**SCRIPT, "timing": {**SCRIPT["timing"], "chars_per_minute": 9000}}
        self.assertIn("interview_rate", kinds(_interview.validate("script", wrong_rate)))
        too_long = {
            "timing": {"target_minutes": 10, "slides": 1, "chars_per_minute": 300,
                       "tolerance_minutes": 1},
            "sections": [{"slide": 1, "title": "全部", "minutes": 10, "script": "字" * 6000}],
        }
        problems = _interview.validate("script", too_long)
        self.assertIn("script_timing", kinds(problems))
        self.assertIn("约20 分钟", "".join(item["message"] for item in problems))

    def test_question_coverage_and_answer_length(self):
        missing = {**QA, "items": QA["items"][:2]}
        self.assertIn("qa_coverage", kinds(_interview.validate("qa", missing)))
        unknown = {**QA, "items": QA["items"] + [
            {"category": "材料来源", "question": "材料读了多少？", "answer": "读" * 10},
        ]}
        self.assertIn("qa_structure", kinds(_interview.validate("qa", unknown)))
        long_answer = {**QA, "items": [*QA["items"][:2], {**QA["items"][2], "answer": "长" * 900}]}
        self.assertIn("qa_answer_length", kinds(_interview.validate("qa", long_answer)))
        no_questions = {**QA, "items": []}
        self.assertIn("qa_structure", kinds(_interview.validate("qa", no_questions)))


class InterviewDraftTests(ComponentCase):
    """在独占目录中建立稿件，检查保存、生成、核对与提交条件。"""

    def begin(self, deliverable_names=("md", "script", "qa")):
        directory = self.output / "proposal"
        directory.mkdir()
        started = self.call("begin_revision", {
            "proposal_dir": str(directory), "expected_state_version": None,
            "inputs": {
                "application_id": "合成项目-面试", "purpose": "面试准备",
                "question_id": "q1", "material_paths": [],
                "deliverables": list(deliverable_names),
            },
        })
        self.assertEqual(started["status"], "ready")
        return directory, started["revision_id"]

    def request(self, directory, revision, **fields):
        state = read_json(directory / "研究计划状态.json")
        return {"proposal_dir": str(directory), "revision_id": revision,
                "expected_state_version": state["state_version"], **fields}

    def save_interview(self, directory, revision, data):
        return self.call("save_revision", self.request(directory, revision, stage="interview", data=data))

    def work(self, directory, revision):
        return read_json(directory / "研究计划状态.json")["works"][revision]

    def test_selected_deliverable_must_be_saved(self):
        directory, revision = self.begin()
        partial = self.save_interview(directory, revision, {"qa": QA})
        self.assertEqual(partial["status"], "needs_input")
        self.assertIn("interview_missing", kinds(partial["issues"]))
        work = self.work(directory, revision)
        data_path = Path(work["steps"]["interview"]["artifacts"]["data"])
        self.assertTrue(data_path.is_file(), "检查未通过也要保存已写好的内容")
        self.assertEqual(read_json(data_path)["qa"]["items"][0]["question"], "为什么用这个方法？")
        self.assertEqual(work["steps"]["interview"]["status"], "pending")

        saved = self.save_interview(directory, revision, {"script": SCRIPT, "qa": QA})
        self.assertEqual(saved["status"], "ready")
        self.assertEqual(self.work(directory, revision)["steps"]["interview"]["status"], "complete")

    def test_second_save_keeps_the_first_deliverable(self):
        """分次保存时不重写全部内容：补齐缺的那一项即可完成。"""
        from research_proposal._interview import step_data

        directory, revision = self.begin()
        first = self.save_interview(directory, revision, {"qa": QA})
        self.assertEqual(first["status"], "needs_input")
        self.assertIn("interview_missing", kinds(first["issues"]))
        second = self.save_interview(directory, revision, {"script": SCRIPT})
        self.assertEqual(second["status"], "ready", second.get("issues"))
        work = self.work(directory, revision)
        self.assertEqual(work["steps"]["interview"]["status"], "complete")
        self.assertIsNotNone(step_data(work, "qa"), "先交的问答不能被后一次保存丢掉")
        self.assertIsNotNone(step_data(work, "script"))

    def test_later_save_overrides_the_same_deliverable(self):
        from research_proposal._interview import step_data

        directory, revision = self.begin()
        self.save_interview(directory, revision, {"script": SCRIPT, "qa": QA})
        changed = {**QA, "max_answer_minutes": 2}
        self.save_interview(directory, revision, {"qa": changed})
        work = self.work(directory, revision)
        self.assertEqual(step_data(work, "qa")["max_answer_minutes"], 2)
        self.assertEqual(step_data(work, "qa")["required_categories"], QA["required_categories"])
        self.assertIsNotNone(step_data(work, "script"), "未出现在本次请求里的讲稿继续保留")

    def test_null_or_empty_payload_never_drops_saved_content(self):
        """不支持删除单项：写成 null 或空对象报错，已保存内容保持不变。"""
        from research_proposal._interview import step_data

        directory, revision = self.begin()
        self.save_interview(directory, revision, {"script": SCRIPT, "qa": QA})
        for payload in ({"script": {}}, {"qa": None}, {"script": None, "qa": QA}, {}):
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    self.save_interview(directory, revision, payload)
                work = self.work(directory, revision)
                self.assertIsNotNone(step_data(work, "script"), "讲稿不能被静默覆盖")
                self.assertIsNotNone(step_data(work, "qa"), "问答不能被静默删除")
                self.assertEqual(work["steps"]["interview"]["status"], "complete")

    def test_unselected_deliverable_is_ignored_but_not_exported(self):
        directory, revision = self.begin(deliverable_names=("md",))
        saved = self.save_interview(directory, revision, {"script": SCRIPT})
        self.assertEqual(saved["status"], "ready")
        result = self.call("export_revision", self.request(directory, revision, formats=["script"]))
        self.assertEqual(result["status"], "needs_input")
        self.assertIn("deliverable_not_selected", kinds(result["issues"]))
        self.assertFalse((directory / "研究计划讲稿.md").exists())

    def test_export_requires_saved_body(self):
        directory, revision = self.begin()
        self.save_interview(directory, revision, {"script": SCRIPT, "qa": QA})
        result = self.call("export_revision", self.request(directory, revision, formats=["script"]))
        self.assertEqual(result["status"], "needs_input")
        self.assertIn("body_required", kinds(result["issues"]))
        self.assertFalse((directory / "研究计划讲稿.md").exists())

    def test_deliverables_input_validation(self):
        for value in (["docx"], ["pdf"], []):
            with self.subTest(deliverables=value):
                directory = self.output / ("reject-" + "-".join(value) if value else "reject-empty")
                directory.mkdir()
                with self.assertRaises(ValueError):
                    self.call("begin_revision", {
                        "proposal_dir": str(directory), "expected_state_version": None,
                        "inputs": {
                            "application_id": "合成项目-面试", "purpose": "面试准备",
                            "question_id": "q1", "material_paths": [],
                            "deliverables": value,
                        },
                    })

    def test_review_reports_edited_deliverable(self):
        directory, revision = self.begin(deliverable_names=("md", "script"))
        self.save_interview(directory, revision, {"script": SCRIPT})
        work = self.work(directory, revision)
        # 直接生成一份正确的交付文件，再把它改坏，模拟用户手改导出稿。
        self.assertEqual(_interview.validate("script", SCRIPT), [])
        target = Path(work["directory"]) / "研究计划讲稿.md"
        target.write_text(_interview.render("script", SCRIPT), encoding="utf-8")
        consistent, details, digests = _interview.review_interview(work, ["script"])
        self.assertTrue(consistent)
        self.assertEqual(len(digests), 1)
        target.write_text(target.read_text(encoding="utf-8") + "手改一句\n", encoding="utf-8")
        consistent, details, _ = _interview.review_interview(work, ["script"])
        self.assertFalse(consistent)
        self.assertTrue(details)

    def test_review_uses_saved_step_not_written_file(self):
        directory, revision = self.begin(deliverable_names=("md", "script"))
        self.save_interview(directory, revision, {"script": SCRIPT})
        work = self.work(directory, revision)
        target = Path(work["directory"]) / "研究计划讲稿.md"
        target.write_text("随手写的内容\n", encoding="utf-8")
        consistent, details, _ = _interview.review_interview(work, ["script"])
        self.assertFalse(consistent)
        self.assertIn("不一致", "".join(details))

    def test_step_digest_tracks_saved_content(self):
        directory, revision = self.begin(deliverable_names=("md", "script"))
        self.save_interview(directory, revision, {"script": SCRIPT})
        before = self.work(directory, revision)
        changed = {**SCRIPT, "sections": [
            {**SCRIPT["sections"][0]},
            {**SCRIPT["sections"][1]},
            {**SCRIPT["sections"][2], "title": "进度与后备方案"},
        ]}
        self.save_interview(directory, revision, {"script": changed})
        updated = self.work(directory, revision)
        self.assertNotEqual(
            updated["steps"]["interview"]["content_digest"],
            before["steps"]["interview"]["content_digest"],
        )
        self.assertEqual(updated["steps"]["script"]["status"], "pending")
        # 正文未变，Markdown 的状态和保存件不受讲稿变化影响。
        self.assertEqual(updated["steps"]["md"], before["steps"]["md"])
        self.assertEqual(updated["steps"]["body"], before["steps"]["body"])


class InterviewStateTests(ComponentCase):
    def begin(self, deliverable_names=("md", "script")):
        directory = self.output / "state"
        directory.mkdir()
        started = self.call("begin_revision", {
            "proposal_dir": str(directory), "expected_state_version": None,
            "inputs": {
                "application_id": "合成项目-面试", "purpose": "面试准备",
                "question_id": "q1", "material_paths": [],
                "deliverables": list(deliverable_names),
            },
        })
        self.assertEqual(started["status"], "ready")
        return directory, started["revision_id"]

    def request(self, directory, revision, **fields):
        state = read_json(directory / "研究计划状态.json")
        return {"proposal_dir": str(directory), "revision_id": revision,
                "expected_state_version": state["state_version"], **fields}

    def test_next_steps_skip_unselected_files_and_deferred_word(self):
        from research_proposal import _state

        directory, revision = self.begin(deliverable_names=("md",))
        work = read_json(directory / "研究计划状态.json")["works"][revision]
        steps = _state._next_steps(work)
        self.assertNotIn("docx", steps)
        self.assertNotIn("script", steps)
        self.assertNotIn("qa", steps)
        self.assertIn("materials", steps)

    def test_interview_delivery_is_listed(self):
        from research_proposal import _state

        directory, revision = self.begin()
        work = read_json(directory / "研究计划状态.json")["works"][revision]
        self.assertEqual(_state._delivery_formats(work), ["md", "script"])
        steps = _state._next_steps(work)
        self.assertEqual(
            steps,
            ["materials", "question", "scheme", "body", "interview", "md", "script", "review"],
        )
        self.assertNotIn("qa", steps)
        self.assertNotIn("docx", steps)
        notes = (Path(work["directory"]) / "研究计划待确认事项.md").read_text(encoding="utf-8")
        self.assertIn("发表讲稿", notes)

    def test_markdown_only_proposal_skips_interview_step(self):
        from research_proposal import _state

        directory, revision = self.begin(deliverable_names=("md",))
        work = read_json(directory / "研究计划状态.json")["works"][revision]
        self.assertEqual(
            _state._next_steps(work),
            ["materials", "question", "scheme", "body", "md", "review"],
        )


class LegacyStateTests(ComponentCase):
    """旧状态没有 interview、script、qa 键时，公开入口仍按原行为工作。"""

    NEW_STEPS = ("interview", "script", "qa")

    def draft_body(self):
        import json
        import subprocess

        markdown = self.output / "legacy-draft.md"
        markdown.write_text(
            "# 研究题目\n\n本文说明为什么研究、研究什么、准备怎么做。\n\n"
            "## 研究方法\n\n采用文本比较。\n",
            encoding="utf-8",
        )
        return json.loads(subprocess.run(
            ["pandoc", str(markdown), "-f", "markdown", "-t", "json"],
            check=True, capture_output=True,
        ).stdout)

    def request(self, directory, revision, **fields):
        state = read_json(directory / "研究计划状态.json")
        return {"proposal_dir": str(directory), "revision_id": revision,
                "expected_state_version": state["state_version"], **fields}

    def save(self, directory, revision, stage, data):
        result = self.call("save_revision", self.request(directory, revision, stage=stage, data=data))
        self.assertEqual(result["status"], "ready", result.get("issues"))
        return result

    def legacy_proposal(self, name, *, committed):
        """建立一份完整稿件，再把它改写成上一版本会写出的状态结构。"""
        directory = self.output / name
        directory.mkdir()
        started = self.call("begin_revision", {
            "proposal_dir": str(directory), "expected_state_version": None,
            "inputs": {"application_id": "合成项目-旧版", "purpose": "联系教授",
                       "question_id": "q1", "material_paths": []},
        })
        self.assertEqual(started["status"], "ready")
        revision = started["revision_id"]
        ok = {"revision": "r1", "status": "confirmed",
              "decision": {"text": "用户确认", "source": "合成测试消息"}}
        self.save(directory, revision, "materials", {"materials": []})
        self.save(directory, revision, "question", {
            "question_id": "q1", "text": "合成本文要回答什么问题？", "confirmation": ok,
        })
        self.save(directory, revision, "scheme", {
            "scheme": {"method": "文本比较"}, "conditions": {"resolved": True, "notes": "本地材料。"},
            "confirmation": ok,
        })
        self.save(directory, revision, "body", {"body": self.draft_body(), "references": []})
        if committed:
            self.assertEqual(self.call("export_revision", self.request(directory, revision))["status"], "ready")
            self.assertTrue(self.call("review_revision", self.request(directory, revision))["checks"]["content_consistent"])
            self.assertEqual(self.call("commit_revision", self.request(directory, revision))["status"], "committed")
        state = read_json(directory / "研究计划状态.json")
        work = state["works"][revision]
        for stage in self.NEW_STEPS:
            work["steps"].pop(stage, None)
            work["fingerprints"].get("stage_files", {}).pop(stage, None)
        write_json(directory / "研究计划状态.json", state)
        return directory, revision, state

    def test_uncommitted_legacy_state_resumes(self):
        directory, revision, state = self.legacy_proposal("legacy-open", committed=False)
        result = self.call("resume_revision", {
            "proposal_dir": str(directory), "expected_state_version": state["state_version"],
        })
        self.assertEqual(result["status"], "ready")
        steps = read_json(directory / "研究计划状态.json")["works"][revision]["steps"]
        self.assertEqual(sorted(steps), sorted(["materials", "question", "scheme", "body",
                                                "docx", "md", "review", *self.NEW_STEPS]))
        self.assertEqual(steps["interview"]["status"], "pending")
        # 正文已保存，未加选讲稿时下一步只剩 Markdown 交付与核对。
        self.assertEqual(result["next_steps"], ["md", "review"])

    def test_committed_legacy_state_reports_committed(self):
        directory, revision, state = self.legacy_proposal("legacy-committed", committed=True)
        result = self.call("commit_revision", self.request(directory, revision))
        self.assertEqual(result["status"], "committed")

    def test_committed_legacy_state_can_start_new_revision(self):
        directory, revision, state = self.legacy_proposal("legacy-next", committed=True)
        work = state["works"][revision]
        result = self.call("begin_revision", {
            "proposal_dir": str(directory), "expected_state_version": state["state_version"],
            "inputs": work["inputs"],
        })
        self.assertEqual(result["status"], "ready")
        resumed = self.call("resume_revision", self.request(directory, result["revision_id"]))
        self.assertNotIn("interview", resumed["next_steps"])

    def test_newly_added_empty_stages_are_not_content_change(self):
        from research_proposal import _state

        directory, revision, _ = self.legacy_proposal("legacy-fingerprint", committed=True)
        # 公开入口读盘时会补齐缺失步骤键，之后已提交稿不应被判成有内容变化。
        result = self.call("resume_revision", self.request(directory, revision))
        self.assertEqual(result["status"], "committed")
        work = result["state"]["works"][revision]
        self.assertEqual(work["steps"]["interview"]["status"], "pending")
        keys = set(_state._dependencies(work)) | {"stage_files"}
        self.assertFalse(_state._fingerprints_changed(
            work["fingerprints"], _state._snapshot(work), keys=keys,
        ))

    def test_readded_stage_with_content_is_a_change(self):
        from research_proposal import _state

        directory, revision, _ = self.legacy_proposal("legacy-content", committed=True)
        self.assertEqual(
            self.call("resume_revision", self.request(directory, revision))["status"], "committed",
        )
        work = read_json(directory / "研究计划状态.json")["works"][revision]
        record = Path(work["directory"]) / "步骤-interview-legacy.json"
        record.write_text('{"script": {}}', encoding="utf-8")
        work["steps"]["interview"] = {"status": "complete", "artifacts": {"data": str(record)}, "issues": []}
        keys = set(_state._dependencies(work)) | {"stage_files"}
        self.assertTrue(_state._fingerprints_changed(
            work["fingerprints"], _state._snapshot(work), keys=keys,
        ))


class InterviewDeliveryFlowTests(ComponentCase):
    """从零建立一份带讲稿的稿件，走完保存、生成、核对与提交。"""

    def setUp(self):
        super().setUp()
        self.directory = self.output / "flow"
        self.directory.mkdir()
        started = self.call("begin_revision", {
            "proposal_dir": str(self.directory), "expected_state_version": None,
            "inputs": {
                "application_id": "合成项目-面试", "purpose": "面试准备",
                "question_id": "q1", "material_paths": [],
                "deliverables": ["md", "script"],
            },
        })
        self.assertEqual(started["status"], "ready")
        self.revision = started["revision_id"]

    def request(self, **fields):
        state = read_json(self.directory / "研究计划状态.json")
        return {"proposal_dir": str(self.directory), "revision_id": self.revision,
                "expected_state_version": state["state_version"], **fields}

    def save(self, stage, data):
        result = self.call("save_revision", self.request(stage=stage, data=data))
        self.assertEqual(result["status"], "ready", result.get("issues"))
        return result

    def body(self):
        import json
        import subprocess

        markdown = self.output / "draft.md"
        markdown.write_text(
            "# 研究题目\n\n本文说明为什么研究、研究什么、准备怎么做。\n\n"
            "## 研究方法\n\n采用文本比较与访谈两种办法。\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            ["pandoc", str(markdown), "-f", "markdown", "-t", "json"],
            check=True, capture_output=True,
        )
        return json.loads(completed.stdout)

    def confirmation(self):
        return {"revision": "r1", "status": "confirmed",
                "decision": {"text": "用户确认了本轮问题与方案", "source": "合成测试消息"}}

    def fill_draft(self):
        self.save("materials", {"materials": []})
        self.save("question", {
            "question_id": "q1", "text": "合成本文要回答什么问题？",
            "confirmation": self.confirmation(),
        })
        self.save("scheme", {
            "scheme": {"method": "文本比较", "steps": ["取材料", "做比较"]},
            "conditions": {"resolved": True, "notes": "材料在本地，可直接读取。"},
            "confirmation": self.confirmation(),
        })
        self.save("body", {"body": self.body(), "references": []})

    def test_export_produces_script_then_review_and_commit(self):
        self.fill_draft()
        self.save("interview", {"script": SCRIPT})
        exported = self.call("export_revision", self.request())
        self.assertEqual(exported["status"], "ready", exported.get("issues"))
        artifacts = exported["artifacts"]
        self.assertTrue(Path(artifacts["md"]).is_file())
        self.assertTrue(Path(artifacts["script"]).is_file())
        reviewed = self.call("review_revision", self.request())
        self.assertEqual(reviewed["checks"]["checked_formats"], ["md", "script"])
        self.assertTrue(reviewed["checks"]["content_consistent"])
        self.assertEqual(set(reviewed["checks"]["deliverable_digests"]), {"script"})
        committed = self.call("commit_revision", self.request())
        self.assertEqual(committed["status"], "committed")
        self.assertEqual(set(committed["artifacts"]), {"md", "script"})
        committed_directory = Path(
            read_json(self.directory / "研究计划状态.json")["current"]["directory"]
        )
        self.assertTrue((committed_directory / "研究计划讲稿.md").is_file())

    def test_changed_script_invalidates_script_and_review_only(self):
        self.fill_draft()
        self.save("interview", {"script": SCRIPT})
        self.call("export_revision", self.request())
        self.assertTrue(self.call("review_revision", self.request())["checks"]["content_consistent"])
        changed = {**SCRIPT, "sections": [
            {**SCRIPT["sections"][0], "script": "改" * 900},
            SCRIPT["sections"][1], SCRIPT["sections"][2],
        ]}
        self.save("interview", {"script": changed})
        work = read_json(self.directory / "研究计划状态.json")["works"][self.revision]
        self.assertEqual(work["steps"]["script"]["status"], "pending")
        self.assertEqual(work["steps"]["md"]["status"], "complete")
        self.assertFalse(work["checks"]["content_consistent"])
        blocked = self.call("commit_revision", self.request())
        self.assertNotEqual(blocked["status"], "committed")
        self.assertEqual(self.call("export_revision", self.request())["status"], "ready")
        self.assertTrue(self.call("review_revision", self.request())["checks"]["content_consistent"])
        self.assertEqual(self.call("commit_revision", self.request())["status"], "committed")

    def test_unchecked_script_content_blocks_export(self):
        self.fill_draft()
        bad = self.call("save_revision", self.request(stage="interview", data={
            "script": {**SCRIPT, "timing": {**SCRIPT["timing"], "chars_per_minute": 9000}},
        }))
        self.assertEqual(bad["status"], "needs_input")
        self.assertIn("interview_rate", kinds(bad["issues"]))
        result = self.call("export_revision", self.request())
        self.assertEqual(result["status"], "needs_input")
        self.assertIn("interview_incomplete", kinds(result["issues"]))
        self.assertFalse((self.directory / "研究计划讲稿.md").exists())
