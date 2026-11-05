"""
08_analysiere_datenluecken.py

Quantifiziert, welche Dimensionen in der INKAR-Datenbasis
geschlechterdifferenziert vorliegen und welche fehlen.

Ausgabe: data/processed/analyse_datenluecken.csv
"""
from pathlib import Path
import pandas as pd

PROJEKT   = Path(__file__).resolve().parents[2]
REPORT    = PROJEKT / "DatenProjekt_Report"
PROCESSED = REPORT / "data" / "processed"
METADATA  = REPORT / "data" / "metadata"

KATALOG = METADATA / "indikatorenliste_final.csv"

katalog = pd.read_csv(KATALOG, sep=";", dtype=str).fillna("")

# Geschlechterbezug kategorisieren
def geschlechterkategorie(row):
    bezug = row["geschlechtsbezug"]
    if bezug in ("Frauen", "Männer"):
        return "geschlechterdifferenziert"
    if bezug == "Geschlechterverhältnis":
        return "geschlechterdifferenziert"
    return "nur gesamt"

katalog["geschlechterkategorie"] = katalog.apply(geschlechterkategorie, axis=1)

# Aggregation pro Dimension
tabelle = (
    katalog
    .groupby(["dimension", "geschlechterkategorie"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

# Spalten sicherstellen
for col in ["geschlechterdifferenziert", "nur gesamt"]:
    if col not in tabelle.columns:
        tabelle[col] = 0

tabelle["gesamt"] = tabelle["geschlechterdifferenziert"] + tabelle["nur gesamt"]
tabelle = tabelle.sort_values("gesamt", ascending=False)

# Fehlende Dimensionen explizit ergänzen
FEHLENDE_DIMENSIONEN = [
    "Einkommen / Gender Pay Gap",
    "Erwerbsbeteiligung / Beschäftigung",
    "Care-Arbeit / Pflege",
    "Mental Load",
    "Ehrenamt",
    "Alltagsmobilität / Wegezeiten",
]

fehlend = pd.DataFrame({
    "dimension": FEHLENDE_DIMENSIONEN,
    "geschlechterdifferenziert": 0,
    "nur gesamt": 0,
    "gesamt": 0,
})

tabelle = pd.concat([tabelle, fehlend], ignore_index=True)

tabelle.to_csv(PROCESSED / "analyse_datenluecken.csv", sep=";",
               index=False, encoding="utf-8-sig")

# Zusammenfassung
print("=" * 60)
print("DATENLÜCKEN-ANALYSE")
print("=" * 60)
print(f"\nIndikatoren gesamt: {len(katalog)}")
print(f"  geschlechterdifferenziert: {(katalog['geschlechterkategorie'] == 'geschlechterdifferenziert').sum()}")
print(f"  nur gesamt:                {(katalog['geschlechterkategorie'] == 'nur gesamt').sum()}")
print(f"\nDimensionen in den Daten: {katalog['dimension'].nunique()}")
print(f"Dimensionen explizit NICHT in den Daten: {len(FEHLENDE_DIMENSIONEN)}")
print("\nVerteilung pro Dimension:")
print(tabelle.to_string(index=False))
print(f"\nGespeichert: {PROCESSED / 'analyse_datenluecken.csv'}")