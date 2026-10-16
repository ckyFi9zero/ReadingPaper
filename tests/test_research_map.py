"""Regression checks for the source-grounded research map layer."""
import copy
import json
import sys
import hashlib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_research_map as research_map

ROOT = Path(__file__).resolve().parents[1]


class ResearchMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.papers = json.loads((ROOT / 'papers.json').read_text(encoding='utf-8'))
        cls.data = research_map.load(ROOT)

    def test_sources_are_valid_and_cover_in_field_library(self):
        research_map.validate(self.data, ROOT, self.papers)
        in_field = {p['slug'] for p in self.papers if p.get('category') == 'in-field'}
        facts = self.data['facts']
        represented = {s for n in self.data['literature']['nodes'] for s in n['source_papers']}
        self.assertEqual(len(in_field), 19)
        self.assertTrue(in_field <= represented)
        self.assertTrue(in_field <= facts.keys())

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

    def test_svg_has_stable_nodes_and_unverified_novelty_is_not_confirmed(self):
        catalogue = {p['slug']: p for p in self.papers}
        graph = research_map.build_literature_graph(self.data, self.data['facts'], catalogue)
        svg = research_map.render_svg_graph(graph, 'literature')
        self.assertEqual(svg.count('data-node-id='), len(graph['nodes']))
        self.assertEqual(svg.count('data-edge-from='), len(graph['edges']))
        self.assertNotIn('node-confirmed', svg)

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
