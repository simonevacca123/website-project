"""Verifica la homepage corrente. Richiede Playwright Python e Chromium.

Non invia email e non contatta Aruba. Il server è temporaneo e locale.
"""

from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
from shutil import which
from threading import Thread
from urllib.parse import parse_qs, unquote, urlsplit
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
CONTACT_EMAIL = 'simone.vacca@edu.unito.it'


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def verify(base):
    for path, mime in [
        ('/', 'text/html'), ('/app.js', 'javascript'),
        ('/contenuti.js', 'javascript'), ('/style.css', 'text/css'),
        ('/assets/favicon.svg', 'image/svg+xml'),
    ]:
        with urlopen(base + path, timeout=10) as response:
            assert response.status == 200, path
            assert mime in response.headers['Content-Type'], path
            assert response.read(), path
    print('PASS 1/7: cinque risorse pubbliche disponibili con tipo corretto')

    with sync_playwright() as p:
        executable = None if os.environ.get('USE_PLAYWRIGHT_BROWSER') == '1' else (which('chromium') or which('chromium-browser'))
        options = {'executable_path': executable} if executable else {}
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'], **options)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000})
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        # Esegue lo stesso app.js, sostituendo soltanto l'effetto esterno
        # window.location.href con un registratore. Non apre app di posta.
        source = (ROOT / 'app.js').read_text(encoding='utf-8')
        test_source = ('globalThis.__testMailtoRequests = [];\n((window) => {\n'
                       + source + '\n})({PORTFOLIO: globalThis.PORTFOLIO, location: {'
                       'set href(value) { globalThis.__testMailtoRequests.push(value); }}});')
        page.route('**/app.js', lambda route: route.fulfill(
            status=200, content_type='text/javascript', body=test_source,
        ))
        page.goto(base, wait_until='networkidle')
        expect(page).to_have_title('Simone Vacca — Software utile al tuo lavoro')
        expect(page.locator('#year')).to_have_text(str(datetime.now().year))
        page.keyboard.press('Tab')
        expect(page.locator('.skip')).to_be_focused()
        page.locator('[data-case="manual"]').focus()
        page.keyboard.press('Space')
        expect(page.locator('[data-case="manual"]')).to_have_attribute('aria-pressed', 'true')
        summary = page.locator('.faq-section summary').first
        summary.focus()
        page.keyboard.press('Enter')
        expect(page.locator('.faq-section details').first).to_have_attribute('open', '')
        print('PASS 2/7: titolo, anno e interazioni principali da tastiera')

        for key, title, service in [
            ('requests', 'Ogni richiesta ha un prossimo passo.', 'Un software su misura'),
            ('manual', 'Inserisci una volta. Riutilizzi il dato.', 'Un software su misura'),
            ('website', 'Capire. Fidarsi. Contattarti.', 'Un sito web'),
        ]:
            button = page.locator(f'[data-case="{key}"]')
            button.click()
            expect(button).to_have_attribute('aria-pressed', 'true')
            expect(page.locator('[data-case][aria-pressed="true"]')).to_have_count(1)
            expect(page.locator('#comparison .after h3')).to_have_text(title)
            page.locator('#case-cta').click()
            expect(page.locator('#service')).to_have_value(service)
        print('PASS 3/7: tre scenari e scelta del servizio nel modulo')

        expect(page.locator('#hours')).to_have_text('5')
        page.locator('#minutes').fill('60')
        page.locator('#days').fill('10')
        page.locator('#reduction').fill('75')
        expect(page.locator('#hours')).to_have_text('7,5')
        expect(page.locator('#before-hours')).to_have_text('10 h')
        expect(page.locator('#after-hours')).to_have_text('2,5 h')
        page.locator('#reduction').fill('0')
        expect(page.locator('#hours')).to_have_text('0')
        page.locator('#reduction').fill('100')
        expect(page.locator('#after-hours')).to_have_text('0 h')
        page.locator('#reset-calc').click()
        expect(page.locator('#hours')).to_have_text('5')
        print('PASS 4/7: calcolatore, estremi della riduzione e ripristino')

        page.locator('#name').fill('   ')
        page.locator('#brief-button').click()
        expect(page.locator('#name')).to_have_attribute('aria-invalid', 'true')
        expect(page.locator('#name')).to_be_focused()
        page.locator('#name').fill('Mario Rossi')
        page.locator('#brief-button').click()
        expect(page.locator('#message')).to_have_attribute('aria-invalid', 'true')
        expect(page.locator('#message')).to_be_focused()
        assert page.evaluate('globalThis.__testMailtoRequests') == []
        expect(page.locator('#email-link')).to_be_visible()
        expect(page.locator('#email-link')).to_have_text(CONTACT_EMAIL)
        email_link = urlsplit(page.locator('#email-link').get_attribute('href'))
        assert email_link.scheme == 'mailto' and unquote(email_link.path) == CONTACT_EMAIL
        expect(page.locator('#brief-button')).to_have_text('Apri la richiesta nella tua email')
        expect(page.locator('#form-note')).to_contain_text('Si aprirà la tua app di posta')
        page.locator('#message').fill('Vorrei semplificare le richieste dei clienti.')
        page.locator('#brief-button').click()
        expect(page.locator('#brief-result')).to_be_visible()
        expected = ('Ciao Simone,\nsono Mario Rossi.\n\nMi interessa: Un sito web.\n\n'
                    'Vorrei semplificare le richieste dei clienti.')
        expect(page.locator('#brief-text')).to_have_value(expected)
        expect(page.locator('#brief-status')).to_contain_text('Inviala dalla tua app di posta')
        expect(page.locator('#brief-status')).to_contain_text(CONTACT_EMAIL)
        navigation_requests = page.evaluate('globalThis.__testMailtoRequests')
        assert len(navigation_requests) == 1, navigation_requests
        mailto_requests = [urlsplit(url) for url in navigation_requests]
        assert mailto_requests[0].scheme == 'mailto'
        assert unquote(mailto_requests[0].path) == CONTACT_EMAIL
        assert parse_qs(mailto_requests[0].query) == {
            'subject': ['Richiesta: Un sito web'], 'body': [expected],
        }
        expect(page.locator('#project-section')).to_be_hidden()
        print('PASS 5/7: validazione, indirizzo pubblico, destinatario/oggetto/testo mailto; nessuna email inviata')

        context.grant_permissions(['clipboard-read', 'clipboard-write'])
        page.locator('#copy-brief').click()
        expect(page.locator('#brief-status')).to_have_text('Testo copiato. Nessun messaggio inviato dal sito.')
        assert page.evaluate('navigator.clipboard.readText()') == expected
        page.evaluate("() => { navigator.clipboard.writeText = () => Promise.reject(new Error('Test: accesso negato')); }")
        page.locator('#copy-brief').click()
        expect(page.locator('#brief-status')).to_contain_text('Selezione pronta')
        assert page.locator('#brief-text').evaluate('(el) => el.selectionEnd - el.selectionStart') == len(expected)
        print('PASS 6/7: copia negli appunti e alternativa quando la copia è negata')

        output = ROOT / 'test-results'
        output.mkdir(exist_ok=True)
        for width in [320, 390, 540, 768, 800, 1024, 1440]:
            page.set_viewport_size({'width': width, 'height': 900})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), f'overflow a {width}px'
            expect(page.locator('h1')).to_be_visible()
            # I testi effettivamente presenti nella pagina, comprese note e demo,
            # devono mantenere una dimensione leggibile a ogni larghezza.
            small_text = page.evaluate('''() => {
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                const small = [];
                while (walker.nextNode()) {
                    const node = walker.currentNode;
                    const el = node.parentElement;
                    if (!node.textContent.trim() || !el.getClientRects().length) continue;
                    if (el.closest('script, style, svg, [hidden], .skip')) continue;
                    const size = parseFloat(getComputedStyle(el).fontSize);
                    if (size < 14) small.push({text: node.textContent.trim(), size});
                }
                return small;
            }''')
            assert not small_text, (width, small_text)
            # Controlla anche gli scenari più densi: allargando i caratteri
            # non devono debordare dai loro contenitori su telefono.
            for key in ['requests', 'manual', 'website']:
                page.locator(f'[data-case="{key}"]').click()
                assert page.locator('#comparison').evaluate('(el) => el.scrollWidth <= el.clientWidth'), (width, key)
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), (width, key)
            if width in (390, 1440):
                page.screenshot(path=str(output / f'homepage-{width}.png'), full_page=True)
        for width in [320, 640]:
            page.set_viewport_size({'width': width, 'height': 900})
            page.evaluate("document.documentElement.style.fontSize = '200%'")
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), f'overflow con testo al 200% a {width}px'
            page.evaluate("document.documentElement.style.fontSize = ''")
        page.emulate_media(reduced_motion='reduce')
        assert page.locator('html').evaluate('(el) => getComputedStyle(el).scrollBehavior') == 'auto'
        assert not errors, errors
        print('PASS 7/7: sette larghezze, testi >=14px, scenari senza overflow, testo al 200%, movimento ridotto, nessun errore JavaScript')
        print('Screenshot salvati in test-results/ (cartella esclusa da Git).')

        # Verifica anche il comportamento senza recapito, con una configurazione
        # temporanea fornita soltanto al browser del test.
        fallback = browser.new_page()
        fallback_errors = []
        fallback.on('pageerror', lambda error: fallback_errors.append(str(error)))
        fallback.route('**/contenuti.js', lambda route: route.fulfill(
            status=200, content_type='text/javascript',
            body='window.PORTFOLIO = {email: "", progetti: []};',
        ))
        fallback.goto(base, wait_until='networkidle')
        expect(fallback.locator('#email-link')).to_be_hidden()
        expect(fallback.locator('#brief-button')).to_contain_text('Prepara la richiesta')
        fallback.locator('#name').fill('Mario Rossi')
        fallback.locator('#message').fill('Vorrei un sito per la mia attività.')
        fallback.locator('#brief-button').click()
        expect(fallback.locator('#brief-status')).to_contain_text('nessun messaggio è stato inviato')
        expect(fallback.locator('#brief-result')).to_be_visible()
        assert not fallback_errors, fallback_errors
        fallback.close()
        browser.close()
        print('PASS aggiuntivo: richiesta copiabile anche senza indirizzo configurato')


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
