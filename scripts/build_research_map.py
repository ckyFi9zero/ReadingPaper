#!/usr/bin/env python3
"""Validate source-grounded YAML and render offline research maps.

The renderer returns pages without writes. The site builder performs the shared
all-destinations preflight before saving, preserving authored reading pages.
"""
import argparse
import html
import hashlib
import json
import re
from datetime import date
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
BASES = {'note-summary': '笔记转述', 'analyst-inference': '阅读者归纳', 'not-assessed': '尚未核验'}
EXPERIMENT_KINDS = {'comparison': '整体评估 / 方法对比', 'ablation': '模块对照', 'design-choice': '设计选择'}
PLAYBOOK_FIELDS = {
    'use_when': '何时考虑使用', 'mechanism': '机制：具体怎样做',
    'engineering_tricks': '实现细节与补丁', 'assumptions_cost': '前提与成本',
    'failure_boundary': '何时谨慎使用', 'reported_effect': '已记录的效果与评测条件',
    'evidence_scope': '这些证据能支持到哪里',
}
# Papers already mapped before the 2026-10-28 classification repair. A pending
# registration is not a mechanism to silently withdraw existing map coverage.
BASELINE_MAPPED = frozenset({
    '3d-outdet-2024', '3d-unoutdet-2025', '4denoisenet-2023', 'adversenet-2025',
    'crfor-2023', 'dcor-2024', 'desnow-gnn-2026', 'dror-2018', 'dsor-2021',
    'lior-2021', 'lior-snow-2020', 'lisnownet-2022', 'ltdnet-2026', 'pmdf-2026',
    'rpsnownet-2026', 'scfnr-2026', 'sdor-2026', 'triplemixer-2025', 'weathernet-2020',
})
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
    pending_path = folder / 'pending-papers.yaml'
    pending = read_yaml(pending_path) if pending_path.exists() else {'version': 1, 'papers': []}
    return dict(literature=literature, challenges=challenges, gate=gate, facts=facts, pending=pending)


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

    def claim(item, where, slug=None):
        require(isinstance(item, dict), f'Missing analysis claim: {where}')
        text(item.get('text'), where)
        basis = item.get('basis')
        expected = {'note-summary': 'source-checked', 'analyst-inference': 'inferred', 'not-assessed': 'unverified'}
        require(basis in expected and item.get('status') == expected[basis], f'Claim basis/status mismatch: {where}')
        values = item.get('evidence')
        if basis == 'not-assessed':
            require(values == [], f'Unassessed claim must not imply checked evidence: {where}')
        else:
            evidence(values, where)
            if slug:
                require(all(ev['paper'] == slug for ev in values), f'Analysis evidence must belong to paper: {where}')

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
        analysis = fact.get('analysis')
        if analysis is not None:
            require(isinstance(analysis, dict), f'Invalid analysis: {slug}')
            for key in ('previous_methods', 'technical_reason', 'insight', 'boundary'):
                claim(analysis.get(key), f'{slug}/{key}', slug)
            contributions = analysis.get('contributions')
            identifiers(contributions, f'{slug}/contributions', set())
            require(contributions, f'Missing contributions: {slug}')
            contribution_ids = {item['id'] for item in contributions}
            module_ids = {item['id'] for item in fact['modules']}
            for item in contributions:
                require(isinstance(item.get('module_ids'), list) and item['module_ids'] and set(item['module_ids']) <= module_ids,
                        f'Unknown contribution module: {slug}/{item["id"]}')
                for key in ('motivation', 'implementation', 'mechanism', 'advantage'):
                    claim(item.get(key), f'{slug}/{item["id"]}/{key}', slug)
            experiments = analysis.get('experiments')
            identifiers(experiments, f'{slug}/experiments', set())
            require(experiments, f'Missing experiment assessment: {slug}')
            for item in experiments:
                require(item.get('kind') in EXPERIMENT_KINDS, f'Invalid experiment kind: {slug}')
                require(item.get('assessment') in {'reported', 'not-reported-in-note', 'not-assessed'}, f'Invalid experiment assessment: {slug}')
                refs = item.get('contribution_ids')
                require(isinstance(refs, list) and set(refs) <= contribution_ids, f'Unknown experiment contribution: {slug}')
                claim(item.get('result'), f'{slug}/{item["id"]}/result', slug)
                claim(item.get('interpretation'), f'{slug}/{item["id"]}/interpretation', slug)
                if item['assessment'] != 'reported':
                    require(not refs, f'Unreported experiment cannot support contribution: {slug}')
                if item['assessment'] == 'not-assessed':
                    require(item['result']['status'] == 'unverified', f'Unassessed experiment needs unverified result: {slug}')

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
    pending_document = data.get('pending', {'version': 1, 'papers': []})
    require(isinstance(pending_document, dict) and pending_document.get('version') == 1,
            'Expected version 1 pending-paper registration')
    pending_items = pending_document.get('papers')
    require(isinstance(pending_items, list), 'Expected pending papers list')
    pending = set()
    for item in pending_items:
        require(isinstance(item, dict), 'Expected pending paper object')
        slug = item.get('paper')
        require(isinstance(slug, str) and slug in catalogue, f'Unknown pending paper: {slug}')
        require(slug not in pending, f'Duplicate pending paper: {slug}')
        require(slug in expected, f'Pending paper must be in-field: {slug}')
        require(slug not in BASELINE_MAPPED, f'Previously mapped paper cannot be pending: {slug}')
        require(slug not in represented and slug not in facts,
                f'Mapped paper cannot also be pending: {slug}')
        require(item.get('status') == 'pending', f'Invalid pending status: {slug}')
        text(item.get('reason'), f'{slug}/pending reason')
        registered = item.get('registered_at')
        require(isinstance(registered, str) and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', registered)),
                f'Invalid pending registration date: {slug}')
        try:
            date.fromisoformat(registered)
        except ValueError as exc:
            raise ValueError(f'Invalid pending registration date: {slug}') from exc
        pending.add(slug)
    mapped = represented & facts.keys()
    require(BASELINE_MAPPED <= mapped,
            f'Missing previously mapped coverage: {sorted(BASELINE_MAPPED - mapped)}')
    require(expected <= mapped | pending,
            f'Missing in-field coverage: {sorted(expected - (mapped | pending))}')

    challenges = data['challenges'].get('challenges')
    identifiers(challenges, 'challenges', all_ids)
    require(challenges, 'Empty challenge tree')
    challenge_ids = {c['id'] for c in challenges}
    insight_sources = set()
    for c in challenges:
        require(c.get('status') in STATUSES, f'Invalid challenge status: {c["id"]}')
        strings(c.get('observable_failures'), c['id'])
        evidence(c.get('evidence'), c['id'])
        claim(c.get('why_hard'), f'{c["id"]}/why_hard')
        identifiers(c.get('insights'), c['id'], all_ids)
        require(c['insights'], f'Missing insights: {c["id"]}')
        for ins in c['insights']:
            require(ins.get('status') in STATUSES, f'Invalid insight status: {ins["id"]}')
            strings(ins.get('techniques'), ins['id']); sources(ins)
            if 'principle' in ins:
                claim(ins['principle'], ins['id'])
                require({ev['paper'] for ev in ins['principle']['evidence']} <= set(ins['source_papers']),
                        f'Principle evidence outside insight sources: {ins["id"]}')
            book = ins.get('playbook')
            require(isinstance(book, dict), f'Missing playbook: {ins["id"]}')
            for key in PLAYBOOK_FIELDS:
                claim(book.get(key), f'{ins["id"]}/{key}')
                require({ev['paper'] for ev in book[key]['evidence']} <= set(ins['source_papers']),
                        f'Playbook evidence outside insight sources: {ins["id"]}/{key}')
            claim(ins.get('open_questions'), f'{ins["id"]}/open_questions')
            require(ins['open_questions']['basis'] == 'not-assessed',
                    f'Open questions must remain unverified: {ins["id"]}')
            locations = ins.get('source_locations')
            require(isinstance(locations, list) and locations, f'Missing source locations: {ins["id"]}')
            require({loc.get('paper') for loc in locations} == set(ins['source_papers']),
                    f'Source locations must cover insight sources: {ins["id"]}')
            for loc in locations:
                text(loc.get('location'), f'{ins["id"]}/source location')
                evidence(loc.get('evidence'), f'{ins["id"]}/source location')
                require(all(ev['paper'] == loc['paper'] for ev in loc['evidence']),
                        f'Source location evidence must belong to paper: {ins["id"]}')
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


def _evidence_detail(values, catalogue):
    return [{
        'href': f'papers/{ev["paper"]}/{ev["stage"]}.html#{quote(ev["anchor"], safe="-._~")}',
        'label': f'{catalogue[ev["paper"]]["name"]} · {ev["stage"]} · #{ev["anchor"]}',
        'status': LABELS[ev['status']],
    } for ev in values]


def _claim_detail(item, catalogue):
    return dict(item, evidence=_evidence_detail(item['evidence'], catalogue), basis_label=BASES[item['basis']])


def _source_detail(slug, facts, catalogue, values=None):
    fact = facts[slug]
    evidence = _evidence_detail(values if values is not None else fact['pipeline']['evidence'], catalogue)
    analysis = fact.get('analysis')
    return {
        'slug': slug,
        'name': catalogue[slug]['name'],
        'year': catalogue[slug].get('year'),
        'href': f'papers/{slug}/index.html',
        'analysis_href': f'research-map.html#paper-{slug}',
        'scope': '领域内' if fact['scope'] == 'in-field' else '领域外来源 · 天气迁移未验证',
        'chain': ([{'label': '失败现象', 'text': fact['problem']['failure_case'], 'basis_label': '笔记转述',
                    'evidence': _evidence_detail(fact['problem']['evidence'], catalogue)}] +
                  [dict(_claim_detail(analysis[key], catalogue), label=label) for key, label in
                   [('technical_reason', '技术原因'), ('insight', '通用 insight')]]) if analysis else [],
        'evidence': evidence,
    }


def _node_detail(node, facts, catalogue, *, challenge=None, insight=None):
    values = (insight or challenge or node).get('evidence', [])
    sources = [_source_detail(slug, facts, catalogue, [ev for ev in values if ev['paper'] == slug]) for slug in node.get('source_papers', [])]
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
        'evidence': _evidence_detail(values, catalogue),
    }
    if challenge:
        detail.update({'description': challenge.get('description', ''),
                       'why_hard': _claim_detail(challenge['why_hard'], catalogue),
                       'observable_failures': challenge.get('observable_failures', [])})
    if insight:
        detail.update({'description': insight.get('transfer_boundary', ''),
                       'techniques': insight.get('techniques', []),
                       'principle': _claim_detail(insight['principle'], catalogue) if 'principle' in insight else None,
                       'playbook': [dict(_claim_detail(insight['playbook'][key], catalogue), label=label)
                                    for key, label in PLAYBOOK_FIELDS.items()],
                       'open_questions': _claim_detail(insight['open_questions'], catalogue),
                       'source_locations': [{'name': catalogue[loc['paper']]['name'], 'location': loc['location'],
                                             'original_href': ('https://doi.org/' + quote(catalogue[loc['paper']]['doi'], safe='/')
                                                               if catalogue[loc['paper']].get('doi') else None),
                                             'evidence': _evidence_detail(loc['evidence'], catalogue)}
                                            for loc in insight['source_locations']]})
    return detail


def _filter_fields(source_papers, facts, catalogue, challenge_ids=()):
    tags = ' '.join(tag for slug in source_papers for tag in facts[slug].get('tags', []))
    weather = [word for word in ['雨', '雪', '雾', '尘'] if word in tags]
    routes = sorted({facts[slug].get('pipeline', {}).get('id', '') for slug in source_papers if facts[slug].get('pipeline')})
    return {
        'weather': weather,
        'route': [route for route in routes if route],
        'challenge': sorted(set(challenge_ids)),
        'search': ' '.join([tags] + [catalogue[slug]['name'] + ' ' + analysis_search(facts[slug]) for slug in source_papers]).lower(),
    }


def build_literature_graph(data, facts, catalogue):
    nodes = data['literature']['nodes']
    children = {node['id']: [] for node in nodes}
    for node in nodes:
        if node.get('parent'):
            children[node['parent']].append(node['id'])
    by_id = {node['id']: node for node in nodes}
    positions = {}
    # Reserve vertical space by subtree, keeping module/follow-up siblings distinct.
    cursor = 48
    def place(ident):
        nonlocal cursor
        node = by_id[ident]
        if node['kind'] == 'module' and children[ident]:
            y = cursor
            cursor += 92
            for child in children[ident]:
                place(child)
        elif children[ident]:
            ys = [place(child) for child in children[ident]]
            y = (ys[0] + ys[-1]) / 2
        else:
            y = cursor
            cursor += 92
        positions[ident] = {'x': LITERATURE_COLUMNS[node['kind']], 'y': round(y)}
        return positions[ident]['y']
    for node in nodes:
        if not node.get('parent'):
            place(node['id'])
            cursor += 30
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
        details[cid]['filters']['search'] = (challenge['why_hard']['text'] + ' ' +
                                            ' '.join(catalogue[s]['name'] for s in node['source_papers'])).lower()
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
                details[iid]['filters']['search'] = (' '.join(catalogue[s]['name'] for s in insight['source_papers']) +
                                                   ' ' + playbook_search(insight)).lower()
                insight_index += 1
            edges.append({'from': cid, 'to': iid, 'color': GRAPH_COLORS[index % len(GRAPH_COLORS)]})
    height = max(430, max((pos['y'] for pos in positions.values()), default=48) + 92)
    return {'type': 'challenge', 'width': 1160, 'height': height, 'nodes': nodes,
            'edges': edges, 'positions': positions, 'details': details, 'columns': CHALLENGE_COLUMNS}


def render_tree_graph(graph, graph_type):
    """Render accessible nodes; JavaScript enhances the list into a mind map."""
    by_id = {node['id']: node for node in graph['nodes']}
    children = {ident: [] for ident in by_id}
    targets = set()
    for edge in graph['edges']:
        children[edge['from']].append(edge)
        targets.add(edge['to'])

    def branch(ident, edge=None, path=''):
        node = by_id[ident]
        detail = graph['details'][ident]
        kind = node.get('kind', 'insight')
        confidence = node.get('confidence', node.get('status', 'inferred'))
        meta = (f'{node.get("novelty_class", "")} 类层级 · {LABELS.get(confidence, confidence)}'
                if graph_type == 'literature' else
                ('技术挑战' if kind == 'challenge' else f'insight · {detail["source_count"]} 个来源'))
        short_label = detail["name"].split(" · ", 1)[0]
        filters = detail.get('filters', {})
        search = ' '.join([detail['name'], detail.get('description', ''),
                           ' '.join(detail.get('techniques', [])), filters.get('search', '')]).lower()
        edge_attrs = (f' data-edge-from="{e(edge["from"])}" data-edge-to="{e(ident)}"'
                      if edge else '')
        branch_id = f'graph-children-{path}{ident}'
        toggle = (f'<button type="button" class="map-branch-toggle" data-toggle-branch aria-expanded="true" '
                  f'aria-controls="{e(branch_id)}" aria-label="收起 {e(detail["name"])} 的分支">−</button>'
                  if children[ident] else '')
        nested = (f'<ul class="map-node-children" id="{e(branch_id)}">' +
                  ''.join(branch(item['to'], item, f'{path}{ident}-') for item in children[ident]) + '</ul>'
                  if children[ident] else '')
        return f'''<li class="map-tree-item{' map-edge' if edge else ''}"{edge_attrs}>
<div class="map-node-row"><button type="button" class="map-tree-node node-{e(kind)} {'node-confirmed' if confidence == 'confirmed' else 'node-provisional'}" data-map-item data-node-id="{e(ident)}" data-node-kind="{e(kind)}" data-source-count="{detail['source_count']}" data-search="{e(search, quote=True)}" data-weather="{e('|'.join(filters.get('weather', [])))}" data-route="{e('|'.join(filters.get('route', [])))}" data-challenge="{e('|'.join(filters.get('challenge', [])))}" aria-expanded="false" aria-controls="map-inspector" aria-label="{e(detail['name'])}" title="{e(detail['name'])}"><span class="map-node-name">{e(short_label)}</span><span class="map-node-full">{e(detail['name'])}</span><span class="map-node-meta">{e(meta)}</span></button>{toggle}</div>{nested}</li>'''

    return '<div class="map-stage"><svg class="map-connectors" aria-hidden="true"></svg><ul class="map-flow-tree">' + ''.join(branch(ident) for ident in by_id if ident not in targets) + '</ul></div>'


def render_node_detail(node, graph, catalogue):
    """Return one node's data; the inspector escapes its HTML representation."""
    return graph['details'][node['id']]


def analysis_search(fact):
    """Only index claim text, not evidence paths or machine labels."""
    def collect(value):
        if isinstance(value, dict):
            return [value['text']] if 'text' in value else [s for k, v in value.items() if k != 'evidence' for s in collect(v)]
        if isinstance(value, list):
            return [s for v in value for s in collect(v)]
        return []
    return ' '.join(collect(fact.get('analysis', {})))


def playbook_search(insight):
    return ' '.join([insight['principle']['text']] +
                    [claim['text'] for claim in insight['playbook'].values()] +
                    [loc['location'] for loc in insight['source_locations']]).lower()


def render_playbook(insight, catalogue):
    body = ''.join(render_claim(insight['playbook'][key], catalogue, label)
                   for key, label in PLAYBOOK_FIELDS.items())
    body += render_claim(insight['open_questions'], catalogue, '仍待核验')
    body += '<h4>论文原文定位（沿用笔记登记）</h4><ul class="weapon-locations">'
    for loc in insight['source_locations']:
        paper = catalogue[loc['paper']]
        original = f' · <a href="https://doi.org/{e(quote(paper["doi"], safe="/"))}">原论文入口</a>' if paper.get('doi') else ''
        body += f'<li><strong>{e(paper["name"])}</strong>：{e(loc["location"])}{original}{evidence_links(loc["evidence"], catalogue)}</li>'
    return body + '</ul>'


def render_claim(item, catalogue, label=None):
    heading = f'<strong>{e(label)}</strong>' if label else ''
    status = BASES[item['basis']]
    return f'<div class="analysis-claim claim-{e(item["status"])}">{heading}<p>{e(item["text"])}</p><span class="analysis-basis">{status}</span>{evidence_links(item["evidence"], catalogue) if item["evidence"] else ""}</div>'


def render_paper_analysis(slug, fact, catalogue):
    analysis = fact.get('analysis')
    if not analysis:
        return '<p class="map-transfer">本篇尚未按模板补充因果解析。</p>'
    task = fact['task']
    contribution_names = '；'.join(item['name'] for item in analysis['contributions'])
    # This is a reader's synthesis, never a reconstruction of the author's abstract.
    abstract = f'<p>任务：{e(task["name"])}；失败现象：{e(fact["problem"]["failure_case"])}</p>'
    abstract += render_claim(analysis['insight'], catalogue, '核心思路')
    abstract += f'<p>本轮整理的技术贡献：{e(contribution_names)}。实验结果与支持边界见 Experiments 分支。</p>'
    intro = render_claim(analysis['previous_methods'], catalogue, '前人怎么做')
    intro += f'<div class="analysis-claim"><strong>失败现象</strong><p>{e(fact["problem"]["failure_case"])}</p>{evidence_links(fact["problem"]["evidence"], catalogue)}</div>'
    intro += render_claim(analysis['technical_reason'], catalogue, '技术原因')
    intro += render_claim(analysis['insight'], catalogue, '可复用的 insight')
    method = f'<div class="analysis-io"><p><strong>输入：</strong>{e(task["input"])}</p><p><strong>输出：</strong>{e(task["output"])}</p></div>'
    method += '<p class="analysis-caption">以下拆解本轮整理的主要贡献，不代表已经穷尽论文所有模块。</p>'
    for item in analysis['contributions']:
        method += f'<article class="analysis-contribution" id="analysis-{slug}-{item["id"]}"><h4>{e(item["name"])}</h4>'
        for key, label in [('motivation', '为什么需要它'), ('implementation', '具体做法'), ('mechanism', '为什么可能起作用'), ('advantage', '预期优势')]:
            method += render_claim(item[key], catalogue, label)
        method += '</article>'
    experiments = '<p class="analysis-caption">整体方法对比不能单独证明某个模块的作用；下列“关联贡献”是阅读者的证据映射。</p>'
    contributions = {item['id']: item['name'] for item in analysis['contributions']}
    for item in analysis['experiments']:
        assessment = {'reported': '笔记已记录', 'not-reported-in-note': '笔记未记录独立验证', 'not-assessed': '待核验'}[item['assessment']]
        experiments += f'<article class="analysis-experiment"><h4>{e(item["name"])}</h4><p class="analysis-caption">{EXPERIMENT_KINDS[item["kind"]]} · {assessment}</p>'
        experiments += render_claim(item['result'], catalogue, '实验记录') + render_claim(item['interpretation'], catalogue, '能支持到哪里')
        if item['contribution_ids']:
            experiments += '<p>关联贡献：' + ' · '.join(f'<a href="#analysis-{slug}-{ident}">{e(contributions[ident])}</a>' for ident in item['contribution_ids']) + '</p>'
        experiments += '</article>'
    limits = render_claim(analysis['boundary'], catalogue, '当前适用边界')
    for item in fact['limitations']:
        limits += f'<p>{e(item["text"])}</p>{evidence_links(item["evidence"], catalogue)}'
    branches = [('abstract', 'Abstract · 速览', task['name'], abstract),
                ('introduction', 'Introduction · 问题与思路', fact['problem']['failure_case'], intro),
                ('method', 'Method · 技术实现', contribution_names, method),
                ('experiments', 'Experiments · 贡献与证据', f'{len(analysis["experiments"])} 组记录 · 分开看整体效果与模块证据', experiments),
                ('limitation', 'Limitation · 边界', analysis['boundary']['text'], limits)]
    tree = '<div class="analysis-toolbar"><button type="button" data-analysis-action="expand">展开五个分支</button><button type="button" data-analysis-action="collapse">收起五个分支</button></div><div class="paper-analysis-tree"><div class="analysis-root">论文解析树</div><div class="analysis-branches">'
    for key, title, hint, body in branches:
        tree += f'<details class="analysis-branch branch-{key}" id="analysis-{slug}-{key}"><summary>{title}<span class="analysis-summary">{e(hint)}</span></summary>{body}</details>'
    return tree + '</div></div>'


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
        terms = words+' '+tags+' '+' '.join(catalogue[s]['name']+' '+analysis_search(facts[s]) for s in sources)
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
        challengebody+=f'<section class="map-challenge" id="{c["id"]}" {attrs(sources,c["id"],c["name"])}><h2>{e(c["name"])}</h2><p>{e(c["description"])} · {LABELS[c["status"]]}</p>{render_claim(c["why_hard"], catalogue, "为什么难")}<p>可能出现的现象：{e("；".join(c["observable_failures"]))}</p><details><summary>挑战的关联证据</summary>{evidence_links(c["evidence"],catalogue)}</details><div class="map-children">'
        for ins in c['insights']:
            principle = render_claim(ins['principle'], catalogue, '可复用的技术认识') if 'principle' in ins else ''
            analyses = ' · '.join(f'<a href="research-map.html#paper-{s}">{e(catalogue[s]["name"])} 解析</a>' for s in ins['source_papers'])
            challengebody+=f'<article class="map-insight" id="{ins["id"]}" {attrs(ins["source_papers"],c["id"],ins["name"]+" "+" ".join(ins["techniques"])+" "+playbook_search(ins))}><h3>{e(ins["name"])}</h3>{principle}<p>检索词：{e(" · ".join(ins["techniques"]))}</p><details class="weapon-playbook"><summary>使用卡：机制、补丁、代价与证据</summary>{render_playbook(ins, catalogue)}</details>{refs(ins)}<p>{analyses}</p></article>'
        challengebody+='</div></section>'
    factbody='<h2 id="paper-facts">单篇论文解析树</h2><p>按模板分为 Abstract、Introduction、Method、Experiments、Limitation 五个分支。速览由现有笔记重组，不表示复原作者的摘要写法；本次核对对象是已有笔记。</p><p class="analysis-key"><span>笔记转述：已核对现有阅读页</span><span>阅读者归纳：解释与证据映射，未经独立验证</span><span>尚未核验：明确保留空缺</span></p>'
    for s,f in sorted(facts.items(), key=lambda pair: (pair[0] != 'dror-2018', pair[1]['scope'] != 'in-field', pair[0])):
        scope='领域内' if f['scope']=='in-field' else '领域外技术来源'
        factbody+=f'<details class="map-fact" id="paper-{s}" {"open" if s == "dror-2018" else ""} {attrs([s],words=f["task"]["name"]+" "+f["problem"]["failure_case"])}><summary>{e(catalogue[s]["name"])} · {scope} · 贡献候选 {f["novelty_assessment"]["novelty_class"]} 类（暂定）</summary><p><a href="papers/{s}/index.html">打开论文阅读页</a> · <a href="papers/{s}/first-pass.html">打开初读</a></p><p class="analysis-caption">分类依据：{e(f["novelty_assessment"]["reason"])}</p>{render_paper_analysis(s,f,catalogue)}'
        positions = [n for n in nodes if s in n['source_papers']]
        factbody += '<p>方法树位置：' + (' · '.join(f'<a href="literature-tree.html#{n["id"]}">{e(n["name"])}</a>' for n in positions) if positions else '领域外技术来源，不并入领域内方法树') + '</p>'
        factbody+='<p>关联挑战：'+' · '.join(f'<a href="challenge-insight-tree.html#{c}">{e(next(x["name"] for x in challenges if x["id"]==c))}</a>' for c in f['challenges'])+'</p></details>'
    gates='<section id="novelty-gate"><h2>候选课题与四种情况闸门</h2><p>情况 1：同任务已有好方案；情况 2：技术内核已在多个领域解决；情况 3：仅少数其他领域解决；情况 4：相关领域均缺少好方案。它们与上面的四类贡献标签不同。</p>'
    for c in data['gate']['candidates']:
        g=c['gate']; case=g['novelty_gate_case']; verdict={'needs-more-retrieval':'需更多检索','change-topic':'换题','go':'可进入方案评估'}.get(c['verdict'],c['verdict'])
        gates+=f'<article class="map-insight" id="{c["id"]}"><h3>{e(c["title"])}</h3><p>示例候选 · 尚未选为研究主线</p><p>输入 → 输出：{e(c["setting"]["input"])} → {e(c["setting"]["output"])}</p><p>待验证 failure case：{e(c["failure_case"])}</p><p>技术挑战假设：{e(c["core_technical_challenge"])}</p><p>四种情况判定：{LABELS.get(case, str(case))} · {e(verdict)}</p>{evidence_links(c["evidence"],catalogue)}<p>问题重要性、技术就绪度及候选 pipeline：尚未评估</p><ul>'+''.join(f'<li>{e(q)}</li>' for q in c.get('retrieval_required',[]))+'</ul></article>'
    gates+='</section>'
    intro=f'<p class="notice">{sum(f["scope"]=="in-field" for f in facts.values())} 篇领域内论文 · {sum(f["scope"]=="out-of-field" for f in facts.values())} 篇领域外技术来源 · {len(challenges)} 类技术挑战。单篇解析为两棵跨论文研究树提供证据。</p><div class="stage-grid"><a class="stage-card" href="literature-tree.html"><h2>Literature tree</h2><p>任务 → 方法路线 → 模块 / 后续工作</p></a><a class="stage-card" href="challenge-insight-tree.html"><h2>Challenge–insight tree</h2><p>技术挑战 → insight → 论文来源</p></a><a class="stage-card" href="#paper-facts"><h2>单篇论文解析树</h2><p>失败原因 → insight → 实现 → 实验与边界</p></a><a class="stage-card" href="#novelty-gate"><h2>Novelty gate</h2><p>具体 failure case 的四种情况判定</p></a></div><p>先看示例：<a href="#paper-dror-2018">DROR</a> · <a href="#paper-lisnownet-2022">LiSnowNet</a> · <a href="#paper-4denoisenet-2023">4DenoiseNet</a> · <a href="#paper-pointnet-plus-plus-2017">PointNet++</a></p>'
    pending_items = data.get('pending', {}).get('papers', [])
    pending_notice = ''
    if pending_items:
        pending_notice = (f'<aside class="notice map-pending" id="map-pending"><h2>地图待整理 · {len(pending_items)} 篇领域内论文</h2>'
                          '<p>这些论文已在论文库分类，但尚未建立跨论文事实层和两棵树的关联；不计入本地图的已整理来源数量。</p><ul>')
        for item in pending_items:
            slug = item['paper']
            pending_notice += (f'<li><a href="papers/{slug}/index.html">{e(catalogue[slug]["name"])}</a>：'
                               f'{e(item["reason"])} <small>登记：{e(item["registered_at"])}</small></li>')
        pending_notice += '</ul></aside>'
    intro += pending_notice
    literature_graph = build_literature_graph(data, facts, catalogue)
    challenge_graph = build_challenge_graph(data, facts, catalogue)

    def graph_section(graph, title, subtitle):
        details = json.dumps({'type': graph['type'], 'details': graph['details']}, ensure_ascii=False).replace('</', '<\\/')
        legend = ('<span class="map-legend-item legend-novelty-1">1 类 task</span><span class="map-legend-item legend-novelty-2">2 类 pipeline</span><span class="map-legend-item legend-novelty-3">3 类 module</span><span class="map-legend-item legend-novelty-4">4 类 follow-up</span>' if graph['type'] == 'literature' else '<span class="map-legend-item legend-challenge">challenge</span><span class="map-legend-item legend-insight">insight</span><span class="map-legend-item legend-external">领域外技术来源</span>')
        return f'''<section class="map-overview" data-graph-type="{graph['type']}">
  <div class="map-overview-head"><div><h2>{e(title)}</h2><p>{e(subtitle)}</p></div><div class="map-overview-toolbar"><button type="button" data-map-action="reset">重置视图</button><button type="button" data-map-action="expand">全部展开</button><button type="button" data-map-action="trunk">只看主干</button></div></div>
  <div class="map-canvas-toolbar" aria-label="脑图视图控制"><button type="button" data-canvas-action="out" aria-label="缩小脑图">−</button><output id="map-zoom" aria-live="polite">100%</output><button type="button" data-canvas-action="in" aria-label="放大脑图">＋</button><button type="button" data-canvas-action="fit">适应窗口</button><button type="button" data-canvas-action="actual">100%</button><button type="button" data-canvas-action="view" aria-pressed="false">列表阅读</button></div>
  <p class="map-layout-hint" id="map-canvas-help">拖动画布平移 · Ctrl / ⌘ + 滚轮缩放 · 方向键平移，Home 适应窗口。点节点看完整说明，点 ＋/− 展开分支。最低 85% 保持可读，大树也可切换列表完整阅读。</p>
  <div class="map-legend">{legend}<span class="map-legend-item legend-provisional">虚线 = 暂定</span></div>
  <div class="map-graph-layout"><div class="map-graph" id="map-graph" tabindex="0" aria-label="{e(title)}脑图画布" aria-describedby="map-canvas-help">{render_tree_graph(graph, graph['type'])}</div><dialog class="map-inspector" id="map-inspector" aria-label="节点完整说明与证据"></dialog></div>
  <script id="map-details" type="application/json">{details}</script>
</section>'''
    outputs={}
    pages = [('research-map.html', '研究地图', intro+filters()+factbody+gates),
             ('literature-tree.html', 'Literature tree', graph_section(literature_graph, 'Literature tree 总览', 'task → pipeline / representation → module / follow-up') + pending_notice + filters() + litbody),
             ('challenge-insight-tree.html', 'Challenge–Insight 武器库',
              f'<p class="notice weapon-intro">{len(challenges)} 类挑战 · {sum(len(c["insights"]) for c in challenges)} 张使用卡 · {len(facts)} 篇既有来源。先按困难或条件检索，再点节点查看技术认识、机制、实现补丁、代价与证据。原文定位沿用公开笔记，本轮未重新审读全部 PDF；跨域迁移与独立因果结论不随整理升级。</p>' +
              filters() + graph_section(challenge_graph, 'Challenge–Insight 武器库', 'challenge → 可复用认识 → 有条件的使用卡与论文证据') + pending_notice + challengebody)]
    for name,title,body in pages:
        head=f'<header class="page-head"><div class="eyebrow">RESEARCH MAP</div><h1>{e(title)}</h1><p><a href="research-map.html">地图入口</a> · <a href="literature-tree.html">任务与方法树</a> · <a href="challenge-insight-tree.html">技术挑战树</a></p></header>'
        page=shell(title,head+body,current='research-map')
        def asset_url(asset):
            if name != 'challenge-insight-tree.html' or asset not in ('research-map.css', 'research-map.js'):
                return f'assets/{asset}'
            digest = hashlib.sha256((Path(root) / 'assets' / asset).read_bytes()).hexdigest()[:12]
            return f'assets/{asset}?v={digest}'
        outputs[name]=page.replace('</head>', f'<link rel="stylesheet" href="{asset_url("research-map.css")}"><script src="assets/map-layout.js" defer></script><script src="assets/map-canvas.js" defer></script><script src="{asset_url("research-map.js")}" defer></script></head>')
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
