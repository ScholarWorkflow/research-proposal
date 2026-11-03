"""RP-09 模板填写组件；实际页面仍由执行者逐页检查。"""

from pathlib import Path
import shutil

from support import FIXTURES, SavedDraftCase, ast_text, digest, read_json, required_path, word_text


class TemplateTests(SavedDraftCase):
    def export_template(self, template, transfer):
        original = template
        template = self.output / original.name
        shutil.copy2(original, template)
        mapping = read_json(required_path("RP_TEMPLATE_MAPPING"))
        self.assertTrue(mapping, "须按 RP-08 实际正文建立学校栏目映射")
        if transfer:
            for entry in mapping:
                entry["target"] = None
        revision = self.begin()
        before = digest(template)
        result = self.export(revision, template_path=str(template), mapping=mapping)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(before, digest(template))
        self.assert_current_unchanged()
        body = read_json(Path(self.work(revision)["directory"]) / "正文.json")
        docx = Path(result["artifacts"]["docx"])
        markdown = Path(result["artifacts"]["md"]).read_text(encoding="utf-8")
        document = word_text(docx)
        self.assertTrue(result["artifacts"]["page_images"])
        for entry in mapping:
            self.assertTrue(entry["body_blocks"])
            expected = "".join(ast_text(body["blocks"][index]) for index in entry["body_blocks"])
            if transfer:
                actual = document
            else:
                target = entry["target"]
                if "table" in target:
                    xpath = (
                        f"(//*[local-name()='body']/*[local-name()='tbl'])[{target['table'] + 1}]"
                        f"/*[local-name()='tr'][{target['row'] + 1}]"
                        f"/*[local-name()='tc'][{target['column'] + 1}]"
                        "//*[local-name()='t']/text()"
                    )
                else:
                    xpath = (
                        f"(//*[local-name()='body']/*[local-name()='p'])[{target['paragraph'] + 1}]"
                        "//*[local-name()='t']/text()"
                    )
                actual = word_text(docx, xpath)
            self.assertIn("".join(expected.split()), "".join(actual.split()))
            # Markdown 标记不能按纯文本子串当成内容丢失；其段落、列表、表格、
            # 引用与 Word 的对应关系沿 RP-09 直接阅读检查，不另建转换判定器。
            self.assertTrue(markdown.strip())
        if transfer:
            self.assertTrue(result["issues"], "须向使用者说明需要转填")
        else:
            self.assertIn("固定声明：参考文献不计入正文篇幅。此表原件须保留。", document)
        print(f"RP-09 实际页面和转填说明须检查此结果目录：{self.output / 'after'}")

    def test_editable_template(self):
        self.export_template(FIXTURES / "templates/editable-form.docx", False)

    def test_transfer_template(self):
        self.export_template(FIXTURES / "templates/transfer-form.pdf", True)
