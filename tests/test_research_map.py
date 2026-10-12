"""Regression checks for the source-grounded research map layer."""
import copy
import json
import sys
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


if __name__ == '__main__':
    unittest.main()
