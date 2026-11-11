def stampa(scaricati: list[dict], da_recuperare: list[dict], scartati_duplicati: int, candidati_esaminati: int, dry_run: bool = False) -> None:
    print("\n" + "=" * 60)
    print("RESOCONTO SCANSIONE" + (" (DRY-RUN: nessun file scaricato, Excel non toccato)" if dry_run else ""))
    print("=" * 60)
    print(f"Candidati esaminati: {candidati_esaminati}")
    print(f"Già presenti in archivio (scartati): {scartati_duplicati}")

    titolo_lista = "Che verrebbero scaricati e aggiunti all'archivio" if dry_run else "Scaricati e aggiunti all'archivio"
    print(f"\n{titolo_lista}: {len(scaricati)}")
    for p in scaricati:
        ambiguo = " [DA CATEGORIZZARE]" if p["filone"] == "Da categorizzare" else ""
        print(f"  - {p['titolo']}")
        print(f"      autori/anno: {p['autore_anno']} | fonte: {p['fonte']}")
        print(f"      cartella: {p['filone']}{ambiguo}")
        print(f"      file: {p['file_rel']}")

    print(f"\nPertinenti ma non scaricabili (in 'Da recuperare'): {len(da_recuperare)}")
    for p in da_recuperare:
        print(f"  - {p['titolo']} — motivo: {p['motivo']}")
        if p.get("link"):
            print(f"      link: {p['link']}")

    print("=" * 60)
