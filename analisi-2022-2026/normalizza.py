"""
Funzione di normalizzazione dei nomi candidati per il matching tra
liste 2022 e 2026.

Importata da tutti gli script della cartella `analisi-2022-2026`.
"""

import re
import unicodedata


# Alias manuali confermati: nomi diversi nei due CSV ma stessa persona reale.
# Mappa: forma_normalizzata_di_partenza  →  forma_normalizzata_canonica
ALIAS_CONFERMATI = {
    "PAPARELLA VITO CORADO": "PAPARELLA VITO CORRADO",  # refuso nei dati 2022
    "POLI MARIDDA MARIA":    "POLI MARIDDA",
}


def normalizza(nome: str) -> str:
    """Normalizza un nome candidato per consentire il match tra 2022 e 2026.

    Operazioni applicate, in ordine:
      1. rimuove tutto ciò che è tra parentesi: '(detta BETTA)', '(indipendente)'
      2. rimuove suffissi 'Detto X' / 'Detta X' fuori parentesi
      3. rimuove '-indipendente' o ' indipendente' come suffisso
      4. sostituisce virgole con spazi
      5. converte in maiuscolo
      6. rimuove accenti (NICOLÒ -> NICOLO)
      7. rimuove apostrofi (NICOLO' -> NICOLO, DELL'OLIO -> DELLOLIO)
      8. compatta gli spazi multipli
      9. applica eventuali alias confermati manualmente

    NB: i suffissi numerici "  2", " 3" usati per disambiguare omonimi
    (vedi fix_omonimi.py) sopravvivono volutamente alla normalizzazione,
    perché distinguono persone diverse.
    """
    if not isinstance(nome, str):
        return ""
    s = nome
    s = re.sub(r"\([^)]*\)", " ", s)                  # 1
    s = re.sub(r"\s+[Dd]ett[oa]\s+\w+", " ", s)       # 2
    s = re.sub(r"\s*-?\s*[Ii]ndipendente\b", " ", s)  # 3
    s = s.replace(",", " ")                           # 4
    s = s.upper()                                     # 5
    s = unicodedata.normalize("NFKD", s)              # 6
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("'", "").replace("\u2019", "")      # 7
    s = re.sub(r"\s+", " ", s).strip()                # 8
    s = ALIAS_CONFERMATI.get(s, s)                    # 9
    return s
