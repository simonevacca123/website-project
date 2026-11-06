# Pubblicazione predisposta, non avviata

> Aggiornamento operativo — 6 novembre 2026: dopo la spiegazione delle modifiche, il proprietario ha autorizzato un commit e il caricamento su GitHub. Le indicazioni precedenti di divieto di commit/push descrivono la fase del 5 novembre e sono superate per questo caricamento. La pubblicazione su Aruba resta separata e non viene eseguita. L’esito del push verrà verificato sul remoto; questo documento non ne anticipa il successo.

Il nuovo master prompt richiede **nessun commit, push o deploy da parte dell'assistente**. Sostituisce la precedente richiesta di automatismo su ogni push. Il workflow locale `.github/workflows/deploy.yml` ora ha solo `workflow_dispatch`, cioè avvio manuale.

**Non è stata verificata una connessione al vero Aruba.** FTPS esplicito è il protocollo implementato e provato su server locali; il supporto del piano, server, certificato e directory effettivi devono essere confermati prima di attivarlo. Non sono stati modificati DNS o credenziali.

## Flusso da usare dopo la revisione

Mac / ambiente Codex → modifiche locali → generazione → test → commit e push eseguiti dal proprietario → GitHub Actions manuale → Aruba, solo quando autorizzato.

1. Esegui i controlli in README e rivedi i file pubblici.
2. Salva e trasferisci tu le versioni con Git. Questo intervento non ha eseguito tali operazioni. Il precedente rifiuto `fatal error in commit_refs_rules` resta non diagnosticato; non forzare il push.
3. Quando il workflow sarà su GitHub, apri **Actions → Pubblica sito su Aruba → Run workflow**.
4. Lascia `publish` disattivato per test e creazione dell'artefatto `sito-da-revisionare`. Non vengono usati i Secrets e non parte alcuna connessione Aruba.
5. Solo dopo aver verificato i dati hosting e autorizzato il caricamento, scegli `main` e attiva `publish`. Un altro ramo non può pubblicare.
6. Prima di trasferire, il workflow esegue tutti i test e prepara il pacchetto; individua la directory, legge i file da sostituire e conserva il backup GitHub per 30 giorni. Se il backup o il suo caricamento come artefatto fallisce, la pubblicazione si ferma.
7. Carica soltanto i file modificati, verifica gli hash e controlla il sito HTTPS. La homepage viene caricata per ultima.

Nessun workflow è stato eseguito su GitHub in questa fase. Il comportamento descritto è quello della configurazione preparata localmente.

## Secrets nell'interfaccia ufficiale

Repository GitHub → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Valore da prendere dal pannello Aruba |
| --- | --- |
| `FTP_SERVER` | Hostname del servizio FTPS, senza protocollo, porta o directory; deve corrispondere al certificato. |
| `FTP_USERNAME` | Utente dell'accesso hosting. |
| `FTP_PASSWORD` | Password FTPS. |

Non incollare password in questa chat, nei file, nelle variabili pubbliche o nei comandi salvati. Riutilizza i nomi esistenti se già configurati; la loro presenza/validità non è stata verificata qui.

Nella scheda **Variables**, `FTP_SERVER_DIR` è il percorso pubblico esatto; `FTP_PORT` è la porta FTPS se diversa da 21. Per compatibilità il percorso può essere un Secret. I percorsi non sono credenziali, ma devono provenire dal pannello: non inventarli.

Se la directory non è configurata, lo script cerca la directory di login e quelle del dominio, accettando un unico sito riconoscibile come Simone Vacca. In caso di ambiguità si ferma. Prima del primo deploy è preferibile confermare la directory esatta con il pannello o il supporto Aruba.

Se l'hosting supporta soltanto SFTP, il codice va adattato con verifica della chiave host. Non usare FTP non cifrato e non disabilitare la verifica del certificato per aggirare un errore. Verificare anche eventuali restrizioni IP verso runner GitHub e la precedenza di un eventuale `index.php`.

## Che cosa finisce sul server

`python3 scripts/deploy_site.py build` prepara `dist/site/`: quattro file base, asset consentiti e i file elencati in `scripts/public-files.json`. L'elenco è prodotto dal generatore e va rivisto quando si aggiungono pagine. Non vengono copiati `content/`, `templates/`, script interni, documenti, test, `.git`, `.github`, backup o file segreti.

Per una prova locale, `DEPLOY_REVISION` deve essere lo SHA completo di un commit esistente. Lo SHA identifica la base; **non dimostra che modifiche locali non committate siano su GitHub**. Gli hash nel manifest descrivono i byte effettivamente confezionati. Nel workflow viene usato `github.sha`.

Prima di caricare, controllare i collegamenti anche servendo `dist/site/`, perché questa è la cartella che verrà pubblicata. Il server di sviluppo della root espone documenti interni e non deve essere usato come root del sito online.

Non c'è sincronizzazione distruttiva. Nessun file remoto estraneo o obsoleto viene cancellato; sono rimossi solo i file temporanei dello stesso trasferimento. Una scheda diventata bozza non rimuove automaticamente una sua precedente pagina online: il ritiro va autorizzato e gestito separatamente.

## Backup e rollback

L'artefatto `aruba-backup-<run>-<tentativo>` contiene i file preesistenti da sostituire e il manifest. Scaricarlo in una posizione privata se deve durare oltre i 30 giorni; non metterlo nella cartella pubblica. Non include una copia completa di file estranei al sito: per un backup totale usare le funzioni hosting appropriate.

Se un upload fallisce, lo script tenta di ripristinare i file preesistenti già coinvolti. Un guasto della connessione può impedire il rollback: resta l'artefatto. I file nuovi non sono cancellati.

Con assistenza e autorizzazione, `python3 scripts/deploy_site.py restore --backup <cartella-backup>` ripristina i file di un artefatto integro, usando credenziali fornite tramite un canale sicuro. Non è un comando da provare sul server reale per esercizio.

Un'altra possibilità è ripristinare localmente i file di una versione nota, verificarli, salvare un nuovo commit a cura del proprietario e avviare manualmente un nuovo deploy. Non occorre cancellare la storia Git.

La rinomina è atomica per singolo file, non per tutto il sito: durante il caricamento possono convivere versioni diverse. La verifica HTTPS fallita non esegue rollback automatico: prima distinguere cache, directory sbagliata e file inattesi. Il trasferimento non garantisce downtime zero.

## Leggere gli errori

- Test rosso: correggere codice o ambiente prima di toccare Aruba.
- Credenziali rifiutate: ricontrollare Secrets e account nel pannello, senza stampare valori.
- Certificato o protocollo non supportato: chiedere i dati ufficiali Aruba, mantenendo TLS verificato.
- Directory ambigua o sito estraneo: fermarsi e verificare `FTP_SERVER_DIR`.
- Backup fallito: nessun upload deve partire.
- Hash cambiato dopo il backup: un altro processo ha modificato il file; evitare scritture concorrenti.
- HTTPS diverso dal pacchetto: controllare URL pubblico, cache e directory prima di annunciare un successo.

Le prove automatiche locali usano certificati di test e credenziali sintetiche temporanee. Non provano il funzionamento del vero hosting.
