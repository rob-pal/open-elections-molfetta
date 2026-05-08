# Elezioni Molfetta

Analisi statistiche delle elezioni comunali di Molfetta, a partire dai dati
pubblici del Comune. La repository raccoglie i dati grezzi, gli script di
elaborazione e i grafici prodotti.

> **Articolo di riferimento:** *(link in arrivo)*
>
> *Roberto A. Palombella - ropalombella@gmail.com*

## Cosa contiene la repository

```
elezioni-molfetta/
├── dati/
│   ├── 8._Voti_di_preferenza_per_lista_2022.pdf      # PDF originale del Comune
│   ├── candidati_consiglieri+preferenze_2022.csv    # CSV estratto dal PDF
│   ├── candidati_consiglieri+preferenze_2022.xlsx   # stessa cosa in xlsx
│   ├── candidati_consiglieri_2026.csv               # liste 2026 trascritte
│   └── candidati_consiglieri_2026.xlsx              # stessa cosa in xlsx
└── analisi-2022-2026/
    ├── normalizza.py                # funzione di normalizzazione nomi
    ├── pdf_to_csv.py         # PDF → CSV (rigenera il dato 2022)
    ├── calcoli_sintetici.py         # numeri usati nell'articolo
    ├── flussi_sankey.py             # diagramma di Sankey 2022 → 2026
    └── diagramma_consiglieri.py     # mappa del consiglio comunale 2025
```

I file `.xlsx` nei dati sono una conversione dei `.csv` per comodità di
chi voglia consultare i dati senza strumenti di programmazione.

## Dati

### Liste 2022 - `candidati_consiglieri+preferenze_2022.csv`

Riga per ogni candidato consigliere alle amministrative 2022. Colonne:

| colonna | significato |
|---|---|
| `lista_num` | numero della lista nel verbale |
| `lista_nome` | nome della lista |
| `candidato_sindaco_num` | numero del candidato sindaco collegato |
| `candidato_sindaco_nome` | nome del candidato sindaco collegato |
| `candidato_num` | numero del candidato dentro la lista |
| `candidato_nome` | nome del candidato consigliere |
| `cifra_individuale` | cifra individuale |
| `preferenze` | preferenze ricevute dal candidato |

Fonte: il PDF `8._Voti_di_preferenza_per_lista_2022.pdf`, scaricato dalla
sezione [Elezioni trasparenti](https://old.comune.molfetta.ba.it/amministrazione/ente/elezioni-trasparenti/category/amministrative)
del sito istituzionale del Comune di Molfetta.

### Liste 2026 - `candidati_consiglieri_2026.csv`

Riga per ogni candidato consigliere alle amministrative 2026. Stesse colonne
del 2022, eccetto `cifra_individuale` e `preferenze` (le elezioni non si sono
ancora tenute al momento dell'analisi).

Fonte: [news24](https://molfetta.news24.city/2026/04/27/elezioni-amministrative-tutte-le-liste-e-i-507-candidati-in-corsa-a-molfetta/)

## Metodi

### 1. Estrazione del CSV 2022 dal PDF - `pdf_to_csv.py`

Il PDF originale è un riepilogo delle preferenze ottenute dai candidati di tutte le liste, una pagina per
lista (25 pagine totali). Lo script:

1. Apre il PDF con `pdfplumber` e itera sulle pagine.
2. Per ogni pagina, riconosce le righe-chiave con espressioni regolari:
   - `Lista: N <NOME>`
   - `Collegata a: N <NOME SINDACO>`
   - righe candidato nella forma `<num> <nome> <cifra_individuale> <preferenze>`,
     dove cifra e preferenze sono numeri in formato italiano (es. `1.359`).
3. Scarta intestazioni, piè di pagina e righe di totale.
4. Emette un CSV con una riga per candidato.

Per rigenerare il CSV dal PDF:

```bash
cd analisi-2022-2026
python pdf_to_csv.py ../dati/8_Voti_di_preferenza_per_lista_2022.pdf \
                            ../dati/candidati_consiglieri+preferenze_2022.csv
```

### 2. Normalizzazione dei nomi - `normalizza.py`

Per confrontare candidati tra il 2022 e il 2026 serve un nome canonico. La
funzione `normalizza()` applica, in ordine:

1. Rimozione di tutto ciò che è tra parentesi: `(detta BETTA)`, `(indipendente)`.
2. Rimozione di suffissi `Detto X` / `Detta X` fuori parentesi.
3. Rimozione di `-indipendente` o ` indipendente` come suffisso.
4. Sostituzione di virgole con spazi.
5. Conversione in maiuscolo.
6. Rimozione degli accenti (es. `NICOLÒ` → `NICOLO`).
7. Rimozione degli apostrofi (es. `DELL'OLIO` → `DELLOLIO`).
8. Compattamento degli spazi multipli.
9. Applicazione di alias manuali (vedi `ALIAS_CONFERMATI` nello script) per
   gestire refusi nei dati di partenza.

### 3. Gestione delle omonimie

In rari casi, nel CSV 2026 lo stesso nome compare più volte all'interno
della stessa coalizione (oppure si verificano omonimie tra anni diversi).
Per evitare doppi conteggi e attribuzioni errate del «ricandidato», le
occorrenze "extra" sono state rinominate aggiungendo un suffisso numerico
(es. `Mario Rossi 2`), in modo che la normalizzazione le tratti come
persone distinte. La regola di assegnazione, dove disponibile, è basata
sulla coerenza politica con la coalizione di provenienza nel 2022.

I CSV pubblicati in questa repository contengono già queste
disambiguazioni applicate.

### 4. Calcoli - `calcoli_sintetici.py`

Stampa a console le statistiche di base usate nell'articolo:

- percentuale di volti nuovi in ognuna delle tre coalizioni 2026;
- matrice complessiva delle destinazioni 2026 dei candidati 2022 (in numero
  di candidati e in voti pesati sulle preferenze 2022);
- percentuale di candidati 2022 che non si ripresentano.

```bash
cd analisi-2022-2026
python calcoli_sintetici.py
```

### 5. Diagramma di Sankey dei flussi - `flussi_sankey.py`

Visualizza i flussi di candidati dal 2022 al 2026, pesati sulle preferenze
ottenute nel 2022.

```bash
cd analisi-2022-2026
python flussi_sankey.py
```

Output: `output/flussi_sankey_voti.png`

### 6. Diagramma del consiglio comunale - `diagramma_consiglieri.py`

Mostra la composizione del consiglio comunale al 17 ottobre 2025 (data delle
dimissioni contestuali che hanno portato allo scioglimento) e il legame di
ciascun consigliere con la coalizione 2026 in cui si ricandida (se si
ricandida). I bordi rossi marcano i consiglieri dimissionari.

```bash
cd analisi-2022-2026
python diagramma_consiglieri.py
```

Output: `output/consiglieri_2022_a_2026.png`

## Come riprodurre i risultati

Requisiti: Python 3.10+ e i pacchetti elencati in `requirements.txt`.

```bash
git clone https://github.com/<utente>/elezioni-molfetta.git
cd elezioni-molfetta
pip install -r requirements.txt

cd analisi-2022-2026
python calcoli_sintetici.py        # i numeri citati nell'articolo
python flussi_sankey.py            # diagramma di flusso
python diagramma_consiglieri.py    # diagramma del consiglio
```

Gli script leggono già i CSV nella cartella `dati/`.
Lo script `pdf_to_csv.py` serve solo se si vuole rigenerare il
`candidati_consiglieri+preferenze_2022.csv` ripartendo dal PDF.

## Limiti dell'analisi

- I dati 2022 sono stati estratti da un PDF, poi
  controllati manualmente; possono restare piccole imprecisioni di
  trascrizione nel PDF originale (refusi nei nomi).
- Il matching tra candidati 2022 e 2026 si basa unicamente sul nome
  normalizzato, perché i dati pubblici non includono date di nascita o
  codici fiscali. In presenza di omonimie, la disambuguazione è soggetta a errori (vedi sezione 3) in ogni caso di piccola entità.
- L'analisi riguarda i candidati consiglieri, non gli elettori. I numeri
  pesati sui voti 2022 misurano il «capitale politico» di candidatura, non
  intenzioni di voto del 2026 né previsioni elettorali.

## Licenza

I contenuti di questa repository sono distribuiti sotto licenze differenti. Maggiori dettagli nei file [LICENSE](LICENSE) e [LICENSE-DATA](LICENSE-DATA).

- **Codice sorgente** (`*.py`): [MIT License](LICENSE)
- **Dati** (`dati/`): [CC0 1.0 (Pubblico Dominio)](LICENSE-DATA)
- **Grafici** (`output/`): [CC BY 4.0](LICENSE-DATA)

Tutti i materiali sono forniti "così come sono", senza alcuna garanzia di esattezza o di adeguatezza ad alcuno scopo. L'utilizzo di questi file non implica in alcun modo che l'autore avalli l'uso o le interpretazioni che terzi ne faranno.

## Citazione

Se utilizzi questi materiali per un tuo progetto o articolo, la citazione della fonte è gradita:

```text
Roberto A. Palombella, "Elezioni Molfetta - analisi 2022/2026",
[https://github.com/rob-pal/elezioni-molfetta](https://github.com/rob-pal/elezioni-molfetta)

```

## Contatti

Per segnalazione di errori, proposte di collaborazione o altro inviare una mail all'indirizzo: ropalombella@gmail.com

Codice sviluppato con il supporto di Claude (Anthropic).
