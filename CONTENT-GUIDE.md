# Aggiungere un progetto, con calma

Una **scheda** è un file di testo JSON: contiene i dati del progetto. Il generatore li trasforma nel catalogo e in una pagina di approfondimento. Non devi ricopiare manualmente l'HTML della homepage.

## 1. Parti da una bozza

Copia `content/bozze/modello.json` con un nome riconoscibile nella stessa cartella. Rimane escluso dal sito. Non mettere dati riservati nel repository: “escluso dal sito” non significa “segreto su GitHub”. Per lavori di clienti servono autorizzazioni prima di inserire nomi, codice o screenshot.

## 2. Compila la scheda

Usa `content/progetti/elenchi.json` come esempio completo. Mantieni virgolette doppie e virgole fra i campi. I testi vengono trattati come testo, non come HTML.

| Campo | Cosa scrivere |
| --- | --- |
| `slug` | Un nome breve nell'URL, solo minuscole, numeri e trattini; es. `elenco-ordini`. |
| `pubblicato` | `false` finché è una bozza; `true` solo quando è verificato e autorizzato. |
| `titolo`, `descrizione` | Nome chiaro e cosa può fare il visitatore. |
| `tipo` | Personale, universitario, demo o cliente, secondo la realtà. |
| `categoria` | Un ambito pertinente; non serve creare una categoria vuota. |
| `stato` | Prototipo, demo funzionante o stato reale. |
| `tecnologie` | Elenco delle tecnologie effettivamente usate. |
| `lab` | `true` per mostrare anche nel laboratorio, `false` per il solo catalogo. |
| `contesto`, `problema`, `obiettivi` | Per chi è il progetto e quale problema affronta. |
| `soluzione`, `interfaccia`, `scelte` | Cosa hai costruito e perché. Devi poterlo spiegare. |
| `compromessi`, `risultati` | Limiti e risultati osservabili. Zero metriche inventate. |
| `demo`, `repository` | Link HTTPS verificato o percorso interno come `/lab/elenchi/`. Vuoto se non disponibile. |
| `immagine` | Facoltativa: immagine autorizzata sotto `assets/`, percorso senza `..`. |
| `periodo` | Facoltativo: periodo reale verificato; non dedurre la data da questa sessione. |

Le bozze con `pubblicato: false` vengono ignorate anche se accidentalmente spostate nella cartella `content/progetti`. Non sono inserite nel JavaScript pubblico. I campi incompleti di una scheda pubblica causano un errore comprensibile.

## 3. Prepara immagini o demo

Per uno screenshot usa WebP/AVIF o PNG quando serve leggibilità del testo; riduci le dimensioni al necessario. Niente informazioni personali visibili. Le immagini sono caricate solo sulle relative pagine progetto, con `loading="lazy"`.

Per un nuovo esperimento crea `lab/nome/` con script separati e un template in `templates/`. Aggiungi la voce in `PAGES` di `scripts/build_pages.py`, con titolo, descrizione e script. Non caricare `app.js`: dipende dagli elementi della homepage. Uno screenshot non sostituisce una demo che dichiari funzionante.

## 4. Genera e controlla

Quando la scheda è pronta, spostala in `content/progetti/` e imposta `pubblicato: true`. Questo cambia solo i file locali:

```sh
python3 scripts/build_pages.py
python3 scripts/check_site.py
python3 scripts/check_js.py
```

Apri il sito locale e controlla `/progetti/`, `/progetti/il-tuo-slug/` e l'eventuale demo. Rileggi testi, limiti e URL. Il comando `--check` verifica che le pagine generate siano aggiornate senza modificarle.

La generazione aggiorna anche sitemap e lista dei file pubblici. Non carica niente su Internet e non crea commit.

## 5. Pubblicazione e ritiro

Commit e push restano al proprietario. Il deploy manuale si prepara seguendo `DEPLOYMENT.md`, dopo revisione e autorizzazione.

Impostare una scheda già pubblicata come bozza la esclude dal prossimo pacchetto, ma **non elimina una vecchia pagina già presente su Aruba o nella cartella locale**. Il trasferimento non cancella file remoti. Per ritirare contenuti online serve un intervento specifico autorizzato, con backup e controllo dell'URL precedente.

## Fotografia e profili

In `templates/chi-sono.html` c'è un monogramma al posto della fotografia. Quando avrai una foto autentica autorizzata, sostituisci il blocco `portrait-mark` con una figura e un'immagine sotto `assets/`, indicando `alt`, `width` e `height` reali per evitare salti di impaginazione. Rigenera e controlla da telefono. Aggiungi soltanto profili di cui hai verificato l'URL; nessun profilo LinkedIn o account GitHub viene dedotto dal nome.

## Progetti candidati e blog

Gestionale completo di turni/presenze, e-commerce artigianale, lavori locali, dashboard e applicazioni AI sono possibili schede future. Non sono stati presentati come lavori completati. Il modello privato è sufficiente finché mancano materiali.

`content/blog/` contiene la convenzione per le bozze editoriali e i primi temi. Non è pubblicata una pagina blog vuota. La ricerca “sviluppatore a Torino” richiede prima una conferma dell'area effettivamente servita: non è stata inventata una sede.
