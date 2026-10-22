from pathlib import Path
import pandas as pd


# ============================================================
# 1. PROJEKTPFADE
# ============================================================

# Das Skript liegt in:
# DatenProjekt/DatenProjekt_Report/data/processed/
#
# parents[3] führt zurück zu:
# DatenProjekt/

projekt = Path(__file__).resolve().parents[2]


# Rohdaten
rohdatei = projekt / "RawData" / "Tabelle 20261007.csv"


# Ausgabe
ausgabe = (
    projekt
    / "DatenProjekt_Report"
    / "data"
    / "processed"
    / "inkar_bayern_2023_bereinigt.csv"
)


# ============================================================
# 2. PFAD KONTROLLIEREN
# ============================================================

print("Projektordner:")
print(projekt)

print("\nGesuchte Rohdatei:")
print(rohdatei)

print("\nExistiert die Rohdatei?")
print(rohdatei.exists())


if not rohdatei.exists():
    raise FileNotFoundError(
        f"""
Die Rohdatei wurde nicht gefunden:

{rohdatei}

Bitte überprüfe:
- den Dateinamen
- den Ordner "RawData"
"""
    )


# ============================================================
# 3. CSV EINLESEN
# ============================================================

daten = pd.read_csv(
    rohdatei,
    sep=";",
    encoding="utf-8-sig",
    skiprows=[1],
    dtype={"Kennziffer": "string"},
)


# ============================================================
# 4. AGS BEREINIGEN
# ============================================================

daten["Kennziffer"] = (
    daten["Kennziffer"]
    .str.strip()
    .str.zfill(5)
)


# ============================================================
# 5. ZAHLENSPALTEN BEREINIGEN
# ============================================================

# Diese Spalten bleiben Text
schluessel = {
    "Kennziffer",
    "Raumeinheit",
    "Aggregat",
}


# Alle anderen Spalten sind Wertespalten
wertespalten = [
    spalte
    for spalte in daten.columns
    if spalte not in schluessel
]


# Deutsche Zahlenformate umwandeln
#
# Beispiel:
# 139.536,00
# ↓
# 139536.00

for spalte in wertespalten:

    daten[spalte] = (
        daten[spalte]
        .astype("string")
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    daten[spalte] = pd.to_numeric(
        daten[spalte],
        errors="coerce"
    )


# ============================================================
# 6. QUALITÄTSKONTROLLE
# ============================================================

print("\n" + "=" * 60)
print("QUALITÄTSKONTROLLE")
print("=" * 60)


# Größe
print("\nZeilen und Spalten:")
print(daten.shape)


# Spalten
print("\nSpalten:")
print(daten.columns.tolist())


# Doppelte AGS
print("\nDoppelte AGS:")
print(
    daten["Kennziffer"].duplicated().sum()
)


# Aggregate
print("\nKreise / Aggregate:")
print(
    daten["Aggregat"]
    .value_counts(dropna=False)
    .to_dict()
)


# Fehlende Werte
print("\nFehlende Werte je Spalte:")
print(
    daten.isna().sum().to_string()
)


# ============================================================
# 7. DATEI SPEICHERN
# ============================================================

ausgabe.parent.mkdir(
    parents=True,
    exist_ok=True
)


daten.to_csv(
    ausgabe,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. FERTIG
# ============================================================

print("\n" + "=" * 60)
print("FERTIG")
print("=" * 60)

print("\nBereinigte Datei gespeichert unter:")
print(ausgabe)

print("\nDatei existiert:")
print(ausgabe.exists())