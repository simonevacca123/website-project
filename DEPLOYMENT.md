# Pubblicazione automatica su Aruba

Il proprietario ha richiesto e autorizzato la pubblicazione automatica dei commit che arrivano sul ramo `main` di GitHub. Il workflow è [.github/workflows/deploy.yml](.github/workflows/deploy.yml), chiamato **Pubblica sito su Aruba**. È disponibile anche l'avvio manuale dalla scheda Actions.

**Stato della verifica:** implementazione e test locali completati; accesso ai Secrets, ai log GitHub e al sito Aruba non verificato da questa macchina a causa del blocco di rete. Non confondere i test con un trasferimento riuscito sul vero hosting. I risultati del primo run GitHub devono ancora essere controllati.

## Come funzionerà nell'uso quotidiano

1. Modifichi il sito e invii i commit a `main` con un push. Se modifichi un file direttamente su GitHub e salvi su `main`, GitHub genera già questo evento.
2. GitHub avvia un computer temporaneo che controlla collegamenti, sintassi, homepage, trasferimento FTPS e backup usando server locali di prova.
3. Prepara una cartella con soli file pubblici.
4. Si collega all'hosting tramite **FTPS esplicito**, con TLS verificato e dati cifrati, sulla porta 21 salvo configurazione diversa.
5. Identifica la cartella del sito, legge tutti i file da sostituire e conserva un backup come artefatto GitHub per 30 giorni. Se la lettura o il salvataggio del backup falliscono, non carica nulla.
6. Controlla che il sito non sia cambiato dopo il backup, carica i file diversi e ne verifica il contenuto. L'HTML viene aggiornato per ultimo.
7. Controlla via HTTPS che la homepage e le risorse pubbliche corrispondano alla versione caricata.

Un commit rimasto soltanto sul tuo computer non aggiorna il sito: deve arrivare a GitHub. Se un controllo fallisce, il run diventa rosso e il passo indica dove intervenire. I dati del modulo non vengono inviati da questo workflow.

## Dati su GitHub: riutilizziamo i nomi già previsti

Apri il repository → **Settings → Secrets and variables → Actions**. Nella scheda **Secrets** i nomi previsti sono:

| Nome | Contenuto |
| --- | --- |
| `FTP_SERVER` | Nome del server FTP indicato da Aruba, senza `ftp://`, porta o cartella. Deve corrispondere al certificato TLS. |
| `FTP_USERNAME` | Utente FTP dell'hosting. Non coincide necessariamente con l'email pubblica del sito. |
| `FTP_PASSWORD` | Password FTP, inserita soltanto nell'interfaccia protetta dei Secrets. |

Se i nomi esistono già, non crearne copie. Da questa macchina non è stato possibile verificarne la presenza o validità. Il vecchio workflow utilizzava gli stessi tre nomi. Non inviare password in chat e non inserirle nel repository.

Nella scheda **Variables** puoi impostare:

| Nome | Quando serve |
| --- | --- |
| `FTP_SERVER_DIR` | Percorso esatto della cartella pubblica indicato da Aruba. È consigliato. Se assente, lo script cerca solo la directory di accesso e quelle del dominio `simonevacca.it` / `www.simonevacca.it`, accettando un unico sito riconoscibile come Simone Vacca. Se non è univoco, si ferma. |
| `FTP_PORT` | Solo se Aruba richiede una porta diversa da 21 per FTPS esplicito. |

Per compatibilità, `FTP_SERVER_DIR` può anche essere un Secret: una Variable con lo stesso nome ha precedenza. Nessun percorso viene inventato in caso di dubbio.

Il workflow verifica l'hosting attraverso la connessione reale prima di qualsiasi scrittura. Non è stato ancora accertato da questa macchina che il tuo specifico accesso supporti FTPS esplicito o consenta connessioni dai runner GitHub. Se il pannello indica solo SFTP o restrizioni sull'accesso FTP, occorre adattare la connessione ai dati reali; non si ripiega sul trasferimento non cifrato e non si disattiva la verifica del certificato.

## File pubblicati

Attualmente il pacchetto contiene cinque file:

```text
index.html
style.css
app.js
contenuti.js
assets/favicon.svg
```

Lo script include gli altri file multimediali autorizzati sotto `assets/` quando vengono aggiunti. Rifiuta link simbolici, percorsi nascosti e tipi non previsti. Non trasferisce `.git`, `.github`, documenti, script, test, requisiti di test, backup o credenziali.

Le pagine future come `/progetti/` e `/lab/` richiederanno un aggiornamento esplicito dell'elenco pubblico in `scripts/deploy_site.py`. Non basta creare una cartella per pubblicarla.

Non c'è sincronizzazione distruttiva: non vengono eliminati file remoti estranei o vecchi asset. Vengono rimossi soltanto i file temporanei creati dallo stesso caricamento.

## Leggere il risultato

Apri **Actions → Pubblica sito su Aruba → ultimo run**:

- Verde: tutti i passi, inclusa la verifica HTTPS della homepage, sono riusciti.
- Rosso al controllo Secrets: manca uno dei tre valori o un nome è errato.
- Errore FTPS: verificare server ufficiale, accesso, password, porta, certificato e restrizioni dal pannello Aruba.
- Cartella non identificabile: impostare `FTP_SERVER_DIR` con il percorso esatto.
- Backup non salvato: il caricamento non parte.
- Verifica HTTPS fallita: distinguere file trasferiti correttamente via FTPS da directory non pubblica, precedenza di un eventuale `index.php`, dominio o cache. Questo errore non avvia automaticamente un ripristino, perché una cache non dimostra un guasto del codice.

Le credenziali non vengono mostrate nei log. Non modificare contemporaneamente gli stessi file via FTP durante un deploy.

## Backup e ripristino

Nella pagina del run, sotto **Artifacts**, scarica `aruba-backup-<numero-run>-<tentativo>`. Conserva una copia fuori dalla cartella pubblica se ti serve oltre i 30 giorni.

Se un trasferimento si interrompe, lo script tenta subito il ripristino dei file preesistenti coinvolti usando la stessa connessione. Se il server non risponde più, il ripristino può fallire: il backup già conservato resta disponibile. I file nuovi non vengono eliminati automaticamente.

Per tornare a una versione del codice già conosciuta, si possono ripristinare soltanto i file pubblici da un commit precedente, controllarli e creare un nuovo commit su `main`, mantenendo il workflow attuale. Questo produce un nuovo deploy con un altro backup.

È disponibile anche un ripristino tecnico da un artefatto integro con `python3 scripts/deploy_site.py restore --backup <cartella-backup>`, in un contesto con i Secrets FTP forniti in modo sicuro. Questa operazione richiede il backup del server corretto; non serve per l'uso quotidiano e va eseguita con assistenza.

Il trasferimento è atomico per singolo file tramite nome temporaneo e rinomina. L'intero sito non cambia in un solo istante: durante un caricamento possono coesistere file di due versioni. Non si promette un deploy atomico completo su un hosting FTP.

## Provare il sistema senza toccare Aruba

Gli strumenti elencati in `requirements-test.txt` servono solo allo sviluppo. In un ambiente dove sono installati:

```sh
python3 -m unittest discover -s tests -p 'test_deploy_*.py' -v
python3 tests/browser_smoke.py
```

Le prove del trasferimento usano un server FTPS locale con certificato di test esplicitamente attendibile; verificano anche il rifiuto di un certificato non attendibile. Le prove HTTPS confrontano homepage e risorse e rilevano una versione online diversa. I test non usano le credenziali Aruba.
