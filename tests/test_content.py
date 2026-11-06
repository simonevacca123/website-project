"""Contenuti: bozze escluse, schede valide, output HTML inerte, SEO coerente."""
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_pages
import deploy_site


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'content/progetti').mkdir(parents=True)
        self.example = json.loads((ROOT / 'content/progetti/elenchi.json').read_text())

    def write(self, name, item):
        (self.root / 'content/progetti' / name).write_text(json.dumps(item))

    def test_drafts_never_render_and_empty_catalog_is_honest(self):
        self.write('draft.json', {'pubblicato': False, 'titolo': 'PRIVATE_SENTINEL'})
        with patch.object(build_pages, 'ROOT', self.root):
            items = build_pages.load_projects()
        self.assertEqual(items, [])
        html = build_pages.catalog(items)
        self.assertNotIn('PRIVATE_SENTINEL', html)
        self.assertIn('Non ci sono ancora', html)

    def test_untrusted_text_is_escaped(self):
        self.example['titolo'] = '<script>alert(1)</script>'
        self.example['problema'] = '<img src=x onerror=alert(1)>'
        html = build_pages.catalog([self.example]) + build_pages.case_study(self.example)
        self.assertNotIn('<script>', html)
        self.assertNotIn('<img src=x', html)
        self.assertIn('&lt;script&gt;', html)

    def test_unsafe_urls_and_slug_are_refused(self):
        for key, value in [('demo', 'javascript:alert(1)'), ('repository', '//evil.test'), ('slug', '../secret'), ('immagine', 'assets/../secret.png')]:
            with self.subTest(key=key):
                self.write('item.json', {**self.example, key: value})
                with patch.object(build_pages, 'ROOT', self.root), self.assertRaises(ValueError):
                    build_pages.load_projects()

    def test_duplicate_and_incomplete_projects_refused(self):
        self.write('first.json', self.example)
        self.write('second.json', self.example)
        with patch.object(build_pages, 'ROOT', self.root), self.assertRaises(ValueError):
            build_pages.load_projects()
        (self.root / 'content/progetti/second.json').unlink()
        self.write('first.json', {**self.example, 'problema': ''})
        with patch.object(build_pages, 'ROOT', self.root), self.assertRaises(ValueError):
            build_pages.load_projects()

    def test_package_excludes_drafts_documents_and_tests(self):
        output = self.root / 'dist'
        manifest = deploy_site.build_release(ROOT, output, 'c' * 40)
        self.assertIn('lab/percorso/ui.js', manifest['files'])
        self.assertIn('progetti/elenchi/index.html', manifest['files'])
        self.assertFalse(any(name.startswith(('content/', 'templates/', 'tests/', 'scripts/', '.')) or name.endswith('.md') for name in manifest['files']))
        for name in manifest['files']:
            if name.endswith(('.html', '.js', '.json')):
                self.assertNotIn('da-compilare', (output / 'site' / name).read_text())

    def test_generated_pages_match_sitemap_and_metadata(self):
        class Metadata(HTMLParser):
            def __init__(self):
                super().__init__(); self.h1 = 0; self.canonical = []; self.titles = 0
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == 'h1': self.h1 += 1
                if tag == 'title': self.titles += 1
                if tag == 'link' and attrs.get('rel') == 'canonical': self.canonical.append(attrs['href'])
        outputs = build_pages.outputs()
        locations = {entry.text for entry in ElementTree.fromstring(outputs['sitemap.xml']).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        urls = set()
        for name, html in outputs.items():
            if not name.endswith('.html'): continue
            data = Metadata(); data.feed(html)
            self.assertEqual(data.h1, 1, name); self.assertEqual(data.titles, 1, name)
            self.assertEqual(len(data.canonical), 1, name)
            urls.add(data.canonical[0])
        self.assertEqual(urls, locations)
        self.assertEqual(len(urls), len([name for name in outputs if name.endswith('.html')]))


if __name__ == '__main__':
    unittest.main()
