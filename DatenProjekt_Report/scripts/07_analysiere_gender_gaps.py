"""
07_analysiere_gender_gaps.py

Berechnet für alle Geschlechter-Familien mit konsistenter Einheit die
Differenz Frauen − Männer (Gender-Gap) auf Kreisebene.

Ausgaben in data/processed/:
- analyse_gaps_kreise.csv      eine Zeile je Kreis, eine Gap-Spalte je Familie
- analyse_gaps_regionen.csv    lang: Merkmal × Regionstyp × Familie × Mittel/Median
- analyse_rankings.csv         Top-10 / Bottom-10 je Gap
"""
from pathlib import Path
import numpy as np
import pandas as pd

PROJEKT   = Path(__file__).resolve().parents[2]
REPORT    = PROJEKT / "DatenProjekt_Report"
PROCESSED = REPORT / "data" / "processed"
METADATA  = REPORT / "data" / "metadata"

MASTER  = PROCESSED / "inkar_bayern_2023_master_validiert.csv"
KATALOG = METADATA  / "indikatorenliste_final.csv"

# Abitur-Sonderfall: 0,0 in den Rohdaten bedeutet "keine Daten",
# nicht "0 %". Laut 02b: 09471 (Bamberg, LK) und 09678 (Schweinfurt, LK).
ABITUR_NULL_AGS = ["09471", "09678"]


# --------------------------------------------------------------------------
# 1. Laden
# --------------------------------------------------------------------------
master = pd.read_csv(MASTER, sep=";", dtype={"Kennziffer": "string"})
master["Kennziffer"] = master["Kennziffer"].str.zfill(5)

katalog = pd.read_csv(KATALOG, sep=";", dtype=str).fillna("")


# --------------------------------------------------------------------------
# 2. Nur Familien, deren Frauen- und Männerwerte direkt vergleichbar sind
# --------------------------------------------------------------------------
gueltig = katalog[
    (katalog["gap_berechenbar"] == "ja")
    & (katalog["einheit_konsistent_in_familie"] == "ja")
]

gaps = master[
    ["Kennziffer", "kreisname", "kreistyp", "regierungsbezirk",
     "lep_gebietskategorie", "rmbh", "Bevölkerung gesamt"]
].copy()

familien = sorted(gueltig["indikator_familie"].unique())

for familie in familien:
    f_liste = gueltig[
        (gueltig["indikator_familie"] == familie)
        & (gueltig["geschlechtsbezug"] == "Frauen")
    ]["indikator"].tolist()
    m_liste = gueltig[
        (gueltig["indikator_familie"] == familie)
        & (gueltig["geschlechtsbezug"] == "Männer")
    ]["indikator"].tolist()

    if len(f_liste) != 1 or len(m_liste) != 1:
        print(f"SKIP {familie}: erwartet 1xF/1xM, "
              f"gefunden {len(f_liste)}/{len(m_liste)}")
        continue

    f_col, m_col = f_liste[0], m_liste[0]
    gap_name = f"gap_{familie}"

    gaps[gap_name] = master[f_col] - master[m_col]

    # Abitur-Sonderfall: 0,0 ist "keine Daten", nicht "0 %"
    if "Hochschulreife" in familie:
        maske = gaps["Kennziffer"].isin(ABITUR_NULL_AGS)
        if maske.any():
            gaps.loc[maske, gap_name] = np.nan
            print(f"Hinweis: {gap_name} bei {ABITUR_NULL_AGS} "
                  f"auf NaN gesetzt (keine Daten).")

gaps.to_csv(PROCESSED / "analyse_gaps_kreise.csv", sep=";",
            index=False, encoding="utf-8-sig")


# --------------------------------------------------------------------------
# 3. Regionale Mittelwerte (lang-Format)
# --------------------------------------------------------------------------
gap_cols = [c for c in gaps.columns if c.startswith("gap_")]

region_lang = []
for gruppe in ["lep_gebietskategorie", "rmbh", "kreistyp", "regierungsbezirk"]:
    for col in gap_cols:
        s = (
            gaps.groupby(gruppe)[col]
                .agg(["mean", "median", "count"])
                .reset_index()
        )
        s.columns = ["regionstyp", "mittelwert", "median", "n"]
        s["merkmal"] = gruppe
        s["familie"] = col.replace("gap_", "")
        region_lang.append(s)

regionen = pd.concat(region_lang, ignore_index=True)
regionen.to_csv(PROCESSED / "analyse_gaps_regionen.csv", sep=";",
                index=False, encoding="utf-8-sig")


# --------------------------------------------------------------------------
# 4. Top-10 / Bottom-10 je Gap
# --------------------------------------------------------------------------
rankings = []
for col in gap_cols:
    tmp = gaps[["Kennziffer", "kreisname", col]].dropna()

    top = (
        tmp.nlargest(10, col)
           .assign(richtung="top",
                   familie=col.replace("gap_", ""))
           .rename(columns={col: "wert"})
    )
    bottom = (
        tmp.nsmallest(10, col)
           .assign(richtung="bottom",
                   familie=col.replace("gap_", ""))
           .rename(columns={col: "wert"})
    )
    rankings.append(pd.concat([top, bottom], ignore_index=True))

rankings = pd.concat(rankings, ignore_index=True)
rankings = rankings[["familie", "richtung", "Kennziffer", "kreisname", "wert"]]
rankings.to_csv(PROCESSED / "analyse_rankings.csv", sep=";",
                index=False, encoding="utf-8-sig")


# --------------------------------------------------------------------------
# 5. Zusammenfassung
# --------------------------------------------------------------------------
print("\n" + "=" * 60)
print("GENDER-GAP-ANALYSE")
print("=" * 60)

print(f"\nKreise: {len(gaps)}   Gap-Spalten: {len(gap_cols)}")

print("\nVerteilung der Gaps (Frauen minus Männer, "
      "in der jeweiligen Einheit der Familie):\n")
for col in gap_cols:
    s = gaps[col].dropna()
    print(f"  {col:55s} "
          f"n={len(s):3d}  "
          f"mean={s.mean():+8.3f}  "
          f"median={s.median():+8.3f}  "
          f"min={s.min():+8.3f}  max={s.max():+8.3f}")

print("\nGespeichert:")
for f in ("analyse_gaps_kreise.csv",
          "analyse_gaps_regionen.csv",
          "analyse_rankings.csv"):
    print(" ", PROCESSED / f)