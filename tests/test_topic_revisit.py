import json
import unittest
import re
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class TopicRevisitTests(unittest.TestCase):
    def test_existing_paper_not_republished_as_new_stage(self):
        papers=json.loads((ROOT/'papers.json').read_text())
        item=next(p for p in papers if p['slug']=='3d-unoutdet-2025')
        self.assertEqual(item['readDate'],'2026-09-24')
        self.assertEqual(set(item['stages']),{'first-pass','code'})
        self.assertEqual(item['revisits'][0]['date'],'2026-11-08')
        self.assertEqual(item['revisits'][0]['anchor'],'revisit-20261108')

    def test_revisit_keeps_version_and_inference_boundary(self):
        s=(ROOT/'papers/3d-unoutdet-2025/first-pass.html').read_text()
        section=s.split('<section id="revisit-20261108"',1)[1].split('</section>',1)[0]
        for text in ['不是新论文','TechRxiv v1','未重新取得 IROS','阅读者分析','7.28 个百分点','S4','Fig. S1(b)','原图局部裁剪']:
            self.assertIn(text,section)
        for n in range(1,13):
            self.assertEqual(s.count(f'id="section-{n:02d}"'),1)
        self.assertIn('data-for="revisit-20261108-fig-s1b"',section)
        self.assertIn('images/revisit-20261108-fig-s1b.png',section)
        self.assertTrue((ROOT/'papers/3d-unoutdet-2025/images/revisit-20261108-fig-s1b.png').is_file())

    def test_topic_figure_has_traceable_offline_media(self):
        s=(ROOT/'papers/3d-unoutdet-2025/first-pass.html').read_text()
        section=s.split('<section id="revisit-20261108"',1)[1].split('</section>',1)[0]
        figure=re.search(r'<figure id="revisit-20261108-fig-s1b".*?</figure>',section,re.S).group(0)
        for required in ['data-visual-role="evidence"','data-origin="paper-crop"','<figcaption>','Fig. S1(b)','PDF p. 2','Raisuddin','<button class="zoom"','https://sporsho.github.io/3DUnOutDet_Suppli.pdf#page=2']:
            self.assertIn(required,figure)
        png=(ROOT/'papers/3d-unoutdet-2025/images/revisit-20261108-fig-s1b.png').read_bytes()
        self.assertEqual(png[:8],b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>II',png[16:24]),(1569,966))
        self.assertIn('data-for="revisit-20261108-fig-s1b"',section)
        self.assertIn('不是新实验或原表图片',section)
        self.assertIn('href="#unoutdet-table1"',section)

if __name__=='__main__':unittest.main()
