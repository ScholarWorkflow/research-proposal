"""JSON command entry; business failures and program failures stay distinct."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import api


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="研究计划材料、稿件和导出工具")
    parser.add_argument("operation", choices=api.__all__)
    parser.add_argument("--request", required=True, type=Path, help="操作请求的 JSON 文件")
    args = parser.parse_args(argv)
    with args.request.open("r", encoding="utf-8") as stream:
        request = json.load(stream)
    if not isinstance(request, dict):
        parser.error("请求必须是 JSON 对象")
    response = getattr(api, args.operation)(request)
    if not isinstance(response, dict) or response.get("status") not in {
        "ready", "needs_input", "blocked", "conflict", "committed"
    } or not isinstance(response.get("issues"), list):
        raise ValueError("操作未返回约定的业务结果")
    json.dump(response, sys.stdout, ensure_ascii=False, allow_nan=False)
    sys.stdout.write("\n")
    return 0 if response["status"] in {"ready", "committed"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
