# Il sito di Simone Vacca

> Aggiornamento operativo — 6 novembre 2026: dopo la spiegazione delle modifiche, il proprietario ha autorizzato un commit e il caricamento su GitHub. Le indicazioni precedenti di divieto di commit/push descrivono la fase del 5 novembre e sono superate per questo caricamento. La pubblicazione su Aruba resta separata e non viene eseguita. L’esito del push verrà verificato sul remoto; questo documento non ne anticipa il successo.

Portfolio commerciale e laboratorio statico: homepage, servizi, chi sono, tre progetti dimostrativi con approfondimenti, due esperimenti, strumenti e demo turni. **Queste modifiche sono locali. Non sono stati eseguiti commit, push o deployment per il nuovo master prompt.**

Il sito mantiene carta, nero, arancione e monogramma s/v. Non usa framework, database, servizi a pagamento o librerie esterne nel browser. Python serve solo in sviluppo per generare pagine e fare verifiche.

## Primo passo: aprire il sito

Dalla cartella del progetto, nel terminale:

```sh
python3 scripts/build_pages.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Il primo comando aggiorna le pagine locali. Il secondo avvia un server: sul tuo computer apri `http://127.0.0.1:8000`. Il terminale resta occupato finché premi Ctrl+C. Nell'ambiente cloud il browser viene usato internamente per i test; non presumere che il link locale sia raggiungibile dal tuo computer.

Questo server espone anche documenti interni: usalo solo in locale. Per l'hosting si prepara una cartella separata con soli file pubblici.

## Cosa puoi aprire

| Percorso | Funzione |
| --- | --- |
| `/` | Servizi in sintesi, scenari, calcolatore completo, metodo, FAQ e contatti. |
| `/servizi/`, `/chi-sono/` | Proposta professionale e presentazione personale verificata. |
| `/progetti/` | Catalogo generato da schede, con tre approfondimenti. |
| `/lab/` | Catalogo degli esperimenti personali. |
| `/lab/elenchi/` | Pulizia di righe duplicate, già presente e conservata. |
| `/lab/percorso/` | Visualizzazione BFS e Dijkstra con ostacoli e terreno pesato. |
| `/strumenti/` | Accesso al calcolatore esistente e alla checklist. |
| `/strumenti/checklist/` | Autovalutazione del sito con report copiabile/scaricabile. |
| `/demo/` | Turni e copertura di un'attività immaginaria. |

Il calcolatore rimane **uno solo**, nella homepage. Le altre pagine lo collegano. I contatti rimangono nella sezione `/#contatti` per evitare duplicazioni.

## Dove modificare

- `index.html`, `app.js`, `style.css`: homepage, comportamenti e stile condiviso. La navigazione e i metadati nei blocchi marcati sono aggiornati dal generatore.
- `contenuti.js`: email pubblica configurabile, attualmente `simone.vacca@edu.unito.it`. Dopo averla modificata, rigenera le pagine per aggiornare anche il recapito senza JavaScript.
- `content/progetti/*.json`: schede autentiche da trasformare in pagine.
- `templates/`: contenuti e layout delle nuove pagine; **modifica qui**, non negli HTML generati.
- `lab/`, `strumenti/`, `demo/`: JavaScript indipendente per ogni applicazione.
- `scripts/build_pages.py`: generatore senza dipendenze; aggiorna anche sitemap e lista pubblica.

La pagina “Chi sono” usa i fatti forniti dal proprietario. Nessuna fotografia, esperienza di lavoro o sede è stata inventata. Vedi [CONTENT-GUIDE.md](CONTENT-GUIDE.md) per aggiungere contenuti passo passo.

## Controlli rapidi

```sh
python3 scripts/build_pages.py --check
python3 scripts/check_site.py
python3 scripts/check_js.py
node tests/algorithms.test.js
node tests/efficiency.test.js
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Per le prove complete installa gli strumenti **solo nell'ambiente di sviluppo**:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-test.txt
python3 -m playwright install chromium
USE_PLAYWRIGHT_BROWSER=1 python3 tests/browser_smoke.py
USE_PLAYWRIGHT_BROWSER=1 python3 tests/lab_smoke.py
USE_PLAYWRIGHT_BROWSER=1 python3 tests/platform_smoke.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

I test avviano e arrestano server temporanei locali. Senza pyftpdlib e pyOpenSSL le tre prove FTPS vengono saltate: leggere l'output, non considerarle superate. In questa macchina i pacchetti FTPS già disponibili sono sotto `/tmp/aruba-ftps-tests`; `PYTHONPATH=/tmp/aruba-ftps-tests` permette di usarli. Chromium di sistema viene usato omettendo `USE_PLAYWRIGHT_BROWSER`.

## Contatti e dati

Il modulo prepara una bozza **mailto**: il visitatore deve inviare dall'app di posta. La copia manuale resta disponibile. Non c'è invio dal server, raccolta lead o password email. Senza JavaScript il modulo è disabilitato e il recapito resta leggibile. Invio e ricezione reali devono essere provati dal proprietario.

Demo e strumenti elaborano dati nella pagina senza cookie applicativi, salvataggi o richieste esterne. Questo descrive il codice del sito: non è una certificazione legale o una verifica dei log Aruba.

## Pubblicazione

Il nuovo documento richiede che sia il proprietario a fare commit/push e che il deploy sia manuale. Il workflow preparato avvia per impostazione predefinita soltanto test e pacchetto; il trasferimento richiede la scelta esplicita `publish`. Nessun push avvia automaticamente la pubblicazione nella configurazione locale attuale.

Protocollo, directory e accesso Aruba devono ancora essere verificati prima dell'attivazione. Il precedente errore remoto `commit_refs_rules` non è stato risolto né ritentato. Non sono stati contattati servizi di produzione in questo intervento.

Leggi [DEPLOYMENT.md](DEPLOYMENT.md) per credenziali, backup e ripristino. [PROGRESS.md](PROGRESS.md) riporta stato e prove; [AUDIT.md](AUDIT.md) contiene evidenze e limiti; [ROADMAP.md](ROADMAP.md) distingue ciò che esiste dalle idee future.
