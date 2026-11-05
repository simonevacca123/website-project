# Come è costruito il sito

## Com'è adesso

Il server invia i file così come sono. Non c'è un programma sul server che elabora richieste commerciali o salva dati. Questa struttura è adatta a una vetrina sul piano Aruba Basic Linux indicato dal proprietario.

Il browser apre `index.html`, applica `style.css` e carica prima `contenuti.js`, poi `app.js`. L'attributo `defer` fa eseguire gli script dopo la lettura dell'HTML, nell'ordine indicato.

`contenuti.js` definisce `window.PORTFOLIO`. `app.js` legge quella configurazione e:

- aggiorna l'anno nel footer;
- crea le eventuali schede progetto;
- mostra uno dei tre scenari dimostrativi;
- calcola le ore potenzialmente risparmiate;
- prepara la richiesta, e apre la posta soltanto se esiste un'email configurata;
- permette di copiare il testo, o selezionarlo se la copia automatica non è disponibile.

I campi del modulo non vengono salvati dal codice del sito né inviati a un server. Eventuali condizioni del browser, dell'app email o dell'hosting restano separate da questa affermazione.

## Primo miglioramento della homepage

La scala dei caratteri usa unità `rem`, relative alla dimensione scelta nel browser: circa 18 pixel per il corpo e almeno 14 per note e dettagli alla dimensione standard. I contenitori possono crescere con il testo e le griglie diventano colonne singole sugli schermi stretti. Non sono stati aggiunti font esterni.

`index.html` contiene un piccolo insieme di simboli SVG riutilizzabili. Le icone statiche li richiamano con `<use>`; `createIcon()` in `app.js` li usa per i pulsanti generati dal codice. Questo evita che le frecce dipendano dalla presenza di un carattere nel font del dispositivo. I testi dei progetti configurabili continuano a essere inseriti come testo.

Il riepilogo dei servizi è un elenco semantico nella homepage. Gli identificatori delle sezioni e i comportamenti di scenari, calcolatore e modulo sono conservati.

## Parti da conservare

Colori crema e arancio, titoli ampi, esempi prima/dopo e linguaggio concreto sono coerenti con il pubblico di piccole aziende. I pulsanti hanno elementi HTML nativi, i campi hanno etichette e gli scenari dichiarano di essere dimostrazioni. Il CSS gestisce schermi piccoli e preferenza per movimento ridotto. Il sito non carica librerie o font esterni.

## Limiti attuali

`app.js` presume di trovare gli elementi della homepage. Non va caricato senza adattamenti su una pagina nuova che non li contiene. Gli scenari sono scritti direttamente nel JavaScript; la configurazione progetti non contiene ancora slug, stato, tecnologie o pagine di approfondimento.

Le schede progetto usano `textContent` per testi configurabili e consentono collegamenti HTTP/HTTPS. Gli scenari usano `innerHTML` con stringhe definite nel codice. Non bisogna estendere quell'inserimento HTML a dati provenienti dagli utenti senza una soluzione appropriata. Questa osservazione non è una certificazione di sicurezza.

## Crescita prevista, ancora da implementare

```text
index.html                 pagina commerciale
progetti/index.html        elenco dei lavori
progetti/<slug>/index.html approfondimento di un lavoro
lab/index.html             catalogo esperimenti
lab/<nome>/index.html      un esperimento funzionante
assets/                    immagini e risorse condivise
```

Una directory con `index.html` permette percorsi come `/lab/` senza un router o un framework. I collegamenti condivisi dovranno funzionare anche dalle pagine annidate. `/contatti/` sarà aggiunta solo se porta un vantaggio rispetto alla sezione esistente.

Per la Fase 1 valuteremo di estendere gradualmente gli oggetti di `contenuti.js` con identificatore, natura del progetto (reale o dimostrativo), problema affrontato, soluzione, stato e collegamenti. Gli elementi sperimentali devono essere distinti dai lavori per clienti. Non è stata ancora cambiata la struttura dati: le pagine attuali continuano a usare i campi esistenti.

Ogni esperimento avrà il proprio JavaScript. Un backend, cioè codice eseguito su un server, si valuterà solo quando una funzione concreta lo richiederà. Non si presume che Aruba Basic Linux possa mantenere servizi Node.js o AI sempre accesi.

## Pubblicazione automatica

Il workflow GitHub esegue controlli e test prima del deploy. `scripts/deploy_site.py` usa soltanto Python standard per produrre `dist/site` con un elenco esplicito di file, creare un backup remoto locale, trasferire tramite FTPS con certificato verificato e controllare il risultato HTTPS. Il backup viene conservato come artefatto GitHub prima della scrittura sul server.

La configurazione FTP viene letta dai Secrets del runner; non viene salvata nei file pubblici. I pacchetti di `requirements-test.txt` servono solo ai test: includono un browser e un server FTPS locale di prova. Aruba continua a ricevere solo HTML, CSS, JavaScript e risorse statiche.

Le nuove directory pubbliche richiederanno un aggiornamento deliberato dell'elenco di pubblicazione. Il workflow non presume che tutte le cartelle del repository appartengano al sito.
