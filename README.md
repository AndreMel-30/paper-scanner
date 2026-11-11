# Scanner paper NTN / O-RAN / 5G satellitare

Scansiona le fonti web configurate per nuovi paper pertinenti alla ricerca, li scarica quando possibile e li integra nell'archivio in `Paper scientifici/` (cartelle per filone + `Confronto_paper_vs_tesi.xlsx`), senza duplicare la logica di `controlla_excel_e_cartelle.py`: lo richiama lui stesso a fine scansione.

**IEEE Xplore e ScienceDirect (Elsevier) non vengono mai scaricati in automatico.** I contratti di licenza istituzionali vietano quasi sempre il download sistematico, anche con credenziali valide: farlo rischierebbe di far sospendere l'accesso a tutto l'ateneo, non solo al tuo account. Quando un paper pertinente esiste solo lì, il tool apre semplicemente la pagina nel tuo browser predefinito (dove sei già loggato), perché tu lo scarichi a mano con un clic — esattamente come faresti comunque.

## Installazione (una volta per macchina)

```
./setup.sh
cp config.locale.yaml.esempio config.locale.yaml
```

Il primo comando crea un ambiente Python locale (`.venv/`) e installa le dipendenze. Il secondo crea la tua copia personale di configurazione: apri `config.locale.yaml` e mettici la tua email (richiesta da Crossref/Unpaywall). Questo file non viene mai versionato — `config.yaml` resta il template condiviso, uguale per chiunque usi il tool.

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

- **Pertinente, filone chiaro, trovato in accesso aperto** (Unpaywall, arXiv) → PDF nella cartella del filone, riga nuova in "Tabella letteratura" dell'Excel.
- **Pertinente, filone ambiguo** → PDF in `Paper scientifici/Da categorizzare/`, da smistare a mano.
- **Pertinente, disponibile solo su IEEE/ScienceDirect** → niente download automatico: si apre la pagina nel browser (fino a `max_pagine_aperte_nel_browser` per scansione, configurabile) e viene segnalato nel foglio "Da recuperare" dell'Excel, perché tu lo scarichi a mano e lo sistemi nella cartella giusta.
- **Pertinente ma senza nessuna copia trovata** → niente PDF, riga nel foglio "Da recuperare" dell'Excel (titolo, link, motivo).
- **Fuori tema** (nessuna parola chiave di `parole_chiave_generali` nel titolo/abstract) → scartato subito, non compare nemmeno nel resoconto.
- **Già presente** (stesso titolo già in archivio) → scartato, contato nel resoconto.

A fine scansione viene stampato un resoconto con cosa è stato scaricato, dove, e cosa è finito in "Da recuperare".

## Modificare cosa viene cercato

`config.yaml`: aggiungi/togli venue, parole chiave generali (il filtro "fuori tema"), parole chiave per filone (usate per decidere in quale cartella va un paper), o il limite di pagine auto-aperte nel browser. Non serve toccare il codice.

## Limiti conosciuti

- Senza una chiave API, Semantic Scholar è spesso saturo (errori 429 nel log): è normale, Crossref e arXiv restano comunque interrogati. Una chiave gratuita (richiedibile su semanticscholar.org/product/api) aiuta parecchio: va messa in `semantic_scholar_api_key` in `config.yaml`.
- La classificazione per filone è a parole chiave: non è infallibile. Controlla ogni tanto la cartella `Da categorizzare/` e, se vedi errori sistematici, aggiusta le parole chiave in `config.yaml`.
- Le colonne di analisi della "Tabella letteratura" (Problema affrontato, Metodologia, Risultati, Limiti) restano vuote: richiedono la lettura del paper, che è compito tuo.
