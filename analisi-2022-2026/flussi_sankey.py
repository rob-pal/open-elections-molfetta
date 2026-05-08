"""
Diagramma di Sankey dei flussi candidati 2022 → 2026, pesato sulle
preferenze ottenute nel 2022.

A SINISTRA: le 4 coalizioni del 2022 (Drago, Infante, Mastropasqua, Minervini T.)
A DESTRA:   le 3 coalizioni del 2026 (Minervini M., Mastropasqua, Logrieco)
            + un nodo "Non si ricandida" che rappresenta i candidati 2022
            che non si ripresentano.

L'altezza di ogni nodo e di ogni flusso è proporzionale al numero di
preferenze ottenute dai candidati nel 2022.

Output: ../output/flussi_sankey_voti.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path as MplPath

from normalizza import normalizza


# Path relativi alla root della repo
ROOT     = Path(__file__).resolve().parent.parent
CSV_2022 = ROOT / "dati" / "candidati_consiglieri+preferenze_2022.csv"
CSV_2026 = ROOT / "dati" / "candidati_consiglieri_2026.csv"
OUTDIR   = ROOT / "output"
OUTDIR.mkdir(exist_ok=True)


SHORT_2022 = {
    "DRAGO PASQUALE":            "Drago '22",
    "MASTROPASQUA PIETRO PAOLO": "Mastropasqua '22",
    "INFANTE GIOVANNI":          "Infante '22",
    "MINERVINI TOMMASO":         "Minervini T. '22",
}
SHORT_2026 = {
    "MANUEL MINERVINI":     "Minervini M. '26",
    "PIETRO MASTROPASQUA":  "Mastropasqua '26",
    "ADAMO LOGRIECO":       "Logrieco '26",
}
NON_RIC = "Non si ricandida"

ORDER_2022 = ["Drago '22", "Infante '22", "Mastropasqua '22", "Minervini T. '22"]
ORDER_2026 = ["Minervini M. '26", "Mastropasqua '26", "Logrieco '26", NON_RIC]

COLORI = {
    "Drago '22":          "#e15759",
    "Mastropasqua '22":   "#4e79a7",
    "Infante '22":        "#8dcfcd",
    "Minervini T. '22":   "#59a14f",
    "Minervini M. '26":   "#c26eaa",
    "Mastropasqua '26":   "#4e79a7",
    "Logrieco '26":       "#f28e2b",
    NON_RIC:              "#bbbbbb",
}


def costruisci_matrice_voti():
    """Restituisce la matrice di flusso pesata sulle preferenze 2022."""
    df22 = pd.read_csv(CSV_2022)
    df26 = pd.read_csv(CSV_2026)
    df22["nome_norm"] = df22["candidato_nome"].map(normalizza)
    df26["nome_norm"] = df26["candidato_nome"].map(normalizza)
    df22["short_22"] = df22["candidato_sindaco_nome"].map(SHORT_2022)
    df26["short_26"] = df26["candidato_sindaco_nome"].map(SHORT_2026)

    df22_u = (df22.groupby("nome_norm")
                  .agg(short_22=("short_22", "first"),
                       voti=("preferenze", "sum")))
    sindaco26 = df26.groupby("nome_norm")["short_26"].first()
    df22_u["short_26"] = df22_u.index.map(sindaco26).fillna(NON_RIC)

    voti = (df22_u.pivot_table(index="short_22", columns="short_26",
                                values="voti", aggfunc="sum", fill_value=0)
                  .reindex(index=ORDER_2022, columns=ORDER_2026, fill_value=0)
                  .astype(int))
    return voti


def disegna_sankey(m: pd.DataFrame, output_path: Path):
    nodi_sx = [n for n in ORDER_2022 if m.loc[n].sum() > 0]
    nodi_dx = [n for n in ORDER_2026 if m[n].sum() > 0]
    out_sx = {n: m.loc[n].sum() for n in nodi_sx}
    in_dx  = {n: m[n].sum()      for n in nodi_dx}
    totale = sum(out_sx.values())

    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=140)
    ax.set_xlim(0, 10); ax.set_ylim(0, totale * 1.08)
    ax.invert_yaxis(); ax.axis("off")
    fig.patch.set_facecolor("#fafafa")

    GAP = totale * 0.025
    BAR_W = 0.35

    # Nodi a sinistra
    y = 0
    pos_sx = {}
    for n in nodi_sx:
        h = out_sx[n]
        pos_sx[n] = (y, h)
        ax.add_patch(Rectangle((1.0, y), BAR_W, h,
                               facecolor=COLORI[n], edgecolor="#222", lw=0.5))
        ax.text(0.95, y + h / 2, n, ha="right", va="center",
                fontsize=12, fontweight="bold")
        # Numero preferenze totali della coalizione
        ax.text(1.0 + BAR_W + 0.08, y + h / 2,
                f"{int(h):,}".replace(",", "."),
                ha="left", va="center", fontsize=10, color="#444")
        y += h + GAP

    # Nodi a destra
    tot_dx = sum(in_dx.values()) + GAP * (len(nodi_dx) - 1)
    y = (totale * 1.08 - tot_dx) / 2
    pos_dx = {}
    for n in nodi_dx:
        h = in_dx[n]
        pos_dx[n] = (y, h)
        ax.add_patch(Rectangle((9.0 - BAR_W, y), BAR_W, h,
                               facecolor=COLORI[n], edgecolor="#222", lw=0.5))
        ax.text(9.05, y + h / 2, n, ha="left", va="center",
                fontsize=12, fontweight="bold")
        y += h + GAP

    # Flussi
    cur_sx = {n: pos_sx[n][0] for n in nodi_sx}
    cur_dx = {n: pos_dx[n][0] for n in nodi_dx}
    for src in nodi_sx:
        for tgt in nodi_dx:
            val = float(m.at[src, tgt])
            if val <= 0:
                continue
            y0a, y0b = cur_sx[src], cur_sx[src] + val
            y1a, y1b = cur_dx[tgt], cur_dx[tgt] + val
            cur_sx[src] += val
            cur_dx[tgt] += val

            x0 = 1.0 + BAR_W
            x1 = 9.0 - BAR_W
            xm = (x0 + x1) / 2
            verts = [(x0, y0a), (xm, y0a), (xm, y1a), (x1, y1a),
                     (x1, y1b), (xm, y1b), (xm, y0b), (x0, y0b),
                     (x0, y0a)]
            codes = [MplPath.MOVETO] + [MplPath.CURVE4] * 3 + \
                    [MplPath.LINETO] + [MplPath.CURVE4] * 3 + [MplPath.CLOSEPOLY]
            base = COLORI[src].lstrip("#")
            r, g, b = (int(base[i:i+2], 16) / 255 for i in (0, 2, 4))
            ax.add_patch(PathPatch(MplPath(verts, codes),
                                   facecolor=(r, g, b, 0.5), edgecolor="none"))

    ax.set_title("Flussi candidati 2022 → 2026 (pesati sulle preferenze 2022)",
                 fontsize=14, pad=14, fontweight="bold")

    fig.text(0.02, 0.02,
             "I numeri accanto ai nodi 2022 indicano il totale delle "
             "preferenze dei singoli candidati, non delle liste.",
             ha="left", va="bottom", fontsize=9, color="#555", style="italic")
    fig.text(0.98, 0.02,
             "Fonte: elaborazione propria su dati del Comune di Molfetta.",
             ha="right", va="bottom", fontsize=8, color="#666", style="italic")

    plt.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"✓ Salvato: {output_path}")


def main():
    voti = costruisci_matrice_voti()
    print("Matrice VOTI (incluso 'Non si ricandida'):")
    print(voti.to_string())
    print()
    disegna_sankey(voti, OUTDIR / "flussi_sankey_voti.png")


if __name__ == "__main__":
    main()
