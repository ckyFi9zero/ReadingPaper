"""Regression gate for the 2026-10-28 no-evidence-figures/category failure.

Synthetic PNG/text fixtures exercise structural gates only, not scientific review.
"""
import copy
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_reading_publish as gate
import build_site as builder
import export_site as exporter


def png(width=128, height=64):
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data) & 0xffffffff)
    raw = b''.join(b'\x00' + bytes([x % 256, y % 256, 127]) * width for y, x in zip(range(height), range(height)))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')


class ReadingPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.paper = {
            'slug': 'new-paper-2026', 'name': 'Fixture', 'title': 'Synthetic fixture',
            'year': 2026, 'venue': 'Test', 'readDate': '2026-10-28',
            'category': 'in-field', 'tags': [], 'summary': 'Synthetic structural fixture only.',
            'stages': {'first-pass': 'first-pass.html'},
            'readingQuality': {
                'version': 1,
                'classification': {'confirmedCategory': 'in-field',
                    'rationale': '人工根据用户已确认的恶劣天气感知研究范围与本文的雪天评测内容判断相关，不按关键词自动分类。',
                    'source': '用户确认的研究范围；论文 Section III–IV，PDF pp. 3–7。', 'reviewedAt': '2026-10-28'},
                'rightsReview': {'basis': '仅选择必要的局部图表用于具体评论，不搬运整篇论文；来源归属与摘录范围经过人工检查，此记录不是法律结论。', 'reviewedAt': '2026-10-28'},
                'visualReview': {'desktop': True, 'mobile': True, 'zoom': True, 'reviewedAt': '2026-10-28'},
                'graphics': {'status': 'included', 'items': [self.item(4)]},
            },
        }
        self.write_article()

    def tearDown(self):
        self.temp.cleanup()

    def item(self, n):
        return {'figureId': f'fig-{n}', 'kind': 'paper-crop', 'label': f'Figure {n}',
                'pdfPage': n, 'sourceUrl': f'https://example.org/paper#fig-{n}', 'analysisId': f'analysis-fig-{n}'}

    def markup(self, n=4):
        analysis = ('此为测试夹具的结构文本，不代表真实科研结论。测试要求图像、来源定位与相邻解释之间存在明确关联，'
                    '且解释默认展开并与图位于同一章节。视觉清晰度、坐标轴含义、数据准确性、版权范围与分类适切性仍须人工复核，'
                    '程序不得把文本长度、文件签名或元数据存在误称为已经证明论文结论。')
        return f'''<section id="section-{n}"><figure id="fig-{n}" data-visual-role="evidence" data-origin="paper-crop">
<button data-open="zoom-{n}"><img src="images/figure.png" alt="测试用论文曲线图局部裁剪，含坐标轴与图例"></button>
<figcaption>Figure {n} · PDF p. {n} · 原图局部裁剪 · 作者测试 <a href="https://example.org/paper#fig-{n}">来源</a></figcaption></figure>
<div id="analysis-fig-{n}" data-for="fig-{n}">{analysis}</div>
<dialog id="zoom-{n}"><img src="images/figure.png" alt="测试用放大图"></dialog></section>'''

    def write_article(self, text=None):
        folder = self.root / 'papers' / self.paper['slug']
        (folder / 'images').mkdir(parents=True, exist_ok=True)
        (folder / 'images' / 'figure.png').write_bytes(png())
        (folder / 'first-pass.html').write_text(text or '<html><body>' + self.markup() + '</body></html>', encoding='utf-8')

    def errors(self):
        return '\n'.join(gate.check_paper(self.root, self.paper))

    def test_repaired_structural_record_passes(self):
        self.assertEqual(self.errors(), '')

    def test_missing_metadata_and_backdated_new_paper_fail(self):
        self.paper.pop('readingQuality')
        self.paper['readDate'] = '2020-01-01'
        self.assertIn('requires readingQuality', self.errors())

    def test_legacy_set_is_fixed_39_and_preserved_without_new_claim(self):
        self.assertEqual(len(gate.LEGACY_SLUGS), 39)
        self.assertNotIn('beyondsnowflakes-2026', gate.LEGACY_SLUGS)
        self.paper['slug'] = next(iter(gate.LEGACY_SLUGS))
        self.paper.pop('readingQuality')
        self.assertEqual(self.errors(), '')

    def test_legacy_opt_in_is_validated_not_ignored(self):
        self.paper['slug'] = next(iter(gate.LEGACY_SLUGS))
        self.paper['readingQuality']['classification'].pop('rationale')
        self.assertIn('concrete human-reviewed rationale', self.errors())

    def test_previous_schematic_only_cannot_count_as_evidence(self):
        self.write_article('<section><figure id="fig-method-summary" data-visual-role="schematic"><img src="images/figure.png" alt="原创概括示意"></figure></section>')
        self.paper['readingQuality']['graphics']['items'] = []
        self.assertIn('schematic or source-only link does not count', self.errors())

    def test_relabelled_schematic_is_not_paper_crop(self):
        self.write_article(self.markup().replace('data-origin="paper-crop"', 'data-origin="original-schematic"'))
        self.assertIn('original schematic cannot substitute', self.errors())

    def test_no_image_remote_only_source_and_tiny_placeholder_fail(self):
        self.write_article(self.markup().replace('src="images/figure.png"', 'src="https://example.org/figure.png"'))
        self.assertIn('offline data or a relative local file', self.errors())
        self.write_article()
        (self.root / 'papers' / self.paper['slug'] / 'images' / 'figure.png').write_bytes(png(1, 1))
        self.assertIn('placeholder/tiny image', self.errors())

    def test_caption_source_analysis_and_zoom_are_required(self):
        self.write_article(self.markup().replace('href="https://example.org/paper#fig-4"', 'href="https://example.org/"').replace('data-for="fig-4"', 'data-for="other"').replace('data-open="zoom-4"', 'data-open="missing"'))
        errors = self.errors()
        self.assertIn('caption must link', errors)
        self.assertIn('explicitly tied', errors)
        self.assertIn('matching zoom dialog', errors)

    def test_hidden_evidence_and_link_only_analysis_fail(self):
        self.write_article(self.markup().replace('<figure id=', '<figure hidden id=').replace('<div id="analysis-fig-4"', '<div hidden id="analysis-fig-4"'))
        self.assertIn('must be visible', self.errors())
        self.assertIn('analysis must be expanded', self.errors())
        self.write_article(self.markup().replace('data-for="fig-4">', 'data-for="fig-4"><span hidden>').replace('</div>', '</span></div>'))
        self.assertIn('substantive adjacent analysis', self.errors())
        self.write_article('<section>' + self.markup().split('<div id=')[0] + '<div id="analysis-fig-4" data-for="fig-4">见原文</div></section>')
        self.assertIn('substantive adjacent analysis', self.errors())

    def test_classification_rationale_source_and_consistency_required(self):
        c = self.paper['readingQuality']['classification']
        c['confirmedCategory'] = 'out-of-field'
        c.pop('rationale')
        c['source'] = '猜测'
        errors = self.errors()
        self.assertIn('confirmedCategory must match', errors)
        self.assertIn('human-reviewed rationale', errors)
        self.assertIn('source evidence', errors)

    def test_user_approved_repair_blocks_old_category_even_if_metadata_agrees(self):
        self.paper['slug'] = 'beyondsnowflakes-2026'
        self.paper['category'] = 'out-of-field'
        self.paper['readingQuality']['classification']['confirmedCategory'] = 'out-of-field'
        self.write_article()
        self.assertIn('explicitly user-approved repair', self.errors())
        self.assertIn('Figure 4, 7 and 8', self.errors())

    def test_user_approved_repair_three_crops_pass(self):
        self.paper['slug'] = 'beyondsnowflakes-2026'
        self.paper['readingQuality']['graphics']['items'] = [self.item(n) for n in (4, 7, 8)]
        self.write_article('<html><body>' + ''.join(self.markup(n) for n in (4, 7, 8)) + '</body></html>')
        self.assertEqual(self.errors(), '')

    def test_visual_check_cannot_be_planned_or_omitted(self):
        self.paper['readingQuality']['visualReview']['mobile'] = False
        self.assertIn('completed desktop/mobile/zoom', self.errors())

    def test_included_graphic_cannot_mark_zoom_not_applicable(self):
        self.paper['readingQuality']['visualReview']['zoom'] = 'not-applicable'
        self.assertIn('zoom=not-applicable is allowed only', self.errors())

    def test_no_figure_exception_requires_full_documented_review(self):
        self.write_article('<section><p>Source-grounded prose for a paper without relevant figures.</p></section>')
        graphics = self.paper['readingQuality']['graphics']
        graphics.update(status='no-suitable-figures', items=[], exception={})
        self.assertIn('full-text review', self.errors())
        graphics['exception'] = {
            'fullTextReviewed': True, 'sourceHasRelevantFigures': False,
            'reason': '完整阅读当前版本全文后，确认其以文字论证为主要表达形式，没有可用于本阶段实质分析的原始 Figure 或 Table。此处不因图片下载失败、版权判断不明或排版时间不足而豁免，也不虚构实验图来填充页面；保留可追溯的正文定位与材料覆盖说明。',
            'sourceEvidence': '当前论文全部 PDF 页 1–8 与正文 Section I–V，逐页检查未发现适合当前阅读阶段的图表。',
            'sourceUrl': 'https://example.org/paper', 'reviewedBy': 'Explicit human/source review record', 'reviewedAt': '2026-10-28'}
        self.paper['readingQuality']['visualReview']['zoom'] = 'not-applicable'
        self.assertEqual(self.errors(), '')
        self.paper['readingQuality']['visualReview']['mobile'] = False
        self.assertIn('completed desktop/mobile/zoom', self.errors())

    def test_public_export_preserves_gate_metadata_and_rechecks_resources(self):
        for name in exporter.ASSETS:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('')
        (self.root / 'papers.json').write_text(json.dumps([self.paper]))
        config = {'papers': [{'slug': self.paper['slug'], 'stages': ['first-pass']}],
                  'overview': False, 'assets': [f"papers/{self.paper['slug']}/images/figure.png"]}
        (self.root / 'publish.json').write_text(json.dumps(config))
        with patch.object(builder, 'ROOT', self.root), patch.object(exporter, 'ROOT', self.root):
            report = exporter.export('public')
        self.assertEqual(report['papers'][0]['readingQuality'], self.paper['readingQuality'])
        out = self.root / '_site-public'
        self.assertEqual(gate.check_reading_publish(out, report['papers']), 1)
        (out / 'papers' / self.paper['slug'] / 'images' / 'figure.png').unlink()
        with self.assertRaisesRegex(ValueError, 'missing/outside evidence image'):
            gate.check_reading_publish(out, report['papers'])

    def test_regulated_build_fails_before_writing_generated_pages(self):
        self.paper.pop('readingQuality')
        for name in ('style.css', 'app.js', 'reader-nav.js'):
            path = self.root / 'assets' / name
            path.parent.mkdir(exist_ok=True)
            path.write_text('')
        source = self.root / 'paper-cards' / 'cross-paper-overview.md'
        source.parent.mkdir(exist_ok=True)
        source.write_text('# Overview')
        marker = self.root / 'index.html'
        marker.write_text('<!doctype html>\n' + builder.MARKER + '\nSENTINEL')
        with patch.object(builder, 'ROOT', self.root):
            with self.assertRaisesRegex(ValueError, 'requires readingQuality'):
                builder.build([self.paper], research_map=False)
        self.assertIn('SENTINEL', marker.read_text())
        self.assertFalse((self.root / 'papers' / self.paper['slug'] / 'index.html').exists())


if __name__ == '__main__':
    unittest.main()
