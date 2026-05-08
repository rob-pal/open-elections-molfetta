"""
Diagramma del consiglio comunale al 17 ottobre 2025 e schieramenti 2026.

A SINISTRA: i consiglieri di OPPOSIZIONE
IN ALTO A SINISTRA, sopra OPPOSIZIONE: Sindaco F.F. e Presidente del Consiglio
sotto: i consiglieri di MAGGIORANZA
LINEE: collegano ogni consigliere al sindaco con cui si ricandida nel 2026
       (niente linea = non si ricandida)
BORDI: rosso = dimissionario al 17/10/2025; azzurro scuro = non dimissionario.

Output: ../output/consiglieri_2022_a_2026.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch, PathPatch, Rectangle
from matplotlib.path import Path as MplPath

from normalizza import normalizza


# Path relativi alla root della repo
ROOT     = Path(__file__).resolve().parent.parent
CSV_2026 = ROOT / "dati" / "candidati_consiglieri_2026.csv"
OUTDIR   = ROOT / "output"
OUTDIR.mkdir(exist_ok=True)
OUTPUT   = OUTDIR / "consiglieri_2022_a_2026.png"

# ============================================================
# DATI — composizione del consiglio comunale al 17/10/2025
# ============================================================
OPPOSIZIONE = [
    ("Azzollini Gabriella",          "Partito Democratico", True),
    ("Binetti Mauro",                "Molfetta Nostra", True),
    ("D'Amato Alberto",              "Partito Democratico", True),
    ("Gagliardi Annamaria Fabrizia", "Drago Sindaco", True),
    ("Gagliardi Domenico",           "Molfetta Libera", True),
    ("Germinario Ippolita",          "Obiettivo Molfetta", True),
    ("Infante Giovanni",             "", True),
    ("Lanza Girolamo Viktor",        "Avanti Molfetta", True),
    ("Mastropasqua Pietro",          "", True),
    ("Spaccavento Felice Antonio",   "Rinascere", True),
]

MAGGIORANZA = [
    ("Ancona Antonio",               "Molfetta in Azione", False),
    ("Crocifero Antonia",            "Ala Democratica", True),
    ("De Gioia Onofrio",             "Minervini Sindaco", False),
    ("De Palma Francesca",           "Molfetta che Vogliamo", False),
    ("Facchini Giovanni",            "Cuore Democratico", False),
    ("Fiorentino Angelo",            "Patto Comune", False),
    ("Germano Carmela",              "Molfetta al Centro", False),
    ("Ginosa Elena",                 "Minervini Sindaco", False),
    ("Minervini Leonardo",           "Cuore Democratico", False),
    ("Paparella Vito Corrado",       "Ala Democratica", False),
    ("Poli Maridda Maria",           "Molfetta Popolare", True),
    ("Petruzzelli Annalisa",         "Insieme per la Città", False),
    ("Salvemini Giacomo",            "Insieme per la Città", False),
]

# Box istituzionali in alto a sinistra: (nome, ruolo, dimissionario)
ISTITUZIONALI = [
    ("Piergiovanni Nicola", "Sindaco F.F.", False),
    ("Amato Robert",        "Presidente",   True),
]

# Override manuale: chi non è nel CSV dei candidati 2026 ma sappiamo dove va
OVERRIDE_DEST = {
    "Mastropasqua Pietro":   "PIETRO MASTROPASQUA",
    "Nicola Piergiovanni":   "PIETRO MASTROPASQUA",
    "Robert Amato":          "PIETRO MASTROPASQUA",
}

SINDACI_2026 = [
    "MANUEL MINERVINI",
    "PIETRO MASTROPASQUA",
    "ADAMO LOGRIECO",
]

# ============================================================
# COLORI
# ============================================================
COL_OPP_BG     = "#fce4e4"
COL_MAJ_BG     = "#e8eef7"
COL_DIM_BORDER = "#c0392b"
COL_NON_BORDER = "#34495e"
COL_IST_BG     = "#e3e1da"
COL_IST_BORDER = "#555452"

COL_SIND = {
    "MANUEL MINERVINI":    "#c26eaa",
    "PIETRO MASTROPASQUA": "#4e79a7",
    "ADAMO LOGRIECO":      "#f28e2b",
}

# ============================================================
# GEOMETRIA
# ============================================================
BOX_W = 4.4
BOX_H = 0.65
GAP_BOX = 0.18
LX = 0.5
RX = 12.2
SX_W = 2.6
SX_H = 4.0
LINE_W = 1.8
LINE_ALPHA = 0.75

IST_BOX_W = BOX_W
IST_BOX_H = 0.70
IST_GAP   = 0.18
IST_TOP_Y = 0.95


# ============================================================
# LOGICA
# ============================================================
def calcola_destinazioni():
    df26 = pd.read_csv(CSV_2026)
    df26["nome_norm"] = df26["candidato_nome"].map(normalizza)
    map26 = dict(zip(df26["nome_norm"], df26["candidato_sindaco_nome"]))

    out = {}
    for nome, _, _ in OPPOSIZIONE + MAGGIORANZA + ISTITUZIONALI:
        out[nome] = OVERRIDE_DEST.get(nome) or map26.get(normalizza(nome))
    return out


def layout_y():
    pos_ist = {}
    y = IST_TOP_Y
    for nome, _, _ in ISTITUZIONALI:
        pos_ist[nome] = y + IST_BOX_H / 2
        y += IST_BOX_H + IST_GAP
    y += 1.4

    pos_cons = {}
    for nome, _, _ in OPPOSIZIONE:
        pos_cons[nome] = y + BOX_H / 2
        y += BOX_H + GAP_BOX
    y += 0.9
    for nome, _, _ in MAGGIORANZA:
        pos_cons[nome] = y + BOX_H / 2
        y += BOX_H + GAP_BOX
    return pos_ist, pos_cons, y + 0.5


def calcola_entry_points(dest, pos_all, sindaco_yc):
    incoming = {s: [] for s in SINDACI_2026}
    for nome, d in dest.items():
        if d in incoming and nome in pos_all:
            incoming[d].append((pos_all[nome], nome))
    entry = {}
    margin = SX_H * 0.1
    usable = SX_H - 2 * margin
    for s, lst in incoming.items():
        lst.sort()
        if not lst:
            continue
        if len(lst) == 1:
            entry[lst[0][1]] = sindaco_yc[s]
        else:
            top = sindaco_yc[s] - SX_H / 2 + margin
            for i, (_, nome) in enumerate(lst):
                entry[nome] = top + (i / (len(lst) - 1)) * usable
    return entry


def disegna_box_consigliere(ax, x, yc, nome, partito, bg, border):
    rect = Rectangle((x, yc - BOX_H / 2), BOX_W, BOX_H,
                     facecolor=bg, edgecolor=border, linewidth=1.4)
    ax.add_patch(rect)
    ax.text(x + 0.18, yc, nome, ha="left", va="center",
            fontsize=10, fontweight="bold")
    ax.text(x + BOX_W - 0.18, yc, partito, ha="right", va="center",
            fontsize=8, color="#666", style="italic")


def disegna_box_istituzionale(ax, x, yc, nome, ruolo, dimissionario):
    border = COL_DIM_BORDER if dimissionario else COL_IST_BORDER
    rect = Rectangle((x, yc - IST_BOX_H / 2), IST_BOX_W, IST_BOX_H,
                     facecolor=COL_IST_BG, edgecolor=border, linewidth=1.6)
    ax.add_patch(rect)
    ax.text(x + 0.18, yc, nome, ha="left", va="center",
            fontsize=10, fontweight="bold")
    ax.text(x + IST_BOX_W - 0.18, yc, ruolo, ha="right", va="center",
            fontsize=8, color=border, fontweight="bold", style="italic")


def disegna_box_sindaco(ax, x, yc, nome, color):
    rect = Rectangle((x, yc - SX_H / 2), SX_W, SX_H,
                     facecolor=color, edgecolor="#222",
                     linewidth=2, alpha=0.9)
    ax.add_patch(rect)
    ax.text(x + SX_W / 2, yc, "\n".join(nome.split()),
            ha="center", va="center",
            fontsize=14, fontweight="bold", color="white")


def disegna_linea(ax, x0, y0, x1, y1, color):
    xm = (x0 + x1) / 2
    verts = [(x0, y0), (xm, y0), (xm, y1), (x1, y1)]
    codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor="none",
                           edgecolor=color, linewidth=LINE_W, alpha=LINE_ALPHA))


def main():
    dest = calcola_destinazioni()
    pos_ist, pos_cons, total_h = layout_y()
    pos_all = {**pos_ist, **pos_cons}

    spacing = (total_h - 3 * SX_H) / 4
    sindaco_yc = {}
    yy = spacing
    for s in SINDACI_2026:
        sindaco_yc[s] = yy + SX_H / 2
        yy += SX_H + spacing

    entry = calcola_entry_points(dest, pos_all, sindaco_yc)

    fig, ax = plt.subplots(figsize=(15.5, max(11.0, total_h * 0.55)), dpi=140)
    ax.set_xlim(0, 16); ax.set_ylim(0, total_h)
    ax.invert_yaxis(); ax.axis("off")

    ax.text(8, 0.4,
            "Consiglio comunale 2025 - schieramenti 2026",
            ha="center", va="center", fontsize=15, fontweight="bold")

    for nome, ruolo, dimissionario in ISTITUZIONALI:
        disegna_box_istituzionale(ax, LX, pos_ist[nome], nome, ruolo,
                                  dimissionario)

    yc_first_opp = pos_cons[OPPOSIZIONE[0][0]]
    ax.text(LX + BOX_W / 2, yc_first_opp - BOX_H / 2 - 0.4,
            "OPPOSIZIONE",
            ha="center", va="center", fontsize=12, fontweight="bold",
            color="#a93226")

    for nome, partito, dimissionario in OPPOSIZIONE:
        border = COL_DIM_BORDER if dimissionario else COL_NON_BORDER
        disegna_box_consigliere(ax, LX, pos_cons[nome], nome, partito,
                                COL_OPP_BG, border)

    yc_first_maj = pos_cons[MAGGIORANZA[0][0]]
    ax.text(LX + BOX_W / 2, yc_first_maj - BOX_H / 2 - 0.4,
            "MAGGIORANZA",
            ha="center", va="center", fontsize=12, fontweight="bold",
            color="#2471a3")

    for nome, partito, dimissionario in MAGGIORANZA:
        border = COL_DIM_BORDER if dimissionario else COL_NON_BORDER
        bg = COL_OPP_BG if dimissionario else COL_MAJ_BG
        disegna_box_consigliere(ax, LX, pos_cons[nome], nome, partito,
                                bg, border)

    for s in SINDACI_2026:
        disegna_box_sindaco(ax, RX, sindaco_yc[s], s, COL_SIND[s])

    for nome in pos_all:
        d = dest.get(nome)
        if d in COL_SIND:
            disegna_linea(ax, LX + BOX_W, pos_all[nome],
                          RX, entry[nome], COL_SIND[d])

    legend_elements = [
        Patch(facecolor='#f5f5f5', edgecolor=COL_DIM_BORDER, linewidth=1.5,
              label='Dimissionario'),
    ]
    ax.legend(handles=legend_elements, loc='lower left',
              bbox_to_anchor=(0.0, 0.0),
              frameon=False, fontsize=11, ncol=2)
    fig.text(0.98, 0.02,
             "Liste di appartenenza riferite alle amministrative 2022.\n"
             "Fonte: dati pubblici del Comune di Molfetta.",
             ha="right", va="bottom", fontsize=8, color="#666", style="italic")

    plt.tight_layout()
    plt.savefig(OUTPUT, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"✓ Salvato: {OUTPUT}")


if __name__ == "__main__":
    main()
