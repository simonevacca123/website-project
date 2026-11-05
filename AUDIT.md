# Verifica iniziale — Fase 0

Data: 5 novembre 2026. Base analizzata: commit `186f2ac`, importazione dello ZIP fornito. Le verifiche riguardano **la copia di sviluppo**; non è stato confrontato o modificato il sito online su Aruba.

Il controllo iniziale riportato sotto è storico. Il contatto e la homepage sono stati successivamente aggiornati: vedere gli aggiornamenti della Fase 1 alla fine di questo documento.

Una baseline è una situazione iniziale conosciuta: serve per capire, dopo ogni modifica, se qualcosa che prima funzionava si è rotto.

## Risultato

La homepage attuale funziona nelle prove locali descritte sotto. Non sono stati modificati i cinque file pubblici. Sono state aggiunte guide, regole di lavoro, `.gitignore` e controlli ripetibili. Non sono stati eseguiti commit, push, merge, tag o deploy in questa fase.

Portfolio esteso, case study, Digital Lab, metadati aggiuntivi e automazione Aruba sono ancora pianificati. I test non dimostrano che il sito generi contatti o che l'hosting sia pronto per il deploy.

## Controlli eseguiti, esito finale

Ambiente: Python 3.12.14, Node.js 24.22.1, Chromium tramite Playwright Python.

| Controllo | Esito e perimetro |
| --- | --- |
| `python3 scripts/check_site.py` | Superato: 15 riferimenti statici della homepage, risorse e frammenti esistenti, nessun ID duplicato. |
| `node --check app.js` | Superato: sintassi JavaScript valida. |
| `node --check contenuti.js` | Superato: sintassi della configurazione valida. |
| `python3 tests/browser_smoke.py` | Superati tutti i 7 gruppi di verifica descritti qui sotto. |
| Esame visivo screenshot 390 e 1440 pixel | Contenuti disposti rispettivamente in una o più colonne; rilevato il limite dei simboli descritto fra le priorità. |

I sette gruppi browser verificano:

1. Risposta HTTP 200, tipo e contenuto non vuoto per HTML, CSS, due JavaScript e favicon.
2. Titolo, anno nel footer, primo accesso da tastiera al salto del contenuto, selezione scenario con Spazio e apertura FAQ con Invio.
3. Tutti i tre scenari, un solo pulsante selezionato e scelta coerente del servizio nel modulo.
4. Calcolo iniziale di 5 ore, esempio da 7,5 ore, riduzione 0%/100% e ripristino.
5. Nome composto solo da spazi e messaggio vuoto rifiutati; focus sul campo errato; testo della richiesta corretto; nessun invio dichiarato; email e progetti vuoti gestiti come previsto.
6. Copia negli appunti e selezione manuale del testo quando il permesso di copia viene negato nel test.
7. Nessuno scorrimento orizzontale del documento a 320, 390, 768 e 1440 pixel; movimento ridotto rispettato per lo scorrimento; nessun errore JavaScript durante le interazioni.

Gli screenshot sono in `test-results/`, esclusa da Git. Il test si basa sulla configurazione iniziale senza email e progetti: dovrà evolvere quando questi verranno aggiunti. Durante la sua preparazione è stata corretta la simulazione del rifiuto degli appunti nello script di test; non è stata necessaria una correzione al sito.

## Cosa funziona già bene

- Messaggio orientato a problemi comprensibili per piccole aziende.
- Coerenza di colori, titoli e sezioni: da conservare.
- Demo dichiarate come tali; il calcolatore presenta una stima, non una promessa di ricavi.
- Il modulo non simula un invio riuscito.
- Campi etichettati, elementi interattivi nativi, stati selezionati e focus visibile definito nel CSS.
- Nessuna libreria o font esterno richiesto dal codice attuale. I cinque file pubblici pesano complessivamente 37.572 byte non compressi: è una misura dei file, non un test di velocità o Core Web Vitals.

## Priorità per i prossimi piccoli interventi

| Priorità | Osservazione verificata | Intervento previsto |
| --- | --- | --- |
| Prima | `contenuti.js` ha email vuota: nessun recapito utilizzabile dal visitatore. | Scegliere un indirizzo reale pubblico, configurarlo e verificare il percorso verso la posta. Non è un guasto del server. |
| Prima | Nessun progetto configurato, quindi la sezione è nascosta. | Preparare una prima prova concreta, distinguendo demo e lavori reali; non inventare clienti. |
| Poi | Presentazione già presente, ma specializzazione AI dichiarata dal proprietario non esplicitata e servizi migliorabili. | Rivedere i testi in un intervento dedicato. |
| Poi | Title e description presenti; canonical, Open Graph, `sitemap.xml` e `robots.txt` assenti. | Verificare il dominio preferito e aggiungere gli elementi coerenti con le pagine effettivamente esistenti. L'assenza di robots non impedisce di per sé l'indicizzazione. |
| Poi | Alcuni simboli come le frecce appaiono come riquadri negli screenshot Chromium di questa macchina. | Verificare i font sui dispositivi di destinazione; valutare SVG per i simboli utili. Non è stato stabilito che accada anche sul sito pubblico. |
| Poi | Numerose scritte secondarie hanno dimensioni piccole nel CSS; il fallback della copia cita solo tasti da computer. | Controllare leggibilità, zoom e istruzioni per telefono durante la revisione accessibilità. |
| Prima di nuove pagine | `app.js` cerca direttamente gli elementi della homepage. | Separare le funzioni necessarie alle nuove pagine senza caricarvi indiscriminatamente tutto lo script. |

## Usabilità: lettura secondo le euristiche di Nielsen

Le euristiche sono criteri pratici per trovare ostacoli nell'uso; questa analisi non sostituisce una prova con utenti reali.

| Criterio | Situazione osservata / passo successivo |
| --- | --- |
| Stato visibile | Scenario selezionato, risultati del calcolo e messaggi del modulo sono visibili. |
| Linguaggio familiare | Gli esempi parlano di richieste, fogli e tempo, senza obbligare a capire termini tecnici. |
| Controllo dell'utente | Il calcolatore si ripristina e il modulo prepara una bozza senza invii automatici dal sito. |
| Coerenza | Pulsanti e colori sono coerenti; mantenere questa identità nelle pagine future. |
| Prevenzione errori | Campi obbligatori, limiti di lunghezza e controlli del modulo presenti; serve una casella reale verificata. |
| Riconoscimento | Tre situazioni esplicite e FAQ aiutano a orientarsi; mancano lavori consultabili. |
| Efficienza | Lo scenario precompila il servizio; la copia riduce la riscrittura della richiesta. |
| Semplicità visiva | Nessuna animazione complessa; da rivedere la leggibilità delle scritte piccole. |
| Recupero dagli errori | Messaggi portano al campo errato e la copia ha un'alternativa; migliorare il testo del fallback su telefono. |
| Aiuto | FAQ e note spiegano limiti del calcolo e invio; guide di manutenzione ora aggiunte nel repository. |

## Non verificato in questa fase

Invio reale di email, app di posta su telefono, casella del proprietario, Safari/Firefox, lettori di schermo, conformità completa WCAG, misure sistematiche del contrasto e dello zoom, metriche di prestazione, indicizzazione, impostazioni del dominio, configurazione TLS e accesso al pannello Aruba. I risultati su larghezze mobile in Chromium non equivalgono a test su un telefono fisico.

## Dati ancora da completare

Solo il primo dato serve al prossimo piccolo intervento; gli altri verranno affrontati più avanti:

1. Email reale da mostrare pubblicamente, senza password.
2. Materiale autorizzato di un primo progetto, oppure scelta di una demo esplicitamente dimostrativa.
3. Conferma dell'indirizzo preferito con o senza `www`, prima dei metadati definitivi.
4. Per la futura pubblicazione: protocollo sicuro, hostname e directory confermati dal pannello Aruba. Credenziali esclusivamente nei canali sicuri appropriati.

## File aggiunti in questa fase

`README.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `DEPLOYMENT.md`, `CHECKLIST.md`, `AUDIT.md`, `AGENTS.md`, `.gitignore`, `scripts/check_site.py`, `tests/browser_smoke.py`.

Il file `AGENTS.md` conserva per le prossime sessioni le regole del proprietario, compreso il divieto di eseguire commit e push. Nessuna funzionalità commerciale nuova è stata presentata come già implementata.

## Aggiornamento — Fase 1, contatto email

Data: 5 novembre 2026. Su richiesta del proprietario, `contenuti.js` ora contiene l'indirizzo pubblico `simone.vacca@edu.unito.it`. Non servono password o servizi nuovi. La logica già presente in `app.js` mostra il recapito e prepara un collegamento `mailto` alla compilazione del modulo; il visitatore invia poi dalla propria app di posta.

Verifiche eseguite con esito positivo:

- Controllo dei 15 riferimenti statici e della sintassi dei due JavaScript.
- I sette gruppi del test browser, aggiornati per il recapito configurato: indirizzo e pulsante visibili, nessuna apertura richiesta con campi invalidi, destinatario corretto, oggetto `Richiesta: Un sito web` e testo corrispondente ai dati inseriti.
- Copia del testo e selezione alternativa, scenari, calcolatore, tastiera, larghezze 320/390/768/1440 e assenza di errori JavaScript durante la prova.
- Caso aggiuntivo senza email, fornendo una configurazione temporanea soltanto al browser del test: il modulo continua a preparare testo senza dichiarare invii.

Il tentativo iniziale di lasciare aprire `mailto` al browser automatico è stato bloccato dall'ambiente. Il test finale esegue lo stesso codice dell'applicazione sostituendo soltanto `window.location.href` con un registratore dell'indirizzo preparato. Non aggira il blocco e non apre programmi esterni. La copia senza email è stata provata anche con lo script originale, senza questa sostituzione.

**Non verificati:** apertura dell'app di posta su un dispositivo reale, invio e ricezione di un messaggio, esistenza o stato della casella. La verifica automatica non invia email. Il proprietario potrà completare la prova manuale sul proprio dispositivo quando la versione sarà disponibile.

File interessati dal passo contatti: `contenuti.js`, `tests/browser_smoke.py`, `README.md`, `ROADMAP.md`, `AUDIT.md`. Nessuna modifica a HTML, CSS o logica di `app.js`. Non sono stati eseguiti commit, push o pubblicazione su Aruba.

Il prossimo intervento previsto è migliorare presentazione e chiarezza dei servizi. Email non più mancante; rimangono da raccogliere i materiali per il primo progetto e, più avanti, le informazioni tecniche dell'hosting.

## Aggiornamento — Homepage: presentazione e leggibilità

Data: 5 novembre 2026. Implementato nella copia di sviluppo il primo intervento sulla homepage richiesto dal proprietario.

- Presentazione esplicita di Simone e delle attività: siti web, applicazioni su misura e automazioni.
- Riepilogo dei servizi in tre voci; mantenuti slogan, palette crema/arancio e scenari dimostrativi.
- Nota personale sugli studi in informatica/AI e sulla curiosità, con testi orientati al dialogo diretto.
- Corpo principale di circa 18 pixel e testi secondari non inferiori a 14 nelle condizioni provate. Etichette e campi più grandi, focus visibile e spazi adattati al contenuto.
- Altezze flessibili per gli esempi, navigazione che va a capo e contenitori che rispettano il testo ingrandito.
- Frecce e simboli principali sostituiti con SVG; nessun font o pacchetto esterno aggiunto. Migliorata anche l'istruzione di copia manuale su telefono.

Verifiche finali eseguite:

| Verifica | Risultato |
| --- | --- |
| Collegamenti statici, inclusi i riferimenti SVG nell'HTML | 26 riferimenti validi, ID univoci. |
| Sintassi `app.js` e `contenuti.js` | Superata. |
| Browser: scenari, calcolatore, tastiera, contatti e appunti | Tutti i sette gruppi superati, più il caso aggiuntivo senza email. Nessun messaggio inviato. |
| Larghezze del browser | 320, 390, 540, 768, 800, 1024 e 1440 pixel: nessun overflow orizzontale del documento; tutti i tre scenari contenuti nella sezione. |
| Dimensioni del testo effettivamente presente | Nessun testo visibile inferiore a 14 pixel nei controlli alle sette larghezze. |
| Testo al 200% | Dimensione radice portata al 200% a 320 e 640 pixel, senza overflow orizzontale. È un test di ingrandimento del testo, non una verifica completa dello zoom di tutti i browser. |
| Movimento ridotto | Scorrimento automatico senza animazione quando richiesto. |
| Errori JavaScript | Nessuno nelle interazioni provate. |

Durante le prove sono stati individuati e corretti debordamenti dei servizi e dei testi lunghi con caratteri al 200%. La soluzione adatta griglie, contenitori e ritorno a capo; non nasconde il contenuto per far passare il controllo.

Contrasto calcolato per le combinazioni principali: testo su crema 14,44:1; testo secondario su crema 5,97:1; arancio su crema 5,21:1; note su sfondo scuro 9,69:1; testo secondario nei contatti 5,35:1. Queste misure superano 4,5:1 per le combinazioni elencate; non costituiscono una certificazione WCAG dell'intero sito.

Il contatto conserva `simone.vacca@edu.unito.it` e il comportamento `mailto` già verificato. Restano validi i limiti sulla posta esterna e sui dispositivi reali indicati sopra. Pagine progetti, laboratorio e metadati aggiuntivi restano pianificati. Nessun commit, push o caricamento su Aruba eseguito.

File applicativi modificati in questo passo: `index.html`, `style.css`, `app.js`. Aggiornati i controlli in `scripts/check_site.py` e `tests/browser_smoke.py`, oltre a README, architettura, roadmap, checklist, audit e regole di lavoro. `contenuti.js` conserva la precedente modifica autorizzata del recapito.

## Aggiornamento — Autorizzazione al salvataggio su GitHub

Il 5 novembre 2026, dopo aver visionato l'intervento sulla homepage, il proprietario ha autorizzato l'assistente a eseguire commit e push delle modifiche correnti. Questa indicazione sostituisce per questo salvataggio il precedente divieto riportato nelle sezioni storiche. Le regole di lavoro, il README e la roadmap sono stati aggiornati di conseguenza.

Il salvataggio richiesto comprende homepage, contatto email, documentazione e strumenti di verifica. Screenshot generati, cache, backup e configurazioni riservate restano esclusi tramite `.gitignore`. Non è stata autorizzata la pubblicazione su Aruba.

### Workflow remoto rilevato durante la sincronizzazione

Il ramo remoto conteneva un aggiornamento aggiuntivo, `806af65`, che configurava un trasferimento FTP su Aruba a ogni push su `main`, senza un elenco dei soli file pubblici. L'aggiornamento remoto è stato preservato nella cronologia e integrato prima di aggiungere le modifiche locali.

Per rispettare la richiesta di aggiornare GitHub senza pubblicare su Aruba, `.github/workflows/deploy.yml` è stato convertito in **Controlli manuali del sito**: solo `workflow_dispatch`, permessi di lettura del codice e controlli locali di collegamenti e sintassi. Nessun passo FTP e nessun accesso ai segreti Aruba. Il precedente trasferimento è consultabile nella cronologia; la futura pubblicazione resta subordinata alle verifiche descritte in `DEPLOYMENT.md`.

Le istruzioni del workflow corrispondono ai controlli eseguiti nella macchina di sviluppo. L'esecuzione del workflow sui runner GitHub non è stata avviata o verificata. Non sono stati ispezionati i precedenti run GitHub né lo stato del sito online.

## Aggiornamento — Pubblicazione automatica richiesta dal proprietario

Il 5 novembre 2026 il proprietario ha esplicitamente richiesto che i commit arrivati su GitHub aggiornino il sito online e ha autorizzato il ripristino di questo flusso. Questa richiesta sostituisce il precedente vincolo di solo avvio manuale per la pubblicazione su main.

Implementato il workflow **Pubblica sito su Aruba** con trigger push su main e workflow_dispatch, esecuzioni seriali, controlli statici, test browser, test di trasferimento, pacchetto pubblico esplicito, backup conservato prima della scrittura, trasferimento FTPS con TLS verificato, verifica dei file caricati e confronto della homepage HTTPS con il contenuto atteso. Non sono consentiti FTP non cifrato o disattivazione della verifica del certificato.

`scripts/deploy_site.py` esclude documentazione, test, script e credenziali dal pacchetto; carica l'HTML per ultimo e non elimina file remoti preesistenti. Cerca una sola directory riconoscibile come il sito del proprietario; se la ricerca è ambigua, richiede FTP_SERVER_DIR. Verifica che i file non siano cambiati dopo il backup. In caso di errore di trasferimento tenta di ripristinare i file preesistenti coinvolti; se la connessione non è più utilizzabile il ripristino può fallire e resta disponibile l'artefatto salvato.

Verifiche locali completate:

- 16 test, tutti passati e nessuno saltato: pacchetto ripetibile, esclusione di file riservati e symlink, backup integro senza scritture, cartella ambigua/estranea rifiutata, modifiche esterne dopo il backup rilevate, trasferimento interrotto e ripristino, file estranei conservati, credenziali mancanti bloccate prima della connessione.
- Le prove di integrazione usano un vero server FTPS locale e un server HTTPS locale. Certificato di test reso attendibile esplicitamente: verifica TLS attiva. Un certificato non attendibile viene rifiutato; una versione HTTPS differente viene rilevata.
- Sette gruppi di test browser, più il caso senza email, passati con Chromium di sistema. Il runner GitHub installerà invece il browser gestito dalla versione fissata di Playwright: questo passaggio sul runner non è ancora stato verificato.
- 26 riferimenti statici validi, sintassi JavaScript valida, pacchetto corrente composto dai cinque soli file pubblici. YAML del workflow letto e verificato per trigger, permessi, serializzazione e ordine backup/artefatto/caricamento.

Limiti esterni ancora presenti: l'API GitHub, la guida ufficiale Aruba e il dominio pubblico sono bloccati dal proxy di questa macchina con 403. Non è stato quindi possibile leggere gli errori dei precedenti run, elencare i Secrets GitHub o verificare il supporto FTPS e la cartella del vero hosting. La presenza di GH_TOKEN è stata controllata senza leggerne o mostrarne il valore; l'operazione GitHub API è stata comunque negata dalla rete.

Sono state salvate nella bozza dell'ambiente le aggiunte di rete api.github.com, guide.hosting.aruba.it, www.simonevacca.it e simonevacca.it, preservando i preset esistenti. La bozza non è applicata al runtime: occorrono revisione/salvataggio nelle impostazioni e pubblicazione dell'ambiente. Nessun nuovo Secret FTP è stato richiesto nell'ambiente cloud; il workflow riutilizza i nomi dei GitHub Actions Secrets già previsti dal tentativo precedente.

Il completamento dei test locali non dimostra un deploy riuscito su Aruba. Occorre ancora controllare il primo run reale e gli eventuali dati mancanti. Questa distinzione resta necessaria finché l'accesso esterno non è disponibile o il proprietario non fornisce l'esito del run.
