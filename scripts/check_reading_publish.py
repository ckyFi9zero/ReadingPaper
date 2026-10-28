#!/usr/bin/env python3
"""Fail closed on new first-pass reading publication quality declarations.

Checks structure and recorded human review, not scientific truth, visual clarity,
semantic relevance, copyright permission, or actual browser execution. A generic
schematic cannot satisfy the evidence-graphic requirement. The fixed legacy set
is a migration boundary, not a date-based exemption or an automatic endorsement.
"""
import argparse
import base64
import json
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
# The 39 pre-existing entries at 4817920, before the 2026-10-28 reading test.
# Do not append new papers here to avoid quality review; opt them into the schema.
LEGACY_SLUGS = frozenset('''3d-unoutdet-2025 adversenet-2025 rpsnownet-2026 smartrainnet-2023
umi-on-legs-2024 3d-outdet-2024 dror-2018 lior-snow-2020 lisnownet-2022 bevformer-2022
density-sensitive-completion-2024 sa-lpcc-2023 hd-fusion-2026 unidmb-2026 sld-ala-2026
lior-2021 scfnr-2026 dhe-net-2026 dsor-2021 electric-arc-2026 weathernet-2020
4denoisenet-2023 pmdf-2026 dcor-2024 triplemixer-2025 crfor-2023 sdor-2026
desnow-gnn-2026 removert-2020 ltdnet-2026 hcdg-2026 bev-devils-2024 pointnet-2017
pointnet-plus-plus-2017 wnnm-2014 implicit-point-to-voxel-lidar-imu-slam
post-refining-lidar-registration metric-semantic-mapping-2025 shape-enhanced-set-det-2026'''.split())
# Explicit user-approved repair on 2026-10-28, NOT a keyword classifier. Changing
# this recorded decision requires a new reviewed classification/graphic decision.
APPROVED_REPAIRS = {'beyondsnowflakes-2026': {'category': 'in-field', 'figures': {'fig-4', 'fig-7', 'fig-8'}}}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Node:
    def __init__(self, tag='', attrs=None, parent=None):
        self.tag, self.attrs, self.parent = tag, attrs or {}, parent
        self.children, self.text_parts = [], []

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def text(self):
        return ' '.join(self.text_parts + [c.text() for c in self.children]).strip()

    def visible_text(self):
        if self.concealed() or self.tag in {'script', 'style', 'template'}:
            return ''
        return ' '.join(self.text_parts + [c.visible_text() for c in self.children]).strip()

    def ancestor(self, tag):
        node = self.parent
        while node:
            if node.tag == tag:
                return node
            node = node.parent
        return None

    def concealed(self):
        node = self
        while node:
            style = re.sub(r'\s+', '', node.attrs.get('style', '').lower())
            if ('hidden' in node.attrs or 'display:none' in style or 'visibility:hidden' in style
                    or (node.tag == 'details' and 'open' not in node.attrs)):
                return True
            node = node.parent
        return False


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.current = self.root
        self.feed(text)
        self.nodes = list(self.root.walk())
        self.ids = {}
        for node in self.nodes:
            if node.attrs.get('id'):
                self.ids.setdefault(node.attrs['id'], []).append(node)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        node = self.current
        while node.parent:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        self.current.text_parts.append(data)


def nonempty(value, minimum=1):
    return isinstance(value, str) and len(value.strip()) >= minimum


def url(value):
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme in {'https', 'http'} and bool(parsed.netloc)


def dated(value):
    try:
        return isinstance(value, str) and date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def image_bytes(src, html_path, root):
    if not nonempty(src):
        raise ValueError('evidence image src is missing')
    if src.startswith('data:image/'):
        match = re.fullmatch(r'data:image/(png|jpeg|webp|gif);base64,([A-Za-z0-9+/=\s]+)', src)
        if not match:
            raise ValueError('evidence image must be a raster crop, not SVG/text/remote data')
        try:
            data = base64.b64decode(match[2], validate=True)
        except ValueError as exc:
            raise ValueError('invalid evidence image data') from exc
    else:
        parsed = urlsplit(src)
        if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith('/'):
            raise ValueError('evidence image must be offline data or a relative local file')
        path = (html_path.parent / unquote(parsed.path)).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('missing/outside evidence image: ' + src)
        data = path.read_bytes()
    # Basic file-signature/empty-placeholder checks; visual/source comparison is
    # deliberately still a required human review, not inferred from file size.
    if data.startswith(b'\x89PNG\r\n\x1a\n') and len(data) >= 24:
        width, height = int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big')
        if width < 100 or height < 50:
            raise ValueError('evidence crop is a placeholder/tiny image')
    elif not (data.startswith(b'\xff\xd8\xff') or data.startswith((b'GIF87a', b'GIF89a')) or (data[:4] == b'RIFF' and data[8:12] == b'WEBP')):
        raise ValueError('evidence image has no supported raster signature')
    if len(data) < 100:
        raise ValueError('evidence image is empty/truncated')


def check_paper(root, paper, rendered=None):
    slug = paper.get('slug', '<missing-slug>')
    if 'first-pass' not in paper.get('stages', {}):
        return []
    quality = paper.get('readingQuality')
    if quality is None and slug in LEGACY_SLUGS:
        return []
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(f'{slug}: {message}')
        return condition

    if not require(isinstance(quality, dict), 'new first-pass reading requires readingQuality; missing/date-backdated metadata is not an exemption'):
        return errors
    require(quality.get('version') == 1, 'readingQuality.version must be 1')
    classification = quality.get('classification', {})
    if not isinstance(classification, dict):
        classification = {}
    require(classification.get('confirmedCategory') == paper.get('category') and paper.get('category') in {'in-field', 'out-of-field', 'uncategorized'}, 'classification confirmedCategory must match category')
    require(nonempty(classification.get('rationale'), 30), 'classification requires a concrete human-reviewed rationale (not keyword classification)')
    require(nonempty(classification.get('source'), 20), 'classification requires user-scope/paper source evidence')
    require(dated(classification.get('reviewedAt')), 'classification requires reviewedAt date')
    approval = APPROVED_REPAIRS.get(slug)
    if approval:
        require(paper.get('category') == approval['category'], 'category conflicts with the explicitly user-approved repair (in-field)')
    rights = quality.get('rightsReview', {})
    if not isinstance(rights, dict):
        rights = {}
    require(nonempty(rights.get('basis'), 30) and dated(rights.get('reviewedAt')), 'rightsReview requires bounded excerpt/source review and date; this is not an automatic legal determination')
    visual = quality.get('visualReview', {})
    if not isinstance(visual, dict):
        visual = {}
    graphics = quality.get('graphics', {})
    if not isinstance(graphics, dict):
        graphics = {}
    zoom_reviewed = visual.get('zoom') is True or (graphics.get('status') == 'no-suitable-figures' and visual.get('zoom') == 'not-applicable')
    require(all(visual.get(k) is True for k in ('desktop', 'mobile')) and zoom_reviewed and dated(visual.get('reviewedAt')), 'visualReview must record completed desktop/mobile/zoom review, not planned checks; zoom=not-applicable is allowed only for a documented no-suitable-figures exception')
    html_path = root / 'papers' / slug / 'first-pass.html'
    key = f'papers/{slug}/first-pass.html'
    html = rendered.get(key) if rendered else None
    if html is None and html_path.is_file():
        html = html_path.read_text(encoding='utf-8')
    if not require(html is not None, 'missing rendered first-pass HTML for evidence review'):
        return errors
    doc = Document(html)
    actual_figures = [n for n in doc.nodes if n.tag == 'figure' and n.attrs.get('data-visual-role') == 'evidence']
    if graphics.get('status') == 'no-suitable-figures':
        exception = graphics.get('exception', {})
        if not isinstance(exception, dict):
            exception = {}
        require(not approval, 'approved figure repair cannot use a no-figure exception')
        require(not actual_figures and not graphics.get('items'), 'no-figure exception cannot claim included evidence figures')
        require(exception.get('fullTextReviewed') is True and exception.get('sourceHasRelevantFigures') is False, 'no-figure exception needs explicit full-text review and no-relevant-figure finding')
        require(nonempty(exception.get('reason'), 80) and nonempty(exception.get('sourceEvidence'), 30), 'no-figure exception requires documented source-specific reason and page/section evidence; unavailable figures are not a no-figure paper')
        require(url(exception.get('sourceUrl')) and nonempty(exception.get('reviewedBy')) and dated(exception.get('reviewedAt')), 'no-figure exception requires source URL, named reviewer and review date')
        return errors
    if not require(graphics.get('status') == 'included', 'graphics.status must be included or a documented no-suitable-figures exception'):
        return errors
    items = graphics.get('items', [])
    if not require(isinstance(items, list) and bool(items), 'at least one paper evidence crop is required; a schematic or source-only link does not count'):
        return errors
    figure_ids = [i.get('figureId') for i in items if isinstance(i, dict)]
    require(len(figure_ids) == len(items) and all(nonempty(i) for i in figure_ids) and len(set(figure_ids)) == len(items), 'graphic items need unique figureId values')
    require({n.attrs.get('id') for n in actual_figures} == set(figure_ids), 'evidence figures in HTML must exactly match reviewed graphic items')
    if approval:
        require(approval['figures'] <= set(figure_ids), 'approved repair requires the specifically reviewed Figure 4, 7 and 8 crops')
    for item in items:
        if not isinstance(item, dict):
            continue
        fid = item.get('figureId')
        nodes = doc.ids.get(fid, [])
        if not require(len(nodes) == 1 and nodes[0].tag == 'figure', f'{fid}: evidence figure must have one unique figure element'):
            continue
        figure = nodes[0]
        section = figure.ancestor('section')
        require(section is not None and not figure.concealed(), f'{fid}: evidence figure must be visible inside its relevant section')
        require(item.get('kind') in {'paper-crop', 'paper-figure-crop'} and figure.attrs.get('data-visual-role') == 'evidence' and figure.attrs.get('data-origin') == 'paper-crop', f'{fid}: an original schematic cannot substitute for a paper evidence crop')
        require(nonempty(item.get('label')) and isinstance(item.get('pdfPage'), int) and item['pdfPage'] > 0 and url(item.get('sourceUrl')), f'{fid}: require original figure label, PDF page and source URL')
        captions = [n for n in figure.walk() if n.tag == 'figcaption']
        caption = captions[0] if len(captions) == 1 else None
        require(caption is not None, f'{fid}: needs one figcaption')
        if caption:
            caption_text = caption.text()
            require(nonempty(item.get('label')) and item['label'] in caption_text and re.search(r'PDF\s*(?:p(?:age)?\.?\s*)?' + str(item.get('pdfPage')) + r'\b', caption_text, re.I), f'{fid}: caption must identify original figure label and PDF page')
            require(any(n.tag == 'a' and n.attrs.get('href') == item.get('sourceUrl') for n in caption.walk()), f'{fid}: caption must link to the reviewed source')
            require(any(term in caption_text for term in ('裁剪', 'crop', '原图')), f'{fid}: caption must disclose original/crop identity')
        imgs = [n for n in figure.walk() if n.tag == 'img']
        if require(bool(imgs), f'{fid}: evidence crop is missing an actual image'):
            for img in imgs:
                require(nonempty(img.attrs.get('alt'), 10), f'{fid}: needs a descriptive alt')
                try:
                    image_bytes(img.attrs.get('src', ''), html_path, root)
                except ValueError as exc:
                    errors.append(f'{slug}: {fid}: {exc}')
            src = imgs[0].attrs.get('src')
            zoom = any(n.tag == 'a' and n.attrs.get('href') == src for n in figure.walk())
            for button in figure.walk():
                target = doc.ids.get(button.attrs.get('data-open'), [])
                if len(target) == 1 and target[0].tag == 'dialog' and any(n.tag == 'img' and n.attrs.get('src') == src for n in target[0].walk()):
                    zoom = True
            require(zoom, f'{fid}: needs a source-size image link or matching zoom dialog')
        analysis_nodes = doc.ids.get(item.get('analysisId'), [])
        if require(len(analysis_nodes) == 1, f'{fid}: requires a unique adjacent analysisId'):
            analysis = analysis_nodes[0]
            require(analysis.ancestor('section') is section and analysis.attrs.get('data-for') == fid and not analysis.concealed(), f'{fid}: analysis must be expanded in the same section and explicitly tied to the figure')
            require(len(re.sub(r'\s', '', analysis.visible_text())) >= 80, f'{fid}: requires substantive adjacent analysis, not a source link/caption only')
    return errors


def check_reading_publish(root=ROOT, papers=None, rendered=None):
    root = Path(root).resolve()
    if papers is None:
        papers = json.loads((root / 'papers.json').read_text(encoding='utf-8'))
    errors = [e for paper in papers for e in check_paper(root, paper, rendered)]
    if errors:
        raise ValueError('Reading publication quality gate failed:\n' + '\n'.join(errors))
    return sum('first-pass' in p.get('stages', {}) and (p.get('slug') not in LEGACY_SLUGS or 'readingQuality' in p) for p in papers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    checked = check_reading_publish(args.root)
    print(f'PASS: {checked} regulated first-pass reading(s); legacy entries preserved without retroactive quality claims.')
