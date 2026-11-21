"""Read Word locations and review markup without accepting any revisions."""

from __future__ import annotations

from pathlib import Path
import posixpath
from zipfile import ZipFile

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "r": R}


def _xml(data: bytes):
    return etree.fromstring(data, etree.XMLParser(resolve_entities=False, no_network=True))


def _text(element) -> str:
    parts = []
    for item in element.iter():
        name = etree.QName(item).localname if isinstance(item.tag, str) else ""
        if name in {"t", "delText"}:
            parts.append(item.text or "")
        elif name == "tab":
            parts.append("\t")
        elif name in {"br", "cr"}:
            parts.append("\n")
    return "".join(parts)


def _locator(element, root, part: str) -> dict:
    """Paragraph indices count the original part's paragraphs, including tables."""
    location = {"kind": "docx", "part": part, "xpath": root.getroottree().getpath(element)}
    body = root.find("w:body", NS)
    scope = body if body is not None else root
    ancestors = [element, *element.iterancestors()]
    tables = scope.findall("w:tbl", NS)
    outer = next((item for item in ancestors if item in tables), None)
    if outer is not None:
        row = next((item for item in ancestors if item.getparent() is outer and item.tag == f"{{{W}}}tr"), None)
        cell = next((item for item in ancestors if row is not None and item.getparent() is row and item.tag == f"{{{W}}}tc"), None)
        if row is not None and cell is not None:
            location.update(table=tables.index(outer), row=outer.findall("w:tr", NS).index(row),
                            column=row.findall("w:tc", NS).index(cell))
            return location
    paragraph = next((item for item in ancestors if item.tag == f"{{{W}}}p"), None)
    if paragraph is not None:
        location["paragraph"] = list(scope.iter(f"{{{W}}}p")).index(paragraph)
    return location


def read_word_structure(path: Path) -> dict:
    """Supplement Pandoc with original XML, including material it may omit."""
    blocks, changes, comments, unsupported = [], [], [], []
    with ZipFile(path) as archive:
        names = set(archive.namelist())
        parts = ["word/document.xml"]
        parts.extend(sorted(name for name in names if name.startswith(("word/header", "word/footer")) and name.endswith(".xml")))
        parts.extend(name for name in ("word/footnotes.xml", "word/endnotes.xml") if name in names)
        anchors = {}
        for part in parts:
            root = _xml(archive.read(part))
            relationships = {}
            relationship_part = posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")
            if relationship_part in names:
                for relation in _xml(archive.read(relationship_part)):
                    relationships[relation.get("Id")] = {
                        "target": relation.get("Target"), "mode": relation.get("TargetMode", "Internal")
                    }
            for paragraph in root.iter(f"{{{W}}}p"):
                # Textbox text needs explicit review; do not also call it ordinary body text.
                if any(parent.tag == f"{{{W}}}txbxContent" for parent in paragraph.iterancestors()):
                    continue
                text = _text(paragraph).strip()
                if text:
                    blocks.append({"text": text, "locator": _locator(paragraph, root, part)})
            for element in root.iter():
                if not isinstance(element.tag, str):
                    continue
                name = etree.QName(element).localname
                location = _locator(element, root, part)
                if name in {"ins", "del", "moveFrom", "moveTo", "pPrChange", "rPrChange", "tblPrChange", "trPrChange", "tcPrChange", "sectPrChange", "numberingChange", "cellIns", "cellDel", "cellMerge"} and etree.QName(element).namespace == W:
                    location.update({key: value for key, value in {
                        "change_id": element.get(f"{{{W}}}id"),
                        "author": element.get(f"{{{W}}}author"),
                        "date": element.get(f"{{{W}}}date"),
                    }.items() if value is not None})
                    changes.append({"kind": name, "text": _text(element) or f"未决格式或结构修订：{name}", "location": location})
                if name in {"commentRangeStart", "commentRangeEnd", "commentReference"}:
                    identifier = element.get(f"{{{W}}}id")
                    anchors.setdefault(identifier, {})[name] = location
                if name in {"object", "txbxContent", "altChunk", "chart", "relIds"}:
                    relations = []
                    for child in element.iter():
                        for attribute, value in child.attrib.items():
                            if attribute.startswith(f"{{{R}}}") and value in relationships:
                                relations.append({"id": value, **relationships[value]})
                    if relations:
                        location["relationships"] = relations
                    unsupported.append({"kind": name, "text": _text(element) or "此对象不能可靠转换为正文；原对象保存在导入原件中。", "location": location})
        if "word/comments.xml" in names:
            comment_root = _xml(archive.read("word/comments.xml"))
            for element in comment_root.findall("w:comment", NS):
                identifier = element.get(f"{{{W}}}id")
                positions = anchors.get(identifier, {})
                location = dict(positions.get("commentRangeStart") or positions.get("commentReference") or {
                    "kind": "docx", "part": "word/comments.xml", "xpath": comment_root.getroottree().getpath(element)
                })
                location["comment_id"] = identifier
                for attribute in ("author", "date"):
                    if element.get(f"{{{W}}}{attribute}") is not None:
                        location[attribute] = element.get(f"{{{W}}}{attribute}")
                if "commentRangeEnd" in positions:
                    location["end"] = positions["commentRangeEnd"]
                comments.append({"kind": "comment", "text": _text(element), "location": location})
        recorded = {item["location"].get("comment_id") for item in comments}
        for identifier, positions in anchors.items():
            if identifier not in recorded:
                unsupported.append({"kind": "missing_comment", "text": "此处存在批注锚点，但原件中没有对应的批注正文。",
                                    "location": {**next(iter(positions.values())), "comment_id": identifier}})
    return {"blocks": blocks, "changes": changes, "comments": comments, "unsupported": unsupported}


_COMMENT = object()


def without_comments(value):
    """Pandoc --track-changes=all puts comment contents in comment-start spans."""
    if isinstance(value, list):
        return [clean for item in value if (clean := without_comments(item)) is not _COMMENT]
    if not isinstance(value, dict):
        return value
    if value.get("t") in {"Span", "Div"}:
        content = value.get("c", [])
        if content and isinstance(content[0], list) and len(content[0]) >= 2:
            classes = content[0][1]
            if any(name in {"comment-start", "comment-end", "comment-reference"} for name in classes):
                return _COMMENT
    if value.get("t") == "Comment":
        return _COMMENT
    return {key: clean for key, item in value.items() if (clean := without_comments(item)) is not _COMMENT}
