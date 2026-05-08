"""
Estrae i dati delle preferenze per lista dal PDF "Riepilogo Generale Preferenze"
del Comune di Molfetta (elezioni amministrative 2022) in un CSV.

Il PDF ha 25 pagine, una per lista. Ogni pagina contiene:
  - numero e nome della lista
  - candidato sindaco collegato
  - elenco candidati con: numero, nome, cifra individuale, preferenze

Output CSV: una riga per candidato, con tutti i dati di contesto della lista.

Uso:
    python pdf_to_csv.py <input.pdf> [output.csv]

Esempio:
    python pdf_to_csv.py ../dati/8_Voti_di_preferenza_per_lista_2022.pdf \\
                                ../dati/candidati_consiglieri+preferenze_2022.csv
"""

import csv
import re
import sys
from pathlib import Path

import pdfplumber


# Regex per le righe che ci interessano
RE_LISTA = re.compile(r"^Lista:\s+(\d+)\s+(.+)$")
RE_COLLEGATA = re.compile(r"^Collegata a:\s+(\d+)\s+(.+)$")
# Riga candidato: NUM  NOME (con spazi/parentesi/apostrofi)  CIFRA  PREF
# Le cifre italiane usano "." come separatore migliaia (es. "1.359")
RE_CANDIDATO = re.compile(r"^(\d+)\s+(.+?)\s+([\d.]+)\s+([\d.]+)$")


def parse_numero_it(s: str) -> int:
    """Converte un numero in formato italiano ('1.359') in int."""
    return int(s.replace(".", ""))


def estrai_dati(pdf_path: Path) -> list[dict]:
    """Estrae tutti i record candidato dal PDF."""
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                print(f"⚠ Pagina {page_num}: testo vuoto, salto", file=sys.stderr)
                continue

            lista_num = lista_nome = None
            candidato_sindaco_num = candidato_sindaco_nome = None

            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue

                # Salto le righe di intestazione/footer
                if line.startswith(("Riepilogo Generale", "Comune di Molfetta",
                                    "Consultazione:", "Scheda:", "Candidato",
                                    "Totale", "Stampato il")):
                    continue

                # Lista
                m = RE_LISTA.match(line)
                if m:
                    lista_num = int(m.group(1))
                    lista_nome = m.group(2).strip()
                    continue

                # Candidato sindaco collegato
                m = RE_COLLEGATA.match(line)
                if m:
                    candidato_sindaco_num = int(m.group(1))
                    candidato_sindaco_nome = m.group(2).strip()
                    continue

                # Riga candidato
                m = RE_CANDIDATO.match(line)
                if m and lista_num is not None:
                    records.append({
                        "lista_num": lista_num,
                        "lista_nome": lista_nome,
                        "candidato_sindaco_num": candidato_sindaco_num,
                        "candidato_sindaco_nome": candidato_sindaco_nome,
                        "candidato_num": int(m.group(1)),
                        "candidato_nome": m.group(2).strip(),
                        "cifra_individuale": parse_numero_it(m.group(3)),
                        "preferenze": parse_numero_it(m.group(4)),
                    })
                    continue

                # Riga non riconosciuta — utile per debug
                print(f"⚠ Pagina {page_num}: riga non riconosciuta: {line!r}",
                      file=sys.stderr)

    return records


def scrivi_csv(records: list[dict], csv_path: Path) -> None:
    """Scrive il CSV con header."""
    fieldnames = [
        "lista_num", "lista_nome",
        "candidato_sindaco_num", "candidato_sindaco_nome",
        "candidato_num", "candidato_nome",
        "cifra_individuale", "preferenze",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    if len(sys.argv) < 2:
        print("Uso: python estrai_preferenze.py <input.pdf> [output.csv]")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    csv_path = Path(sys.argv[2]) if len(sys.argv) > 2 else pdf_path.with_suffix(".csv")

    records = estrai_dati(pdf_path)
    scrivi_csv(records, csv_path)

    liste = sorted({(r["lista_num"], r["lista_nome"]) for r in records})
    print(f"Estratti {len(records)} record da {len(liste)} liste")
    print(f"CSV scritto in: {csv_path}")


if __name__ == "__main__":
    main()
