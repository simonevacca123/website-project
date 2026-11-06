# Architettura attuale

## Runtime statico

Aruba serve HTML, CSS, JavaScript e asset. Ogni route ha il proprio `index.html`, quindi funziona anche da URL diretto senza router server, SPA o Node persistente. Il comportamento effettivo della directory pubblica del vero hosting resta da verificare.

La homepage è conservata e modificata incrementalmente. `app.js` gestisce scenari, contatti e UI del calcolatore; `strumenti/efficiency.js` contiene le formule pure. Nessuna seconda implementazione del calcolatore.

## Contenuti e generazione

`content/progetti/*.json` → `scripts/build_pages.py` → catalogo, case study e Lab in HTML. Le schede vengono validate, filtrate per `pubblicato: true` ed escaped. Gli URL ammettono HTTPS o directory interne con slug sicuri. Le bozze non sono inviate al browser. `content/bozze` e `content/blog` non vengono letti dal generatore.

`templates/layout.html` contiene shell comune; `templates/*.html` i corpi delle nuove pagine. La generazione aggiorna solo due blocchi marcati della homepage (navigazione e SEO). Gli output sono normali file leggibili, disponibili anche senza eseguire il generatore sul server. `--check` verifica la riproducibilità degli output e rileva modifiche manuali agli HTML generati.

La generazione aggiorna `sitemap.xml`, `robots.txt` e `scripts/public-files.json`. Quest'ultimo è un elenco interno esplicito: lo script di deployment aggiunge solo tali file e gli asset consentiti al pacchetto. Non esiste una copia indiscriminata del repository. Gli HTML vecchi rimasti fuori manifest non vengono pubblicati; le versioni già online richiedono un ritiro esplicito perché non si cancellano file remoti.

## Applicazioni indipendenti

- `lab/lab.js`: pulizia elenchi, ora caricata da `/lab/elenchi/`; confronto Unicode NFC, Set, nessun salvataggio.
- `lab/percorso/algorithms.js`: BFS e Dijkstra puri, esportabili per test Node; `ui.js` gestisce mappa, timer, tastiera e stati. Modifiche o reset annullano l'animazione.
- `strumenti/checklist.js`: report da risposte esplicite, con invalidazione al cambio input, copia/fallback e file testo tramite Blob locale.
- `demo/turni.js`: stato sintetico in memoria; una fascia per persona/giorno, conteggi per fascia e totale ore. Nessuna gestione personale reale.

Nessuno di questi script carica `app.js`. Il CSS comune usa componenti semplici e stili specifici alle demo. Il costo del CSS condiviso è misurato nell'audit; non servono librerie di componenti o bundler.

## Contatti e integrazioni future

Il recapito è in `contenuti.js`. Il modulo prepara il testo e apre `mailto`; un futuro trasporto server-side sostituirà soltanto quella parte dopo aver definito endpoint, validazione server, limiti, spam, gestione errori, privacy e conservazione. Il messaggio “inviato” sarà mostrato solo dopo una risposta reale del servizio.

Per future app con backend usare un endpoint HTTPS configurato, con timeout e stato di indisponibilità; non inserire API key nel frontend. Isolare l'app su un hosting adatto o sottodominio, mantenendo portfolio e demo statiche autonomi. Autenticazione, CORS e database saranno valutati sulla singola funzione, non predisposti come infrastruttura vuota.

## Deployment predisposto

Solo avvio manuale GitHub Actions, scelta `publish` false di default. Test e pacchetto precedono qualsiasi connessione remota. FTPS esplicito con TLS verificato è l'implementazione predisposta, non una dichiarazione del supporto del piano Aruba. Backup salvato come artefatto prima delle scritture, verifica hash, ripristino best effort, controllo HTTPS finale. Vedi DEPLOYMENT.md per limiti e autorizzazioni.
