"""Carrier readers with source locations; no paper-analysis or state writes."""

from __future__ import annotations

import copy
import codecs
from email.message import Message
from html.parser import HTMLParser as DeclarationParser
import json
import os
from pathlib import Path
import posixpath
import subprocess
from urllib.parse import unquote, urlsplit, urlunsplit
from xml.etree import ElementTree
from zipfile import ZipFile

from lxml import etree, html

from ._common import hash_file, issue, json_digest, run_tool
from ._material_word import read_word_structure
from ._record_paths import decode_record_paths, read_record, write_record


def ast_text(value) -> str:
    """Read Pandoc constructors, never attribute strings or numeric table metadata."""
    if isinstance(value, list):
        return "".join(ast_text(item) for item in value)
    if not isinstance(value, dict):
        return ""
    kind, content = value.get("t"), value.get("c")
    if kind == "Str":
        return content
    if kind in {"Space", "SoftBreak", "LineBreak"}:
        return "\n" if kind == "LineBreak" else " "
    if kind in {"Code", "CodeBlock", "Math", "RawInline", "RawBlock"}:
        return content[-1]
    if kind in {"Span", "Div", "Cite"}:
        return ast_text(content[1])
    if kind in {"Link", "Image"}:
        return ast_text(content[1])
    if kind == "Header":
        return ast_text(content[2])
    if kind in {"Para", "Plain"}:
        return ast_text(content) + "\n"
    if "blocks" in value:
        return ast_text(value["blocks"])
    return ast_text(content)


def pandoc_body(path: Path | None, reader: str, *, data: bytes | None = None,
                media_dir: Path | None = None, track_changes: bool = False) -> dict:
    arguments = ["-f", reader, "-t", "json"]
    if track_changes:
        arguments.append("--track-changes=all")
    if media_dir is not None:
        arguments.extend(["--extract-media", str(media_dir)])
    if path is not None:
        arguments.append(str(path))
    output = run_tool("pandoc", arguments, input=data)
    body = json.loads(output.stdout)
    if not isinstance(body, dict) or not isinstance(body.get("blocks"), list) or not body.get("pandoc-api-version"):
        raise ValueError("Pandoc 没有返回可读的正文结构。")
    return body


def decode_text(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    return data.decode("utf-8-sig")


def read_text(path: Path, directory: Path, markdown: bool, *, movable_root: Path | None = None) -> tuple[list, list, str]:
    source = decode_text(path)
    lines = source.splitlines()
    if not markdown:
        blocks = []
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            locator = {"kind": "text", "line": number}
            blocks.append({"text": line, "locator": locator})
        return blocks, [], "原始文本（UTF-8 或带字节序标记的 UTF-16）"
    body = pandoc_body(None, "markdown", data=source.encode("utf-8"))
    body = decode_record_paths(body, path.parent)
    write_record(directory / "结构.json", body, movable_root=movable_root)
    blocks, issues, cursor, section = [], [], 0, None
    characters, source_lines = [], []
    for number, line in enumerate(lines, 1):
        for character in line:
            if not character.isspace():
                characters.append(character)
                source_lines.append(number)
    searchable = "".join(characters)
    for index, block in enumerate(body["blocks"]):
        text = ast_text(block).strip()
        if not text:
            continue
        if block.get("t") == "Header":
            section = text
        # Find actual source text; punctuation/markup-only blocks retain a missing-locator issue.
        def strings(node):
            if isinstance(node, dict):
                if node.get("t") == "Str":
                    yield node["c"]
                elif node.get("t") in {"Code", "CodeBlock", "Math"}:
                    yield node["c"][-1]
                elif node.get("t") == "Note":
                    # A footnote's definition can appear later; it must not move the main-text cursor.
                    return
                else:
                    for child in node.values():
                        yield from strings(child)
            elif isinstance(node, list):
                for child in node:
                    yield from strings(child)
        tokens = ["".join(token.split()) for token in strings(block) if token.strip()]
        offset, located = cursor, None
        for token in tokens:
            found = searchable.find(token, offset)
            if found < 0:
                located = None
                break
            if located is None:
                located = source_lines[found]
            offset = found + len(token)
        locator = {"kind": "text", "ast_block": index}
        if located is not None:
            locator["line"] = located
            # Character offsets distinguish repeated paragraphs and multiple blocks on one source line.
            cursor = offset
        else:
            issues.append(issue("location_unresolved", "已读入此 Markdown 块，但不能可靠映射到原文件行号；引用前需核对。", {"path": str(path), "ast_block": index}))
        if section:
            locator["section"] = section
        blocks.append({"text": text, "locator": locator})
    return blocks, issues, "Pandoc Markdown AST，原始行定位"


_FLOW = {"p", "div", "section", "article", "main", "aside", "header", "footer", "nav", "body",
         "blockquote", "ul", "ol", "li", "dl", "dt", "dd", "pre", "table", "thead", "tbody", "tfoot",
         "tr", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "figure", "figcaption"}
_IGNORE = {"head", "script", "style", "noscript"}


class _HtmlEncodingError(ValueError):
    def __init__(self, kind: str, message: str, **location):
        super().__init__(message)
        self.kind = kind
        self.location = location


class _EncodingDeclarations(DeclarationParser):
    """Read declaration syntax, not document text, before selecting a codec."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.declarations = []
        self.in_body = False

    def add(self, value, origin):
        line, column = self.getpos()
        if not isinstance(value, str) or not value.strip():
            raise _HtmlEncodingError("html_encoding_declaration_invalid", "HTML 编码声明没有有效的编码名称。",
                                     declaration=origin, line=line, column=column)
        self.declarations.append({"encoding": value.strip(), "declaration": origin, "line": line})

    def handle_pi(self, data):
        if self.in_body:
            return
        data = data[:-1] if data.endswith("?") else data
        parts = data.split(None, 1)
        if len(parts) != 2 or parts[0].lower() != "xml":
            return
        try:
            attributes = ElementTree.fromstring("<declaration " + parts[1] + " />").attrib
        except ElementTree.ParseError as error:
            raise _HtmlEncodingError("html_encoding_declaration_invalid", "XML 声明无法解析，未猜测原文件编码。",
                                     declaration="xml", line=self.getpos()[0]) from error
        if "encoding" in attributes:
            self.add(attributes["encoding"], "xml")

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        if self.in_body or tag != "meta":
            return
        for name, value in attrs:
            if name == "charset":
                self.add(value, "meta charset")
        if any(name == "http-equiv" and (value or "").strip().lower() == "content-type" for name, value in attrs):
            for name, value in attrs:
                if name != "content" or value is None:
                    continue
                content_type = Message()
                content_type["content-type"] = value
                for parameter, encoding in content_type.get_params(header="content-type", failobj=[]):
                    if parameter.lower() == "charset":
                        self.add(encoding, "meta http-equiv")


def _decode_html(data: bytes) -> str:
    """Strictly decode a declared encoding before libxml2 sees document bytes."""
    signature, decoder = None, None
    for marker, encoding, codec in (
        (codecs.BOM_UTF32_LE, "utf-32-le", "utf-32"),
        (codecs.BOM_UTF32_BE, "utf-32-be", "utf-32"),
        (codecs.BOM_UTF16_LE, "utf-16-le", "utf-16"),
        (codecs.BOM_UTF16_BE, "utf-16-be", "utf-16"),
        (codecs.BOM_UTF8, "utf-8", "utf-8-sig"),
    ):
        if data.startswith(marker):
            signature, decoder = encoding, codec
            break
    if decoder is None:
        # XML's byte-order signatures allow its own declaration to be read without guessing.
        for marker, encoding in ((b"\x00\x00\x00<", "utf-32-be"), (b"<\x00\x00\x00", "utf-32-le"),
                                 (b"\x00<\x00?", "utf-16-be"), (b"<\x00?\x00", "utf-16-le")):
            if data.startswith(marker):
                signature = decoder = encoding
                break

    def strict_decode(encoding):
        try:
            return data.decode(encoding, errors="strict")
        except UnicodeDecodeError as error:
            raise _HtmlEncodingError("html_decode_failed", f"原文件不能按 {encoding} 严格解码；未以替换字符继续读取。",
                                     encoding=encoding, byte_offset=len(data) - len(error.object) + error.start) from error
        except UnicodeError as error:
            raise _HtmlEncodingError("html_decode_failed", f"原文件不能按 {encoding} 严格解码：{error}。", encoding=encoding) from error
        except (LookupError, TypeError) as error:
            raise _HtmlEncodingError("html_encoding_unknown", f"声明的 {encoding} 不是可用的文本编码。", encoding=encoding) from error

    # Latin-1 is only a one-byte view for ASCII declaration syntax, never the material decoding.
    probe = strict_decode(decoder) if decoder else data.decode("latin-1")
    declarations = _EncodingDeclarations()
    declarations.feed(probe)
    declarations.close()
    declared = []
    for entry in declarations.declarations:
        try:
            canonical = codecs.lookup(entry["encoding"]).name
        except LookupError as error:
            raise _HtmlEncodingError("html_encoding_unknown", f"无法识别声明编码 {entry['encoding']}，请核对原文件。", **entry) from error
        declared.append("utf-8" if canonical == "utf-8-sig" else canonical)
    if signature:
        compatible = {signature}
        if signature.startswith("utf-16-"):
            compatible.add("utf-16")
        elif signature.startswith("utf-32-"):
            compatible.add("utf-32")
        conflict = any(encoding not in compatible for encoding in declared)
    else:
        conflict = len(set(declared)) > 1
    if conflict:
        raise _HtmlEncodingError("html_encoding_conflict", "字节顺序或编码声明互相冲突；未自行选择其中一种。",
                                 signature=signature, declarations=declarations.declarations)
    decoded = strict_decode(decoder or (declared[0] if declared else "utf-8"))
    if "\x00" in decoded:
        raise _HtmlEncodingError("html_encoding_unresolved", "解码结果含空字符，无法确认声明与实际字节编码一致；未交给恢复解析器忽略。")
    return decoded


def _name(element) -> str:
    return etree.QName(element).localname.lower() if isinstance(element.tag, str) else ""


def _html_segments(root, fragment: str, kind: str) -> tuple[list, dict]:
    """Wrap source flow segments with private IDs for one structured Pandoc pass."""
    fragments, locations = [], {}
    paragraph = 0

    def add(element, payload):
        nonlocal paragraph
        if not "".join(payload.itertext()).strip() and not payload.xpath(".//img"):
            return
        paragraph += 1
        ancestors = [element, *element.iterancestors()]
        anchor = next((item.get("id") for item in ancestors if item.get("id")), None)
        identifier = f"rp-material-{paragraph}"
        locator = {"kind": kind, "fragment": fragment + (f"#{anchor}" if anchor else ""),
                   "paragraph": paragraph, "xpath": root.getroottree().getpath(element)}
        heading = next(("".join(item.itertext()).strip() for item in element.itersiblings(preceding=True)
                        if _name(item) in {"h1", "h2", "h3", "h4", "h5", "h6"}), None)
        if heading:
            locator["section"] = heading
        locations[identifier] = locator
        wrapper = etree.Element("div", id=identifier)
        payload.tail = None
        wrapper.append(payload)
        fragments.append(etree.tostring(wrapper, encoding="unicode", method="html"))

    def visit(element):
        name = _name(element)
        if not name or name in _IGNORE:
            return
        if not any(_name(child) in _FLOW for child in element.iterdescendants()):
            add(element, copy.deepcopy(element))
            return
        pending = etree.Element("p")
        pending.text = element.text
        for child in element:
            if _name(child) in _IGNORE:
                pass
            elif _name(child) in _FLOW or any(_name(node) in _FLOW for node in child.iterdescendants()):
                add(element, pending)
                pending = etree.Element("p")
                visit(child)
            else:
                duplicate = copy.deepcopy(child)
                duplicate.tail = None
                pending.append(duplicate)
            if child.tail:
                if len(pending):
                    pending[-1].tail = (pending[-1].tail or "") + child.tail
                else:
                    pending.text = (pending.text or "") + child.tail
        add(element, pending)

    body = next((element for element in root.iter() if _name(element) == "body"), root)
    visit(body)
    return fragments, locations


def _read_html_bytes(data: bytes, fragment: str, kind: str, directory: Path) -> tuple[list, list, dict]:
    decoded = _decode_html(data)
    # Encoding is settled with a strict codec before HTML recovery can discard invalid bytes.
    parser = html.HTMLParser(encoding="UTF-8", no_network=True, recover=True)
    root = html.document_fromstring(decoded.encode("utf-8"), parser=parser)
    issues = []
    location = {"kind": kind, "fragment": fragment}
    if "\ufffd" in decoded or any("\ufffd" in value for value in root.itertext()):
        issues.append(issue("html_replacement_character", "原文或结构解析结果含 U+FFFD 替换字符，文字尚未可靠核实；不能按完整材料引用。", location))
    encoding_errors = {getattr(etree.ErrorTypes, name, None) for name in ("ERR_INVALID_ENCODING", "ERR_UNSUPPORTED_ENCODING")}
    for entry in parser.error_log:
        if entry.type in encoding_errors:
            issues.append(issue("html_encoding_parse_error", "HTML 结构解析报告编码错误：" + entry.message,
                                {**location, "line": entry.line, "column": entry.column, "error_type": entry.type_name}))
    fragments, locations = _html_segments(root, fragment, kind)
    normalized = ("<!doctype html><html><head><meta charset='utf-8'></head><body>" + "\n".join(fragments) + "</body></html>").encode("utf-8")
    body = pandoc_body(None, "html+native_divs", data=normalized)
    blocks = []

    def consume(node):
        if isinstance(node, dict):
            if node.get("t") == "Div" and node["c"][0][0] in locations:
                locator = locations[node["c"][0][0]]
                text = ast_text(node["c"][1]).strip()
                if text:
                    blocks.append({"text": text, "locator": locator})
                else:
                    issues.append(issue("nontext_object", "此原文区域没有可提取文字，图像或对象需另行查看。", locator))
                return
            for value in node.values():
                consume(value)
        elif isinstance(node, list):
            for value in node:
                consume(value)
    consume(body)
    if len(blocks) + sum(item["kind"] == "nontext_object" for item in issues) != len(locations):
        issues.append(issue("unmapped_structure", "部分网页结构未能可靠读入，原文件仍保留。", {"kind": kind, "fragment": fragment}))
    return blocks, issues, body


def read_html(path: Path, directory: Path, *, movable_root: Path | None = None) -> tuple[list, list, str]:
    try:
        blocks, issues, body = _read_html_bytes(path.read_bytes(), path.name, "html", directory)
    except _HtmlEncodingError as error:
        return [], [issue(error.kind, str(error), {"kind": "html", "path": str(path), "fragment": path.name, **error.location})], "HTML 编码未确认，原件保留"
    body = decode_record_paths(body, path.parent)
    write_record(directory / "结构.json", body, movable_root=movable_root)
    return blocks, issues, "按编码声明严格解码，再由固定 UTF-8 的 lxml 与 Pandoc 读取结构"


def read_epub(path: Path, directory: Path, *, movable_root: Path | None = None) -> tuple[list, list, str]:
    blocks, issues, structures = [], [], []
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    with ZipFile(path) as archive:
        container = etree.fromstring(archive.read("META-INF/container.xml"), parser)
        roots = container.xpath("//*[local-name()='rootfile']/@full-path")
        if not roots:
            raise ValueError("EPUB 没有声明内容清单。")
        package_path = roots[0]
        package = etree.fromstring(archive.read(package_path), parser)
        namespace = {"o": "http://www.idpf.org/2007/opf"}
        manifest = {item.get("id"): item for item in package.findall("o:manifest/o:item", namespace)}
        for position, reference in enumerate(package.findall("o:spine/o:itemref", namespace), 1):
            item = manifest.get(reference.get("idref"))
            if item is None:
                issues.append(issue("missing_epub_item", "阅读顺序引用的章节不在内容清单中。", {"kind": "epub", "spine": position}))
                continue
            href = item.get("href", "")
            member = posixpath.normpath(posixpath.join(posixpath.dirname(package_path), unquote(href.split("#", 1)[0])))
            if member.startswith("../") or member.startswith("/"):
                issues.append(issue("invalid_epub_path", "电子书章节路径无法安全读取。", {"kind": "epub", "fragment": href}))
                continue
            if item.get("media-type") not in {"application/xhtml+xml", "text/html"}:
                issues.append(issue("unsupported_epub_item", "此电子书章节需转换为 HTML 或图像后读取。", {"kind": "epub", "fragment": member}))
                continue
            try:
                content = archive.read(member)
                # XHTML's XML declaration is authoritative; emit UTF-8 for the HTML reader.
                if item.get("media-type") == "application/xhtml+xml":
                    document = etree.fromstring(content, parser)
                    for node in document.iter():
                        if isinstance(node.tag, str):
                            node.tag = etree.QName(node).localname
                            if node.tag.lower() == "meta":
                                attributes = {name.lower(): name for name in node.attrib}
                                if "charset" in attributes:
                                    node.set(attributes["charset"], "utf-8")
                                equivalent = node.get(attributes.get("http-equiv", "http-equiv"), "")
                                if equivalent.strip().lower() == "content-type" and "content" in attributes:
                                    content_type = Message()
                                    content_type["content-type"] = node.get(attributes["content"], "text/html")
                                    content_type.set_param("charset", "utf-8", header="content-type", replace=True)
                                    node.set(attributes["content"], str(content_type["content-type"]))
                    # XML has already decoded the source; old HTML metadata must describe
                    # this UTF-8 serialization rather than trigger a false second conflict.
                    content = etree.tostring(document, encoding="utf-8", method="html")
                    content = b'<meta charset="utf-8">' + content
                chapter_blocks, chapter_issues, body = _read_html_bytes(content, member, "epub", directory)
                # Archive-local media cannot be resolved against the filesystem cwd.
                # Keep only referenced members as product-owned copies beside the structure record.
                def retain_media(node):
                    if isinstance(node, dict):
                        if node.get("t") in {"Image", "Link"}:
                            target = node["c"][2]
                            parsed = urlsplit(target[0])
                            if parsed.path and not parsed.scheme and not parsed.netloc:
                                resource = posixpath.normpath(posixpath.join(posixpath.dirname(member), unquote(parsed.path)))
                                if not resource.startswith(("../", "/")) and resource in archive.namelist():
                                    retained = directory / "epub-assets" / resource
                                    retained.parent.mkdir(parents=True, exist_ok=True)
                                    retained.write_bytes(archive.read(resource))
                                    target[0] = urlunsplit(("", "", str(retained), parsed.query, parsed.fragment))
                                else:
                                    chapter_issues.append(issue("epub_resource_unavailable", "此章节的本地引用无法在原电子书中取得；引用仍待核对。", {"kind": "epub", "fragment": member, "target": target[0]}))
                        for value in node.values():
                            retain_media(value)
                    elif isinstance(node, list):
                        for value in node:
                            retain_media(value)
                retain_media(body)
                blocks.extend(chapter_blocks)
                issues.extend(chapter_issues)
                structures.append({"fragment": member, "body": body})
            except _HtmlEncodingError as error:
                issues.append(issue(error.kind, str(error), {"kind": "epub", "fragment": member, **error.location}))
            except (KeyError, ValueError, etree.XMLSyntaxError, subprocess.SubprocessError, OSError) as error:
                issues.append(issue("epub_chapter_failed", f"此章节未能读取：{type(error).__name__}；已读章节保留。", {"kind": "epub", "fragment": member}))
    write_record(directory / "章节结构.json", structures, movable_root=movable_root)
    return blocks, issues, "EPUB 原阅读顺序、章节片段与 Pandoc HTML AST"


def read_docx(path: Path, directory: Path, *, movable_root: Path | None = None) -> tuple[list, list, str]:
    structure = read_word_structure(path)
    issues = [issue("unsupported_word_object", item["text"], item["location"]) for item in structure["unsupported"]]
    if structure["changes"]:
        issues.append(issue("unresolved_changes", "材料含未决 Word 修订，插入和删除均保留；引用前须确定采用的版本。", str(path)))
    # XML supplies original positions; Pandoc supplies the retained structured representation.
    try:
        body = pandoc_body(path, "docx+styles", media_dir=directory / "media", track_changes=True)
        body = decode_record_paths(body, path.parent)
        write_record(directory / "结构.json", body, movable_root=movable_root)
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        issues.append(issue("word_structure_failed", f"Pandoc 结构读取失败（{type(error).__name__}）；已从原 XML 取得的文字和位置保留。", str(path)))
    write_record(directory / "Word标记.json", {key: structure[key] for key in ("changes", "comments", "unsupported")}, movable_root=movable_root)
    return structure["blocks"], issues, "Pandoc docx+styles 与原 Word XML"


def _vision_configuration() -> tuple[str | None, list]:
    supplied = os.environ.get("VISION_ENV_FILE")
    if not supplied:
        return None, [issue("vision_configuration", "图片文字识别需要显式设置 VISION_ENV_FILE。", "VISION_ENV_FILE")]
    path = Path(supplied).expanduser().resolve()
    if not path.is_file():
        return None, [issue("vision_configuration", "指定的图片识别配置文件不存在。", str(path))]
    values = {}
    # Match the fixed upstream client's env-file syntax; do not reveal values in results.
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"').strip("'")
    missing = [key for key in ("VISION_API_KEY", "VISION_BASE_URL", "VISION_MODEL") if not values.get(key, "").strip()]
    if missing:
        return None, [issue("vision_configuration", "指定配置文件缺少：" + "、".join(missing), str(path))]
    return hash_file(path), []


def _positions(length: int, limit: int = 1024, overlap: int = 96) -> list[int]:
    if length <= limit:
        return [0]
    points = list(range(0, length - limit + 1, limit - overlap))
    if points[-1] != length - limit:
        points.append(length - limit)
    return points


def _parse_ocr_output(raw: str, location: dict, raw_output_path: str) -> dict:
    """Separate output structures, without claiming they were absent from the image.

    The fixed glance CLI returns the provider's string, not typed OCR evidence.
    Markdown is only an output-structure parser here. Every extracted item still
    needs comparison with the actual input image; service-written coordinates
    remain unverified text and never replace the known input region.
    """
    issues = [issue("ocr_visual_review_required", "此区域的识别结果尚未对照原图核对。候选文字、遗漏、遮挡和输出说明均需实际查看；没有 [?] 不代表内容完整或可直接引用。", location)]
    interpretations = []
    omitted = object()

    def separate(node):
        if isinstance(node, list):
            return [clean for item in node if (clean := separate(item)) is not omitted]
        if not isinstance(node, dict):
            return node
        kind, content = node.get("t"), node.get("c")
        if kind in {"BlockQuote", "RawBlock", "RawInline", "CodeBlock", "Image"}:
            text = content[-1] if kind in {"RawBlock", "RawInline", "CodeBlock"} else ast_text(node).strip()
            interpretations.append({
                "kind": "unverified_output_structure", "text": text,
                "locator": dict(location), "verification": "needs_input",
                "raw_output_path": raw_output_path, "output_structure": kind,
            })
            return omitted
        return {key: clean for key, value in node.items() if (clean := separate(value)) is not omitted}

    try:
        body = pandoc_body(None, "markdown-smart", data=raw.encode("utf-8"))
        text = ast_text(separate(body)).strip()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        text = ""
        interpretations.append({"kind": "unverified_output_structure", "text": raw,
                                "locator": dict(location), "verification": "needs_input",
                                "raw_output_path": raw_output_path, "output_structure": "unparsed"})
        issues.append(issue("ocr_output_parse_failed", f"识别输出的结构未能分开（{type(error).__name__}）；原输出完整保留，不能直接当作逐字转录。", location))
    if interpretations:
        issues.append(issue("ocr_output_structure_unverified", "识别输出含引用、原始标记或其他结构片段，已另存。尚未核对它们是否出现在原图中，不据格式认定其来源，也不采用其中坐标作为确定定位。", location))
    if "[?]" in raw:
        issues.append(issue("uncertain_transcription", "此区域含无法辨认的文字或符号，原输出中的 [?] 已保留；引用前需核对，不能补猜。", location))
    return {"text": text, "interpretation": interpretations, "issues": issues}


def _ocr_image(path: Path, width: int, height: int, directory: Path, locator: dict,
               *, transform=None, movable_root: Path | None = None) -> tuple[list, list, dict]:
    configuration, issues = _vision_configuration()
    blocks, interpretations, outputs = [], [], []
    cache = directory / "ocr"
    cache.mkdir(parents=True, exist_ok=True)
    image_digest = hash_file(path)

    def retain(raw, location, box, key, origin):
        raw_path = cache / f"{key}-stdout.txt"
        raw_path.write_text(raw, encoding="utf-8")
        outputs.append({"raw_output_path": str(raw_path), "input_image": str(path),
                        "input_bbox": box, "locator": dict(location), "origin": origin})
        if not raw.strip():
            return
        parsed = _parse_ocr_output(raw, location, str(raw_path))
        if parsed["text"]:
            blocks.append({"text": parsed["text"], "locator": location,
                           "verification": "needs_input", "raw_output_path": str(raw_path)})
        interpretations.extend(parsed["interpretation"])
        issues.extend(parsed["issues"])

    for top in _positions(height):
        for left in _positions(width):
            box = [left, top, min(left + 1024, width), min(top + 1024, height)]
            location = {**locator, "bbox": transform(box) if transform else box}
            if transform:
                location["image_bbox"] = box
            key = json_digest({"image": image_digest, "box": box})
            cache_file = cache / f"{key}.json"
            previous = read_record(cache_file) if cache_file.is_file() else None
            if previous and previous.get("configuration") == configuration and configuration:
                raw = previous.get("raw_output", previous["text"])
                origin = previous.get("raw_output_origin", "legacy_cache_text")
            elif configuration:
                try:
                    response = run_tool("vision-glance", [str(path), "--ocr", "--region", ",".join(map(str, box))], timeout=300)
                    (cache / f"{key}-stdout.txt").write_bytes(response.stdout)
                    raw = response.stdout.decode("utf-8")
                    origin = "live_stdout"
                    write_record(cache_file, {"configuration": configuration, "text": raw.strip(), "locator": location,
                                              "raw_output": raw, "raw_output_origin": origin}, movable_root=movable_root)
                except (OSError, subprocess.SubprocessError, UnicodeError) as error:
                    diagnostic = cache / f"{key}-error.txt"
                    detail = getattr(error, "stderr", None)
                    if isinstance(detail, bytes):
                        detail = detail.decode("utf-8", errors="replace")
                    detail = detail or str(error)
                    # Keep the useful original client error, with known credential values removed.
                    secret = os.environ.get("VISION_API_KEY")
                    if secret:
                        detail = detail.replace(secret, "[已隐藏密钥]")
                    configuration_file = Path(os.environ["VISION_ENV_FILE"]).expanduser()
                    for line in configuration_file.read_text(encoding="utf-8").splitlines():
                        key_name, separator, value = line.partition("=")
                        if separator and key_name.strip() == "VISION_API_KEY":
                            secret = value.strip().strip('"').strip("'")
                            if secret:
                                detail = detail.replace(secret, "[已隐藏密钥]")
                    diagnostic.write_text(detail, encoding="utf-8")
                    issues.append(issue("ocr_failed", f"图片文字识别未完成（{type(error).__name__}）；原错误另存于诊断文件，可读结果和原图保留，未猜测内容。", {**location, "diagnostic_path": str(diagnostic)}))
                    if previous:
                        retain(previous.get("raw_output", previous["text"]), location, box, key,
                               previous.get("raw_output_origin", "legacy_cache_text"))
                    continue
            else:
                # Already saved transcriptions remain available when a later dependency fails.
                if previous:
                    retain(previous.get("raw_output", previous["text"]), location, box, key,
                           previous.get("raw_output_origin", "legacy_cache_text"))
                continue
            if not raw.strip():
                retain(raw, location, box, key, origin)
                issues.append(issue("ocr_empty", "此区域未返回可读文字；不能把它认定为空白材料。", location))
                continue
            retain(raw, location, box, key, origin)
    return blocks, issues, {"interpretation": interpretations, "ocr_outputs": outputs}


def read_image(path: Path, directory: Path, *, movable_root: Path | None = None) -> tuple[list, list, str, dict]:
    from PIL import Image
    blocks, issues = [], []
    details = {"interpretation": [], "ocr_outputs": []}
    with Image.open(path) as original:
        for frame in range(getattr(original, "n_frames", 1)):
            original.seek(frame)
            normalized = directory / f"图像-{frame + 1}.png"
            # Do not rotate/resize: returned pixel boxes use the original pixel coordinate system.
            original.convert("RGB").save(normalized)
            locator = {"kind": "image", "image": str(path)}
            if getattr(original, "n_frames", 1) > 1:
                locator["frame"] = frame + 1
            read_blocks, read_issues, read_details = _ocr_image(normalized, *original.size, directory, locator, movable_root=movable_root)
            blocks.extend(read_blocks)
            issues.extend(read_issues)
            for name in details:
                details[name].extend(read_details[name])
    return blocks, issues, "Pillow 原像素归一及固定 vision-glance --ocr 分区识别；候选结果待原图核对", details


def read_pdf(path: Path, directory: Path, *, movable_root: Path | None = None) -> tuple[list, list, str, dict]:
    import pymupdf
    blocks, issues = [], []
    details = {"interpretation": [], "ocr_outputs": []}
    with pymupdf.open(path) as document:
        if document.needs_pass:
            return [], [issue("encrypted_pdf", "PDF 需要密码；请提供有读取权限的可打开副本。", str(path))], "PyMuPDF", details
        for number, page in enumerate(document, 1):
            location = {"kind": "pdf", "page": number}
            label = page.get_label()
            if label:
                location["printed_label"] = label
            try:
                extracted = page.get_text("blocks")
                text_length, image_area = 0, 0
                for item in extracted:
                    if item[6] == 0 and item[4].strip():
                        text_length += len(item[4].strip())
                        blocks.append({"text": item[4].strip(), "locator": {
                            **location, "bbox": [float(value) for value in item[:4]], "block": item[5], "bbox_units": "PDF points"
                        }})
                    elif item[6] == 1:
                        image_area += max(0, item[2] - item[0]) * max(0, item[3] - item[1])
                if text_length == 0 or (text_length < 80 and image_area > page.rect.get_area() * 0.2):
                    page_image = directory / f"原页-{number}.png"
                    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
                    pixmap.save(page_image)
                    def transform(box):
                        return [round(page.rect.x0 + box[0] * page.rect.width / pixmap.width, 4),
                                round(page.rect.y0 + box[1] * page.rect.height / pixmap.height, 4),
                                round(page.rect.x0 + box[2] * page.rect.width / pixmap.width, 4),
                                round(page.rect.y0 + box[3] * page.rect.height / pixmap.height, 4)]
                    read_blocks, read_issues, read_details = _ocr_image(page_image, pixmap.width, pixmap.height, directory,
                                                                      {**location, "bbox_units": "PDF points", "page_image": str(page_image)},
                                                                      transform=transform, movable_root=movable_root)
                    blocks.extend(read_blocks)
                    issues.extend(read_issues)
                    for name in details:
                        details[name].extend(read_details[name])
            except (OSError, ValueError, RuntimeError) as error:
                issues.append(issue("pdf_page_failed", f"本页未能完整读取（{type(error).__name__}）；其余页的有效结果保留。", location))
    return blocks, issues, "PyMuPDF 物理页与文字块；扫描区域使用固定 vision-glance --ocr，候选结果待原图核对", details
