# Paper Scanner

Strumento da riga di comando che scansiona periodicamente alcune fonti web per nuovi paper scientifici pertinenti a un filone di ricerca (nel mio caso: reti satellitari non-terrestri 5G/6G, O-RAN), li scarica quando legalmente possibile e li integra in un archivio bibliografico organizzato per argomento.

Nato per il mio lavoro di dottorato, ma scritto in modo da poter essere adattato ad altri argomenti e archivi cambiando solo la configurazione.

## Cosa fa

- Interroga **Crossref**, **Semantic Scholar** e **arXiv** per trovare paper recenti, filtrati per rivista/conferenza e per parole chiave di pertinenza.
- Scarta automaticamente i paper già presenti in archivio (confronto per titolo) e quelli fuori tema.
- Classifica ogni paper pertinente nella cartella giusta dell'archivio, in base a parole chiave configurabili.
- Scarica il PDF quando esiste una copia ad accesso aperto (via **Unpaywall** o **arXiv**).
- Aggiorna un foglio Excel di tracciamento della letteratura, mantenendo coerenti cartelle e righe.
- Alla fine di ogni scansione, stampa un resoconto di cosa è stato scaricato, dove, e cosa resta da recuperare a mano.

## Cosa NON fa (di proposito)

**Non scarica mai automaticamente da IEEE Xplore o ScienceDirect (Elsevier)**, anche se l'utente ha un accesso istituzionale valido. I contratti di licenza tra le università e questi editori vietano quasi sempre il download sistematico/automatizzato, indipendentemente da chi esegue l'accesso: farlo rischierebbe di far sospendere l'accesso a tutto l'ateneo, non solo all'account di chi ha lanciato lo script.

Quando un paper pertinente risulta disponibile solo su questi due editori, il tool si limita ad **aprire la pagina nel browser predefinito** dell'utente (dove presumibilmente è già loggato), perché lo scarichi a mano con un clic — esattamente come farebbe comunque senza il tool.

## Requisiti sull'archivio di destinazione

Questo tool non crea un archivio da zero: si aspetta che esista già, con questa struttura (quella con cui è stato scritto e testato):

- Una cartella per "filone"/argomento (es. `Survey/`, `Testbed/`...), ciascuna con i PDF già nominati in modo descrittivo.
- Un file Excel con un foglio "Tabella letteratura" (colonne: Filone, Autore e anno, Titolo e sede, ..., File) e un foglio "Da recuperare" (Paper, Link, Stato).
- Uno script di validazione a parte (nel mio caso `controlla_excel_e_cartelle.py`) che verifica la coerenza tra l'Excel e le cartelle — il tool lo richiama a fine scansione invece di duplicarne la logica.

Per usarlo su un archivio diverso, verifica/adatta `archivio.py` ai nomi reali dei fogli e delle colonne, e `config.yaml` a filoni e parole chiave del nuovo argomento.

## Installazione

```
./setup.sh
cp config.locale.yaml.esempio config.locale.yaml
```

Il primo comando crea un ambiente Python locale (`.venv/`) e installa le dipendenze. Il secondo crea la copia personale di configurazione: apri `config.locale.yaml` e mettici la tua email (richiesta dalle API di Crossref/Unpaywall). Questo file non va mai versionato — `config.yaml` resta il template condiviso, uguale per chiunque usi il tool.

## Uso

Prima prova, senza toccare nulla:

```
./scan.sh --dry-run
```

Scansione vera e propria:

```
./scan.sh
```

Altre opzioni:

- `--since-days N` — forza la finestra temporale (default in `config.yaml`).

## Dove finiscono i paper trovati

- **Pertinente, filone chiaro, trovato in accesso aperto** (Unpaywall, arXiv) → PDF nella cartella del filone, riga nuova in "Tabella letteratura".
- **Pertinente, filone ambiguo** → PDF in `Da categorizzare/`, da smistare a mano.
- **Pertinente, disponibile solo su IEEE/ScienceDirect** → niente download automatico: si apre la pagina nel browser (fino a `max_pagine_aperte_nel_browser` per scansione) e viene segnalato in "Da recuperare", perché lo si scarichi a mano e lo si sistemi nella cartella giusta.
- **Pertinente ma senza nessuna copia trovata** → niente PDF, riga in "Da recuperare" (titolo, link, motivo).
- **Fuori tema** (nessuna parola chiave generale nel titolo/abstract) → scartato subito, non compare nemmeno nel resoconto.
- **Già presente** (stesso titolo già in archivio) → scartato, contato nel resoconto.

## Personalizzazione

Tutto quello che riguarda cosa viene cercato sta in `config.yaml`, senza toccare il codice: venue da monitorare, parole chiave generali (il filtro "fuori tema"), parole chiave per filone (decidono in quale cartella va un paper), categorie arXiv, limite di pagine auto-aperte nel browser.

## Limiti conosciuti

- Senza una chiave API, Semantic Scholar è spesso saturo (errori 429 nel log): è normale, Crossref e arXiv restano comunque interrogati. Una chiave gratuita (richiedibile su semanticscholar.org/product/api) aiuta parecchio: va messa in `semantic_scholar_api_key`.
- La classificazione per filone è a parole chiave: non è infallibile. Controllare ogni tanto `Da categorizzare/` e, in caso di errori sistematici, aggiustare le parole chiave in `config.yaml`.
- Le colonne di analisi della "Tabella letteratura" (Problema affrontato, Metodologia, Risultati, Limiti) restano vuote: richiedono la lettura del paper, che resta compito dell'utente.

## Licenza

Nessuna licenza specificata: tutti i diritti sono riservati per default. Se vuoi che altri possano riusare/modificare liberamente il codice, valuta di aggiungere un file `LICENSE` (es. MIT).
