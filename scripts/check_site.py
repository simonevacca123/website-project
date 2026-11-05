"""Controlla file e frammenti locali della homepage, senza dipendenze esterne."""

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
    page = Page()
    page.feed((ROOT / 'index.html').read_text(encoding='utf-8'))
    errors = []
    for element, count in Counter(page.ids).items():
        if count > 1:
            errors.append(f'ID duplicato: {element}')
    for reference in page.references:
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            continue
        path = unquote(url.path)
        target = (ROOT / path.lstrip('/')).resolve() if path else ROOT / 'index.html'
        if not target.is_relative_to(ROOT):
            errors.append(f'Percorso fuori dal sito: {reference}')
            continue
        if target.is_dir():
            target = target / 'index.html'
        if not target.is_file():
            errors.append(f'File mancante: {reference}')
            continue
        if url.fragment and target.suffix == '.html':
            other = page
            if target != ROOT / 'index.html':
                other = Page()
                other.feed(target.read_text(encoding='utf-8'))
            if unquote(url.fragment) not in other.ids:
                errors.append(f'Destinazione interna mancante: {reference}')
    if errors:
        for error in errors:
            print('ERRORE:', error)
        return 1
    print(f'PASS: {len(page.references)} riferimenti statici della homepage e ID univoci.')
    print('Non controlla link esterni, risorse generate da JavaScript o il sito online.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
