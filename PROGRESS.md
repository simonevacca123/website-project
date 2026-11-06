# Stato di avanzamento — master prompt

> Aggiornamento operativo — 6 novembre 2026: dopo la spiegazione delle modifiche, il proprietario ha autorizzato un commit e il caricamento su GitHub. Le indicazioni precedenti di divieto di commit/push descrivono la fase del 5 novembre e sono superate per questo caricamento. La pubblicazione su Aruba resta separata e non viene eseguita. L’esito del push verrà verificato sul remoto; questo documento non ne anticipa il successo.

Aggiornamento del 5 novembre 2026. Riferimento: master prompt allegato dal proprietario. **Tutto il nuovo lavoro è locale. Nessun commit, push, merge, tag, collegamento alla produzione o deployment eseguito in questo intervento.** Il divieto attuale sostituisce le autorizzazioni precedenti.

La base trovata era HEAD `e353ae2` più modifiche non committate al laboratorio. È stata conservata e ampliata. Il vecchio errore remoto `commit_refs_rules` non è stato ritentato.

## Report per fase

### Fase 0 — Fondamenta completate localmente

**Modifiche:** audit aggiornato, guide, regole operative, template comuni, schede JSON e generatore statico. **Decisione:** Python standard solo in sviluppo evita duplicazioni senza introdurre un runtime su Aruba. **Test:** regressione iniziale homepage/Lab, 40 riferimenti iniziali e 14 test deploy. **Aperti:** dati hosting e materiali personali mancanti. **Fase successiva svolta:** portfolio.

### Fase 1 — Portfolio implementato e verificato localmente

**Modifiche:** navigazione comune, servizi dettagliati, pagina Chi sono, inviti a progetti/demo, servizio automazioni nel modulo e contatti mailto espliciti. **Decisione:** conservare la homepage e il contatto nella stessa sezione; monogramma al posto di una foto inventata. **Test:** homepage completa, fallback senza email, tastiera, responsive, contatto contestuale e indirizzo senza JavaScript. **Aperti:** apertura e invio reali nell'app email, foto/profili autentici facoltativi. **Fase successiva svolta:** catalogo.

### Fase 2 — Progetti e case study implementati e verificati

**Modifiche:** `/progetti/` e approfondimenti di elenchi, percorso e turni; dati in `content/progetti`; modello privato per bozze. **Decisione:** tutte le schede attuali sono demo effettivamente implementate, nessun cliente inventato. **Test:** 6 prove contenuti, XSS come testo, URL/slug invalidi, bozze escluse, pacchetto senza documenti, HTML e sitemap coerenti; catalogo leggibile senza JS. **Aperti:** pubblicazione di lavori reali richiede materiali e diritti. **Fase successiva svolta:** Lab.

### Fase 3 — Digital Lab implementato e verificato

**Modifiche:** catalogo `/lab/`, pulizia elenchi conservata in `/lab/elenchi/`, griglia `/lab/percorso/` con BFS/Dijkstra, costi, ostacoli e controlli. **Decisione:** algoritmo puro separato dalla UI, quattro direzioni, costi positivi, 96 celle. **Test:** 160 confronti con oracolo indipendente; casi pesati e senza percorso; tastiera, pausa, reset, modifica durante animazione, movimento ridotto; suite elenchi completa. **Aperti:** screen reader e browser fisici non provati. **Fase successiva svolta:** strumenti.

### Fase 4 — Strumenti implementati e verificati

**Modifiche:** calcolatore esistente ampliato (mesi attivi, valore orario, annualità, formule); `/strumenti/` e checklist a otto domande con report. **Decisione:** nessun secondo calcolatore; autovalutazione dichiarata, nessuna scansione esterna o richiesta di dati personali. **Test:** formule, estremi/errori, reset, report misto/ignoto, priorità, copia/fallback, download e invalidazione al cambio delle risposte. **Aperti:** stime da confrontare con processi reali prima di usarle per decisioni economiche. **Fase successiva svolta:** showroom.

### Fase 5 — Showroom implementato e verificato

**Modifiche:** `/demo/` con tre persone sintetiche, tre giorni, due fasce, copertura e ore. **Decisione:** stato solo in memoria, nessuna proprietà intellettuale o dato di terzi. **Test:** aggiornamento conteggi, copertura, dati invalidi, reset e CTA che seleziona software nel modulo. **Aperti:** è un prototipo; niente vincoli contrattuali, autenticazione o persistenza. **Fase successiva svolta:** preparazione deploy.

### Fase 6 — Deploy predisposto; verifica su Aruba bloccata per dati e autorizzazione

**Modifiche:** workflow solo manuale, `publish` false di default, test prima dei trasferimenti, pacchetto selettivo, backup e rollback documentati. **Decisione:** nessun automatismo su push dopo il nuovo master prompt. **Test:** 14 unitari e 3 integrazioni FTPS/HTTPS locali; YAML manuale e default verificati; pacchetto isolato servito e provato nel browser. **Aperti:** supporto FTPS/SFTP, hostname, cartella, credenziali nei Secrets e accesso dei runner reali. Nessun run GitHub o deploy avviato. **Fase successiva svolta:** qualità locale.

### Fase 7 — Qualità e SEO verificate entro i limiti dichiarati

**Modifiche:** title/description univoci, canonical, Open Graph, sitemap/robots, controlli e rifiniture. **Test:** 229 link statici, 8 script, 13 URL diretti a 320/390/768/1440px e testo 200%, tutte le interazioni nelle tre suite browser; nessun errore JS/HTTP o richiesta esterna nelle prove. Contrasti principali e peso 135.626 byte del pacchetto misurati. **Aperti:** audit screen reader, altri browser, Core Web Vitals e comportamento live. Nessuna dichiarazione di piena conformità WCAG o indicizzazione garantita. **Fase successiva svolta:** roadmap.

### Fase 8 — Crescita documentata, senza infrastrutture anticipate

**Modifiche:** ROADMAP, ARCHITECTURE e convenzioni per bozze blog, backend, API, database, AI, analytics, monitoring, staging, sottodomini e deploy separati. **Decisione:** nessun backend o servizio a pagamento introdotto senza necessità. **Verifica:** nessuna dipendenza runtime esterna nelle richieste browser; file interni esclusi dal pacchetto. **Aperti:** ogni futuro servizio richiede una funzione concreta e verifica dei requisiti dati/privacy/costi. **Prossimo passo:** revisione guidata locale con il proprietario.

## Come riprendere

1. Leggere questo file e AGENTS.md; ispezionare `git status --short` senza creare commit.
2. Avviare il sito come in README. Non modificare direttamente le nuove pagine generate: usare templates e schede.
3. Mostrare al proprietario il Lab e provare un esperimento insieme. Per aggiungere un suo progetto seguire CONTENT-GUIDE.
4. Completare prove manuali, dati autentici e informazioni Aruba prima di proporre una pubblicazione concreta.
5. Per attivare deploy o riprendere commit/push serve una nuova istruzione esplicita, perché l'ultima li vieta.

Test di riferimento: `build_pages.py --check`, `check_site.py`, `check_js.py`, due suite Node, test Python contenuti/deploy, `browser_smoke.py`, `lab_smoke.py`, `platform_smoke.py`. Risultati e limiti dettagliati in AUDIT.md. Screenshot locali in test-results, esclusi da Git e dal sito.
