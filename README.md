# Paper Scanner

Paper Scanner is a command-line tool that looks for new scientific papers on a research topic. It downloads the papers that are legally free to read and files them into an existing bibliography archive.

The tool runs periodically. Each run queries a few web sources, skips papers that are already known, and sorts the rest by topic.

The tool was built for the author's PhD research on satellite non-terrestrial networks, 5G and 6G, and O-RAN (Open Radio Access Network). It is written so that another topic or another archive can be used by changing only the configuration file, not the code.

## What it does

Each run queries three public sources for recent papers:

- **Crossref** is a public database of scholarly metadata. It records basic publication details and a DOI (Digital Object Identifier, a permanent identifier for a paper) for each work.
- **Semantic Scholar** is a public academic search API. An API is a program interface that other programs use to request data.
- **arXiv** is a repository of preprints, which are papers posted online before or without formal journal publication.

The queries are filtered by journal or conference name (called the venue) and by relevance keywords.

After the queries, the tool does the following:

- Skips papers that are already in the archive. Papers are matched by title.
- Skips papers that are off topic.
- Sorts each relevant paper into a folder of the archive, based on keywords set for each folder.
- Downloads the PDF when a legal open-access copy exists. The tool looks for that copy through **Unpaywall**, a service that finds free legal copies of papers that are otherwise behind a paywall, and through arXiv.
- Updates the tracking records, so the folders and the records stay consistent.
- Prints a summary at the end of the run. The summary lists what was downloaded, where it was saved, and what must still be retrieved by hand.

## What it does not do

The tool never downloads automatically from **IEEE Xplore** or **ScienceDirect** (published by Elsevier), even when the user has valid institutional access. University license agreements with these publishers almost always forbid systematic, automated downloading, no matter who runs it. If it happens, the university as a whole can lose access, not only the one account that ran the script.

When a relevant paper is available only on one of these two sites, the tool opens the paper's page in the default browser. The user is probably already logged in there. The user downloads the paper with one click, as they would without the tool.

## Requirements for the archive

The tool does not create an archive. The archive must already exist. By default, the tool expects this layout:

- The tool's own folder sits inside the archive folder.
- Next to the tool's folder, there is one folder for each topic or subject area. Each topic folder already contains PDFs with descriptive file names.

The tool keeps track of known and pending papers in one of two ways. The first way is the default:

- If no spreadsheet is configured, the tool keeps a hidden JSON file inside the archive folder. It also writes a plain Markdown file named "Da recuperare.md". That file lists the papers that were found but not downloaded. No spreadsheet software is needed.
- If a spreadsheet is configured, the tool uses it instead. The spreadsheet must have a sheet named "Tabella letteratura" (literature table) and a sheet named "Da recuperare" (to retrieve). The configuration points to the file with `percorso_excel` (Excel path) and can name a check script with `script_verifica` (verification script). The check script confirms that the spreadsheet and the folders match.

The default setup is what anyone who clones the repository gets. The spreadsheet setup is specific to the author's own archive. It is kept in a local configuration file, so the shared configuration stays generic.

## Installation

This tool is developed and used mainly on Linux. It also works on Windows, through the PowerShell scripts described below, but that path is less tested in practice.

On Linux or macOS:

```
./setup.sh
cp config.locale.yaml.esempio config.locale.yaml
```

On Windows, in PowerShell:

```
.\setup.ps1
copy config.locale.yaml.esempio config.locale.yaml
```

The first command creates a local Python virtual environment in the `.venv/` folder and installs the dependencies.

The second command creates a personal configuration file, `config.locale.yaml`. Open it and put your email address in it. The Crossref and Unpaywall APIs require an email address. The local file is never committed to version control. `config.yaml` stays the shared template, and it is the same for everyone who uses the tool.

## Usage

Start with a dry run. A dry run does not change any file. On Linux or macOS:

```
./scan.sh --dry-run
```

On Windows, in PowerShell:

```
.\scan.ps1 --dry-run
```

To run a real scan, drop `--dry-run` from either command above.

One extra option is available:

- `--since-days N` sets the time window for the search, in days. The default value is set in `config.yaml`.

## Where found papers end up

Downloaded PDFs are named after the first author's surname and the publication year, lowercase, no separator, for example `volk2024.pdf`. This matches the naming already used in the archive. If that name is already taken in the destination folder, a number is appended (`volk2024-2.pdf`, and so on).

- **Relevant, clear topic, open-access copy found:** the PDF is saved in that topic's folder, and a new record is added to the literature table.
- **Relevant, unclear topic:** the PDF is saved in a folder for unclear cases. The default name is "Da categorizzare". The user sorts these papers by hand.
- **Relevant, available only on IEEE Xplore or ScienceDirect:** nothing is downloaded. The tool opens the page in the browser, up to a configurable number of pages per run (`max_pagine_aperte_nel_browser`). The paper is logged as something to retrieve manually.
- **Relevant, no copy found anywhere:** nothing is downloaded. The paper is logged as something to retrieve manually, with its title, link, and the reason.
- **Off topic** (no general relevance keyword in the title or abstract): dropped at once. It does not appear in the summary.
- **Already in the archive** (same title already present): dropped, and counted in the summary.

## Customization

All search settings are in `config.yaml`. No code changes are needed to change them. The file controls:

- the journals and conferences to monitor;
- the general relevance keywords, which act as the off-topic filter;
- the keywords for each folder, which decide where a paper is filed;
- the arXiv categories;
- the limit on browser pages opened automatically.

## Known limitations

- Without an API key, the public Semantic Scholar endpoint is often rate-limited. The log then shows HTTP 429 errors. This is expected. Crossref and arXiv are still queried normally. A free API key can be requested at semanticscholar.org/product/api. Put the key in `semantic_scholar_api_key`. It helps a lot.
- Topic classification is based on keywords, so it is not perfect. Check the "Da categorizzare" folder from time to time. If the same kind of mistake repeats, adjust the keywords in `config.yaml`.
- The analysis columns of the literature table (problem addressed, methodology, results, limitations) are left blank. Filling them requires reading the paper, which the user still does.

## Attribution

This project uses the Semantic Scholar API. Results and contributions coming from it are provided by [Semantic Scholar](https://www.semanticscholar.org/), a product of the Allen Institute for AI. If you use this tool's output in a published work, cite "The Semantic Scholar Open Data Platform" (Kinney et al., 2023), as required by the Semantic Scholar API license.

## License

This project is licensed under the MIT License. See the `LICENSE` file for the full text.
