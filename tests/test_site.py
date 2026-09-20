"""Regression checks for source preservation, Markdown stages and export boundaries."""
import base64
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_site as builder
import export_site as exporter
from check_site import check


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.patches = [patch.object(builder, 'ROOT', self.root), patch.object(exporter, 'ROOT', self.root)]
        for p in self.patches: p.start()
        self.paper = dict(slug='sample-2026', name='Sample', title='Sample paper', year=2026,
                          venue='Test', readDate='2026-09-17', tags=['LiDAR'], summary='A summary.',
                          stages={'first-pass': 'first-pass.md', 'code': 'code.md'})
        self.put('papers.json', json.dumps([self.paper]))
        self.put('publish.json', json.dumps(dict(papers=[], overview=False, assets=[])))
        self.put('papers/sample-2026/first-pass.md', '# First pass\n\n## Evidence\n\nAn observation.')
        self.put('papers/sample-2026/code.md', '# Code\n\n![diagram](images/diagram.png)\n\n## Method\n\n[Evidence](first-pass.html#evidence)')
        self.put('papers/sample-2026/images/diagram.png', b'image fixture')
        self.put('paper-cards/cross-paper-overview.md', '# Private overview\n\nPRIVATE_RESEARCH_MARKER')
        for relative in exporter.ASSETS:
            self.put(relative, '// fixture' if relative.endswith('.js') else '')

    def tearDown(self):
        for p in reversed(self.patches): p.stop()
        self.temp.cleanup()

    def put(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value if isinstance(value, bytes) else value.encode())

    def publish(self, **kwargs):
        policy = dict(papers=[dict(slug='sample-2026', stages=['first-pass'], **kwargs)], overview=False, assets=[])
        self.put('publish.json', json.dumps(policy))

    def test_markdown_all_stages_and_relative_assets(self):
        builder.build()
        self.assertIn('src="images/diagram.png"', (self.root/'papers/sample-2026/code.html').read_text())
        self.assertIn('data-stages="code first-pass"', (self.root/'index.html').read_text())
        check(self.root)

    def test_papers_directory_links_and_pdf_resources(self):
        self.put('pdf/sample.pdf', b'PDF fixture')
        p = dict(self.paper, pdf='pdf/sample.pdf')
        self.put('papers.json', json.dumps([p]))
        builder.build()
        self.assertFalse((self.root/'sample-2026').exists())
        home = (self.root/'index.html').read_text()
        self.assertIn('href="papers/sample-2026/index.html"', home)
        self.assertIn('href="papers/sample-2026/first-pass.html"', home)
        page = (self.root/'papers/sample-2026/index.html').read_text()
        self.assertIn('href="../../index.html"', page)
        self.assertIn('href="../../pdf/sample.pdf"', page)
        self.assertIn('href="first-pass.html"', page)
        for profile in ['local', 'public']:
            self.publish(include_pdf=True)
            exporter.export(profile)
            folder = self.root/('_site-public' if profile == 'public' else '_site')
            self.assertFalse((folder/'sample-2026').exists())
            self.assertEqual((folder/'pdf/sample.pdf').read_bytes(), b'PDF fixture')
            self.assertTrue((folder/'papers/sample-2026/first-pass.html').is_file())
            check(folder)

    def test_source_relative_link_across_directories(self):
        p = copy.deepcopy(self.paper)
        p['card'] = 'paper-cards/card.md'
        self.put('paper-cards/card.md', '# Deep\n\n![figure](figure.png)')
        self.put('paper-cards/figure.png', b'figure')
        pages, _ = builder.build([p], write=False)
        self.assertIn('src="../../paper-cards/figure.png"', pages['papers/sample-2026/deep-read.html'])

    def test_category_defaults_and_all_values(self):
        pages, papers = builder.build([self.paper], write=False)
        self.assertEqual(papers[0]['category'], 'uncategorized')
        self.assertNotIn('category', self.paper)
        for key, label in builder.CATEGORIES.items():
            p = dict(self.paper, category=key)
            pages, _ = builder.build([p], write=False)
            self.assertIn(f'data-category="{key}"', pages['index.html'])
            self.assertIn(f'{label}（1）', pages['index.html'])
            self.assertIn(f'{label} · 阅读日期', pages['papers/sample-2026/index.html'])

    def test_invalid_category_does_not_write(self):
        builder.build()
        before = (self.root/'index.html').read_bytes()
        for bad in ['outside', '', None, ['in-field']]:
            with self.assertRaisesRegex(ValueError, 'Invalid category'):
                builder.build([dict(self.paper, category=bad)])
        self.assertEqual((self.root/'index.html').read_bytes(), before)

    def test_category_survives_local_and_public_export(self):
        self.put('papers.json', json.dumps([dict(self.paper, category='out-of-field')]))
        self.publish()
        for profile in ['local', 'public']:
            report = exporter.export(profile)
            self.assertEqual(report['papers'][0]['category'], 'out-of-field')
            self.assertEqual(report['papers'][0]['venue'], 'Test')
            folder = '_site' if profile == 'local' else '_site-public'
            self.assertIn('data-category="out-of-field"', (self.root/folder/'index.html').read_text())
            check(self.root/folder)

    def test_checker_detects_wrong_category(self):
        builder.build()
        path = self.root/'index.html'
        self.put('index.html', path.read_text().replace('data-category="uncategorized"', 'data-category="in-field"'))
        with self.assertRaisesRegex(ValueError, 'Wrong paper category'):
            check(self.root)

    def test_venue_grouping_and_escaping(self):
        venue = 'Journal & "Conference"'
        papers = [dict(self.paper, category='in-field', venue=venue),
                  dict(self.paper, slug='other-2026', category='out-of-field', venue='  ' + venue + '  ', stages={})]
        pages, normalized = builder.build(papers, write=False)
        escaped = 'Journal &amp; &quot;Conference&quot;'
        self.assertEqual(normalized[1]['venue'], venue)
        self.assertIn(f'<option value="{escaped}">Journal &amp; &quot;Conference&quot;（2）</option>', pages['index.html'])
        self.assertEqual(pages['index.html'].count(f'data-venue="{escaped}"'), 2)
        self.assertIn('data-category="in-field"', pages['index.html'])
        self.assertIn('data-category="out-of-field"', pages['index.html'])

    def test_venue_validation_and_checker(self):
        for value in ['', '  ', None, []]:
            with self.assertRaisesRegex(ValueError, 'Invalid venue'):
                builder.build([dict(self.paper, venue=value)], write=False)
        builder.build()
        path = self.root/'index.html'
        self.put('index.html', path.read_text().replace('data-venue="Test"', 'data-venue="Wrong"'))
        with self.assertRaisesRegex(ValueError, 'Wrong publication venue'):
            check(self.root)

    def test_asset_version_changes_with_script_content(self):
        first, _ = builder.build(write=False)
        self.put('assets/app.js', '// updated filters')
        second, _ = builder.build(write=False)
        self.assertNotEqual(first['index.html'], second['index.html'])
        self.assertIn('assets/app.js?v=', second['index.html'])
        self.assertIn('../../assets/app.js?v=', second['papers/sample-2026/index.html'])

    def test_late_conflict_leaves_all_files_unchanged(self):
        builder.build()
        original = (self.root/'index.html').read_bytes()
        self.put('overview.html', '<html>AUTHORED CONTENT</html>')
        with self.assertRaisesRegex(ValueError, 'Refusing to overwrite'):
            builder.build()
        self.assertEqual((self.root/'index.html').read_bytes(), original)
        self.assertIn('AUTHORED CONTENT', (self.root/'overview.html').read_text())

    def test_review_cannot_be_claimed_without_evidence(self):
        p = copy.deepcopy(self.paper)
        p['reviews'] = {'code': {'status':'source-checked','checkedAt':'2026-09-17'}}
        with self.assertRaisesRegex(ValueError, 'evidence'):
            builder.build([p], write=False)

    def test_no_public_selection_is_blocked(self):
        with self.assertRaisesRegex(ValueError, 'No public papers'):
            exporter.export('public')
        self.assertFalse((self.root/'_site-public').exists())

    def test_public_selection_excludes_other_stages_and_sources(self):
        self.publish()
        report = exporter.export('public')
        out = self.root/'_site-public'
        self.assertNotIn('PRIVATE_RESEARCH_MARKER', (out/'overview.html').read_text())
        self.assertIn('未公开', (out/'papers/sample-2026/code.html').read_text())
        self.assertFalse((out/'paper-cards').exists())
        self.assertFalse((out/'papers.json').exists())
        self.assertEqual(set(report['papers'][0]['stages']), {'first-pass'})

    def test_public_unapproved_dependency_blocks_export(self):
        self.publish()
        exporter.export('public')
        original = (self.root/'_site-public/index.html').read_bytes()
        self.put('papers/sample-2026/first-pass.md', '# Note\n\n[private](../../paper-cards/cross-paper-overview.md)')
        with self.assertRaisesRegex(ValueError, 'Unapproved file'):
            exporter.export('public')
        self.assertEqual((self.root/'_site-public/index.html').read_bytes(), original)

    def test_embedded_image_needs_review_and_is_byte_preserved(self):
        data = b'unchanged image bytes'
        p = copy.deepcopy(self.paper)
        p['stages'] = {'first-pass': 'first-pass.html'}
        self.put('papers.json', json.dumps([p]))
        html = '<html><body><img loading="lazy" src="data:image/png;base64,' + base64.b64encode(data).decode() + '"></body></html>'
        self.put('papers/sample-2026/first-pass.html', html)
        self.publish()
        with self.assertRaisesRegex(ValueError, 'embedded paper images'):
            exporter.export('public')
        self.publish(allow_embedded_images=True)
        report = exporter.export('public')
        image = self.root/'_site-public/assets/paper-images'/f'{hashlib.sha256(data).hexdigest()}.png'
        self.assertEqual(image.read_bytes(), data)
        self.assertEqual((self.root/'papers/sample-2026/first-pass.html').read_text(), html)
        self.assertEqual(report['extractedImageFiles'], 1)

    def test_local_export_closes_resource_links(self):
        exporter.export('local')
        out = self.root/'_site'
        self.assertTrue((out/'papers/sample-2026/images/diagram.png').exists())
        self.assertFalse((out/'scripts').exists())
        check(out)

    def test_project_prefix_rejects_absolute_links(self):
        self.put('papers/sample-2026/first-pass.md', '# Note\n\n[bad](/index.html)')
        with self.assertRaisesRegex(ValueError, 'leaves repository'):
            builder.build(write=False)


if __name__ == '__main__':
    unittest.main()
