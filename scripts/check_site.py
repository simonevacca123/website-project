"""Controlla file e frammenti di homepage e laboratorio, senza dipendenze esterne."""

import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.references = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        attribute = 'href' if tag in ('a', 'link', 'use') else 'src'
        if tag in ('a', 'link', 'script', 'img', 'use') and attrs.get(attribute):
            self.references.append(attrs[attribute])


def main():
    errors = []
    count = 0
    files = json.loads((ROOT / 'scripts/public-files.json').read_text())
    for filename in ['index.html'] + [name for name in files if name.endswith('.html')]:
        document = ROOT / filename
        page = Page()
        page.feed(document.read_text(encoding='utf-8'))
        for element, duplicates in Counter(page.ids).items():
            if duplicates > 1:
                errors.append(f'{filename}: ID duplicato: {element}')
        count += len(page.references)
        for reference in page.references:
            url = urlsplit(reference)
            if url.scheme or url.netloc:
                continue
            path = unquote(url.path)
            if not path:
                target = document
            elif path.startswith('/'):
                target = (ROOT / path.lstrip('/')).resolve()
            else:
                target = (document.parent / path).resolve()
            if not target.is_relative_to(ROOT):
                errors.append(f'{filename}: percorso fuori dal sito: {reference}')
                continue
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                errors.append(f'{filename}: file mancante: {reference}')
                continue
            if url.fragment and target.suffix == '.html':
                other = Page()
                other.feed(target.read_text(encoding='utf-8'))
                if unquote(url.fragment) not in other.ids:
                    errors.append(f'{filename}: destinazione mancante: {reference}')
    if errors:
        for error in errors:
            print('ERRORE:', error)
        return 1
    print(f'PASS: {count} riferimenti statici delle pagine pubbliche, ID univoci.')
    print('Non controlla link esterni o il sito online.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
