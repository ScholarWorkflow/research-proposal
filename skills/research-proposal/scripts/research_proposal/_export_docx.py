"""Fill explicit Word locations without flattening Pandoc document content.

The original package is never saved.  A field receives complete OOXML blocks
from a Pandoc fragment, with its own styles, numbering and related parts.
Bookmarks delimit the inserted blocks for later reading of the actual output.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import posixpath
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from docx import Document
from lxml import etree


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"
C = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"w": W, "r": R}
XML_PARSER = etree.XMLParser(resolve_entities=False, no_network=True)


class TemplateFallback(ValueError):
    """The school form cannot be filled safely; export a transfer draft."""


def _xml(data):
    return etree.fromstring(data, parser=XML_PARSER)


def _serialized(element):
    return etree.tostring(element, encoding="UTF-8", xml_declaration=True, standalone=True)


def _read_package(path):
    with ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def _write_package(parts, path):
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)


def _rels_path(part):
    directory, filename = posixpath.split(part)
    return posixpath.join(directory, "_rels", filename + ".rels")


def _rels(parts, name):
    if name in parts:
        return _xml(parts[name])
    return etree.Element(f"{{{P}}}Relationships", nsmap={None: P})


def _next_id(root, attribute, prefix=""):
    values = {node.get(attribute) for node in root.iter()}
    number = 1
    while f"{prefix}{number}" in values:
        number += 1
    return f"{prefix}{number}"


def _part_type(parts, name):
    root = _xml(parts["[Content_Types].xml"])
    extension = posixpath.splitext(name)[1].lstrip(".")
    for entry in root:
        if entry.tag == f"{{{C}}}Override" and entry.get("PartName") == "/" + name:
            return entry.get("ContentType")
    for entry in root:
        if entry.tag == f"{{{C}}}Default" and entry.get("Extension") == extension:
            return entry.get("ContentType")
    raise TemplateFallback(f"Word 关联部件缺少内容类型：{name}")


def _add_type(parts, name, content_type):
    root = _xml(parts["[Content_Types].xml"])
    part_name = "/" + name
    if not any(node.get("PartName") == part_name for node in root):
        etree.SubElement(root, f"{{{C}}}Override", PartName=part_name, ContentType=content_type)
    parts["[Content_Types].xml"] = _serialized(root)


def _ensure_document_relation(parts, kind, target):
    name = "word/_rels/document.xml.rels"
    root = _rels(parts, name)
    relation_type = R + "/" + kind
    if not any(node.get("Type") == relation_type for node in root):
        etree.SubElement(root, f"{{{P}}}Relationship", {
            "Id": _next_id(root, "Id", "rId"), "Type": relation_type, "Target": target,
        })
    parts[name] = _serialized(root)


def _merge_styles(parts, donor, elements, prefix):
    source = _xml(donor["word/styles.xml"])
    target = _xml(parts["word/styles.xml"])
    ids = {node.get(f"{{{W}}}styleId"): prefix + node.get(f"{{{W}}}styleId")
           for node in source if node.tag == f"{{{W}}}style"}
    references = {f"{{{W}}}{tag}" for tag in ("pStyle", "rStyle", "tblStyle", "basedOn", "next", "link", "styleLink", "numStyleLink")}
    for root in [*elements, source]:
        for node in root.iter():
            if node.tag in references and node.get(f"{{{W}}}val") in ids:
                node.set(f"{{{W}}}val", ids[node.get(f"{{{W}}}val")])
    for node in source:
        if node.tag == f"{{{W}}}style":
            node.set(f"{{{W}}}styleId", ids[node.get(f"{{{W}}}styleId")])
            node.attrib.pop(f"{{{W}}}default", None)
            target.append(node)
    parts["word/styles.xml"] = _serialized(target)
    return ids


def _merge_numbering(parts, donor, elements, style_ids):
    if "word/numbering.xml" not in donor:
        return
    source = _xml(donor["word/numbering.xml"])
    target = (_xml(parts["word/numbering.xml"]) if "word/numbering.xml" in parts
              else etree.Element(f"{{{W}}}numbering", nsmap={"w": W}))
    abstract_ids, number_ids = {}, {}
    for node in source:
        if node.tag == f"{{{W}}}abstractNum":
            old = node.get(f"{{{W}}}abstractNumId")
            new = _next_id(target, f"{{{W}}}abstractNumId")
            abstract_ids[old] = new
            copied = deepcopy(node)
            copied.set(f"{{{W}}}abstractNumId", new)
            for link in copied.iter():
                if link.tag in {f"{{{W}}}pStyle", f"{{{W}}}styleLink", f"{{{W}}}numStyleLink"}:
                    value = link.get(f"{{{W}}}val")
                    if value in style_ids:
                        link.set(f"{{{W}}}val", style_ids[value])
            insertion = next((target.index(child) for child in target
                              if child.tag in {f"{{{W}}}num", f"{{{W}}}numIdMacAtCleanup"}), len(target))
            target.insert(insertion, copied)
    for node in source:
        if node.tag == f"{{{W}}}num":
            old = node.get(f"{{{W}}}numId")
            new = _next_id(target, f"{{{W}}}numId")
            number_ids[old] = new
            copied = deepcopy(node)
            copied.set(f"{{{W}}}numId", new)
            for link in copied.findall(f"{{{W}}}abstractNumId"):
                link.set(f"{{{W}}}val", abstract_ids[link.get(f"{{{W}}}val")])
            insertion = next((target.index(child) for child in target
                              if child.tag == f"{{{W}}}numIdMacAtCleanup"), len(target))
            target.insert(insertion, copied)
    for root in elements:
        for node in root.iter(f"{{{W}}}numId"):
            value = node.get(f"{{{W}}}val")
            if value in number_ids:
                node.set(f"{{{W}}}val", number_ids[value])
    # Numbering may also be referenced by the newly copied paragraph styles.
    styles = _xml(parts["word/styles.xml"])
    for style in styles:
        if style.get(f"{{{W}}}styleId") in style_ids.values():
            for node in style.iter(f"{{{W}}}numId"):
                value = node.get(f"{{{W}}}val")
                if value in number_ids:
                    node.set(f"{{{W}}}val", number_ids[value])
    parts["word/styles.xml"] = _serialized(styles)
    parts["word/numbering.xml"] = _serialized(target)
    _add_type(parts, "word/numbering.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml")
    _ensure_document_relation(parts, "numbering", "numbering.xml")


def _merge_relationships(parts, donor, elements, prefix):
    source = _rels(donor, "word/_rels/document.xml.rels")
    target = _rels(parts, "word/_rels/document.xml.rels")
    relations = {entry.get("Id"): entry for entry in source}
    copied_parts, relation_ids = {}, {}

    def clone_part(name):
        if name in copied_parts:
            return copied_parts[name]
        if name not in donor:
            raise TemplateFallback(f"Word 关联部件不存在：{name}")
        destination = posixpath.join("word", prefix, name)
        copied_parts[name] = destination
        parts[destination] = donor[name]
        _add_type(parts, destination, _part_type(donor, name))
        relation_file = _rels_path(name)
        if relation_file in donor:
            children = _xml(donor[relation_file])
            for child in children:
                if child.get("TargetMode") != "External":
                    linked = posixpath.normpath(posixpath.join(posixpath.dirname(name), child.get("Target")))
                    new_linked = clone_part(linked)
                    child.set("Target", posixpath.relpath(new_linked, posixpath.dirname(destination)))
            parts[_rels_path(destination)] = _serialized(children)
        return destination

    for root in elements:
        for node in root.iter():
            for attribute, value in list(node.attrib.items()):
                if not attribute.startswith("{" + R + "}"):
                    continue
                if value not in relation_ids:
                    if value not in relations:
                        raise TemplateFallback(f"Word 填写内容缺少关联：{value}")
                    relation = deepcopy(relations[value])
                    new_id = _next_id(target, "Id", "rId")
                    relation.set("Id", new_id)
                    if relation.get("TargetMode") != "External":
                        name = posixpath.normpath(posixpath.join("word", relation.get("Target")))
                        relation.set("Target", posixpath.relpath(clone_part(name), "word"))
                    target.append(relation)
                    relation_ids[value] = new_id
                node.set(attribute, relation_ids[value])
    parts["word/_rels/document.xml.rels"] = _serialized(target)


def _target_element(body, target):
    try:
        if set(target) == {"paragraph"}:
            return body.findall(f"{{{W}}}p")[target["paragraph"]]
        if set(target) == {"table", "row", "column"}:
            table = body.findall(f"{{{W}}}tbl")[target["table"]]
            row = table.findall(f"{{{W}}}tr")[target["row"]]
            return row.findall(f"{{{W}}}tc")[target["column"]]
    except (IndexError, KeyError, TypeError) as error:
        raise TemplateFallback(f"模板中找不到指定填写位置：{target}") from error
    raise TemplateFallback(f"模板填写位置格式不受支持：{target}")


def inspect_template(path, mapping, body):
    if Path(path).suffix.lower() != ".docx":
        raise TemplateFallback("该模板不是可直接填写的 DOCX 文件")
    try:
        Document(str(path))
        parts = _read_package(path)
        document = _xml(parts["word/document.xml"])
        settings = _xml(parts["word/settings.xml"]) if "word/settings.xml" in parts else None
        if settings is not None and settings.find(f"{{{W}}}documentProtection") is not None:
            raise TemplateFallback("学校模板设置了编辑保护")
        unsupported = {f"{{{W}}}{name}" for name in ("sdt", "txbxContent", "object", "altChunk", "ins", "del")}
        if any(node.tag in unsupported for node in document.iter()):
            raise TemplateFallback("学校模板含内容控件、修订或复杂嵌入对象")
        def has_note(value):
            if isinstance(value, dict):
                return value.get("t") == "Note" or any(has_note(child) for child in value.values())
            return isinstance(value, list) and any(has_note(child) for child in value)
        if has_note(body):
            raise TemplateFallback("正文包含脚注；当前模板填入器不能保证脚注编号与学校原件兼容")
        root = document.find(f"{{{W}}}body")
        targets = [_target_element(root, entry["target"]) for entry in mapping]
        if len({id(target) for target in targets}) != len(targets):
            raise TemplateFallback("多个学校栏目指向同一填写位置")
        return parts, document, targets
    except TemplateFallback:
        raise
    except Exception as error:
        raise TemplateFallback(f"学校模板无法可靠读入：{error}") from error


def fill_template(path, mapping, body, fragments, output):
    parts, document, targets = inspect_template(path, mapping, body)
    regions = []
    for index, (entry, target, fragment) in enumerate(zip(mapping, targets, fragments)):
        donor = _read_package(fragment)
        donor_body = _xml(donor["word/document.xml"]).find(f"{{{W}}}body")
        elements = [deepcopy(node) for node in donor_body if node.tag != f"{{{W}}}sectPr"]
        if not elements:
            raise TemplateFallback(f"栏目 {entry['field']} 没有可填写内容")
        prefix = f"rp_{uuid4().hex[:12]}_{index}_"
        style_ids = _merge_styles(parts, donor, elements, prefix)
        _merge_numbering(parts, donor, elements, style_ids)
        _merge_relationships(parts, donor, elements, prefix)
        drawing_ids = [int(node.get("id")) for node in document.iter()
                       if node.tag.rsplit("}", 1)[-1] in {"docPr", "cNvPr"}
                       and node.get("id", "").isdigit()]
        next_drawing = max(drawing_ids + [0]) + 1
        for root in elements:
            for node in root.iter():
                if node.tag.rsplit("}", 1)[-1] in {"docPr", "cNvPr"} and "id" in node.attrib:
                    node.set("id", str(next_drawing))
                    next_drawing += 1
        # Donor bookmarks must not collide with the school form or other fields.
        names, bookmark_ids = {}, {}
        next_bookmark = max([int(node.get(f"{{{W}}}id", "0"))
                             for node in document.iter(f"{{{W}}}bookmarkStart")] + [0]) + 1
        for root in elements:
            for node in root.iter(f"{{{W}}}bookmarkStart"):
                old_id = node.get(f"{{{W}}}id")
                bookmark_ids[old_id] = str(next_bookmark)
                next_bookmark += 1
                old_name = node.get(f"{{{W}}}name")
                names[old_name] = prefix + old_name
                node.set(f"{{{W}}}id", bookmark_ids[old_id])
                node.set(f"{{{W}}}name", names[old_name])
        for root in elements:
            for node in root.iter():
                if node.tag == f"{{{W}}}bookmarkEnd" and node.get(f"{{{W}}}id") in bookmark_ids:
                    node.set(f"{{{W}}}id", bookmark_ids[node.get(f"{{{W}}}id")])
                if node.tag == f"{{{W}}}hyperlink" and node.get(f"{{{W}}}anchor") in names:
                    node.set(f"{{{W}}}anchor", names[node.get(f"{{{W}}}anchor")])
        marker = prefix + "field"
        paragraphs = [node for root in elements for node in root.iter(f"{{{W}}}p")]
        if not paragraphs:
            raise TemplateFallback(f"栏目 {entry['field']} 无法标记填写区域")
        start = etree.Element(f"{{{W}}}bookmarkStart", {f"{{{W}}}id": str(next_bookmark), f"{{{W}}}name": marker})
        end = etree.Element(f"{{{W}}}bookmarkEnd", {f"{{{W}}}id": str(next_bookmark)})
        first = paragraphs[0]
        first.insert(1 if first.find(f"{{{W}}}pPr") is not None else 0, start)
        paragraphs[-1].append(end)
        if target.tag == f"{{{W}}}tc":
            for child in list(target):
                if child.tag != f"{{{W}}}tcPr":
                    target.remove(child)
            target.extend(elements)
            if elements[-1].tag != f"{{{W}}}p":
                target.append(etree.Element(f"{{{W}}}p"))
        else:
            parent, position = target.getparent(), target.getparent().index(target)
            parent.remove(target)
            for offset, node in enumerate(elements):
                parent.insert(position + offset, node)
        container = target if target.tag == f"{{{W}}}tc" else parent
        cursor, depth = start, 0
        while cursor is not container:
            cursor, depth = cursor.getparent(), depth + 1
        regions.append({"field": entry["field"], "marker": marker,
                        "container_depth": depth, "body_blocks": entry["body_blocks"]})
    parts["word/document.xml"] = _serialized(document)
    _write_package(parts, output)
    return regions


def extract_region(docx_path, marker, output, container_depth):
    """Make a readback document containing only the actual inserted field."""
    parts = _read_package(docx_path)
    document = _xml(parts["word/document.xml"])
    starts = document.xpath(".//w:bookmarkStart[@w:name=$marker]", namespaces=NS, marker=marker)
    if len(starts) != 1:
        raise ValueError(f"填写区域标记缺失或重复：{marker}")
    start = starts[0]
    ends = document.xpath(".//w:bookmarkEnd[@w:id=$identifier]", namespaces=NS, identifier=start.get(f"{{{W}}}id"))
    if len(ends) != 1:
        raise ValueError(f"填写区域终点缺失或重复：{marker}")
    # Depth disambiguates an inserted nested table from its school-form cell.
    container = start
    for _ in range(container_depth):
        container = container.getparent()
        if container is None:
            raise ValueError(f"填写区域所在位置已改变：{marker}")
    if container.tag not in {f"{{{W}}}body", f"{{{W}}}tc"}:
        raise ValueError(f"填写区域所在位置已改变：{marker}")
    def direct_child(node):
        while node.getparent() is not container:
            node = node.getparent()
            if node is None:
                raise ValueError(f"填写区域边界不在同一位置：{marker}")
        return node
    begin, finish = direct_child(start), direct_child(ends[0])
    selected = list(container)[container.index(begin):container.index(finish) + 1]
    body = document.find(f"{{{W}}}body")
    section = body.find(f"{{{W}}}sectPr")
    for child in list(body):
        body.remove(child)
    body.extend(deepcopy(selected))
    if section is not None:
        body.append(section)
    parts["word/document.xml"] = _serialized(document)
    _write_package(parts, output)
