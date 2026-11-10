import json
from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class November10ReadingTests(unittest.TestCase):
    def test_one_frontier_entry_and_twelve_stage1_sections(self):
        papers = json.loads((ROOT / 'papers.json').read_text())
        neo = [p for p in papers if p['slug'] == 'neo-vla-2026']
        self.assertEqual(len(neo), 1)
        self.assertEqual(neo[0]['category'], 'out-of-field')
        self.assertIn('拓展阅读', neo[0]['tags'])
        self.assertEqual(neo[0]['stages'], {'first-pass': 'first-pass.html'})
        text = (ROOT / 'papers/neo-vla-2026/first-pass.html').read_text()
        self.assertEqual(re.findall(r'<section id="(section-\d+)"', text), [f'section-{i:02}' for i in range(1, 13)])
        remember = text.split('id="section-11"', 1)[1].split('</section>', 1)[0]
        self.assertEqual(remember.count('<li>'), 5)
        self.assertIn('../../assets/reader-nav.js', text)
        for item in ['2611.06918v2', '未附带', '64.9', '90.9', '92.5', '3.0', '6.3', 'CC BY 4.0', '不声称全面SOTA']:
            self.assertIn(item, text)
        self.assertEqual(len(neo[0]['readingQuality']['graphics']['items']), 5)

    def test_revisit_is_independent_and_traceable(self):
        papers = json.loads((ROOT / 'papers.json').read_text())
        self.assertEqual(sum(p['slug'] == 'lisnownet-2022' for p in papers), 1)
        r = next(r for r in json.loads((ROOT / 'revisits.json').read_text())['revisits'] if r['id'] == 'lisnownet-20261110')
        self.assertEqual((r['paper'], r['date']), ('lisnownet-2022', '2026-11-10'))
        text = (ROOT / r['file']).read_text()
        for item in ['不是新论文', '2211.10023v1', '每个β', '没有保持α不变', '没有测试β=0或1', '推理判定', '../papers/lisnownet-2022/first-pass.html', 'CC BY 4.0']:
            self.assertIn(item, text)
        self.assertNotIn('lisnownet-20261110', (ROOT / 'papers/lisnownet-2022/first-pass.html').read_text())
        self.assertEqual(len(r['graphics']), 2)
        for g in r['graphics']:
            self.assertIn(f'data-for="{g["figureId"]}"', text)
        for s in ('desktop', 'mobile', 'zoom'):
            self.assertTrue(r['visualReview'][s])

    def test_map_evidence_keeps_negative_results_and_original_task(self):
        fact = yaml.safe_load((ROOT / 'research-map/sources/paper-facts/neo-vla-2026.yaml').read_text())
        self.assertEqual(fact['paper'], 'neo-vla-2026')
        self.assertIn('64.9', (ROOT / 'research-map/sources/paper-facts/neo-vla-2026.yaml').read_text())
        text = (ROOT / 'research-map/challenge-insight-tree.yaml').read_text()
        for item in ['insight-action-depth-readout', '预训练', '天气', 'Table8', 'revisit: lisnownet-20261110']:
            self.assertIn(item, text)
        doc = yaml.safe_load(text)
        ids = [i['id'] for c in doc['challenges'] for i in c.get('insights', [])]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids.count('insight-frequency'), 1)
        self.assertEqual(ids.count('insight-action-depth-readout'), 1)
