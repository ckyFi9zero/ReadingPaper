#!/usr/bin/env python3
"""Validate source-grounded YAML and render offline research maps.

The renderer returns pages without writes. The site builder performs the shared
all-destinations preflight before saving, preserving authored reading pages.
"""
import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

import yaml
from evidence import page_ids

PAGES = ('research-map.html', 'literature-tree.html', 'challenge-insight-tree.html')
STAGES = {'first-pass', 'deep-read', 'code'}
STATUSES = {'source-checked', 'inferred', 'unverified'}
KINDS = {'task': 1, 'pipeline': 2, 'module': 3, 'follow-up': 4}
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
LABELS = {'source-checked': '已核对现有笔记', 'inferred': '跨论文推断', 'unverified': '待核验',
          'provisional': '暂定', 'confirmed': '已确认', 'pending': '待检索'}
e = html.escape


class StrictLoader(yaml.SafeLoader):
    pass


def mapping(loader, node):
    result = {}
    for key_node, val_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f'Duplicate YAML key: {key}')
        result[key] = loader.construct_object(val_node)
    return result


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_yaml(path):
    try:
        data = yaml.load(path.read_text(encoding='utf-8'), Loader=StrictLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f'Invalid YAML: {path.name}: {exc}') from exc
    require(isinstance(data, dict) and data.get('version') == 1, f'Expected version 1 object: {path.name}')
    return data


def forbid_key(data, key):
    if isinstance(data, dict):
        require(key not in data, f'Field separation: {key} in wrong document')
        for value in data.values():
            forbid_key(value, key)
    elif isinstance(data, list):
        for value in data:
            forbid_key(value, key)


def load(root):
    root = Path(root)
    folder = root / 'research-map'
    literature = read_yaml(folder / 'literature-tree.yaml')
    challenges = read_yaml(folder / 'challenge-insight-tree.yaml')
    gate = read_yaml(folder / 'novelty-gate.yaml')
    facts = {}
    for path in sorted((folder / 'sources/paper-facts').glob('*.yaml')):
        fact = read_yaml(path)
        slug = fact.get('paper')
        require(slug == path.stem and slug not in facts, f'Duplicate/mismatched fact paper: {path.name}')
        facts[slug] = fact
    return dict(literature=literature, challenges=challenges, gate=gate, facts=facts)


def validate(data, root, papers, rendered=None):
    """Check all relationships and evidence before returning any generated output."""
    root = Path(root).resolve()
    catalogue = {p['slug']: p for p in papers}
    facts = data['facts']
    rendered = rendered or {}
    anchor_cache = {}

    def text(value, where):
        require(isinstance(value, str) and bool(value.strip()), f'Missing text: {where}')

    def strings(values, where):
        require(isinstance(values, list), f'Expected list: {where}')
        for value in values:
            text(value, where)

    def identifiers(items, where, seen):
        require(isinstance(items, list), f'Expected list: {where}')
        for item in items:
            require(isinstance(item, dict), f'Expected object: {where}')
            ident = item.get('id')
            require(isinstance(ident, str) and ID.fullmatch(ident), f'Invalid node ID: {ident}')
            require(ident not in seen, f'Duplicate node ID: {ident}')
            seen.add(ident)
            text(item.get('name', item.get('title')), ident)

    def evidence(values, where):
        require(isinstance(values, list) and values, f'Missing evidence: {where}')
        for ev in values:
            require(isinstance(ev, dict), f'Invalid evidence: {where}')
            slug, stage, anchor = ev.get('paper'), ev.get('stage'), ev.get('anchor')
            require(slug in catalogue and slug in facts, f'Unknown evidence paper: {slug}')
            require(stage in STAGES and stage in catalogue[slug].get('stages', {}), f'Unavailable evidence stage: {slug}/{stage}')
            require(ev.get('status') in STATUSES, f'Invalid evidence status: {where}')
            text(anchor, where)
            name = f'papers/{slug}/{stage}.html'
            if name not in anchor_cache:
                if name in rendered:
                    from evidence import _IDParser
                    parser = _IDParser(); parser.feed(rendered[name]); anchor_cache[name] = parser.ids
                else:
                    path = root / name
                    require(path.is_file(), f'Missing evidence page: {name}')
                    anchor_cache[name] = page_ids(path)
            require(anchor in anchor_cache[name], f'Missing HTML anchor: {name}#{anchor}')

    def sources(item):
        slugs = item.get('source_papers')
        require(isinstance(slugs, list) and slugs, f'Missing source papers: {item["id"]}')
        require(all(isinstance(s, str) and s in catalogue and s in facts for s in slugs), f'Unknown source paper: {item["id"]}')
        require(len(set(slugs)) == len(slugs), f'Duplicate source paper: {item["id"]}')
        evidence(item.get('evidence'), item['id'])
        require(set(slugs) <= {ev['paper'] for ev in item['evidence']}, f'Source paper without evidence: {item["id"]}')

    for document in [data['literature'], data['challenges'], *facts.values()]:
        forbid_key(document, 'novelty_gate_case')
    forbid_key(data['gate'], 'novelty_class')
    for slug, fact in facts.items():
        require(slug in catalogue, f'Unknown fact paper: {slug}')
        require(fact.get('scope') == catalogue[slug].get('category'), f'Fact scope mismatch: {slug}')
        require(fact.get('evidence_status') in STATUSES, f'Invalid fact evidence status: {slug}')
        assessment = fact.get('novelty_assessment', {})
        require(type(assessment.get('novelty_class')) is int and assessment['novelty_class'] in range(1, 5), f'Invalid novelty_class: {slug}')
        require(assessment.get('confidence') in {'provisional', 'confirmed'}, f'Invalid novelty confidence: {slug}')
        text(assessment.get('reason'), slug)
        for section in ('task', 'problem', 'pipeline'):
            require(isinstance(fact.get(section), dict), f'Missing fact section: {slug}/{section}')
            evidence(fact[section].get('evidence'), f'{slug}/{section}')
        for key in ('name', 'input', 'output'):
            text(fact['task'].get(key), f'{slug}/task/{key}')
        text(fact['problem'].get('failure_case'), f'{slug}/problem')
        identifiers(fact.get('modules'), f'{slug}/modules', set())
        require(fact['modules'], f'Missing modules: {slug}')
        for item in fact['modules']:
            text(item.get('motivation'), item['id']); evidence(item.get('evidence'), item['id'])
        require(isinstance(fact.get('limitations'), list), f'Missing limitations: {slug}')
        for item in fact['limitations']:
            text(item.get('text'), slug); evidence(item.get('evidence'), slug)

    all_ids = set()
    nodes = data['literature'].get('nodes')
    identifiers(nodes, 'literature nodes', all_ids)
    require(nodes, 'Empty literature tree')
    by_id = {n['id']: n for n in nodes}
    for n in nodes:
        require(n.get('kind') in KINDS, f'Invalid literature kind: {n["id"]}')
        require(type(n.get('novelty_class')) is int and n['novelty_class'] == KINDS[n['kind']], f'Invalid novelty_class for layer: {n["id"]}')
        require(n.get('confidence') in {'provisional', 'confirmed'}, f'Invalid novelty confidence: {n["id"]}')
        if n['confidence'] == 'confirmed':
            require(n.get('first_work_status') == 'verified', f'Confirmed novelty needs first-work verification: {n["id"]}')
            evidence(n.get('first_work_evidence'), n['id'])
        parent = n.get('parent')
        require(parent is None or parent in by_id, f'Unknown parent: {n["id"]}')
        sources(n)
        require(all(facts[s]['scope'] == 'in-field' for s in n['source_papers']), f'Out-of-field paper in literature tree: {n["id"]}')
    # Traverse first to diagnose cycles even when they also violate layer order.
    for n in nodes:
        seen = set(); current = n
        while current:
            require(current['id'] not in seen, f'Literature cycle: {n["id"]}')
            seen.add(current['id']); current = by_id.get(current.get('parent'))
    for n in nodes:
        parent = by_id.get(n.get('parent'))
        allowed = {'task': {None}, 'pipeline': {'task'}, 'module': {'pipeline'}, 'follow-up': {'module', 'pipeline'}}
        require((parent['kind'] if parent else None) in allowed[n['kind']], f'Invalid parent layer: {n["id"]}')
    expected = {s for s,p in catalogue.items() if p.get('category') == 'in-field'}
    represented = {s for n in nodes for s in n['source_papers']}
    require(expected <= represented and expected <= facts.keys(), f'Missing in-field coverage: {sorted(expected - (represented & facts.keys()))}')

    challenges = data['challenges'].get('challenges')
    identifiers(challenges, 'challenges', all_ids)
    require(challenges, 'Empty challenge tree')
    challenge_ids = {c['id'] for c in challenges}
    insight_sources = set()
    for c in challenges:
        require(c.get('status') in STATUSES, f'Invalid challenge status: {c["id"]}')
        strings(c.get('observable_failures'), c['id'])
        evidence(c.get('evidence'), c['id'])
        identifiers(c.get('insights'), c['id'], all_ids)
        require(c['insights'], f'Missing insights: {c["id"]}')
        for ins in c['insights']:
            require(ins.get('status') in STATUSES, f'Invalid insight status: {ins["id"]}')
            strings(ins.get('techniques'), ins['id']); sources(ins)
            insight_sources.update(ins['source_papers'])
    for slug,f in facts.items():
        strings(f.get('challenges'), slug)
        require(set(f['challenges']) <= challenge_ids, f'Unknown fact challenge: {slug}')
        require(f['pipeline'].get('id') in by_id or f['scope'] == 'out-of-field', f'Unknown fact pipeline: {slug}')
        require(f['scope'] == 'in-field' or slug in insight_sources, f'Unused external fact: {slug}')

    candidates = data['gate'].get('candidates')
    identifiers(candidates, 'candidates', all_ids)
    for c in candidates:
        text(c.get('failure_case'), c['id']); text(c.get('core_technical_challenge'), c['id'])
        evidence(c.get('evidence'), c['id'])
        require(set(c.get('challenge_ids', [])) <= challenge_ids, f'Unknown candidate challenge: {c["id"]}')
        g = c.get('gate', {}); case = g.get('novelty_gate_case')
        require(case == 'pending' or type(case) is int and case in range(1,5), f'Invalid novelty_gate_case: {c["id"]}')
        for key in ('same_task_evidence', 'related_domain_evidence', 'citation_graph_evidence'):
            require(isinstance(g.get(key), list), f'Missing gate evidence list: {key}')
        require(isinstance(c.get('candidate_pipelines'), list), f'Missing candidate pipelines: {c["id"]}')
        if case == 'pending':
            require(not c['candidate_pipelines'] and c.get('verdict') == 'needs-more-retrieval', 'Pending gate cannot select a pipeline')
        elif case in (1,2):
            require(not c['candidate_pipelines'] and c.get('verdict') == 'change-topic', 'Gate cases 1/2 must change topic')
        else:
            require(all(g[k] for k in ('same_task_evidence', 'related_domain_evidence', 'citation_graph_evidence')), 'Gate cases 3/4 need retrieval in all three evidence lists')
    return data


def evidence_links(values, catalogue):
    links = []
    for ev in values:
        slug = ev['paper']; href = f'papers/{slug}/{ev["stage"]}.html#{quote(ev["anchor"], safe="-._~")}'
        label = LABELS[ev['status']]
        original = ev.get('original_pdf_review_status', 'unregistered')
        origin = '原文核对已登记' if original == 'source-checked' else '原文核对未登记'
        links.append(f'<li><a href="{e(href, quote=True)}">{e(catalogue[slug]["name"])} · {e(ev["stage"])} · #{e(ev["anchor"])}</a> <small>{label} · {origin}</small></li>')
    return '<ul class="map-evidence">' + ''.join(links) + '</ul>'


LITERATURE_COLUMNS = {'task': 180, 'pipeline': 520, 'module': 900, 'follow-up': 900}
CHALLENGE_COLUMNS = {'challenge': 220, 'insight': 760}
GRAPH_COLORS = ['#176758', '#2f7180', '#8a6a2f', '#6d7d69', '#76538a', '#92713c', '#3b6875']


def _source_detail(slug, facts, catalogue):
    fact = facts[slug]
    evidence = []
    for item in (fact.get('task', {}).get('evidence', []) + fact.get('pipeline', {}).get('evidence', [])):
        evidence.append({
            'href': f'papers/{slug}/{item["stage"]}.html#{quote(item["anchor"], safe="-._~")}',
            'label': f'{item["stage"]} · #{item["anchor"]}',
            'status': LABELS.get(item.get('status'), item.get('status', '待核验')),
        })
    return {
        'slug': slug,
        'name': catalogue[slug]['name'],
        'year': catalogue[slug].get('year'),
        'href': f'papers/{slug}/index.html',
        'evidence': evidence,
    }


def _node_detail(node, facts, catalogue, *, challenge=None, insight=None):
    sources = [_source_detail(slug, facts, catalogue) for slug in node.get('source_papers', [])]
    detail = {
        'id': node['id'],
        'name': node.get('name', node.get('title', node['id'])),
        'kind': node.get('kind', 'insight'),
        'description': node.get('description', ''),
        'novelty_class': node.get('novelty_class'),
        'confidence': LABELS.get(node.get('confidence'), node.get('confidence', '')),
        'status': LABELS.get(node.get('status'), node.get('status', '')),
        'source_count': len(sources),
        'sources': sources,
        'parent': node.get('parent'),
        'techniques': node.get('techniques', []),
        'motivation': node.get('motivation', ''),
        'transfer_boundary': node.get('transfer_boundary', ''),
    }
    if challenge:
        detail.update({'description': challenge.get('description', ''),
                       'observable_failures': challenge.get('observable_failures', [])})
    if insight:
        detail.update({'description': insight.get('transfer_boundary', ''),
                       'techniques': insight.get('techniques', [])})
    return detail


def _filter_fields(source_papers, facts, catalogue, challenge_ids=()):
    tags = ' '.join(tag for slug in source_papers for tag in facts[slug].get('tags', []))
    weather = [word for word in ['雨', '雪', '雾', '尘'] if word in tags]
    routes = sorted({facts[slug].get('pipeline', {}).get('id', '') for slug in source_papers if facts[slug].get('pipeline')})
    return {
        'weather': weather,
        'route': [route for route in routes if route],
        'challenge': sorted(set(challenge_ids)),
        'search': ' '.join([tags] + [catalogue[slug]['name'] for slug in source_papers]).lower(),
    }


def build_literature_graph(data, facts, catalogue):
    nodes = data['literature']['nodes']
    children = {node['id']: [] for node in nodes}
    for node in nodes:
        if node.get('parent'):
            children[node['parent']].append(node['id'])
    by_id = {node['id']: node for node in nodes}
    grouped = {kind: [node for node in nodes if node['kind'] == kind] for kind in KINDS}
    positions = {}
    for kind, group in grouped.items():
        step = 94 if len(group) <= 1 else max(74, min(112, 520 / (len(group) - 1)))
        start = 72 if len(group) <= 5 else 42
        for index, node in enumerate(group):
            positions[node['id']] = {'x': LITERATURE_COLUMNS[kind], 'y': round(start + index * step)}
    edges = [{'from': node['parent'], 'to': node['id']} for node in nodes if node.get('parent')]
    details = {}
    for node in nodes:
        details[node['id']] = _node_detail(node, facts, catalogue)
        details[node['id']]['children'] = children[node['id']]
        details[node['id']]['filters'] = _filter_fields(node['source_papers'], facts, catalogue, [c for slug in node['source_papers'] for c in facts[slug].get('challenges', [])])
    height = max(380, max((pos['y'] for pos in positions.values()), default=72) + 100)
    return {'type': 'literature', 'width': 1160, 'height': height, 'nodes': nodes,
            'edges': edges, 'positions': positions, 'details': details, 'columns': LITERATURE_COLUMNS}


def build_challenge_graph(data, facts, catalogue):
    nodes, edges, positions, details = [], [], {}, {}
    challenges = data['challenges']['challenges']
    insight_index = 0
    challenge_count = len(challenges)
    for index, challenge in enumerate(challenges):
        cid = challenge['id']
        node = {'id': cid, 'kind': 'challenge', 'name': challenge['name'],
                'source_papers': list(dict.fromkeys(slug for insight in challenge['insights'] for slug in insight['source_papers'])),
                'status': challenge.get('status', 'inferred'), 'description': challenge.get('description', '')}
        nodes.append(node)
        positions[cid] = {'x': CHALLENGE_COLUMNS['challenge'], 'y': round(48 + index * max(92, min(126, 620 / max(1, challenge_count - 1))))}
        details[cid] = _node_detail(node, facts, catalogue, challenge=challenge)
        details[cid]['filters'] = _filter_fields(node['source_papers'], facts, catalogue, [cid])
        for insight in challenge['insights']:
            iid = insight['id']
            if iid not in positions:
                inode = {'id': iid, 'kind': 'insight', 'name': insight['name'], 'source_papers': insight['source_papers'],
                         'status': insight.get('status', 'inferred'), 'techniques': insight.get('techniques', []),
                         'transfer_boundary': insight.get('transfer_boundary', '')}
                nodes.append(inode)
                positions[iid] = {'x': CHALLENGE_COLUMNS['insight'], 'y': round(48 + insight_index * 86)}
                details[iid] = _node_detail(inode, facts, catalogue, challenge=challenge, insight=insight)
                details[iid]['filters'] = _filter_fields(inode['source_papers'], facts, catalogue, [cid])
                insight_index += 1
            edges.append({'from': cid, 'to': iid, 'color': GRAPH_COLORS[index % len(GRAPH_COLORS)]})
    height = max(430, max((pos['y'] for pos in positions.values()), default=48) + 92)
    return {'type': 'challenge', 'width': 1160, 'height': height, 'nodes': nodes,
            'edges': edges, 'positions': positions, 'details': details, 'columns': CHALLENGE_COLUMNS}


def render_svg_graph(graph, graph_type):
    node_width, node_height = 246, 62
    positions = graph['positions']
    paths = []
    for edge in graph['edges']:
        source = positions[edge['from']]; target = positions[edge['to']]
        x1, x2 = source['x'] + node_width, target['x']
        y1, y2 = source['y'] + node_height / 2, target['y'] + node_height / 2
        mid = (x1 + x2) / 2
        color = edge.get('color', '#a7bbb0')
        paths.append(f'<path class="map-edge" data-edge-from="{e(edge["from"])}" data-edge-to="{e(edge["to"])}" d="M{x1:.1f},{y1:.1f} C{mid:.1f},{y1:.1f} {mid:.1f},{y2:.1f} {x2:.1f},{y2:.1f}" style="--edge-color:{e(color)}"/>')
    nodes = []
    for node in graph['nodes']:
        pos = positions[node['id']]
        detail = graph['details'][node['id']]
        kind = node.get('kind', 'insight')
        novelty = node.get('novelty_class', '')
        confidence = node.get('confidence', node.get('status', 'inferred'))
        meta = f'{novelty} 类层级 · {LABELS.get(confidence, confidence)}' if graph_type == 'literature' else ('challenge' if kind == 'challenge' else f'insight · {detail["source_count"]} 个来源')
        label = detail['name']
        if len(label) > 19:
            label = label[:18] + '…'
        filters = detail.get('filters', {})
        search = ' '.join([detail['name'], detail.get('description', ''), ' '.join(detail.get('techniques', [])), filters.get('search', '')]).lower()
        nodes.append(f'''<g class="map-svg-node node-{e(kind)} {'node-confirmed' if confidence == 'confirmed' else 'node-provisional'}" data-map-item data-node-id="{e(node['id'])}" data-node-kind="{e(kind)}" data-source-count="{detail['source_count']}" data-search="{e(search, quote=True)}" data-weather="{e('|'.join(filters.get('weather', [])))}" data-route="{e('|'.join(filters.get('route', [])))}" data-challenge="{e('|'.join(filters.get('challenge', [])))}" tabindex="0" role="button" aria-label="{e(detail['name'])}">
  <rect x="{pos['x']}" y="{pos['y']}" width="{node_width}" height="{node_height}" rx="9"/>
  <text class="map-node-name" x="{pos['x'] + 14}" y="{pos['y'] + 25}">{e(label)}</text>
  <text class="map-node-meta" x="{pos['x'] + 14}" y="{pos['y'] + 46}">{e(meta)}</text>
</g>''')
    return f'<svg class="map-svg" role="img" aria-label="{e("Literature tree" if graph_type == "literature" else "Challenge–insight tree")}" viewBox="0 0 {graph["width"]} {graph["height"]}" preserveAspectRatio="xMinYMin meet"><g class="map-edges">{"".join(paths)}</g><g class="map-nodes">{"".join(nodes)}</g></svg>'


def render_node_detail(node, graph, catalogue):
    """Return JSON data consumed by the safe textContent-based inspector."""
    return graph['details']


def render(root, papers, shell, rendered=None):
    data = validate(load(root), root, papers, rendered)
    catalogue = {p['slug']:p for p in papers}; facts = data['facts']; nodes = data['literature']['nodes']
    challenges = data['challenges']['challenges']; by_id = {n['id']:n for n in nodes}
    routes = {f['pipeline']['id']:f['pipeline']['name'] for f in facts.values()}
    def attrs(sources, cid=None, words=''):
        fs = [facts[s] for s in sources]
        tags = ' '.join(t for f in fs for t in f.get('tags',[]))
        weather = [w for w in ['雨','雪','雾','尘'] if w in tags]
        cs = {cid} if cid else {c for f in fs for c in f['challenges']}
        terms = words+' '+tags+' '+' '.join(catalogue[s]['name'] for s in sources)
        return f'data-map-item data-weather="{e("|".join(weather))}" data-route="{e("|".join(sorted({f["pipeline"]["id"] for f in fs})))}" data-challenge="{e("|".join(sorted(cs)))}" data-search="{e(terms.lower(), quote=True)}"'
    def refs(n):
        links = ' · '.join(f'<a href="papers/{s}/index.html">{e(catalogue[s]["name"])} ({catalogue[s]["year"]})</a>' for s in sorted(n['source_papers'], key=lambda s:(catalogue[s]['year'],s)))
        return f'<p class="map-papers">{links}</p>'+evidence_links(n['evidence'], catalogue)
    def filters():
        def select(id,label,options):
            return f'<label>{label}<select id="{id}"><option value="">全部</option>'+''.join(f'<option value="{e(v,quote=True)}">{e(l)}</option>' for v,l in options)+'</select></label>'
        return '<div class="map-filters"><label>关键词<input id="map-search" type="search" placeholder="论文、模块或技术挑战"></label>'+select('map-weather','天气',[(w,w) for w in ['雨','雪','雾','尘']])+select('map-route','方法路线',list(routes.items()))+select('map-challenge','技术挑战',[(c['id'],c['name']) for c in challenges])+'<button id="map-reset" type="button">清除筛选</button></div><p id="map-results" role="status" aria-live="polite"></p><p id="map-empty" hidden>没有匹配的节点，请调整筛选条件。</p>'
    def literature(n):
        kids = [k for k in nodes if k.get('parent') == n['id']]
        sources = list(dict.fromkeys(n['source_papers'] + [s for k in kids for s in k['source_papers']]))
        content = refs(n)
        return f'<details class="map-branch" id="{n["id"]}" {attrs(sources,words=n["name"]+" "+n.get("description",""))} open><summary><strong>{e(n["name"])}</strong> <span class="map-badge">{n["novelty_class"]} 类层级 · {LABELS[n["confidence"]]}</span></summary><p>{e(n.get("description",""))}</p>{content}<div class="map-children">'+''.join(literature(k) for k in kids)+'</div></details>'
    litbody='<p class="notice">四类 novelty 表示贡献层级候选；当前仅核对已有阅读笔记，未完成首创和引文图检索。方法路线分组并不表示其中每篇论文都是 seminal work。</p><div class="map-tree">'+''.join(literature(n) for n in nodes if not n.get('parent'))+'</div>'
    challengebody='<p class="notice">challenge 与 insight 是跨论文归纳。领域外技术提供参考，迁移到恶劣天气去噪的有效性尚未验证。</p>'
    for c in challenges:
        sources=list(dict.fromkeys(s for ins in c['insights'] for s in ins['source_papers']))
        challengebody+=f'<section class="map-challenge" id="{c["id"]}" {attrs(sources,c["id"],c["name"])}><h2>{e(c["name"])}</h2><p>{e(c["description"])} · {LABELS[c["status"]]}</p><p>可能出现的现象：{e("；".join(c["observable_failures"]))}</p><details><summary>挑战的关联证据</summary>{evidence_links(c["evidence"],catalogue)}</details><div class="map-children">'
        for ins in c['insights']:
            challengebody+=f'<article class="map-insight" id="{ins["id"]}" {attrs(ins["source_papers"],c["id"],ins["name"]+" "+" ".join(ins["techniques"]))}><h3>{e(ins["name"])}</h3><p>{e(" · ".join(ins["techniques"]))}</p><p>{LABELS[ins["status"]]} · {e(ins["transfer_boundary"])}</p>{refs(ins)}</article>'
        challengebody+='</div></section>'
    factbody='<h2 id="paper-facts">逐篇事实与边界</h2><p>新抽取核对对象是现有笔记，不是重新核验 PDF。原文核对登记与本次笔记核对分别显示。</p>'
    for s,f in facts.items():
        scope='领域内' if f['scope']=='in-field' else '领域外技术来源'
        factbody+=f'<details class="map-fact" id="paper-{s}" {attrs([s],words=f["task"]["name"]+" "+f["problem"]["failure_case"])}><summary>{e(catalogue[s]["name"])} · {scope} · 贡献候选 {f["novelty_assessment"]["novelty_class"]} 类（暂定）</summary><p>任务：{e(f["task"]["name"])}。输入：{e(f["task"]["input"])}；输出：{e(f["task"]["output"])}</p><p>问题：{e(f["problem"]["failure_case"])}</p>{evidence_links(f["problem"]["evidence"],catalogue)}<p>方法：{e(f["pipeline"]["description"])}</p>{evidence_links(f["pipeline"]["evidence"],catalogue)}<p>模块：{e(f["modules"][0]["name"])}。动机：{e(f["modules"][0]["motivation"])}</p><p>分类依据：{e(f["novelty_assessment"]["reason"])}</p>'
        for limit in f['limitations']:
            factbody+=f'<p>边界：{e(limit["text"])}</p>{evidence_links(limit["evidence"],catalogue)}'
        factbody+='<p>关联挑战：'+' · '.join(f'<a href="challenge-insight-tree.html#{c}">{e(next(x["name"] for x in challenges if x["id"]==c))}</a>' for c in f['challenges'])+'</p></details>'
    gates='<section id="novelty-gate"><h2>候选课题与四种情况闸门</h2><p>情况 1：同任务已有好方案；情况 2：技术内核已在多个领域解决；情况 3：仅少数其他领域解决；情况 4：相关领域均缺少好方案。它们与上面的四类贡献标签不同。</p>'
    for c in data['gate']['candidates']:
        g=c['gate']; case=g['novelty_gate_case']; verdict={'needs-more-retrieval':'需更多检索','change-topic':'换题','go':'可进入方案评估'}.get(c['verdict'],c['verdict'])
        gates+=f'<article class="map-insight" id="{c["id"]}"><h3>{e(c["title"])}</h3><p>示例候选 · 尚未选为研究主线</p><p>输入 → 输出：{e(c["setting"]["input"])} → {e(c["setting"]["output"])}</p><p>待验证 failure case：{e(c["failure_case"])}</p><p>技术挑战假设：{e(c["core_technical_challenge"])}</p><p>四种情况判定：{LABELS.get(case, str(case))} · {e(verdict)}</p>{evidence_links(c["evidence"],catalogue)}<p>问题重要性、技术就绪度及候选 pipeline：尚未评估</p><ul>'+''.join(f'<li>{e(q)}</li>' for q in c.get('retrieval_required',[]))+'</ul></article>'
    gates+='</section>'
    intro=f'<p class="notice">{sum(f["scope"]=="in-field" for f in facts.values())} 篇领域内论文 · {sum(f["scope"]=="out-of-field" for f in facts.values())} 篇领域外技术来源 · {len(challenges)} 类技术挑战。点击树节点、论文或证据链接，回到已有阅读笔记。</p><div class="stage-grid"><a class="stage-card" href="literature-tree.html"><h2>Literature tree</h2><p>任务 → 方法路线 → 模块 / 后续工作</p></a><a class="stage-card" href="challenge-insight-tree.html"><h2>Challenge–insight tree</h2><p>技术挑战 → insight → 论文来源</p></a><a class="stage-card" href="#novelty-gate"><h2>Novelty gate</h2><p>具体 failure case 的四种情况判定</p></a></div>'
    literature_graph = build_literature_graph(data, facts, catalogue)
    challenge_graph = build_challenge_graph(data, facts, catalogue)

    def graph_section(graph, title, subtitle):
        details = json.dumps({'type': graph['type'], 'details': graph['details']}, ensure_ascii=False).replace('</', '<\\/')
        legend = ('<span class="map-legend-item legend-novelty-1">1 类 task</span><span class="map-legend-item legend-novelty-2">2 类 pipeline</span><span class="map-legend-item legend-novelty-3">3 类 module</span><span class="map-legend-item legend-novelty-4">4 类 follow-up</span>' if graph['type'] == 'literature' else '<span class="map-legend-item legend-challenge">challenge</span><span class="map-legend-item legend-insight">insight</span><span class="map-legend-item legend-external">领域外技术来源</span>')
        return f'''<section class="map-overview" data-graph-type="{graph['type']}">
  <div class="map-overview-head"><div><h2>{e(title)}</h2><p>{e(subtitle)}</p></div><div class="map-overview-toolbar"><button type="button" data-map-action="reset">重置视图</button><button type="button" data-map-action="expand">全部展开</button><button type="button" data-map-action="trunk">只看主干</button></div></div>
  <div class="map-legend">{legend}<span class="map-legend-item legend-provisional">虚线 = 暂定</span></div>
  <div class="map-graph-layout"><div class="map-graph" id="map-graph" aria-label="{e(title)}总览图">{render_svg_graph(graph, graph['type'])}</div><aside class="map-inspector" id="map-inspector" aria-live="polite"><p class="map-inspector-empty">点击图中的节点查看定义、关联论文和证据。</p></aside></div>
  <script id="map-details" type="application/json">{details}</script>
</section>'''
    outputs={}
    pages = [('research-map.html', '研究地图', intro+gates+filters()+factbody),
             ('literature-tree.html', 'Literature tree', graph_section(literature_graph, 'Literature tree 总览', 'task → pipeline / representation → module / follow-up') + filters() + litbody),
             ('challenge-insight-tree.html', 'Challenge–insight tree', graph_section(challenge_graph, 'Challenge–insight tree 总览', 'technical challenge → insight / technique → source papers') + filters() + challengebody)]
    for name,title,body in pages:
        head=f'<header class="page-head"><div class="eyebrow">RESEARCH MAP</div><h1>{e(title)}</h1><p><a href="research-map.html">地图入口</a> · <a href="literature-tree.html">任务与方法树</a> · <a href="challenge-insight-tree.html">技术挑战树</a></p></header>'
        page=shell(title,head+body,current='research-map')
        outputs[name]=page.replace('</head>','<link rel="stylesheet" href="assets/research-map.css"><script src="assets/research-map.js" defer></script></head>')
    return outputs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate only; do not write pages')
    args=parser.parse_args()
    import build_site
    papers=json.loads((build_site.ROOT/'papers.json').read_text())
    if args.check:
        validate(load(build_site.ROOT),build_site.ROOT,papers)
        print('Research map sources and evidence valid')
    else:
        outputs=render(build_site.ROOT,papers,build_site.shell)
        build_site.write_pages(outputs)
        print('Built 3 research map pages')


if __name__=='__main__':
    main()
