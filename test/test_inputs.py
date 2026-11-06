"""RP-03 至 RP-06、RP-10 的组件检查；正式执行条件见 plan/test-plan.md。"""

from pathlib import Path
import shutil

from support import (
    ComponentCase, FIXTURES, ast_text, digest, read_json, required_path,
    word_text, write_json,
)


class DiscoveryTests(ComponentCase):
    def setUp(self):
        super().setUp()
        # 路径来自 prepare_inputs.py 的合成外部输入；缺少绑定不能跳过。
        self.cases = read_json(required_path("RP_INPUT_CASES"))

    def check_discovery(self, path, case, next_step):
        result = self.call("discover", {
            "path": path,
            "selection": case["selection"],
        })
        self.assertEqual(result["status"], "ready")
        expected_professor = Path(case["professor_path"]).resolve()
        self.assertEqual(Path(result["selected"]).resolve(), expected_professor)
        matching = [
            item for item in result["objects"]
            if item["professor_path"]
            and Path(item["professor_path"]).resolve() == expected_professor
        ]
        self.assertEqual(len(matching), 1)
        item = matching[0]
        self.assertEqual(
            Path(item["application_root"]).resolve(),
            Path(case["application_root"]).resolve(),
        )
        self.assertEqual(item["next_step"], next_step)
        available = {Path(value).resolve() for value in item["valid_artifacts"].values()}
        self.assertIn(Path(case["input_file"]).resolve(), available)
        if next_step == "proposal":
            self.assertIn(Path(case["candidate_file"]).resolve(), available)
        else:
            self.assertNotIn(Path(case["candidate_file"]).resolve(), available)

    def test_four_paths_reuse_complete_input(self):
        case = self.cases["complete"]
        # 顺序为专攻、教授研究、单教授、正式产物；四条路径由执行说明绑定。
        self.assertEqual(len(case["paths"]), 4)
        for path in case["paths"]:
            with self.subTest(path=path):
                self.check_discovery(path, case, "proposal")

    def test_missing_candidates_routes_to_stage3(self):
        case = self.cases["without_candidates"]
        self.assertFalse(Path(case["candidate_file"]).exists())
        self.check_discovery(case["path"], case, "stage3")

    def test_multiple_objects_and_directions_require_actual_selection(self):
        case = self.cases["multiple"]
        result = self.call("discover", {"path": case["application_root"]})
        self.assertEqual(result["status"], "needs_input")
        self.assertIsNone(result["selected"])
        self.assertIn("professor_selection_required", {item["kind"] for item in result["issues"]})
        self.assertEqual(
            {Path(item["professor_path"]).resolve() for item in result["objects"]},
            {Path(case["professor_path"]).resolve(), Path(case["other_professor_path"]).resolve()},
        )
        result = self.call("discover", {
            "path": case["application_root"],
            "selection": {"professor_path": case["professor_path"]},
        })
        self.assertEqual(result["status"], "needs_input")
        self.assertIn("direction_selection_required", {item["kind"] for item in result["issues"]})
        self.check_discovery(case["application_root"], case, "proposal")


class UpstreamRoutingTests(ComponentCase):
    def test_missing_inputs_return_the_required_next_step(self):
        cases = read_json(required_path("RP_INPUT_CASES"))
        # stage3 已由 RP-03 的缺候选用例覆盖，不重复执行。
        for next_step in ("collect", "preview", "stage0", "stage1", "stage2"):
            with self.subTest(next_step=next_step):
                case = cases[next_step]
                request = {"path": case["path"]}
                if "selection" in case:
                    request["selection"] = case["selection"]
                result = self.call("discover", request)
                self.assertEqual(result["status"], "ready")
                self.assertEqual(len(result["objects"]), 1)
                item = result["objects"][0]
                self.assertEqual(item["next_step"], next_step)
                self.assertEqual(Path(item["application_root"]).resolve(), Path(case["application_root"]).resolve())
                if next_step == "collect":
                    self.assertIsNone(item["professor_path"])
                else:
                    self.assertEqual(Path(item["professor_path"]).resolve(), Path(case["professor_path"]).resolve())


class AnalysisRoutingTests(ComponentCase):
    def test_loose_analysis_keeps_its_owner_and_required_prerequisites(self):
        cases = read_json(required_path("RP_INPUT_CASES"))
        for next_step in ("stage0", "stage1", "stage2"):
            with self.subTest(next_step=next_step):
                case = cases["analysis_" + next_step]
                result = self.call("discover", {"path": case["path"], "selection": case["selection"]})
                self.assertEqual(result["status"], "ready")
                self.assertEqual(Path(result["selected"]).resolve(), Path(case["professor_path"]).resolve())
                self.assertEqual(len(result["objects"]), 1)
                item = result["objects"][0]
                self.assertEqual(item["next_step"], next_step)
                self.assertEqual(Path(item["application_root"]).resolve(), Path(case["application_root"]).resolve())
                materials = {Path(value).resolve() for value in item["materials"]}
                self.assertIn(Path(case["analysis_file"]).resolve(), materials)
                self.assertIn(Path(case["facts_file"]).resolve(), materials)


class MaterialTests(ComponentCase):
    def test_text_carriers_and_locations(self):
        cases = (
            ("txt", "text", ("十二人", "十八人", "不表示零次借阅")),
            ("md", "text", ("书籍", "24", "期刊", "6", "空白登记")),
            ("html", "html", ("每周二上午开放", "雨天仍开放", "期刊只供馆内阅览")),
            ("epub", "epub", ("书籍二十四册", "期刊六种", "期刊只供馆内阅览")),
            ("pdf", "pdf", ("十二人", "十八人", "期刊")),
            ("docx", "docx", ("十二人", "十八人", "24", "6")),
        )
        for extension, locator_kind, excerpts in cases:
            with self.subTest(carrier=extension):
                source = self.output / f"reading-room.{extension}"
                shutil.copyfile(FIXTURES / "materials" / source.name, source)
                original_digest = digest(source)
                result = self.call("read_material", {
                    "path": str(source), "material_type": "合成史料",
                    "source": "松川町阅览室合成测试材料",
                    "output_dir": str(self.output / extension),
                })
                self.assertEqual(result["status"], "ready")
                material = result["material"]
                self.assertEqual(Path(material["original_path"]).resolve(), source.resolve())
                self.assertEqual(material["material_type"], "合成史料")
                self.assertEqual(material["source"], "松川町阅览室合成测试材料")
                self.assertTrue(material["material_id"])
                self.assertTrue(material["digest"])
                self.assertTrue(material["reader"])
                blocks = material["blocks"]
                self.assertTrue(blocks)
                text = "".join("".join(block["text"].split()) for block in blocks)
                for excerpt in excerpts:
                    self.assertIn(excerpt, text)
                for block in blocks:
                    self.assertTrue(block["block_id"])
                    locator = block["locator"]
                    self.assertEqual(locator["kind"], locator_kind)
                    if locator_kind == "pdf":
                        self.assertIn(locator["page"], (1, 2))
                    elif locator_kind == "docx":
                        self.assertIsNone(locator.get("page"))
                        if "paragraph" in locator:
                            self.assertGreaterEqual(locator["paragraph"], 0)
                        else:
                            for key in ("table", "row", "column"):
                                self.assertGreaterEqual(locator[key], 0)
                    elif locator_kind in {"epub", "html"}:
                        self.assertTrue(locator["fragment"])
                        self.assertGreaterEqual(locator["paragraph"], 1)
                    else:
                        positions = [locator[key] for key in ("line", "paragraph") if key in locator]
                        self.assertTrue(positions)
                        self.assertTrue(all(value >= 1 for value in positions))
                if locator_kind == "pdf":
                    self.assertTrue(any(
                        "十二人" in "".join(block["text"].split())
                        and block["locator"]["page"] == 1 for block in blocks
                    ))
                    self.assertTrue(any(
                        "期刊" in block["text"] and block["locator"]["page"] == 2
                        for block in blocks
                    ))
                if locator_kind == "docx":
                    located = []
                    for block in blocks:
                        if "24" not in block["text"]:
                            continue
                        locator = block["locator"]
                        if "table" in locator:
                            xpath = (
                                f"(//*[local-name()='body']/*[local-name()='tbl'])[{locator['table'] + 1}]"
                                f"/*[local-name()='tr'][{locator['row'] + 1}]"
                                f"/*[local-name()='tc'][{locator['column'] + 1}]"
                            )
                        else:
                            xpath = f"(//*[local-name()='body']//*[local-name()='p'])[{locator['paragraph'] + 1}]"
                        located.append(word_text(source, f"string({xpath})"))
                    self.assertTrue(any("24" in text for text in located), "24 的定位须回到实际表格单元格")
                # 其余四类允许等价的段落分组；按原检查方式直接对照原文。
                # PDF 和 Word 已直接检查原页/单元格，不重复人工证明同一定位。
                if extension in {"txt", "md", "html", "epub"}:
                    result_path = self.output / f"{extension}-reading.json"
                    write_json(result_path, result)
                    print(f"RP-06 须按 Recipe 核对原文定位：{result_path}")
                self.assertEqual(digest(source), original_digest)

    def test_unsupported_material_reports_conversion_need(self):
        source = self.output / "unsupported.xyz"
        shutil.copyfile(FIXTURES / "materials" / source.name, source)
        original_digest = digest(source)
        result = self.call("read_material", {
            "path": str(source), "material_type": "合成史料",
            "source": "未支持载体样本", "output_dir": str(self.output / "unsupported"),
        })
        self.assertIn(result["status"], ("needs_input", "blocked"))
        self.assertTrue(result["issues"])
        self.assertTrue(any(issue["message"] and issue["location"] for issue in result["issues"]))
        self.assertEqual(digest(source), original_digest)


class RevisionImportTests(ComponentCase):
    def import_source(self, filename, statuses=("ready",)):
        source = self.output / filename
        shutil.copyfile(FIXTURES / "revisions" / filename, source)
        original_digest = digest(source)
        result = self.call("import_revision", {
            "path": str(source),
            "baseline_body": str(FIXTURES / "revisions" / "baseline.json"),
            "output_dir": str(self.output / source.stem),
        })
        self.assertIn(result["status"], statuses)
        self.assertEqual(digest(source), original_digest)
        self.assertEqual(digest(result["original_copy"]), original_digest)
        self.assertIsInstance(result["body"]["blocks"], list)
        self.assertTrue(result["body"]["pandoc-api-version"])
        return result

    def test_markdown_import_returns_body_and_content_difference(self):
        result = self.import_source("wording.md")
        self.assertIn("逐段比较", ast_text(result["body"]))
        self.assertIn("材料取得条件尚未核实", ast_text(result["body"]))
        self.assertTrue(result["changes"])
        self.assertEqual(result["comments"], [])
        self.assertEqual(result["unsupported"], [])
