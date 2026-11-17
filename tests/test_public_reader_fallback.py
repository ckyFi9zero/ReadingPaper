import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import linked_reader
import build_site
import tempfile
from unittest.mock import patch

class PublicReaderFallbackTests(unittest.TestCase):
    def test_missing_private_pdf_has_real_public_entry(self):
        root = Path(__file__).resolve().parents[1]
        paper = {'slug': '3d-unoutdet-2025', 'name': '3D-UnOutDet', 'available': {'first-pass', 'code'}}
        result = linked_reader.render(root, paper)
        self.assertIn('https://sporsho.github.io/3DUnOutDet', result)
        self.assertIn('10.1109/IROS60139.2025.11247379', result)
        self.assertNotIn('source.pdf', result)
        self.assertNotIn('evidence-reader.js', result)
        self.assertIn('name="note-viewer"', result)
        self.assertIn('href="code.html" target="note-viewer"', result)
        self.assertIn('不提供内嵌 PDF', result)
    def test_no_unverified_source_does_not_render(self):
        self.assertEqual(linked_reader.render_public_fallback({'slug':'x'}, {'viewer':{}}), '')
        self.assertEqual(linked_reader.render_public_fallback({'slug':'x'}, {'viewer':{'public_source':'javascript:alert(1)'}}), '')

    def test_fallback_is_rebuildable_generated_output(self):
        result = linked_reader.render_public_fallback({'slug':'x'}, {'viewer':{'public_source':'https://example.com/paper'}})
        self.assertTrue(result.startswith('<!doctype html>\n' + build_site.MARKER))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(build_site, 'ROOT', root):
                build_site.write_pages({'papers/x/linked-reader.html': result})
                build_site.write_pages({'papers/x/linked-reader.html': result})
            self.assertEqual((root/'papers/x/linked-reader.html').read_text(), result)
