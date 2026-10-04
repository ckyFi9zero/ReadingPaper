#!/usr/bin/env python3
"""Shared validation and rendering helpers for paper evidence maps."""

import html
import json
import math
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlsplit


NODE_KINDS = {"note", "pdf", "code"}
RELATION_TYPES = {"derived-from", "supports", "implements", "differs", "related"}
STATUS_TYPES = {"source-checked", "static-read", "inferred", "unverified"}
STAGES = {"first-pass", "deep-read", "code"}
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
START_MARKER = "<!-- EvidenceLinks:START -->"
END_MARKER = "<!-- EvidenceLinks:END -->"
EVIDENCE_STYLE = """<style data-evidence-links>
.evidence-panel{margin:28px 0;padding:22px;background:#f7faf7;border:1px solid #dce4dc;border-radius:8px;color:#243631;font:15px/1.7 system-ui,-apple-system,"Noto Sans CJK SC","Microsoft YaHei",sans-serif}.evidence-panel h2{margin:0;font-size:22px}.evidence-panel-heading{display:flex;justify-content:space-between;gap:12px;align-items:baseline;border-bottom:1px solid #dce4dc;padding-bottom:10px}.evidence-panel-heading span,.evidence-intro,.evidence-status{color:#5e7068;font-size:13px}.evidence-intro{margin:10px 0 16px}.evidence-card{padding:14px 0;border-top:1px solid #dce4dc}.evidence-card:first-of-type{border-top:0}.evidence-card-head{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.evidence-card-head strong{font-size:14px}.evidence-relation{padding:2px 7px;border-radius:999px;background:#eaf0e8;color:#176758;font-size:12px}.evidence-locations{display:flex;flex-wrap:wrap;gap:7px 12px;align-items:center;margin-top:8px}.evidence-link,.evidence-local{overflow-wrap:anywhere}.evidence-link{text-decoration:none;font-weight:600}.evidence-note{color:#176758}.evidence-pdf{color:#8a5a13}.evidence-code{color:#245d78}.evidence-local{font-size:13px;color:#5e7068}.evidence-arrow{color:#9b6b27}.evidence-status{margin-top:7px}.evidence-status-source-checked{color:#176758;font-weight:650}.evidence-status-static-read{color:#245d78;font-weight:650}.evidence-status-inferred{color:#8a5a13;font-weight:650}.evidence-status-unverified{color:#8b4437;font-weight:650}.evidence-note-text{margin-left:10px}.evidence-note-text:before{content:"· ";color:#9b6b27}
</style>"""


class _IDParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])


def page_ids(path):
    parser = _IDParser()
    parser.feed(Path(path).read_text(encoding="utf-8"))
    return parser.ids


def map_path(root, slug):
    return Path(root) / "papers" / slug / "evidence-map.json"


def load_map(root, slug):
    path = map_path(root, slug)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid evidence map JSON: {path}: {exc}") from exc
    validate_shape(data, slug)
    return data


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _validate_region(region, label):
    _require(isinstance(region, dict), f"PDF region must be an object: {label}")
    for key in ("x", "y", "width", "height"):
        _require(isinstance(region.get(key), (int, float)) and math.isfinite(region[key]), f"PDF region needs numeric {key}: {label}")
    _require(0 <= region["x"] < 1 and 0 <= region["y"] < 1 and 0 < region["width"] <= 1 and 0 < region["height"] <= 1 and region["x"] + region["width"] <= 1 and region["y"] + region["height"] <= 1, f"PDF region must stay within page bounds: {label}")


def _http_url(value, field):
    parsed = urlsplit(value)
    _require(parsed.scheme in ("http", "https") and parsed.netloc, f"Evidence {field} must be an http(s) URL")


def validate_shape(data, slug):
    _require(isinstance(data, dict), "Evidence map must be an object")
    _require(data.get("version") == 1, f"Evidence map version must be 1: {slug}")
    _require(data.get("paper") == slug, f"Evidence map paper does not match slug: {slug}")
    nodes = data.get("nodes")
    edges = data.get("edges")
    _require(isinstance(nodes, list) and nodes, f"Evidence map nodes must be a non-empty list: {slug}")
    _require(isinstance(edges, list) and edges, f"Evidence map edges must be a non-empty list: {slug}")
    viewer = data.get("viewer", {})
    _require(isinstance(viewer, dict), f"Evidence viewer must be an object: {slug}")
    if viewer:
        local_pdf = viewer.get("local_pdf")
        _require(isinstance(local_pdf, str) and local_pdf.strip() and not Path(local_pdf).is_absolute() and ".." not in Path(local_pdf).parts,
                 f"Evidence viewer local_pdf must stay inside the paper directory: {slug}")
        default_stage = viewer.get("default_stage", "first-pass")
        _require(default_stage in STAGES, f"Invalid evidence viewer default stage: {slug}")

    ids = set()
    for node in nodes:
        _require(isinstance(node, dict), f"Evidence node must be an object: {slug}")
        node_id = node.get("id")
        _require(isinstance(node_id, str) and node_id.strip(), f"Evidence node needs an id: {slug}")
        _require(node_id not in ids, f"Duplicate evidence node id: {node_id}")
        ids.add(node_id)
        kind = node.get("kind")
        _require(kind in NODE_KINDS, f"Invalid evidence node kind for {node_id}: {kind}")
        if kind == "note":
            _require(node.get("stage") in STAGES, f"Invalid note stage for {node_id}")
            _require(isinstance(node.get("anchor"), str) and node["anchor"].strip(), f"Note node needs anchor: {node_id}")
        elif kind == "pdf":
            _require(isinstance(node.get("href"), str) and node["href"].strip(), f"PDF node needs href: {node_id}")
            parsed = urlsplit(node["href"])
            if parsed.scheme or parsed.netloc:
                _http_url(node["href"], f"PDF href for {node_id}")
            else:
                _require(not parsed.path.startswith("/") and ".." not in Path(parsed.path).parts,
                         f"PDF href leaves paper directory: {node_id}")
            _require(isinstance(node.get("page"), int) and node["page"] > 0, f"PDF node needs positive page: {node_id}")
            if "quote" in node:
                _require(isinstance(node["quote"], str) and node["quote"].strip(), f"PDF quote must be a non-empty string: {node_id}")
            if "quotes" in node:
                _require(isinstance(node["quotes"], list) and node["quotes"], f"PDF quotes must be a non-empty list: {node_id}")
                _require(all(isinstance(quote, str) and quote.strip() for quote in node["quotes"]), f"PDF quotes must contain non-empty strings: {node_id}")
            if "regions" in node:
                _require(isinstance(node["regions"], list) and node["regions"], f"PDF regions must be a non-empty list: {node_id}")
                for region in node["regions"]:
                    _validate_region(region, node_id)
            anchors = node.get("anchors", [])
            _require(isinstance(anchors, list), f"PDF anchors must be a list: {node_id}")
            for anchor in anchors:
                _require(isinstance(anchor, dict) and anchor.get("stage") in STAGES and isinstance(anchor.get("anchor"), str) and anchor["anchor"].strip(),
                         f"Invalid PDF local anchor: {node_id}")
        else:
            _require(isinstance(node.get("repo"), str), f"Code node needs repo: {node_id}")
            _http_url(node["repo"], f"code repo for {node_id}")
            _require(node["repo"].rstrip("/").startswith("https://github.com/"), f"Code repo must be GitHub HTTPS: {node_id}")
            _require(isinstance(node.get("commit"), str) and SHA_RE.fullmatch(node["commit"]), f"Code node needs full commit SHA: {node_id}")
            path = node.get("path")
            _require(isinstance(path, str) and path.strip() and not path.startswith("/") and ".." not in Path(path).parts, f"Invalid code path: {node_id}")
            _require(isinstance(node.get("start"), int) and node["start"] > 0, f"Code node needs positive start line: {node_id}")
            _require(isinstance(node.get("end"), int) and node["end"] >= node["start"], f"Code node needs valid end line: {node_id}")
            if "stage" in node:
                _require(node["stage"] in STAGES and isinstance(node.get("anchor"), str) and node["anchor"].strip(), f"Invalid code local anchor: {node_id}")
            if "href" in node:
                expected = code_href(node)
                _require(node["href"] == expected, f"Code href does not match commit/path/lines: {node_id}")

    edge_ids = set()
    for index, edge in enumerate(edges, 1):
        _require(isinstance(edge, dict), f"Evidence edge must be an object: {slug}")
        edge_id = edge.get("id", f"edge-{index}")
        _require(isinstance(edge_id, str) and edge_id.strip(), f"Evidence edge needs an id: {slug}")
        _require(edge_id not in edge_ids, f"Duplicate evidence edge id: {edge_id}")
        edge_ids.add(edge_id)
        _require(edge.get("from") in ids and edge.get("to") in ids, f"Evidence edge references unknown node: {edge_id}")
        _require(edge.get("type") in RELATION_TYPES, f"Invalid evidence relation: {edge_id}")
        _require(edge.get("status") in STATUS_TYPES, f"Invalid evidence status: {edge_id}")
        if "region" in edge:
            _validate_region(edge["region"], edge_id)
    return data


def code_href(node):
    repo = node["repo"].rstrip("/")
    path = quote(node["path"], safe="/-._~")
    suffix = f"#L{node['start']}" if node["start"] == node["end"] else f"#L{node['start']}-L{node['end']}"
    return f"{repo}/blob/{node['commit']}/{path}{suffix}"


def _label(node):
    return html.escape(node.get("label", node["id"]))


def _local_href(node, slug, current_stage=None):
    stage = node.get("stage")
    anchor = node.get("anchor")
    if not stage or not anchor:
        return None
    prefix = "" if current_stage == stage else f"{stage}.html"
    return f"{prefix}#{quote(anchor, safe='-._~')}"


def _node_link(node, slug, current_stage=None):
    kind = node["kind"]
    if kind == "note":
        href = _local_href(node, slug, current_stage)
        text = f"笔记 · {node['stage']} · #{node['anchor']}"
        return f'<a class="evidence-link evidence-note" href="{html.escape(href, quote=True)}">{html.escape(text)}</a>'
    if kind == "pdf":
        href = node["href"]
        text = f"PDF · 第 {node['page']} 页"
        if node.get("figure"):
            text += f" · {node['figure']}"
        links = [f'<a class="evidence-link evidence-pdf" href="{html.escape(href, quote=True)}" target="_blank" rel="noopener">{html.escape(text)} ↗</a>']
        for anchor in node.get("anchors", []):
            local = _local_href(anchor | {"kind": "note", "stage": anchor["stage"], "anchor": anchor["anchor"]}, slug, current_stage)
            links.append(f'<a class="evidence-local" href="{html.escape(local, quote=True)}">页面 #{html.escape(anchor["anchor"])} ↗</a>')
        return " ".join(links)
    href = node.get("href") or code_href(node)
    text = f"代码 · {node['path']} · L{node['start']}–{node['end']}"
    links = [f'<a class="evidence-link evidence-code" href="{html.escape(href, quote=True)}" target="_blank" rel="noopener">{html.escape(text)} ↗</a>']
    local = _local_href(node, slug, current_stage)
    if local:
        links.append(f'<a class="evidence-local" href="{html.escape(local, quote=True)}">代码笔记定位 ↗</a>')
    return " ".join(links)


def render_panel(data, slug, current_stage=None, title="证据链"):
    nodes = {node["id"]: node for node in data["nodes"]}
    cards = []
    for index, edge in enumerate(data["edges"], 1):
        source = nodes[edge["from"]]
        target = nodes[edge["to"]]
        edge_id = html.escape(edge.get("id", f"edge-{index}"), quote=True)
        note = html.escape(edge.get("note", ""))
        cards.append(
            f'<article class="evidence-card" id="evidence-{edge_id}">'
            f'<div class="evidence-card-head"><strong>{_label(source)}</strong>'
            f'<span class="evidence-relation">{html.escape(edge["type"])}</span>'
            f'<strong>{_label(target)}</strong></div>'
            f'<div class="evidence-locations">{_node_link(source, slug, current_stage)}<span class="evidence-arrow">↔</span>{_node_link(target, slug, current_stage)}</div>'
            f'<div class="evidence-status">状态：<span class="evidence-status-{html.escape(edge["status"])}">{html.escape(edge["status"])}</span>{f"<span class=\"evidence-note-text\">{note}</span>" if note else ""}</div>'
            '</article>'
        )
    return f'<section class="evidence-panel" id="evidence-links"><div class="evidence-panel-heading"><h2>{html.escape(title)}</h2><span>{len(cards)} 条关联</span></div><p class="evidence-intro">从笔记观点跳到原文定位和固定版本源码，也可以沿页面锚点返回。</p>{"".join(cards)}</section>'
