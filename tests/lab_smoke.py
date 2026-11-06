"""Verifica il laboratorio nel browser, senza servizi esterni."""

import os
from functools import partial
from http.server import ThreadingHTTPServer
from shutil import which
from threading import Thread
from playwright.sync_api import expect, sync_playwright
from browser_smoke import ROOT, QuietHandler


def verify(base):
    with sync_playwright() as p:
        executable = None if os.environ.get('USE_PLAYWRIGHT_BROWSER') == '1' else (which('chromium') or which('chromium-browser'))
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'], **({'executable_path': executable} if executable else {}))
        context = browser.new_context(viewport={'width': 1440, 'height': 1000})
        page = context.new_page()
        errors, requests = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: requests.append(request.url))
        page.goto(base, wait_until='networkidle')
        page.get_by_role('link', name='Laboratorio', exact=True).click()
        expect(page).to_have_url(base + '/lab/')
        expect(page.locator('nav [aria-current="page"]')).to_have_text('Laboratorio')
        page.goto(base + '/lab/elenchi/', wait_until='networkidle')
        page.locator('#cleaner-form button[type="submit"]').click()
        expect(page.locator('#source-list')).to_be_focused()
        expect(page.locator('#source-list')).to_have_attribute('aria-invalid', 'true')
        page.locator('#load-example').click()
        network_before = len(requests)
        page.locator('#cleaner-form button[type="submit"]').click()
        expect(page.locator('#input-count')).to_have_text('5')
        expect(page.locator('#unique-count')).to_have_text('3')
        expect(page.locator('#duplicate-count')).to_have_text('2')
        expect(page.locator('#clean-list')).to_have_value('Controllare preventivo\nAggiornare catalogo\nContattare fornitore')
        assert len(requests) == network_before
        page.locator('#ignore-case').uncheck()
        expect(page.locator('#cleaner-result')).to_be_hidden()
        page.locator('#cleaner-form button[type="submit"]').click()
        expect(page.locator('#unique-count')).to_have_text('4')
        print('PASS: collegamento dalla home, errori, esempio e confronto maiuscole/minuscole')

        context.grant_permissions(['clipboard-read', 'clipboard-write'])
        page.locator('#copy-list').click()
        expected = page.locator('#clean-list').input_value()
        assert page.evaluate('navigator.clipboard.readText()') == expected
        page.evaluate("() => { navigator.clipboard.writeText = () => Promise.reject(new Error('Test')); }")
        page.locator('#copy-list').click()
        expect(page.locator('#cleaner-status')).to_contain_text('Testo selezionato')
        assert page.locator('#clean-list').evaluate('(el) => el.selectionEnd - el.selectionStart') == len(expected)
        page.locator('#clear-list').click()
        expect(page.locator('#source-list')).to_have_value('')
        expect(page.locator('#cleaner-result')).to_be_hidden()
        page.locator('#source-list').fill('café\ncafe\u0301\n<img src=x onerror=alert(1)>')
        page.locator('#cleaner-form button[type="submit"]').click()
        expect(page.locator('#unique-count')).to_have_text('2')
        expect(page.locator('#clean-list')).to_have_value('café\n<img src=x onerror=alert(1)>')
        expect(page.locator('.lab-tool img')).to_have_count(0)
        print('PASS: copia e alternativa, reset, accenti Unicode e testo HTML trattato come testo')

        page.locator('#source-list').fill('\n'.join('Voce ' + str(i) for i in range(500)))
        page.locator('#cleaner-form button[type="submit"]').click()
        expect(page.locator('#unique-count')).to_have_text('500')
        page.locator('#source-list').fill('\n'.join('Voce ' + str(i) for i in range(501)))
        page.locator('#cleaner-form button[type="submit"]').click()
        expect(page.locator('#cleaner-status')).to_contain_text('massimo 500')
        expect(page.locator('#cleaner-result')).to_be_hidden()
        page.locator('#source-list').evaluate("el => { el.value = 'x'.repeat(20001); }")
        page.locator('#cleaner-form button[type="submit"]').click()
        expect(page.locator('#source-list')).to_have_attribute('aria-invalid', 'true')
        print('PASS: limiti di 500 righe e 20.000 caratteri')

        page.locator('#clear-list').click()
        page.locator('#load-example').click()
        page.locator('#cleaner-form button[type="submit"]').click()
        output = ROOT / 'test-results'
        output.mkdir(exist_ok=True)
        for width in [320, 390, 768, 1440]:
            page.set_viewport_size({'width': width, 'height': 1000})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
            page.screenshot(path=str(output / f'laboratorio-{width}.png'), full_page=True) if width in (390, 1440) else None
        page.set_viewport_size({'width': 320, 'height': 1000})
        page.evaluate("document.documentElement.style.fontSize = '200%'")
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors, errors
        assert all(url.startswith(base) for url in requests), requests
        browser.close()
        print('PASS: quattro larghezze, testo al 200%, nessun errore JavaScript o richiesta esterna')


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        verify(f'http://127.0.0.1:{server.server_port}')
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
