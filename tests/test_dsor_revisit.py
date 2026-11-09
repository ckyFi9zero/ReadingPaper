import json
from pathlib import Path
import unittest
import yaml
ROOT=Path(__file__).resolve().parents[1]
class DSORRevisitTests(unittest.TestCase):
 def test_registered_without_duplicate_paper(self):
  papers=json.loads((ROOT/'papers.json').read_text());self.assertEqual(sum(p['slug']=='dsor-2021' for p in papers),1)
  record=next(r for r in json.loads((ROOT/'revisits.json').read_text())['revisits'] if r['id']=='dsor-20261109')
  self.assertEqual(record['paper'],'dsor-2021');self.assertEqual(record['date'],'2026-11-09')
  self.assertEqual(len(record['graphics']),2)
  self.assertNotIn('revisit-20261109',(ROOT/'papers/dsor-2021/first-pass.html').read_text())
 def test_denominators_versions_and_graphics_are_explicit(self):
  s=(ROOT/'revisits/dsor-20261109.html').read_text()
  for text in ['不是新论文','2109.07078v2','65.07','95.60','71.51','91.89','FP / (FP + TN)','平均','全部环境点被删掉34.9%','CC BY-SA 4.0','Algorithm 1','原图局部裁剪','../papers/dsor-2021/first-pass.html']:
   self.assertIn(text,s)
  for name in ['fig5','fig6']:self.assertIn(f'data-for="dsor-20261109-{name}"',s)
 def test_revisit_evidence_preserves_old_review_status(self):
  f=yaml.safe_load((ROOT/'research-map/sources/paper-facts/dsor-2021.yaml').read_text())
  self.assertEqual(f['task']['evidence'][0]['original_pdf_review_status'],'unregistered')
  self.assertEqual(f['source_review']['checked_at'],'2026-11-09')
  self.assertEqual(f['limitations'][-1]['evidence'][0]['revisit'],'dsor-20261109')
  tree=yaml.safe_load((ROOT/'research-map/challenge-insight-tree.yaml').read_text())
  nodes=tree.get('challenges',[])
  if not isinstance(nodes,list):self.fail('invalid challenge structure')
  card=next(i for c in nodes for i in c.get('insights',[]) if i['id']=='insight-distance')
  self.assertIn('不同分母',card['playbook']['evidence_scope']['text'])
  self.assertTrue(any(e.get('revisit')=='dsor-20261109' for e in card['playbook']['failure_boundary']['evidence']))
