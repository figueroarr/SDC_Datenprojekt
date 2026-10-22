from pathlib import Path
import pandas as pd


# ============================================================
# 1. Pfade
# ============================================================

# Das Skript liegt in:
# DatenProjekt/DatenProjekt_Report/scripts/
#
# parents[2] führt zurück zu:
# DatenProjekt/

projekt = Path(__file__).resolve().parents[2]

REPORT_DIR = projekt / "DatenProjekt_Report"

PROCESSED_DIR = REPORT_DIR / "data" / "processed"
METADATA_DIR = REPORT_DIR / "data" / "metadata"


INKAR_FILE = PROCESSED_DIR / "inkar_bayern_2023_bereinigt.csv"
KREISLISTE_FILE = METADATA_DIR / "kreisliste.csv"
STMWI_FILE = METADATA_DIR / "stmwi_raumstruktur_2023.csv"

OUTPUT_FILE = PROCESSED_DIR / "inkar_bayern_2023_master.csv"

# ============================================================
# 2. INKAR-Daten laden
# ============================================================

inkar = pd.read_csv(
    INKAR_FILE,
    sep=",",
    dtype={"Kennziffer": str},
    encoding="utf-8-sig"
)

inkar["Kennziffer"] = (
    inkar["Kennziffer"]
    .astype(str)
    .str.strip()
    .str.zfill(5)
)

print(f"INKAR-Zeilen: {len(inkar)}")


# ============================================================
# 3. Kreisliste laden
# ============================================================

kreise = pd.read_csv(
    KREISLISTE_FILE,
    sep=",",
    dtype={"ags": str},
    encoding="utf-8-sig"
)

kreise["ags"] = (
    kreise["ags"]
    .astype(str)
    .str.strip()
    .str.zfill(5)
)

# AGS für den Merge gleich benennen
kreise = kreise.rename(
    columns={"ags": "Kennziffer"}
)


# ============================================================
# 4. StMWi-Raumstruktur laden
# ============================================================

stmwi = pd.read_csv(
    STMWI_FILE,
    sep=";",
    dtype={"ags": str},
    encoding="utf-8-sig"
)

stmwi["ags"] = (
    stmwi["ags"]
    .astype(str)
    .str.strip()
    .str.zfill(5)
)

# AGS für den Merge gleich benennen
stmwi = stmwi.rename(
    columns={"ags": "Kennziffer"}
)


print(f"Kreise aus Metadaten: {len(kreise)}")
print(f"StMWi-Zeilen: {len(stmwi)}")


# ============================================================
# 5. Prüfen: AGS eindeutig?
# ============================================================

if inkar["Kennziffer"].duplicated().any():
    raise ValueError(
        "INKAR enthält doppelte Kennziffern."
    )

if kreise["Kennziffer"].duplicated().any():
    raise ValueError(
        "kreisliste.csv enthält doppelte AGS."
    )

if stmwi["Kennziffer"].duplicated().any():
    raise ValueError(
        "stmwi_raumstruktur_2023.csv enthält doppelte AGS."
    )


# ============================================================
# 6. INKAR + Kreisliste
# ============================================================

master = inkar.merge(
    kreise[
        [
            "Kennziffer",
            "kreisname",
            "aggregat",
            "kreistyp",
            "strukturwandelregion",
            "im_untersuchungsgebiet",
        ]
    ],
    on="Kennziffer",
    how="left",
    validate="one_to_one"
)


# ============================================================
# 7. StMWi-Raumstruktur hinzufügen
# ============================================================

master = master.merge(
    stmwi[
        [
            "Kennziffer",
            "kreisname_stmwi",
            "regierungsbezirk",
            "lep_gebietskategorie",
            "rmbh",
        ]
    ],
    on="Kennziffer",
    how="left",
    suffixes=("", "_stmwi"),
    validate="one_to_one"
)

# ============================================================
# 8. Master-Datensatz aufräumen
# ============================================================

master = master.drop(
    columns=[
        "aggregat",
        "kreisname_stmwi",
        "strukturwandelregion",
        "im_untersuchungsgebiet"
    ]
)

# ============================================================
# 9. Qualitätskontrolle
# ============================================================

print("\nMaster-Datensatz:")
print(f"Zeilen: {len(master)}")
print(f"Spalten: {len(master.columns)}")

print("\nDoppelte Kennziffern:")
print(
    master[master["Kennziffer"].duplicated(keep=False)]
    [["Kennziffer", "kreisname"]]
)


# Fehlende Kreisnamen
fehlende_kreise = master[
    master["kreisname"].isna()
]

print(
    f"\nFehlende Kreisnamen: {len(fehlende_kreise)}"
)


# Fehlende StMWi-Zuordnungen
fehlende_stmwi = master[
    master["lep_gebietskategorie"].isna()
]

print(
    f"Fehlende StMWi-Zuordnungen: {len(fehlende_stmwi)}"
)

if len(fehlende_stmwi) > 0:
    print(
        fehlende_stmwi[
            ["Kennziffer", "kreisname"]
        ].to_string(index=False)
    )


# ============================================================
# 10. Verteilungen kontrollieren
# ============================================================

print("\nLEP-Gebietskategorien:")
print(
    master["lep_gebietskategorie"]
    .value_counts(dropna=False)
)


print("\nRmbH:")
print(
    master["rmbh"]
    .value_counts(dropna=False)
)


print("\nRegierungsbezirke:")
print(
    master["regierungsbezirk"]
    .value_counts(dropna=False)
)


# ============================================================
# 11. Master speichern
# ============================================================

master.to_csv(
    OUTPUT_FILE,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\nMaster-Datei erfolgreich erstellt:")
print(OUTPUT_FILE)