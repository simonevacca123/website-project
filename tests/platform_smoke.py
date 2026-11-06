"""Prove delle nuove sezioni via HTTP locale: nessuna produzione o invio email."""
import json
import os
import re
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from shutil import which
from threading import Thread
from playwright.sync_api import expect, sync_playwright
from browser_smoke import ROOT, QuietHandler


def verify(base):
    pages = ['/' if name == 'index.html' else '/' + name.removesuffix('index.html') for name in ['index.html'] + json.loads((ROOT / 'scripts/public-files.json').read_text()) if name.endswith('.html')]
    with sync_playwright() as p:
        executable = None if os.environ.get('USE_PLAYWRIGHT_BROWSER') == '1' else which('chromium')
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'], **({'executable_path': executable} if executable else {}))
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
        page = context.new_page()
        errors, requests, failures = [], [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda req: requests.append(req.url))
        page.on('response', lambda response: failures.append(response.url) if response.status >= 400 else None)
        titles = set()
        output = ROOT / 'test-results'
        output.mkdir(exist_ok=True)
        for route in pages:
            response = page.goto(base + route, wait_until='networkidle')
            assert response.status == 200, route
            expect(page.locator('h1')).to_have_count(1)
            title = page.title(); assert title not in titles; titles.add(title)
            expect(page.locator('link[rel=canonical]')).to_have_attribute('href', 'https://www.simonevacca.it' + route)
            page.keyboard.press('Tab'); expect(page.locator('.skip')).to_be_focused()
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 1000})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (route, width)
            page.set_viewport_size({'width': 320, 'height': 1000})
            page.evaluate("document.documentElement.style.fontSize='200%'")
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (route, '200%')
            page.evaluate("document.documentElement.style.fontSize=''")
            page.locator('h1').click()
            if route in ['/lab/', '/lab/percorso/', '/demo/', '/progetti/', '/chi-sono/', '/strumenti/checklist/']:
                name = route.strip('/').replace('/', '-')
                for width in [390, 1440]:
                    page.set_viewport_size({'width': width, 'height': 1000})
                    page.screenshot(path=str(output / f'{name}-{width}.png'), full_page=True)
        print(f'PASS: {len(pages)} URL diretti, titoli unici, canonical, tastiera, 4 larghezze e testo 200%.')

        page.goto(base + '/lab/percorso/')
        page.locator('#path-clear').click()
        page.locator('[data-cell="0"]').focus(); page.keyboard.press('ArrowRight')
        expect(page.locator('[data-cell="1"]')).to_be_focused()
        page.keyboard.press('Space'); expect(page.locator('[data-cell="1"]')).to_contain_text('#')
        page.locator('#path-clear').click()
        page.locator('#path-step').click(); expect(page.locator('#path-visited')).to_have_text('1')
        page.locator('#path-start').click(); page.locator('#path-pause').click()
        visited = page.locator('#path-visited').inner_text()
        page.wait_for_timeout(250); expect(page.locator('#path-visited')).to_have_text(visited)
        page.locator('#path-reset').click(); expect(page.locator('#path-visited')).to_have_text('0')
        page.emulate_media(reduced_motion='reduce')
        page.locator('#paint-mode').select_option('weight')
        for cell in [26, 27, 28]: page.locator(f'[data-cell="{cell}"]').click()
        page.locator('#path-start').click()
        expect(page.locator('#path-length')).to_have_text('9'); expect(page.locator('#path-cost')).to_have_text('21')
        page.locator('#algorithm').select_option('dijkstra')
        page.locator('#path-start').click()
        expect(page.locator('#path-length')).to_have_text('11'); expect(page.locator('#path-cost')).to_have_text('11')
        page.locator('#path-clear').click(); page.locator('#paint-mode').select_option('wall')
        for cell in [13, 24, 26, 37]: page.locator(f'[data-cell="{cell}"]').click()
        page.locator('#path-start').click(); expect(page.locator('#path-status')).to_contain_text('Nessun percorso')
        page.locator('#path-clear').click(); page.locator('#paint-mode').select_option('start')
        page.locator('[data-cell="34"]').click(); expect(page.locator('#path-status')).to_contain_text('distinti')
        page.emulate_media(reduced_motion='no-preference')
        page.locator('#path-start').click(); page.locator('#paint-mode').select_option('wall'); page.locator('[data-cell="10"]').click()
        page.wait_for_timeout(250); expect(page.locator('#path-visited')).to_have_text('0')
        print('PASS: pathfinding da tastiera, pausa/reset, costi BFS/Dijkstra, assenza percorso, edit durante animazione.')

        page.goto(base + '/#valore')
        page.locator('#hourly-rate').fill('25'); page.locator('#active-months').fill('10')
        expect(page.locator('#annual-hours')).to_have_text('50')
        expect(page.locator('#monthly-value')).to_contain_text('125,00'); expect(page.locator('#annual-value')).to_have_text(re.compile(r'1[.]?250,00\s*€'))
        page.locator('#hourly-rate').fill('-1'); expect(page.locator('#hourly-rate')).to_have_attribute('aria-invalid', 'true')
        expect(page.locator('#monthly-value')).to_have_text('Non indicato')
        page.locator('#reset-calc').click(); expect(page.locator('#hourly-rate')).to_have_value(''); expect(page.locator('#annual-hours')).to_have_text('60')
        print('PASS: calcolatore unico, mesi attivi, valore orario, input errato e reset.')

        page.goto(base + '/strumenti/checklist/')
        page.locator('#checklist-form button[type=submit]').click()
        expect(page.locator('#check-0')).to_be_focused(); expect(page.locator('#checklist-result')).to_be_hidden()
        for i in range(8): page.locator(f'#check-{i}').select_option('yes' if i < 3 else 'no' if i < 6 else 'unknown')
        page.locator('#checklist-form button[type=submit]').click()
        expect(page.locator('#checklist-status')).to_contain_text('3 punti positivi, 3 problemi potenziali e 2 aspetti')
        expect(page.locator('#report-title')).to_be_focused()
        report = page.locator('#checklist-report').input_value()
        assert report.index('Priorità alta') < report.index('Priorità media')
        context.grant_permissions(['clipboard-read', 'clipboard-write'])
        page.locator('#report-copy').click(); assert page.evaluate('navigator.clipboard.readText()') == report
        page.evaluate("() => { navigator.clipboard.writeText = () => Promise.reject(new Error('test')); }")
        page.locator('#report-copy').click(); expect(page.locator('#report-status')).to_contain_text('Testo selezionato')
        with page.expect_download() as download_info: page.locator('#report-download').click()
        download = download_info.value
        assert download.suggested_filename == 'autovalutazione-sito.txt'
        assert Path(download.path()).read_text() == report
        page.locator('#check-0').select_option('no'); expect(page.locator('#checklist-result')).to_be_hidden()
        page.locator('#checklist-form button[type=reset]').click(); expect(page.locator('#check-0')).to_have_value('')
        for i in range(8): page.locator(f'#check-{i}').select_option('unknown')
        page.locator('#checklist-form button[type=submit]').click(); expect(page.locator('#checklist-status')).to_contain_text('8 aspetti da verificare')
        print('PASS: checklist incompleta, priorità, report misto/ignoto, copia/fallback, download e risultati invalidati.')

        page.goto(base + '/demo/')
        expect(page.locator('#schedule-status')).to_have_text('Fasce coperte: 1 su 6. Assegnazioni mancanti: 5.')
        expect(page.locator('#schedule-total')).to_contain_text('42 ore')
        page.locator('#coverage-target').fill('1'); expect(page.locator('#schedule-status')).to_contain_text('Fasce coperte: 6 su 6')
        page.locator('#shift-0-0').select_option('off'); expect(page.locator('#schedule-total')).to_contain_text('36 ore')
        page.locator('#coverage-target').fill('0'); expect(page.locator('#coverage-target')).to_have_attribute('aria-invalid', 'true'); expect(page.locator('.coverage-item')).to_have_count(0)
        page.locator('#schedule-reset').click(); expect(page.locator('#coverage-target')).to_have_value('2'); expect(page.locator('#shift-0-0')).to_have_value('morning')
        page.get_by_role('link', name='Parliamo del tuo lavoro', exact=True).click(); expect(page.locator('#service')).to_have_value('Un software su misura')
        print('PASS: turni sintetici, copertura, ore, input invalidi, ripristino e CTA contestuale.')

        no_js = browser.new_context(java_script_enabled=False)
        static_page = no_js.new_page()
        static_page.goto(base + '/progetti/'); expect(static_page.locator('.catalog-item')).to_have_count(3)
        static_page.goto(base + '/'); expect(static_page.locator('noscript p')).to_contain_text('simone.vacca@edu.unito.it'); expect(static_page.locator('#brief-button')).to_be_disabled()
        no_js.close()
        assert not errors, errors
        assert not failures, failures
        assert all(url.startswith(base) or url.startswith('blob:' + base) for url in requests), requests
        assert page.evaluate('localStorage.length') == 0
        assert context.cookies() == []
        browser.close()
        print('PASS: catalogo senza JavaScript, nessun errore JS/HTTP, richiesta esterna, cookie o localStorage nelle prove.')


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=os.environ.get('SITE_TEST_ROOT', str(ROOT))))
    thread = Thread(target=server.serve_forever, daemon=True); thread.start()
    try: verify(f'http://127.0.0.1:{server.server_port}')
    finally: server.shutdown(); server.server_close(); thread.join(timeout=5)
