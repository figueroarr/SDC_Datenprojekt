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

METADATA_DIR = REPORT_DIR / "data" / "metadata"

KREISLISTE_FILE = METADATA_DIR / "kreisliste.csv"

OUTPUT_FILE = METADATA_DIR / "stmwi_raumstruktur_2023.csv"


# ============================================================
# 2. Kreisliste laden
# ============================================================

kreise = pd.read_csv(
    KREISLISTE_FILE,
    sep=",",
    dtype={"ags": str},
    encoding="utf-8-sig"
)

kreise["ags"] = (
    kreise["ags"]
    .str.strip()
    .str.zfill(5)
)

print(f"Kreise aus kreisliste.csv: {len(kreise)}")


# ============================================================
# 3. Regierungsbezirke
# ============================================================

regierungsbezirke = {
    "091": "Oberbayern",
    "092": "Niederbayern",
    "093": "Oberpfalz",
    "094": "Oberfranken",
    "095": "Mittelfranken",
    "096": "Unterfranken",
    "097": "Schwaben",
}


# ============================================================
# 4. LEP-Gebietskategorien
#
# Quelle:
# StMWi, Abgrenzung der Gebietskategorien,
# Stand 1. Juni 2023.
#
# LR = Ländlicher Raum
# VR = Verdichtungsraum
#
# Verwendet werden die letzten drei Stellen des AGS.
# ============================================================

lr = [
    # Oberbayern
    "171", "172", "173", "176", "177",
    "180", "181", "182", "183", "185",
    "186", "187", "189", "190",

    # Niederbayern
    "261", "262", "263",
    "271", "272", "273", "274", "275",
    "276", "277", "278", "279",

    # Oberpfalz
    "361", "363",
    "371", "372", "373", "374", "375",
    "376", "377",

    # Oberfranken
    "462", "463", "464",
    "471", "472", "473", "475", "476",
    "477", "478", "479",

    # Mittelfranken
    "561", "571", "575", "576", "577",

    # Unterfranken
    "662", "672", "673", "674", "675",
    "677", "678",

    # Schwaben
    "762", "763", "764", "771", "773",
    "774", "776", "777", "778", "779", "780",
]


vr = [
    # Oberbayern
    "161", "162", "163", "174", "175",
    "178", "179", "184", "188",

    # Oberpfalz
    "362",

    # Oberfranken
    "461", "474",

    # Mittelfranken
    "562", "563", "564", "565",
    "572", "573", "574",

    # Unterfranken
    "661", "663", "671", "676", "679",

    # Schwaben
    "761", "772", "775",
]


# ============================================================
# 5. Raum mit besonderem Handlungsbedarf (RmbH)
#
# Die Markierungen wurden anhand der blauen Flächen
# in der offiziellen StMWi-Tabelle übernommen.
#
# Hinweis: RmbH bezieht sich hier auf die
# LEP-Teilfortschreibung 2018.
# ============================================================

rmbh = [
    # Oberbayern
    "180", "183",

    # Niederbayern
    "262", "272", "275", "276", "277",

    # Oberpfalz
    "361", "363", "371", "372",
    "374", "376", "377",

    # Oberfranken
    "462", "463", "464",
    "471", "472", "473", "475", "476",
    "477", "478", "479",

    # Mittelfranken
    "561", "571", "575", "576", "577",

    # Unterfranken
    "661", "662", "671", "672", "673",
    "674", "675", "676", "677", "678", "679",

    # Schwaben
    "773",
]


# ============================================================
# 6. Zuordnung erstellen
# ============================================================

lr = set(lr)
vr = set(vr)
rmbh = set(rmbh)

# Prüfen, ob die Gebietskategorien sich überschneiden.
if lr & vr:
    raise ValueError(
        f"AGS stehen gleichzeitig in LR und VR: {lr & vr}"
    )

# Alle Kreise aus der offiziellen Zuordnung.
bekannte_ags = lr | vr

# AGS aus der Kreisliste ableiten.
kreise["kreiscode"] = kreise["ags"].str[-3:]

# Prüfen, ob alle Kreise einer Kategorie zugeordnet sind.
nicht_zugeordnet = kreise[
    ~kreise["kreiscode"].isin(bekannte_ags)
]

if not nicht_zugeordnet.empty:
    print("\nWARNUNG: Diese Kreise haben noch keine LEP-Zuordnung:")
    print(
        nicht_zugeordnet[["ags", "kreisname"]]
        .to_string(index=False)
    )

    raise ValueError(
        "Nicht alle Kreise konnten einer LEP-Kategorie zugeordnet werden."
    )


# Regierungsbezirk ergänzen.
kreise["regierungsbezirk"] = (
    kreise["ags"].str[:3].map(regierungsbezirke)
)

if kreise["regierungsbezirk"].isna().any():
    raise ValueError(
        "Mindestens ein Regierungsbezirk konnte nicht zugeordnet werden."
    )


# LEP-Kategorie ergänzen.
kreise["lep_gebietskategorie"] = kreise["kreiscode"].apply(
    lambda code: "LR" if code in lr else "VR"
)

# RmbH ergänzen.
kreise["rmbh"] = kreise["kreiscode"].apply(
    lambda code: "Ja" if code in rmbh else "Nein"
)


# ============================================================
# 7. Ergebnis zusammenstellen
# ============================================================

stmwi = kreise[
    [
        "ags",
        "kreisname",
        "regierungsbezirk",
        "lep_gebietskategorie",
        "rmbh",
    ]
].copy()

stmwi = stmwi.rename(
    columns={
        "kreisname": "kreisname_stmwi"
    }
)


# ============================================================
# 8. Qualitätskontrolle
# ============================================================

print("\nLEP-Gebietskategorien:")
print(
    stmwi["lep_gebietskategorie"]
    .value_counts()
    .to_string()
)

print("\nRmbH-Verteilung:")
print(
    stmwi["rmbh"]
    .value_counts()
    .to_string()
)

print("\nVerteilung nach Regierungsbezirk:")
print(
    stmwi["regierungsbezirk"]
    .value_counts()
    .to_string()
)

print(f"\nAnzahl Zeilen: {len(stmwi)}")
print(f"Anzahl eindeutiger AGS: {stmwi['ags'].nunique()}")

if stmwi["ags"].duplicated().any():
    raise ValueError("Die Datei enthält doppelte AGS.")

if len(stmwi) != len(kreise):
    raise ValueError(
        f"Erwartet wurden {len(kreise)} Kreise, "
        f"gefunden wurden {len(stmwi)}."
    )


# ============================================================
# 9. CSV speichern
# ============================================================

stmwi.to_csv(
    OUTPUT_FILE,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\nStMWi-Raumstruktur erfolgreich gespeichert:")
print(OUTPUT_FILE)