# Il sito di Simone Vacca

Un sito per presentare cosa puoi costruire per le aziende. In seguito ospiterà anche un laboratorio di esperimenti. Si procede una fase alla volta: **la Fase 0 è completata; nella Fase 1 sono stati configurati il contatto email e il primo miglioramento della homepage**. Pagine progetto e laboratorio sono ancora da realizzare.

La homepage mantiene colori crema e arancio, presenta esplicitamente i tre servizi e conserva una nota personale sugli studi e sulla curiosità di Simone. I paragrafi principali sono di circa 18 pixel; i testi secondari partono da 14 pixel. La disposizione si adatta a telefono e testo ingrandito. Le modifiche vengono salvate su GitHub tramite commit e push autorizzati; la pubblicazione su Aruba richiede un passaggio separato.

## Da dove partire

Non devi leggere tutta la documentazione insieme. Comincia da questa pagina; [ROADMAP.md](ROADMAP.md) indica il passo successivo. Il sito usa HTML, CSS e JavaScript, senza installazioni di pacchetti, database o compilazione.

| File | A cosa serve |
| --- | --- |
| `index.html` | Testi e struttura della pagina principale. |
| `style.css` | Colori, caratteri e disposizione degli elementi. |
| `app.js` | Scenari interattivi, calcolatore, modulo e visualizzazione progetti. |
| `contenuti.js` | Email pubblica e lista dei progetti da mostrare. |
| `assets/favicon.svg` | Piccola icona della scheda del browser. |
| `scripts/check_site.py` | Controllo automatico dei collegamenti interni e delle risorse. |
| `tests/browser_smoke.py` | Prova delle funzioni principali in un browser automatico. |
| `.github/workflows/deploy.yml` | Controlli statici ad avvio manuale su GitHub; nessun caricamento su Aruba. |

## Aprire il sito durante lo sviluppo

Nell'ambiente cloud Python 3 e Node.js sono già disponibili. Python avvia un piccolo server: un programma che consegna i file al browser. Node.js serve soltanto a controllare la sintassi JavaScript; non è necessario al sito su Aruba.

Nel terminale, cioè la finestra in cui si scrivono i comandi, esegui:

```sh
cd /workspace/website-project
python3 -m http.server 8000 --bind 127.0.0.1
```

Il comando resta attivo: è normale. Per fermarlo premi **Ctrl+C** nello stesso terminale. Su un tuo computer sostituisci il percorso con la cartella del progetto; il sito sarà visibile nel browser all'indirizzo locale indicato dal server, porta 8000. Nell'interfaccia cloud di onboarding i link di anteprima locali non sono supportati: qui le verifiche avvengono internamente.

Questa copia di sviluppo non modifica il sito pubblicato su Aruba.

## Controllare che funzioni

In un secondo terminale, nella cartella del progetto:

```sh
python3 scripts/check_site.py
node --check app.js
node --check contenuti.js
```

Il primo comando segnala file o destinazioni interne mancanti. Gli altri cercano errori di scrittura nel JavaScript: nessun messaggio e codice di uscita 0 significano che la sintassi è valida. Questi controlli da soli non provano le interazioni.

Nell'ambiente cloud è disponibile anche una prova automatica con Chromium:

```sh
python3 tests/browser_smoke.py
```

Il test avvia e arresta da solo un server temporaneo; non serve prima avviare la porta 8000. Richiede gli strumenti di test Playwright per Python e Chromium, già presenti in questa macchina. Non sono dipendenze del sito e non vanno caricati su Aruba. Su un altro computer, se mancano, puoi seguire intanto i controlli manuali in [CHECKLIST.md](CHECKLIST.md).

Su GitHub è predisposto il workflow **Controlli manuali del sito**, nella sezione **Actions**. Con **Run workflow** si avviano il controllo dei collegamenti e della sintassi JavaScript. Il nome del file è ancora `deploy.yml`, ma il suo contenuto non trasferisce file su Aruba e non si avvia a ogni push. Non esegue i test browser: quelli restano un controllo distinto. Non è stato avviato su GitHub durante questa preparazione.

## Contatti e progetti: situazione attuale

In `contenuti.js` l'email pubblica è `simone.vacca@edu.unito.it`, scelta dal proprietario. La lista progetti è ancora vuota, quindi la sezione progetti resta nascosta.

Il visitatore può cliccare sull'indirizzo oppure compilare il modulo. Il pulsante prepara un collegamento `mailto`: chiede al dispositivo di aprire l'app di posta con destinatario, oggetto e messaggio già compilati. Il visitatore controlla la bozza e preme **Invia** nella propria app. Il sito non spedisce email dal server e non usa la password della tua casella.

Se l'app di posta non si apre o non è configurata, il testo preparato resta disponibile da copiare; il destinatario è visibile nella pagina. La verifica automatica controlla i dati preparati, sostituendo soltanto l'apertura dell'app esterna con un registratore nel test. L'apertura reale della posta e la ricezione devono ancora essere provate su un dispositivo del proprietario. Il test controlla anche che senza email configurata torni disponibile la sola preparazione del testo.

La configurazione del contatto viene versionata insieme al sito. Il salvataggio su GitHub non la pubblica automaticamente su Aruba.

Per aggiungere un progetto verificato, gli attuali campi supportati sono `titolo`, `tipo`, `descrizione`, `url` e `immagine` (facoltativa, un percorso sotto `assets/`). La lista `progetti` contiene un oggetto per ogni lavoro. Nella Fase 1 prepareremo insieme il primo inserimento e distingueremo lavori reali ed esperimenti. Non occorre compilare schede inventate adesso.

## Come conserviamo le versioni

Git registra la storia del progetto; GitHub ne conserva una copia online. Un **commit** è un punto salvato nella storia; un **push** trasferisce i commit a GitHub. Nessuna di queste operazioni pubblica automaticamente su Aruba nella configurazione attuale.

Il 5 novembre 2026 hai autorizzato l'assistente a eseguire commit e push delle modifiche correnti dopo la verifica. Per le attività successive si seguiranno le tue indicazioni; merge, tag e pubblicazione su Aruba richiedono una richiesta specifica. Per vedere le modifiche prima di salvarle nella storia:

```sh
git status --short
git diff
```

`git diff` mostra le differenze dei file già tracciati; i file nuovi vanno aperti e letti a parte. Prima di tornare a una versione precedente, salva una copia del lavoro attuale fuori dalla cartella pubblica. Guarda `git log --oneline` per individuare la versione e ripristina solo i file necessari con assistenza: non usare comandi che cancellano tutto. Per il ripristino del sito online segui [DEPLOYMENT.md](DEPLOYMENT.md).

## Le altre guide

- [AUDIT.md](AUDIT.md): cosa è stato verificato e quali problemi restano.
- [ARCHITECTURE.md](ARCHITECTURE.md): come sono collegati i file e come potrà crescere il sito.
- [ROADMAP.md](ROADMAP.md): fasi future, chiaramente separate dal lavoro fatto.
- [CHECKLIST.md](CHECKLIST.md): verifiche prima di una pubblicazione.
- [DEPLOYMENT.md](DEPLOYMENT.md): pubblicazione, backup e ripristino su Aruba.
