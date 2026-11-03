"""供已批准组件用例复用的输入读取与独占目录安排。"""

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from research_proposal import api


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def read_json(path, expression="."):
    completed = subprocess.run(
        ["jq", "-ce", expression, str(path)], check=True,
        capture_output=True, text=True,
    )
    return json.loads(completed.stdout)


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def required_path(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"执行前须绑定 {name}，不能跳过对应用例")
    path = Path(value).resolve(strict=True)
    return path


def word_text(path, xpath="//*[local-name()='t']/text()"):
    document = subprocess.run(
        ["unzip", "-p", str(path), "word/document.xml"],
        check=True, capture_output=True,
    ).stdout
    return subprocess.run(
        ["xmllint", "--xpath", xpath, "-"], input=document,
        check=True, capture_output=True,
    ).stdout.decode("utf-8")


def ast_text(value):
    if isinstance(value, dict):
        if value.get("t") == "Str":
            return value["c"]
        if value.get("t") in {"Space", "SoftBreak", "LineBreak"}:
            return " "
        return "".join(ast_text(item) for item in value.values())
    if isinstance(value, list):
        return "".join(ast_text(item) for item in value)
    return ""


class ComponentCase(unittest.TestCase):
    def setUp(self):
        output = required_path("RP_TEST_OUTPUT")
        self.output = Path(tempfile.mkdtemp(prefix=self.id().split(".")[-1] + ".", dir=output))

    def call(self, name, request):
        result = getattr(api, name)(copy.deepcopy(request))
        self.assertIn(result["status"], {"ready", "needs_input", "blocked", "conflict", "committed"})
        self.assertIsInstance(result["issues"], list)
        return result


class SavedDraftCase(ComponentCase):
    """逐用例快照并恢复同一路径，保持真实基准中的绝对路径有效。"""

    def setUp(self):
        super().setUp()
        self.proposal = required_path("RP_TEST_PROPOSAL")
        data_root = required_path("RP_CONSUMER") / "input"
        if not self.proposal.is_relative_to(data_root) or self.proposal == data_root:
            raise RuntimeError("组件测试只可使用本轮独占消费者 input 中的真实稿件")
        self.state_path = self.proposal / "研究计划状态.json"
        self.initial = read_json(self.state_path)
        self.assertIsNotNone(self.initial["current"], "须先取得 RP-08 的真实成稿")
        self.before = self.output / "before"
        shutil.copytree(self.proposal, self.before, symlinks=True)
        self.addCleanup(self.restore)

    def restore(self):
        if self.proposal.exists():
            shutil.copytree(self.proposal, self.output / "after", symlinks=True)
            shutil.rmtree(self.proposal)
        shutil.copytree(self.before, self.proposal, symlinks=True)
        print(f"组件用例文件保存在：{self.output}")

    def state(self):
        return read_json(self.state_path)

    def begin(self, inputs=None):
        state = self.state()
        current = state["works"][state["current"]["revision_id"]]
        result = self.call("begin_revision", {
            "proposal_dir": str(self.proposal),
            "expected_state_version": state["state_version"],
            "inputs": copy.deepcopy(current["inputs"] if inputs is None else inputs),
        })
        self.assertEqual(result["status"], "ready")
        return result["revision_id"]

    def request(self, revision, **fields):
        return {
            "proposal_dir": str(self.proposal), "revision_id": revision,
            "expected_state_version": self.state()["state_version"], **fields,
        }

    def work(self, revision):
        return self.state()["works"][revision]

    def export(self, revision, formats=None, **fields):
        return self.call("export_revision", self.request(
            revision, formats=formats or ["docx", "md"], **fields,
        ))

    def controlled_review(self, revision, passed=True):
        # RP-11 明确允许控制返回结果。这里不是实际页面合格声明，
        # 不能被引用为 RP-08 或 RP-09 的页面检查结果。
        return self.call("review_revision", self.request(
            revision, page_review={
                "passed": passed,
                "notes": "RP-11 状态与提交失败分支的受控页面返回；不作真实页面验收",
            },
        ))

    def ready_work(self):
        revision = self.begin()
        self.assertEqual(self.export(revision)["status"], "ready")
        review = self.controlled_review(revision)
        self.assertTrue(review["checks"]["content_consistent"])
        self.assertTrue(review["checks"]["pages_ok"])
        return revision

    def assert_current_unchanged(self):
        self.assertEqual(self.state()["current"], self.initial["current"])
        old = Path(self.initial["current"]["directory"])
        relative = old.relative_to(self.proposal)
        for name in ("正文.json", "研究计划草稿.docx", "研究计划草稿.md"):
            self.assertEqual(digest(old / name), digest(self.before / relative / name))
