"""Genera pagine statiche da template e schede. Solo Python standard, nessun server.

La homepage resta scritta a mano: vengono aggiornati solo i blocchi marcati.
--check verifica che gli output corrispondano ai sorgenti, senza scrivere.
"""
import argparse
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://www.simonevacca.it'
PAGES = [
    ('demo/', 'Demo gestionale turni — Simone Vacca', 'Prova una gestione turni dimostrativa: persone sintetiche, copertura delle fasce, modifiche e ripristino nel browser.', 'demo.html', ['demo/turni.js']),
    ('strumenti/checklist/', 'Checklist del sito — Autovalutazione per aziende', 'Otto domande per valutare chiarezza, contatti e facilità d’uso del sito. Report copiabile, senza scansioni o raccolta dati.', 'checklist.html', ['strumenti/checklist.js']),
    ('lab/percorso/', 'BFS e Dijkstra — Visualizzatore di percorsi', 'Disegna ostacoli e terreno lento: confronta BFS e Dijkstra passo passo in una griglia interattiva accessibile da tastiera.', 'percorso.html', ['lab/percorso/algorithms.js', 'lab/percorso/ui.js']),
    ('servizi/', 'Servizi web, software e automazioni — Simone Vacca', 'Siti web per piccole aziende, software gestionali personalizzati e automazioni: problemi concreti, ambito e costi da definire insieme.', 'servizi.html', []),
    ('chi-sono/', 'Chi sono — Simone Vacca, informatica e sviluppo software', 'Il percorso di Simone Vacca: studi in informatica e intelligenza artificiale, sviluppo web e attenzione ai problemi reali.', 'chi-sono.html', []),
    ('lab/', 'Laboratorio — Esperimenti di Simone Vacca', 'Algoritmi e automazioni da provare nel browser. Demo personali con scelte tecniche, stato e limiti dichiarati.', 'lab.html', []),
    ('strumenti/', 'Strumenti gratuiti per piccole aziende — Simone Vacca', 'Calcolatore di efficienza e checklist del sito: stime trasparenti e autovalutazioni senza raccolta di dati personali.', 'strumenti.html', []),
    ('lab/elenchi/', 'Elimina righe duplicate — Laboratorio di Simone Vacca', 'Una demo personale per trovare doppioni negli elenchi. Elaborazione locale nel browser, senza caricamenti o salvataggi.', 'elenchi.html', ['lab/lab.js']),
]


def nav(base, current=''):
    links = [('servizi/', 'Servizi'), ('progetti/', 'Progetti'), ('lab/', 'Laboratorio'), ('strumenti/', 'Strumenti'), ('chi-sono/', 'Chi sono')]
    anchors = ''.join(f'<a href="{base}{path}"' + (' aria-current="page"' if current == path else '') + f'>{label}</a>' for path, label in links)
    return f'<header class="wrap header"><a class="brand" href="{base}" aria-label="Simone Vacca, homepage"><span class="brand-symbol">s/v</span><span>Simone<br>Vacca</span></a><nav aria-label="Navigazione principale">{anchors}</nav><a class="header-cta" href="{base}#contatti">Parliamone</a></header>'


def seo(path, title, description):
    url = ORIGIN + '/' + path
    return f'<link rel="canonical" href="{url}">\n<meta property="og:type" content="website"><meta property="og:locale" content="it_IT"><meta property="og:site_name" content="Simone Vacca"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{url}">'


def page(path, title, description, body, scripts=()):
    base = '../' * len(path.strip('/').split('/'))
    replacements = {'title': escape(title), 'description': escape(description, quote=True), 'base': base, 'seo': seo(path, title, description), 'nav': nav(base, path), 'body': body,
                    'scripts': ''.join(f'<script src="{base}{s}" defer></script>' for s in scripts)}
    html = (ROOT / 'templates/layout.html').read_text()
    for key, value in replacements.items():
        html = html.replace('{{' + key + '}}', value)
    return '\n'.join(line.rstrip() for line in html.splitlines()).rstrip() + '\n'



def load_projects():
    projects = []
    slugs = set()
    required = ('titolo', 'tipo', 'categoria', 'stato', 'descrizione', 'contesto', 'problema', 'obiettivi', 'soluzione', 'interfaccia', 'scelte', 'compromessi', 'risultati')
    for source in sorted((ROOT / 'content/progetti').glob('*.json')):
        item = json.loads(source.read_text())
        if item.get('pubblicato') is not True:
            continue
        slug = item.get('slug', '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs:
            raise ValueError('Slug non valido o duplicato: ' + str(source))
        if any(not isinstance(item.get(k), str) or not item[k].strip() for k in required):
            raise ValueError('Scheda pubblica incompleta: ' + str(source))
        if not isinstance(item.get('tecnologie'), list) or not all(isinstance(t, str) for t in item['tecnologie']):
            raise ValueError('Tecnologie non valide: ' + str(source))
        for key in ('demo', 'repository'):
            url = item.get(key, '')
            if url and not re.fullmatch(r'https://[^\s<>"\x00-\x1f]+|/(?:[a-z0-9-]+/)+', url):
                raise ValueError('URL non consentito: ' + key)
        image = item.get('immagine', '')
        if image and (not re.fullmatch(r'assets/[a-zA-Z0-9_/-]+\.(?:png|jpg|jpeg|webp|avif|svg)', image) or not (ROOT / image).is_file()):
            raise ValueError('Immagine mancante o non valida')
        slugs.add(slug)
        projects.append(item)
    return projects


def project_links(item, base):
    links = []
    for key, label in [('demo', 'Prova la demo'), ('repository', 'Leggi il codice')]:
        url = item.get(key, '')
        if url:
            url = base + url.lstrip('/') if url.startswith('/') else url
            links.append(f'<a class="text-link" href="{escape(url, quote=True)}">{label}</a>')
    return '<div class="controls">' + ''.join(links) + '</div>'


def catalog(projects, base='../'):
    if not projects:
        return '<p>Non ci sono ancora progetti pubblicati. Le bozze restano private.</p>'
    rows = []
    for i, item in enumerate(projects, 1):
        rows.append(f'<article class="catalog-item"><div><span class="catalog-number">{i:02d}</span><p class="tag-line">{escape(item["categoria"])}<br>{escape(item["tipo"])}</p></div><div><p class="tag-line">{escape(item["stato"])}</p><h2>{escape(item["titolo"])}</h2><p>{escape(item["descrizione"])}</p><p class="tag-line">{escape(" · ".join(item["tecnologie"]))}</p><a class="text-link" href="{base}progetti/{item["slug"]}/">Leggi il progetto</a>{project_links(item, base)}</div></article>')
    return ''.join(rows)


def case_study(item):
    sections = [('contesto', 'Il contesto'), ('problema', 'Il problema'), ('obiettivi', 'Gli obiettivi'), ('soluzione', 'La soluzione'), ('interfaccia', "L'interfaccia"), ('scelte', 'Scelte tecniche'), ('compromessi', 'Difficoltà e limiti'), ('risultati', 'Risultati osservabili')]
    intro = f'<section class="wrap page-intro"><a class="text-link" href="../">Tutti i progetti</a><p class="eyebrow">{escape(item["tipo"])} / {escape(item["stato"])}</p><h1>{escape(item["titolo"])}</h1><p class="lead">{escape(item["descrizione"])}</p>{project_links(item, "../../")}</section>'
    intro += '<div class="wrap"><p class="tag-line">' + escape(' · '.join(item['tecnologie'])) + '</p></div>'
    if item.get('periodo'):
        intro += '<p class="wrap tag-line">Periodo: ' + escape(str(item['periodo'])) + '</p>'
    image = item.get('immagine')
    if image:
        intro += f'<figure class="wrap"><img class="project-image" src="../../{escape(image)}" alt="Interfaccia: {escape(item["titolo"], quote=True)}" loading="lazy"></figure>'
    body = ''.join(f'<article><h2>{label}</h2><p>{escape(item[key])}</p></article>' for key, label in sections)
    return intro + '<section class="wrap editorial-list">' + body + '</section><section class="wrap closing-note"><h2>Un problema simile?</h2><a class="button" href="../../#contatti">Raccontamelo</a></section>'

def outputs():
    result = {}
    projects = load_projects()
    for path, title, description, template, scripts in PAGES:
        body = (ROOT / 'templates' / template).read_text()
        body = body.replace('{{catalog}}', catalog([p for p in projects if p.get('lab')]))
        result[path + 'index.html'] = page(path, title, description, body, scripts)
    result['progetti/index.html'] = page('progetti/', 'Progetti e demo — Simone Vacca', 'Progetti personali verificabili: problemi, soluzioni, scelte tecniche e demo funzionanti. Nessun risultato commerciale inventato.', '<section class="wrap page-intro"><p class="eyebrow">PROGETTI / DAL PROBLEMA ALLA PROVA</p><h1>Apri. Prova.<br><span>Guarda come funziona.</span></h1><p class="lead">Qui raccolgo progetti personali e dimostrazioni, con le scelte tecniche e i limiti. Quelli attuali sono demo: non rappresentano lavori venduti a clienti.</p></section><section class="wrap">' + catalog(projects) + '</section>')
    for item in projects:
        path = 'progetti/' + item['slug'] + '/'
        result[path + 'index.html'] = page(path, item['titolo'] + ' — Progetto di Simone Vacca', item['descrizione'], case_study(item))
    home = (ROOT / 'index.html').read_text()
    home = re.sub(r'<!-- NAV:START -->.*?<!-- NAV:END -->', '<!-- NAV:START -->' + nav('./') + '<!-- NAV:END -->', home, flags=re.S)
    title = re.search(r'<title>(.*?)</title>', home).group(1)
    description = re.search(r'<meta name="description" content="(.*?)"', home).group(1)
    home = re.sub(r'<!-- SEO:START -->.*?<!-- SEO:END -->', '<!-- SEO:START -->' + seo('', title, description) + '<!-- SEO:END -->', home, flags=re.S)
    # Mantiene il recapito senza JS coerente con l'unica configurazione pubblica.
    config = (ROOT / 'contenuti.js').read_text()
    match = re.search(r'email:\s*("(?:[^"\\]|\\.)*")', config)
    email = json.loads(match.group(1)) if match else ''
    fallback = ('Scrivi a ' + escape(email) + ' dalla tua app di posta. ') if re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) else 'Recapito non configurato. '
    home = re.sub(r'<noscript><p>.*?</p></noscript>', lambda _: '<noscript><p>' + fallback + 'Il modulo interattivo richiede JavaScript.</p></noscript>', home, flags=re.S)
    result['index.html'] = home
    routes = ['' if name == 'index.html' else name.removesuffix('index.html') for name in result if name.endswith('index.html')]
    result['sitemap.xml'] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + ORIGIN + '/' + route + '</loc></url>' for route in sorted(routes)) + '</urlset>\n'
    result['robots.txt'] = 'User-agent: *\nAllow: /\nSitemap: ' + ORIGIN + '/sitemap.xml\n'
    extra = sorted(set(result) - {'index.html'} | {script for _, _, _, _, scripts in PAGES for script in scripts} | {'strumenti/efficiency.js'})
    result['scripts/public-files.json'] = json.dumps(extra, indent=2) + '\n'
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = outputs()
    changed = []
    for name, value in result.items():
        path = ROOT / name
        if not path.exists() or path.read_text() != value:
            changed.append(name)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value)
    if args.check and changed:
        raise SystemExit('Rigenerare con python3 scripts/build_pages.py: ' + ', '.join(changed))
    print(f'PASS: {len(result)} output statici ' + ('verificati.' if args.check else 'generati.'))


if __name__ == '__main__':
    main()
