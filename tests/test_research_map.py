"""Regression checks for the source-grounded research map layer."""
import copy
import json
import sys
import hashlib
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_research_map as research_map

ROOT = Path(__file__).resolve().parents[1]


class ResearchMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.papers = json.loads((ROOT / 'papers.json').read_text(encoding='utf-8'))
        cls.data = research_map.load(ROOT)

    def test_sources_cover_in_field_library_or_explicit_pending(self):
        research_map.validate(self.data, ROOT, self.papers)
        in_field = {p['slug'] for p in self.papers if p.get('category') == 'in-field'}
        facts = self.data['facts']
        represented = {s for n in self.data['literature']['nodes'] for s in n['source_papers']}
        pending = {p['paper'] for p in self.data['pending']['papers']}
        self.assertEqual(len(research_map.BASELINE_MAPPED), 19)
        self.assertTrue(research_map.BASELINE_MAPPED <= represented)
        self.assertTrue(research_map.BASELINE_MAPPED <= facts.keys())
        self.assertTrue(in_field <= (represented & facts.keys()) | pending)
        self.assertFalse(pending & represented)
        self.assertFalse(pending & facts.keys())

    def pending_fixture(self):
        """Keep pending-state regressions independent of real papers becoming mapped."""
        data = copy.deepcopy(self.data)
        papers = copy.deepcopy(self.papers)
        paper = copy.deepcopy(next(p for p in papers if p['category'] == 'in-field'))
        paper.update(slug='pending-fixture-2026', name='Pending fixture')
        papers.append(paper)
        data['pending']['papers'] = [{
            'paper': paper['slug'], 'status': 'pending', 'registered_at': '2026-10-30',
            'reason': 'Test-only source awaiting a factual map',
        }]
        return data, papers

    def test_unregistered_in_field_paper_is_not_silently_omitted(self):
        bad, papers = self.pending_fixture()
        bad['pending']['papers'] = []
        with self.assertRaisesRegex(ValueError, 'Missing in-field coverage.*pending-fixture-2026'):
            research_map.validate(bad, ROOT, papers)

    def test_pending_does_not_allow_withdrawing_old_map_coverage(self):
        bad = copy.deepcopy(self.data)
        bad['pending']['papers'].append({
            'paper': 'dsor-2021', 'status': 'pending', 'registered_at': '2026-10-28',
            'reason': 'Attempt to hide an existing mapped source',
        })
        with self.assertRaisesRegex(ValueError, 'Previously mapped paper cannot be pending'):
            research_map.validate(bad, ROOT, self.papers)
        bad = copy.deepcopy(self.data)
        del bad['facts']['dsor-2021']
        with self.assertRaises(ValueError):
            research_map.validate(bad, ROOT, self.papers)

    def test_pending_registration_requires_known_in_field_paper_reason_and_date(self):
        for field, value, message in [
            ('paper', 'unknown-paper', 'Unknown pending paper'),
            ('paper', 'pointnet-2017', 'Pending paper must be in-field'),
            ('reason', '', 'pending reason'),
            ('registered_at', '2026-02-30', 'Invalid pending registration date'),
            ('registered_at', '', 'Invalid pending registration date'),
            ('status', 'organized', 'Invalid pending status'),
        ]:
            with self.subTest(field=field, value=value):
                bad, papers = self.pending_fixture()
                bad['pending']['papers'][0][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    research_map.validate(bad, ROOT, papers)

    def test_pending_registration_cannot_be_duplicate_or_mapped(self):
        bad, papers = self.pending_fixture()
        bad['pending']['papers'].append(copy.deepcopy(bad['pending']['papers'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate pending paper'):
            research_map.validate(bad, ROOT, papers)
        bad, papers = self.pending_fixture()
        bad['pending']['papers'][0]['paper'] = 'dsor-2021'
        # Isolate the generic mapped/pending conflict from the stricter historical
        # coverage protection, which has its own regression above.
        with mock.patch.object(research_map, 'BASELINE_MAPPED', research_map.BASELINE_MAPPED - {'dsor-2021'}):
            with self.assertRaisesRegex(ValueError, 'Mapped paper cannot also be pending'):
                research_map.validate(bad, ROOT, papers)

    def test_pending_notice_does_not_fabricate_map_nodes(self):
        from build_site import shell
        data, papers = self.pending_fixture()
        with mock.patch.object(research_map, 'load', return_value=data):
            outputs = research_map.render(ROOT, papers, shell)
        for output in outputs.values():
            self.assertIn('地图待整理 · 1 篇领域内论文', output)
            self.assertIn('papers/pending-fixture-2026/index.html', output)
            self.assertNotIn('id="paper-pending-fixture-2026"', output)
        self.assertNotIn('pending-fixture-2026', data['facts'])

    def test_completed_snow_papers_have_facts_and_both_tree_links(self):
        from build_site import shell
        slugs = {'beyondsnowflakes-2026', 'snowremovalnet-2026'}
        represented = {s for n in self.data['literature']['nodes'] for s in n['source_papers']}
        insights = {s for c in self.data['challenges']['challenges'] for i in c['insights'] for s in i['source_papers']}
        pending = {p['paper'] for p in self.data['pending']['papers']}
        self.assertTrue(slugs <= self.data['facts'].keys())
        self.assertTrue(slugs <= represented)
        self.assertTrue(slugs <= insights)
        self.assertFalse(slugs & pending)
        outputs = research_map.render(ROOT, self.papers, shell)
        for slug in slugs:
            self.assertIn(f'id="paper-{slug}"', outputs['research-map.html'])
            self.assertIn(f'papers/{slug}/first-pass.html#', outputs['literature-tree.html'])
            self.assertIn(f'papers/{slug}/first-pass.html#', outputs['challenge-insight-tree.html'])
        if not pending:
            for output in outputs.values():
                self.assertNotIn('id="map-pending"', output)

    def test_novelty_labels_are_separate(self):
        literature = self.data['literature']
        gate = self.data['gate']
        self.assertTrue(all('novelty_gate_case' not in node for node in literature['nodes']))
        self.assertTrue(all('novelty_class' not in candidate for candidate in gate['candidates']))
        self.assertIn('novelty_class', literature['nodes'][0])
        self.assertIn('novelty_gate_case', gate['candidates'][0]['gate'])

    def test_rendered_pages_expose_navigation_and_evidence_links(self):
        from build_site import shell
        outputs = research_map.render(ROOT, self.papers, shell)
        self.assertEqual(set(outputs), {'research-map.html', 'literature-tree.html', 'challenge-insight-tree.html'})
        self.assertIn('literature-tree.html', outputs['research-map.html'])
        self.assertIn('papers/sdor-2026/first-pass.html#section-05', outputs['literature-tree.html'])
        self.assertIn('challenge-density', outputs['challenge-insight-tree.html'])

    def test_graph_nodes_edges_and_details_match_sources(self):
        literature = research_map.build_literature_graph(self.data, self.data['facts'], {p['slug']: p for p in self.papers})
        challenge = research_map.build_challenge_graph(self.data, self.data['facts'], {p['slug']: p for p in self.papers})
        self.assertEqual(len(literature['nodes']), len(self.data['literature']['nodes']))
        self.assertTrue(all(edge['from'] in literature['positions'] and edge['to'] in literature['positions'] for edge in literature['edges']))
        self.assertTrue(all(edge['from'] in challenge['positions'] and edge['to'] in challenge['positions'] for edge in challenge['edges']))
        self.assertEqual(set(literature['details']), set(literature['positions']))
        self.assertEqual(set(challenge['details']), set(challenge['positions']))
        self.assertTrue(all(detail['source_count'] > 0 for detail in literature['details'].values()))
        self.assertTrue(all(detail['source_count'] > 0 for detail in challenge['details'].values()))

    def test_flow_tree_preserves_every_node_edge_and_complete_label(self):
        catalogue = {p['slug']: p for p in self.papers}
        for build in (research_map.build_literature_graph, research_map.build_challenge_graph):
            graph = build(self.data, self.data['facts'], catalogue)
            markup = research_map.render_tree_graph(graph, graph['type'])
            self.assertEqual(markup.count('data-node-id='), len(graph['nodes']))
            self.assertEqual(markup.count('data-edge-from='), len(graph['edges']))
            self.assertNotIn('node-confirmed', markup)
            self.assertIn('class="map-stage"', markup)
            self.assertIn('class="map-connectors" aria-hidden="true"', markup)
            for node in graph['nodes']:
                self.assertIn(research_map.e(graph['details'][node['id']]['name']), markup)
            for edge in graph['edges']:
                self.assertIn(f'data-edge-from="{edge["from"]}" data-edge-to="{edge["to"]}"', markup)


    def test_missing_anchor_is_rejected(self):
        bad = copy.deepcopy(self.data)
        bad['literature']['nodes'][0]['evidence'][0]['anchor'] = 'does-not-exist'
        with self.assertRaisesRegex(ValueError, 'Missing HTML anchor'):
            research_map.validate(bad, ROOT, self.papers)

    def test_pending_gate_cannot_have_pipeline(self):
        bad = copy.deepcopy(self.data)
        candidate = bad['gate']['candidates'][0]
        candidate['candidate_pipelines'] = ['pipeline-statistical-filtering']
        with self.assertRaisesRegex(ValueError, 'Pending gate cannot select'):
            research_map.validate(bad, ROOT, self.papers)

    def test_all_facts_have_distinct_insight_and_implementation(self):
        for slug, fact in self.data['facts'].items():
            analysis = fact['analysis']
            with self.subTest(slug=slug):
                self.assertEqual(analysis['insight']['basis'], 'analyst-inference')
                self.assertEqual(analysis['technical_reason']['status'], 'inferred')
                self.assertNotEqual(analysis['insight']['text'], analysis['contributions'][0]['implementation']['text'])
                self.assertEqual(analysis['contributions'][0]['implementation']['status'], 'source-checked')

    def test_five_branch_template_and_bidirectional_map_links(self):
        from build_site import shell
        outputs = research_map.render(ROOT, self.papers, shell)
        page = outputs['research-map.html']
        self.assertEqual(page.count('class="paper-analysis-tree"'), len(self.data['facts']))
        for branch in ('abstract', 'introduction', 'method', 'experiments', 'limitation'):
            self.assertIn(f'id="analysis-dror-2018-{branch}"', page)
        self.assertIn('literature-tree.html#module-dror-2018', page)
        self.assertIn('完整五分支解析树', (ROOT / 'assets/research-map.js').read_text())
        self.assertIn('research-map.html#paper-dror-2018', outputs['literature-tree.html'])

    def test_cannot_promote_reader_inference_to_checked_claim(self):
        bad = copy.deepcopy(self.data)
        bad['facts']['dror-2018']['analysis']['insight']['status'] = 'source-checked'
        with self.assertRaisesRegex(ValueError, 'basis/status mismatch'):
            research_map.validate(bad, ROOT, self.papers)

    def test_analysis_must_cite_own_paper_and_real_anchor(self):
        for paper, anchor, expected in [('pointnet-2017', 'section-04', 'belong to paper'),
                                         ('dror-2018', 'missing-anchor', 'Missing HTML anchor')]:
            with self.subTest(paper=paper, anchor=anchor):
                bad = copy.deepcopy(self.data)
                ev = bad['facts']['dror-2018']['analysis']['insight']['evidence'][0]
                ev.update(paper=paper, anchor=anchor)
                with self.assertRaisesRegex(ValueError, expected):
                    research_map.validate(bad, ROOT, self.papers)

    def test_missing_evidence_and_unknown_contribution_are_rejected(self):
        bad = copy.deepcopy(self.data)
        bad['facts']['dror-2018']['analysis']['insight']['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'Missing evidence'):
            research_map.validate(bad, ROOT, self.papers)
        bad = copy.deepcopy(self.data)
        bad['facts']['dror-2018']['analysis']['experiments'][0]['contribution_ids'] = ['invented-module']
        with self.assertRaisesRegex(ValueError, 'Unknown experiment contribution'):
            research_map.validate(bad, ROOT, self.papers)

    def test_unreported_experiment_cannot_support_a_contribution(self):
        bad = copy.deepcopy(self.data)
        item = bad['facts']['dsor-2021']['analysis']['experiments'][1]
        item['contribution_ids'] = ['contribution-main']
        with self.assertRaisesRegex(ValueError, 'Unreported experiment cannot support'):
            research_map.validate(bad, ROOT, self.papers)

    def test_principles_are_distinct_from_technique_names(self):
        for challenge in self.data['challenges']['challenges']:
            for insight in challenge['insights']:
                self.assertEqual(insight['principle']['status'], 'inferred')
                self.assertNotIn(insight['principle']['text'], insight['techniques'])

    def test_weapon_cards_preserve_coverage_and_separate_claim_types(self):
        sources = set()
        for challenge in self.data['challenges']['challenges']:
            self.assertEqual(challenge['why_hard']['basis'], 'analyst-inference')
            for insight in challenge['insights']:
                sources.update(insight['source_papers'])
                self.assertEqual(set(insight['playbook']), set(research_map.PLAYBOOK_FIELDS))
                self.assertEqual(insight['playbook']['mechanism']['basis'], 'note-summary')
                self.assertEqual(insight['playbook']['reported_effect']['basis'], 'note-summary')
                self.assertEqual(insight['playbook']['evidence_scope']['basis'], 'analyst-inference')
                self.assertEqual(insight['open_questions']['evidence'], [])
                self.assertEqual({loc['paper'] for loc in insight['source_locations']}, set(insight['source_papers']))
        self.assertEqual(sources, set(self.data['facts']))

    def test_weapon_claims_reject_missing_fields_unrelated_sources_and_false_verification(self):
        for kind in ('missing', 'unrelated', 'fake-anchor', 'promoted', 'wrong-location'):
            bad = copy.deepcopy(self.data)
            insight = bad['challenges']['challenges'][0]['insights'][0]
            if kind == 'missing':
                del insight['playbook']['engineering_tricks']
            elif kind == 'unrelated':
                insight['playbook']['mechanism']['evidence'][0]['paper'] = 'pointnet-2017'
            elif kind == 'fake-anchor':
                insight['source_locations'][0]['evidence'][0]['anchor'] = 'invented-location'
            elif kind == 'promoted':
                insight['open_questions'].update(basis='note-summary', status='source-checked')
            else:
                insight['source_locations'][0]['evidence'][0]['paper'] = 'pointnet-2017'
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                research_map.validate(bad, ROOT, self.papers)

    def test_weapon_details_and_search_include_operational_content(self):
        catalogue = {p['slug']: p for p in self.papers}
        graph = research_map.build_challenge_graph(self.data, self.data['facts'], catalogue)
        for ident, term in [('insight-adaptive', 'blending'), ('insight-confidence', 'icm'),
                            ('insight-offline-labels', '教师'), ('insight-parallel', 'boundary band')]:
            detail = graph['details'][ident]
            self.assertIn(term, detail['filters']['search'])
            self.assertEqual(len(detail['playbook']), len(research_map.PLAYBOOK_FIELDS))
            self.assertTrue(detail['source_locations'])
        from build_site import shell
        output = research_map.render(ROOT, self.papers, shell)['challenge-insight-tree.html']
        self.assertLess(output.index('id="map-search"'), output.index('id="map-graph"'))
        self.assertIn('论文原文定位（沿用笔记登记）', output)
        self.assertIn('何时谨慎使用', output)
        for asset in ('research-map.css', 'research-map.js'):
            digest = hashlib.sha256((ROOT / 'assets' / asset).read_bytes()).hexdigest()[:12]
            self.assertIn(f'assets/{asset}?v={digest}', output)

    def test_svg_final_column_has_no_overlapping_modules(self):
        graph = research_map.build_literature_graph(self.data, self.data['facts'], {p['slug']: p for p in self.papers})
        columns = {}
        for pos in graph['positions'].values():
            columns.setdefault(pos['x'], []).append(pos['y'])
        for values in columns.values():
            values.sort()
            self.assertTrue(all(right-left >= 62 for left,right in zip(values, values[1:])))

    def test_inspector_uses_node_evidence_not_generic_fact_evidence(self):
        graph = research_map.build_literature_graph(self.data, self.data['facts'], {p['slug']: p for p in self.papers})
        node = next(n for n in graph['nodes'] if n['id'] == 'module-dror-2018')
        detail = graph['details'][node['id']]
        self.assertEqual(len(detail['evidence']), len(node['evidence']))
        for source in detail['sources']:
            self.assertTrue(source['chain'])
            self.assertIn('#paper-', source['analysis_href'])

    def test_unassessed_claim_stays_explicitly_unverified(self):
        data = copy.deepcopy(self.data)
        claim = data['facts']['dror-2018']['analysis']['technical_reason']
        claim.update(text='尚未核验机制', basis='not-assessed', status='unverified', evidence=[])
        research_map.validate(data, ROOT, self.papers)
        markup = research_map.render_claim(claim, {})
        self.assertIn('尚未核验', markup)
        self.assertNotIn('已核对', markup)

    def test_claim_html_is_escaped(self):
        claim = dict(text='<img src=x onerror=alert(1)>', basis='not-assessed', status='unverified', evidence=[])
        markup = research_map.render_claim(claim, {})
        self.assertIn('&lt;img', markup)
        self.assertNotIn('<img', markup)

    def test_render_does_not_modify_authored_pages_or_catalogue(self):
        from build_site import shell
        paths = [ROOT/'papers.json', *ROOT.glob('papers/*/*.html')]
        before = {path: hashlib.sha256(path.read_bytes()).digest() for path in paths}
        research_map.render(ROOT, self.papers, shell)
        self.assertEqual(before, {path: hashlib.sha256(path.read_bytes()).digest() for path in paths})

    def test_public_build_has_no_research_map_or_analysis_payload(self):
        import build_site
        outputs, _ = build_site.build(self.papers, write=False, research_map=False)
        self.assertTrue(set(research_map.PAGES).isdisjoint(outputs))
        self.assertNotIn('research-map.html', outputs['index.html'])
        self.assertNotIn('paper-analysis-tree', outputs['index.html'])


if __name__ == '__main__':
    unittest.main()
