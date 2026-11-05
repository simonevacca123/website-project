# Checklist da ripetere prima della pubblicazione

Le caselle sono lasciate vuote perché vanno compilate **per ciascuna nuova versione**. I risultati della verifica iniziale sono in `AUDIT.md`.

## Nella copia di sviluppo

- [ ] `python3 scripts/check_site.py` termina senza errori.
- [ ] `node --check app.js` e `node --check contenuti.js` terminano senza errori.
- [ ] `python3 tests/browser_smoke.py` passa, se gli strumenti browser sono disponibili.
- [ ] Titolo, testi e contatti sono corretti; non ci sono clienti o risultati inventati.
- [ ] I tre pulsanti degli scenari cambiano contenuto e segnalano quello selezionato.
- [ ] Il collegamento sotto uno scenario seleziona il servizio corretto nel modulo.
- [ ] Il calcolatore parte da 5 ore; 60 minuti × 10 giorni × 75% mostra 7,5 ore; il ripristino torna a 5.
- [ ] Nome o messaggio vuoti mostrano un errore chiaro e portano il cursore al campo.
- [ ] La richiesta generata corrisponde ai dati inseriti, senza dichiarare invii inesistenti.
- [ ] La copia funziona oppure il testo può essere selezionato e copiato manualmente.
- [ ] Se è configurata l'email, l'app di posta apre il destinatario e il testo corretti. Verificare manualmente su un dispositivo reale: il test automatico non invia posta.
- [ ] Tutti i collegamenti portano alla destinazione prevista, comprese le nuove pagine eventualmente aggiunte.
- [ ] Navigazione con Tab e attivazione con Invio/Spazio sono possibili; il focus è visibile.
- [ ] Controllo visivo su desktop e telefono; niente testo tagliato o scorrimento orizzontale imprevisto.
- [ ] Note e descrizioni restano leggibili; il testo ingrandito al 200% torna a capo senza far debordare la pagina.
- [ ] Le icone sono visibili e i loro simboli SVG esistono; nessun riquadro al posto delle frecce.
- [ ] Console senza errori JavaScript e richieste delle risorse riuscite.
- [ ] Eventuali progetti dimostrativi sono distinti da lavori realmente consegnati.
- [ ] Controllate le modifiche con `git status --short` e `git diff`, aprendo anche i file nuovi.

## Prima di caricare su Aruba

- [ ] Autorizzazione esplicita alla pubblicazione.
- [ ] Backup dei file online da sostituire, conservato fuori dalla cartella pubblica.
- [ ] Protocollo sicuro, destinazione e certificato/chiave verificati.
- [ ] Solo file pubblici nell'elenco di caricamento, senza credenziali, documenti interni, test o backup.
- [ ] Nessuna opzione che elimini automaticamente i file remoti.
- [ ] Procedura di ripristino disponibile prima del trasferimento.

## Dopo il caricamento

- [ ] Verifiche funzionali ripetute sul dominio pubblico, anche da telefono.
- [ ] Recapito e percorso email ricontrollati.
- [ ] Annotata la versione pubblicata e il backup corrispondente.
- [ ] In caso di errore, ripristinati i file dal backup e verificato il risultato.
