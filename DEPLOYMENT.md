# Pubblicare su Aruba, con calma

**Questa è una guida preparatoria. Non è stato eseguito alcun caricamento su Aruba da parte dell'assistente.** Nel codice aggiornato il workflow GitHub è dedicato ai soli controlli manuali, senza automazione di pubblicazione. Il piano Basic Linux e il sito già online sono informazioni fornite dal proprietario, non verificate accedendo al pannello.

## Tre posti diversi

1. **Ambiente di sviluppo:** la cartella in cui lavoriamo e proviamo le modifiche.
2. **GitHub:** la copia del codice con la sua storia. Un push aggiorna GitHub.
3. **Aruba:** lo spazio da cui i visitatori ricevono il sito. Serve un caricamento separato finché non verrà preparata e autorizzata un'automazione.

Cambiare file qui non cambia automaticamente il sito online.

## Prima di scegliere come caricare

Dal pannello e dalla documentazione ufficiale del tuo specifico hosting occorre verificare:

- quale protocollo cifrato è disponibile: FTPS oppure SFTP, senza presumere che siano entrambi supportati;
- hostname, porta e directory pubblica effettiva;
- come effettuare backup e ripristino;
- quale indirizzo è quello preferito tra dominio con `www` e senza `www`.

FTPS e SFTP sono due modi differenti di trasferire file con una connessione protetta. Non scegliere un protocollo soltanto perché il programma di trasferimento lo propone. Non disattivare i controlli del certificato o della chiave del server. Le credenziali vanno inserite nello strumento sicuro appropriato, mai nei file del sito o in chat.

## Cosa va pubblicato adesso

Soltanto questi file, mantenendo la cartella `assets`:

```text
index.html
style.css
app.js
contenuti.js
assets/favicon.svg
```

Le nuove pagine, quando esisteranno, richiederanno un elenco aggiornato. Non caricare l'intera cartella del repository: `.git`, guide, test, script, `.env`, backup e credenziali non fanno parte del sito pubblico. `.gitignore` aiuta Git, ma non impedisce a un programma FTP di caricare un file.

## Procedura per una futura pubblicazione autorizzata

1. Eseguire le verifiche di `CHECKLIST.md` sulla versione candidata.
2. Salvare una copia dei file online che saranno sostituiti, mantenendo i percorsi. Conservare il backup fuori dalla directory pubblica, con la data e l'indicazione della versione. Non confonderlo con una copia delle modifiche locali.
3. Dopo autorizzazione, caricare soltanto i file pubblici approvati. Non attivare opzioni di sincronizzazione che eliminano file remoti.
4. Provare il sito online da desktop e telefono: stili, scenari, calcolatore, contatti e console del browser. Una ricarica forzata può aiutare a non vedere file precedenti conservati dal browser.
5. Se qualcosa non funziona, ripristinare dal backup i file sostituiti e ricontrollare. Non cancellare file remoti aggiuntivi senza un controllo e un'autorizzazione specifici.

Un caricamento manuale di più file può mostrare temporaneamente versioni miste. Prima di cambiamenti a più pagine, verificare se l'hosting offre staging o un passaggio atomico fra versioni. Non promettere una pubblicazione senza interruzioni finché la modalità effettiva non è stata verificata.

## Automazione futura

Il workflow di pubblicazione GitHub Actions sarà preparato soltanto dopo aver verificato l'accesso supportato. Dovrà avere avvio manuale o approvazione esplicita iniziale, test prima del trasferimento, credenziali in Actions Secrets, elenco esplicito dei file da pubblicare, backup e procedura di ripristino. Nessuna cancellazione remota automatica.

Il file attuale `.github/workflows/deploy.yml` esegue soltanto controlli statici con avvio manuale. Sostituisce il precedente trasferimento FTP automatico conservato nella cronologia al commit `806af65`. Il workflow precedente non va ripristinato per pubblicare senza prima verificare protocollo, backup ed esclusione dei file interni. Non sono state lette o modificate credenziali dell'hosting.

Non sono ancora richiesti segreti: prima identifichiamo il servizio e il protocollo realmente necessari. La preparazione di un workflow non autorizza ad attivarlo o a pubblicare.
