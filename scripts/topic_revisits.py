"""Independent topic-revisit records, media gate and directory rendering.

A revisit references a paper; it is never another paper or a fourth stage.
"""
import html
import json
import re
import struct
import base64
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


class MediaPage(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids = set(); self.figures = {}; self.current = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'): self.ids.add(attrs['id'])
        if tag == 'figure':
            self.current = dict(attrs=attrs, images=[], links=[], caption=False, caption_text='', in_caption=False, zoom=False)
            self.figures[attrs.get('id')] = self.current
        if self.current is not None:
            if tag == 'img': self.current['images'].append(attrs)
            if tag == 'a': self.current['links'].append(attrs.get('href'))
            if tag == 'figcaption': self.current['caption'] = True; self.current['in_caption'] = True
            if tag == 'button' and 'zoom' in attrs.get('class', '').split(): self.current['zoom'] = True

    def handle_data(self, data):
        if self.current is not None and self.current['in_caption']: self.current['caption_text'] += data

    def handle_endtag(self, tag):
        if self.current is not None and tag == 'figcaption': self.current['in_caption'] = False
        if tag == 'figure': self.current = None


def revisit_path(ident):
    if not isinstance(ident, str) or not ID.fullmatch(ident):
        raise ValueError(f'Invalid topic revisit ID: {ident}')
    return f'revisits/{ident}.html'


def load_revisits(root, papers):
    """Validate persisted records before build/check; missing registry is compatible."""
    root = Path(root).resolve(); path = root / 'revisits.json'
    if not path.is_file(): return []
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('revisits'), list):
        raise ValueError('Invalid revisits.json registry')
    catalogue = {p['slug']: p for p in papers}; seen = set(); records = data['revisits']
    for r in records:
        ident = r.get('id'); expected = revisit_path(ident)
        if ident in seen or r.get('file') != expected or r.get('paper') not in catalogue:
            raise ValueError(f'Duplicate/mismatched topic revisit: {ident}')
        seen.add(ident); date.fromisoformat(r['date'])
        for key in ('title', 'sourceScope'):
            if not isinstance(r.get(key), str) or not r[key].strip(): raise ValueError(f'Missing revisit {key}: {ident}')
        target = (root / expected).resolve()
        if not target.is_relative_to(root) or not target.is_file(): raise ValueError(f'Missing topic page: {expected}')
        text = target.read_text(encoding='utf-8'); page = MediaPage(text)
        if '专题回看' not in text or '不是新论文' not in text: raise ValueError(f'Missing topic identity: {ident}')
        if r.get('anchor') not in page.ids: raise ValueError(f'Missing topic root anchor: {ident}')
        graphics = r.get('graphics')
        if not isinstance(graphics, list) or not graphics: raise ValueError(f'Missing topic evidence graphics: {ident}')
        for g in graphics:
            fid = g.get('figureId'); fig = page.figures.get(fid)
            if not fig or fig['attrs'].get('data-origin') != 'paper-crop' or fig['attrs'].get('data-visual-role') != 'evidence':
                raise ValueError(f'Missing original topic figure: {ident}/{fid}')
            if not fig['caption'] or not fig['zoom'] or len(fig['images']) != 1 or g.get('sourceUrl') not in fig['links'] or not isinstance(g.get('pdfPage'), int) or g.get('label', '') not in fig['caption_text']:
                raise ValueError(f'Untraceable topic figure: {ident}/{fid}')
            if f'data-for="{fid}"' not in text: raise ValueError(f'Missing topic figure analysis: {ident}/{fid}')
            for im in fig['images']:
                src = im.get('src', '')
                if not im.get('alt', '').strip(): raise ValueError(f'Missing topic image description: {ident}')
                if src.startswith('data:image/png;base64,'):
                    pixels = base64.b64decode(src.split(',', 1)[1], validate=True)
                elif not src or src.startswith(('/', 'http:', 'https:')): raise ValueError(f'Non-offline topic image: {ident}')
                else:
                    image = (target.parent / src).resolve()
                    if not image.is_relative_to(root) or not image.is_file(): raise ValueError(f'Missing topic PNG: {ident}/{src}')
                    pixels = image.read_bytes()
                if pixels[:8] != b'\x89PNG\r\n\x1a\n' or len(pixels) < 24 or min(struct.unpack('>II', pixels[16:24])) < 64:
                    raise ValueError(f'Invalid/tiny topic PNG: {ident}/{src}')
        rights = r.get('rightsReview', {})
        if not isinstance(rights.get('basis'), str) or not rights['basis'].strip(): raise ValueError(f'Missing topic rights review: {ident}')
        date.fromisoformat(rights['reviewedAt'])
        visual = r.get('visualReview', {})
        if not all(visual.get(k) is True for k in ('desktop', 'mobile', 'zoom')): raise ValueError(f'Incomplete topic visual review: {ident}')
        date.fromisoformat(visual['reviewedAt'])
    return records


def directory_body(papers, records):
    esc = html.escape; by_paper = {}
    for r in records: by_paper.setdefault(r['paper'], []).append(r)
    reviewed = len(by_paper); rows = []
    for p in sorted(papers, key=lambda p: (p['slug'] not in by_paper, p['name'].casefold())):
        items = sorted(by_paper.get(p['slug'], []), key=lambda r: r['date'], reverse=True)
        search = ' '.join([p['name'], p['title'], *[r['title'] for r in items]]).casefold()
        topics = ''.join(f'<li><time datetime="{r["date"]}">{r["date"]}</time> · <a href="{esc(r["file"], quote=True)}#{esc(r["anchor"], quote=True)}">{esc(r["title"])}</a></li>' for r in items)
        state = '已回看' if items else '暂无专题回看记录'
        rows.append(f'<article class="paper-card revisit-paper" data-revisit-state="{"reviewed" if items else "not-yet"}" data-revisit-search="{esc(search, quote=True)}"><div class="card-top"><h2><a href="papers/{p["slug"]}/index.html">{esc(p["name"])}</a></h2><span class="badge{ " neutral" if not items else ""}">{state}</span></div><p class="paper-title">{esc(p["title"])}</p>{"<ul>"+topics+"</ul>" if topics else "<p>已有论文阅读状态保持原样；此处仅表示尚无独立专题记录。</p>"}<p><a href="papers/{p["slug"]}/first-pass.html">原论文初读 →</a></p></article>')
    return f'''<header class="page-head"><div class="eyebrow">TOPIC REVISITS</div><h1>专题回看</h1><p>把已读论文按具体问题重新核对，独立记录主题、日期与来源。不是新论文，也不是新增阅读阶段。</p></header>
<div class="stats"><span><strong>{reviewed}</strong> 篇已有专题回看</span><span><strong>{len(records)}</strong> 次回看记录</span><span><strong>{len(papers)-reviewed}</strong> 篇暂无回看记录</span></div><p class="notice">“暂无回看记录”不等于没有读过。论文初读、写作精读和代码阅读仍在原页面；没有配额或欠账。</p>
<div class="toolbar"><label class="search"><input id="revisit-search" type="search" aria-label="搜索专题回看" placeholder="搜索论文、主题或关键词…" autocomplete="off"></label><select id="revisit-status" aria-label="回看状态"><option value="all">全部论文</option><option value="reviewed">已有专题回看</option><option value="not-yet">暂无回看记录</option></select><button id="revisit-reset" type="button">清除筛选</button></div><p id="revisit-count" role="status" aria-live="polite">{len(papers)} 篇论文</p><div id="revisit-list" class="paper-list">{''.join(rows)}</div><section id="revisit-empty" class="empty" hidden><h2>没有匹配的回看记录</h2><p>可更换关键词或回看状态。</p></section><noscript><p>全部论文及回看记录已列出；搜索和筛选需要 JavaScript。</p></noscript><script src="assets/revisits.js" defer></script>'''
