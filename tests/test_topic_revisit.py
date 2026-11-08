import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from topic_revisits import load_revisits, directory_body
import build_research_map as maps

class TopicRevisitTests(unittest.TestCase):
    def test_revisit_is_independent_not_new_paper_or_stage(self):
        papers=json.loads((ROOT/'papers.json').read_text())
        item=next(p for p in papers if p['slug']=='3d-unoutdet-2025')
        self.assertEqual(item['readDate'],'2026-09-24')
        self.assertEqual(set(item['stages']),{'first-pass','code'})
        self.assertNotIn('revisits',item)
        records=load_revisits(ROOT,papers)
        self.assertEqual(records[0]['file'],'revisits/3d-unoutdet-20261108.html')
        original=(ROOT/'papers/3d-unoutdet-2025/first-pass.html').read_text()
        self.assertNotIn('revisit-20261108',original)
        for n in range(1,13):self.assertEqual(original.count(f'id="section-{n:02d}"'),1)

    def test_topic_keeps_versions_evidence_and_original_backlink(self):
        s=(ROOT/'revisits/3d-unoutdet-20261108.html').read_text()
        for text in ['不是新论文','TechRxiv v1','未重新取得 IROS','阅读者分析','7.28 个百分点','S4','Fig. S1(b)','原图局部裁剪','Table I','原表局部裁剪']:
            self.assertIn(text,s)
        self.assertIn('href="../revisits.html"',s)
        self.assertIn('../papers/3d-unoutdet-2025/first-pass.html#unoutdet-table1',s)
        for fid in ['revisit-20261108-fig-s1b','revisit-20261108-table-i']:
            self.assertIn(f'data-for="{fid}"',s)

    def test_directory_distinguishes_reviewed_and_not_yet(self):
        papers=json.loads((ROOT/'papers.json').read_text());records=load_revisits(ROOT,papers)
        s=directory_body(papers,records)
        self.assertEqual(s.count('data-revisit-state="reviewed"'),1)
        self.assertEqual(s.count('data-revisit-state="not-yet"'),len(papers)-1)
        self.assertIn('2026-11-08',s)
        self.assertIn('revisits/3d-unoutdet-20261108.html#revisit-20261108',s)
        self.assertIn('暂无回看记录',s)

    def test_gate_rejects_bad_records(self):
        papers=json.loads((ROOT/'papers.json').read_text());data=json.loads((ROOT/'revisits.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for path in [r['file'] for r in data['revisits']]+['revisits/images/3d-unoutdet-20261108-fig-s1b.png','revisits/images/3d-unoutdet-20261108-table-i.png']:
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/path).read_bytes())
            def check(data):
                (root/'revisits.json').write_text(json.dumps(data));return load_revisits(root,papers)
            check(data)
            variants=[]
            d=copy.deepcopy(data);d['revisits'].append(copy.deepcopy(d['revisits'][0]));variants.append(d)
            d=copy.deepcopy(data);d['revisits'][0]['file']='../outside.html';variants.append(d)
            d=copy.deepcopy(data);d['revisits'][0]['paper']='unknown';variants.append(d)
            d=copy.deepcopy(data);d['revisits'][0]['anchor']='missing';variants.append(d)
            d=copy.deepcopy(data);d['revisits'][0]['visualReview']['mobile']=False;variants.append(d)
            d=copy.deepcopy(data);d['revisits'][0]['rightsReview']['basis']='';variants.append(d)
            for d in variants:
                with self.subTest(record=d),self.assertRaises((ValueError,KeyError)):check(d)
            (root/'revisits/images/3d-unoutdet-20261108-table-i.png').unlink()
            with self.assertRaises(ValueError):check(data)

    def test_map_topic_reference_is_not_a_fake_stage(self):
        ev={'paper':'3d-unoutdet-2025','revisit':'3d-unoutdet-20261108','anchor':'revisit-20261108-thresholds'}
        self.assertEqual(maps.evidence_kind(ev),'专题回看')
        self.assertEqual(maps.evidence_href(ev),'revisits/3d-unoutdet-20261108.html#revisit-20261108-thresholds')

if __name__=='__main__':unittest.main()
