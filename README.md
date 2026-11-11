# Scanner paper NTN / O-RAN / 5G satellitare

Scansiona le fonti web configurate per nuovi paper pertinenti alla ricerca, li scarica quando possibile e li integra nell'archivio in `Paper scientifici/` (cartelle per filone + `Confronto_paper_vs_tesi.xlsx`), senza duplicare la logica di `controlla_excel_e_cartelle.py`: lo richiama lui stesso a fine scansione.

## Installazione (una volta per macchina)

```
./setup.sh
```

Crea un ambiente Python locale (`.venv/`) e installa le dipendenze, incluso il browser usato per il login istituzionale.

## Uso

Prima prova, senza toccare nulla:

```
./scan.sh --dry-run --skip-institutional
```

Login istituzionale (una tantum, finché la sessione resta valida — quando scade basta rifarlo):

```
./scan.sh --login-ieee
./scan.sh --login-sciencedirect
```

Si apre Brave con un profilo dedicato (separato dal tuo profilo principale, dentro `.sessioni/`): fai login come fai di solito con la mail istituzionale, poi torna al terminale e premi Invio. **La prima volta**, se vuoi usare Bitwarden per il login, installa e accedi all'estensione in questa finestra: resterà salvata in questo profilo dedicato per le volte successive (non è lo stesso profilo di Brave che usi normalmente, va fatto lì una volta).

Scansione vera e propria:

```
./scan.sh
```

Altre opzioni:

- `--since-days N` — forza la finestra temporale (default in `config.yaml`).
- `--skip-institutional` — usa solo le fonti aperte (Crossref, Semantic Scholar, arXiv, Unpaywall), anche se hai sessioni istituzionali salvate.
- `--logout` — elimina le sessioni istituzionali salvate.

## Dove finiscono i paper trovati

- **Pertinente, filone chiaro, scaricabile** → PDF nella cartella del filone, riga nuova in "Tabella letteratura" dell'Excel.
- **Pertinente, filone ambiguo** → PDF in `Paper scientifici/Da categorizzare/`, da smistare a mano.
- **Pertinente ma non scaricabile** (paywall, nessuna sessione istituzionale attiva) → niente PDF, riga nel foglio "Da recuperare" dell'Excel (titolo, link, motivo).
- **Fuori tema** (nessuna parola chiave di `parole_chiave_generali` nel titolo/abstract) → scartato subito, non compare nemmeno nel resoconto.
- **Già presente** (stesso DOI o stesso titolo già in archivio) → scartato, contato nel resoconto.

A fine scansione viene stampato un resoconto con cosa è stato scaricato, dove, e cosa è finito in "Da recuperare".

## Modificare cosa viene cercato

`config.yaml`: aggiungi/togli venue, parole chiave generali (il filtro "fuori tema"), o parole chiave per filone (usate per decidere in quale cartella va un paper). Non serve toccare il codice.

## Sicurezza: la cartella `.sessioni/`

Contiene un profilo Brave dedicato per IEEE Xplore e uno per ScienceDirect (cookie di login, ed eventualmente Bitwarden se lo installi lì) dopo `--login-ieee` / `--login-sciencedirect`. **Equivale a un login attivo**: non copiarla, non condividerla, non sincronizzarla fuori da questa macchina. Se mai questa cartella finisse sotto controllo di versione o backup condiviso, escludila esplicitamente.

## Limiti conosciuti

- Senza una chiave API, Semantic Scholar è spesso saturo (errori 429 nel log): è normale, Crossref e arXiv restano comunque interrogati. Una chiave gratuita (richiedibile su semanticscholar.org/product/api) aiuta parecchio: va messa in `semantic_scholar_api_key` in `config.yaml`.
- I connettori IEEE/ScienceDirect cercano un link "PDF" nella pagina dell'articolo dopo il login: se quei siti cambiano il loro layout, potrebbero smettere di trovarlo. In quel caso il paper finisce in "Da recuperare" e lo scarichi a mano.
- La classificazione per filone è a parole chiave: non è infallibile. Controlla ogni tanto la cartella `Da categorizzare/` e, se vedi errori sistematici, aggiusta le parole chiave in `config.yaml`.
- Le colonne di analisi della "Tabella letteratura" (Problema affrontato, Metodologia, Risultati, Limiti) restano vuote: richiedono la lettura del paper, che è compito tuo.
# paper-scanner
# paper-scanner
# paper-scanner
