"""
Calcoli sintetici di flusso 2022 → 2026.

Stampa a console le statistiche di base usate nell'articolo:
  1. Destinazione 2026 dei candidati di Minervini T. '22 ricandidati
  2. % di volti nuovi in ognuna delle tre coalizioni 2026
  3. Matrice destinazioni 2026 (teste e voti) e % non ricandidati
"""

from pathlib import Path

import pandas as pd

from normalizza import normalizza


# Path relativi alla root della repo
ROOT     = Path(__file__).resolve().parent.parent
CSV_2022 = ROOT / "dati" / "candidati_consiglieri+preferenze_2022.csv"
CSV_2026 = ROOT / "dati" / "candidati_consiglieri_2026.csv"


def main():
    df22 = pd.read_csv(CSV_2022)
    df26 = pd.read_csv(CSV_2026)
    df22["nome_norm"] = df22["candidato_nome"].map(normalizza)
    df26["nome_norm"] = df26["candidato_nome"].map(normalizza)

    nomi_2022_tutti = set(df22["nome_norm"])
    nomi_2026_tutti = set(df26["nome_norm"])
    sindaco26_per_nome = df26.groupby("nome_norm")["candidato_sindaco_nome"].first()

    # ============================================================
    # 2) % volti nuovi per coalizione 2026
    # ============================================================
    print()
    print("=" * 72)
    print("1) % VOLTI NUOVI NELLE COALIZIONI 2026")
    print("   (= candidati 2026 non presenti in nessuna lista 2022)")
    print("=" * 72)

    rows = []
    df26_uniq = df26.drop_duplicates(
        subset=["nome_norm", "candidato_sindaco_nome", "lista_nome"]
    )
    for sindaco, gruppo in df26_uniq.groupby("candidato_sindaco_nome"):
        tot   = len(gruppo)
        nuovi = (~gruppo["nome_norm"].isin(nomi_2022_tutti)).sum()
        gia   = tot - nuovi
        rows.append({
            "coalizione_2026":  sindaco,
            "totale_candidati": tot,
            "volti_nuovi":      int(nuovi),
            "gia_in_2022":      int(gia),
            "%_nuovi":          round(nuovi / tot * 100, 2),
        })
    tab = pd.DataFrame(rows).set_index("coalizione_2026")
    tab = tab.sort_values("%_nuovi", ascending=False)
    print()
    print(tab.to_string())

    # ============================================================
    # 3) Destinazioni 2026 dei candidati 2022
    # ============================================================
    print()
    print("=" * 72)
    print("2) DESTINAZIONI 2026 DEI CANDIDATI 2022")
    print("=" * 72)

    df22_u = (df22.groupby("nome_norm")
                  .agg(sindaco_22=("candidato_sindaco_nome", "first"),
                       voti=("preferenze", "sum")))
    df22_u["dest_26"] = (df22_u.index.map(sindaco26_per_nome)
                                       .fillna("Non ricandidato"))

    tot, voti_tot = len(df22_u), df22_u["voti"].sum()
    non_ric = (df22_u["dest_26"] == "Non ricandidato").sum()
    voti_nr = df22_u.loc[df22_u["dest_26"] == "Non ricandidato", "voti"].sum()
    print(f"\n% candidati 2022 non ricandidati: "
          f"{non_ric/tot*100:.2f}% ({non_ric}/{tot})")
    print(f"% voti 2022 non ricandidati:      "
          f"{voti_nr/voti_tot*100:.2f}% ({voti_nr}/{voti_tot})")

    ric = df22_u[df22_u["dest_26"] != "Non ricandidato"]
    m_t = ric.pivot_table(index="sindaco_22", columns="dest_26",
                          values="voti", aggfunc="count", fill_value=0)
    m_v = ric.pivot_table(index="sindaco_22", columns="dest_26",
                          values="voti", aggfunc="sum", fill_value=0)

    print("\nMatrice % TESTE (su soli ricandidati, per riga):")
    print((m_t.div(m_t.sum(axis=1), axis=0) * 100).round(1).to_string())
    print(f"  totali ricandidati: {m_t.sum(axis=1).to_dict()}")

    print("\nMatrice % VOTI (su soli ricandidati, per riga):")
    print((m_v.div(m_v.sum(axis=1), axis=0) * 100).round(1).to_string())
    print(f"  totali voti: {m_v.sum(axis=1).to_dict()}")


if __name__ == "__main__":
    main()
