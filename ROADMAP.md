# Il percorso, un passo alla volta

Ogni passo deve lasciare una versione funzionante. Le attività future in questa pagina non sono già implementate. Il proprietario ha autorizzato commit e push delle modifiche correnti e successivamente ha richiesto la pubblicazione automatica su Aruba. Merge e tag restano subordinati a una richiesta specifica.

## Fase 0 — Conoscere e mettere in ordine: completata in sviluppo

- [x] Leggere HTML, CSS, JavaScript e configurazione.
- [x] Preparare le guide e `.gitignore`.
- [x] Salvare controlli ripetibili e una checklist.
- [x] Verificare la copia locale in Chromium, anche a dimensioni mobile.
- [x] Documentare problemi e dati mancanti in `AUDIT.md`.

Durante la Fase 0 i file dell'applicazione sono rimasti identici alla versione ricevuta. Il sito online non è stato modificato o verificato contro questi file.

## Fase 1 — Portfolio, divisa in piccoli interventi

1. **Contatto email configurato in sviluppo:** inserito `simone.vacca@edu.unito.it`, fornito dal proprietario. Verificati indirizzo visibile, destinatario, oggetto e testo del collegamento `mailto`, oltre alla copia alternativa. Restano la prova nell'app di posta su un dispositivo reale e la futura pubblicazione autorizzata.
2. **Presentazione e servizi, primo intervento completato in sviluppo:** introduzione con nome e attività, riepilogo dei tre servizi, nota personale sugli studi in AI e sulla curiosità. Migliorate tipografia, gerarchie e spazi mantenendo colori e identità. Nessun cliente o risultato inventato.
3. **Primo progetto:** raccogliere materiale reale o una demo dichiarata; preparare una scheda e il primo approfondimento.
4. **Pagina progetti:** creare `/progetti/` e riutilizzare una struttura dati semplice.
5. **Accessibilità e ricerca, parzialmente affrontate:** testi visibili di almeno 14 pixel, controlli più ampi, icone SVG, reflow verificato con testo al 200%. Restano verifica su dispositivi reali, audit accessibilità completo, dominio preferito, canonical, Open Graph, sitemap e robots.

Per ogni intervento: spiegare cosa cambia, modificare solo il necessario, provare e mostrare il risultato. Non serve affrontare tutti i punti contemporaneamente.

## Fase 2 — Primo laboratorio: da iniziare

Creare `/lab/`, con categorie, stato, descrizioni, tecnologie e collegamenti verificati. Prima idea da valutare: uno strumento che pulisce un piccolo elenco di dati e mostra i duplicati, elaborando tutto nel browser. È una proposta, non una demo già realizzata. Deve essere comprensibile e dichiarare i limiti.

## Fase 3 — Gestione delle versioni: basi documentate

Avvio, verifiche, struttura e distinzione tra copia locale, GitHub e Aruba sono spiegati. Dopo la revisione della homepage, il proprietario ha autorizzato l'assistente a salvare e trasferire su GitHub le modifiche correnti. Il salvataggio comprende codice, guide e test; nessuna pubblicazione su Aruba è stata richiesta.

## Fase 4 — Pubblicazione automatica: implementata, da verificare sull'hosting reale

Su esplicita richiesta del proprietario, il workflow `.github/workflows/deploy.yml` è stato aggiornato per i push su `main` e per l'avvio manuale. Esegue test, prepara solo i file pubblici, verifica il collegamento FTPS, conserva il backup su GitHub prima del trasferimento, aggiorna l'HTML per ultimo e confronta il risultato HTTPS con la versione attesa. Non elimina file remoti estranei. Sono previste prove automatiche locali e ripristino dei file preesistenti in caso di errore di trasferimento.

Restano da verificare il primo run GitHub, la presenza/validità dei Secrets esistenti, il supporto FTPS e la directory del vero hosting. Questa macchina non può ancora leggere API GitHub, guida Aruba o sito pubblico per il blocco della rete; sono state salvate le aggiunte necessarie alla configurazione dell'ambiente. La scelta dell'avvio automatico sostituisce per richiesta del proprietario il precedente piano di solo avvio manuale.

## Fase 5 — In seguito, solo quando serve

Valutare invio contatti protetto da spam, backend, database, strumenti AI, analytics rispettosi della privacy e monitoraggio in base a esigenze concrete, costi e compatibilità. Non è prevista un'installazione immediata di questi servizi.
