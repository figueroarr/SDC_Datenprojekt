import sys
import pandas as pd

from config import PROCESSED_DIR, METADATA_DIR


# ============================================================
# 1. Pfade
# ============================================================

MASTER_FILE = (
    PROCESSED_DIR
    / "inkar_bayern_2023_master.csv"
)

KREISLISTE_FILE = (
    METADATA_DIR
    / "kreisliste.csv"
)

STMWI_FILE = (
    METADATA_DIR
    / "stmwi_raumstruktur_2023.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "inkar_bayern_2023_master_validiert.csv"
)


# Erwartete Anzahl bayerischer Kreise
ERWARTET_KREISE = 96

# Bayern:
# 25 kreisfreie Städte
# 71 Landkreise
ERWARTET_KREISFREI = 25
ERWARTET_LANDKREISE = 71


# Fehler:
# Wenn vorhanden, wird keine validierte Datei geschrieben.
fehler = []

# Warnungen:
# Die Validierung kann trotzdem erfolgreich sein.
warnungen = []


# ============================================================
# 2. Hilfsfunktion
# ============================================================

def pruefe(bedingung, erfolg, fehlertext):
    """
    Gibt das Ergebnis einer Prüfung aus und
    speichert Fehler für den späteren Abbruch.
    """

    if bedingung:
        print(f"  OK       {erfolg}")
    else:
        print(f"  FEHLER   {fehlertext}")
        fehler.append(fehlertext)


# ============================================================
# 3. Dateien laden
# ============================================================

print("=" * 60)
print("DATEIEN LADEN")
print("=" * 60)


# ------------------------------------------------------------
# Prüfen, ob Dateien existieren
# ------------------------------------------------------------

dateien = [
    MASTER_FILE,
    KREISLISTE_FILE,
    STMWI_FILE,
]

for datei in dateien:

    if not datei.exists():

        raise FileNotFoundError(
            f"Datei nicht gefunden: {datei}"
        )


# ------------------------------------------------------------
# Master laden
# ------------------------------------------------------------

master = pd.read_csv(
    MASTER_FILE,
    sep=";",
    dtype={"Kennziffer": str},
    encoding="utf-8-sig",
)


master["Kennziffer"] = (
    master["Kennziffer"]
    .astype(str)
    .str.strip()
    .str.zfill(5)
)


# ------------------------------------------------------------
# Kreisliste laden
# ------------------------------------------------------------

kreise = pd.read_csv(
    KREISLISTE_FILE,
    sep=",",
    dtype={"ags": str},
    encoding="utf-8-sig",
)


kreise["ags"] = (
    kreise["ags"]
    .astype(str)
    .str.strip()
    .str.zfill(5)
)


# ------------------------------------------------------------
# StMWi-Raumstruktur laden
# ------------------------------------------------------------

stmwi = pd.read_csv(
    STMWI_FILE,
    sep=";",
    dtype={"ags": str},
    encoding="utf-8-sig",
)


stmwi["ags"] = (
    stmwi["ags"]
    .astype(str)
    .str.strip()
    .str.zfill(5)
)


# ------------------------------------------------------------
# Übersicht
# ------------------------------------------------------------

print(
    f"Master:     {len(master)} Zeilen, "
    f"{len(master.columns)} Spalten"
)

print(
    f"Kreisliste: {len(kreise)} Zeilen"
)

print(
    f"StMWi:      {len(stmwi)} Zeilen"
)


# ============================================================
# 4. Prüfungen
# ============================================================

print("\n" + "=" * 60)
print("PRÜFUNGEN")
print("=" * 60)


# ============================================================
# 4.1 Master: Zeilenzahl und AGS
# ============================================================

print("\n[1] Zeilenzahl und AGS")


# ------------------------------------------------------------
# 96 Kreise?
# ------------------------------------------------------------

pruefe(
    len(master) == ERWARTET_KREISE,
    f"{ERWARTET_KREISE} Kreise vorhanden",
    (
        f"Erwartet {ERWARTET_KREISE} Kreise, "
        f"gefunden {len(master)}"
    ),
)


# ------------------------------------------------------------
# Doppelte AGS?
# ------------------------------------------------------------

doppelte_ags = (
    master["Kennziffer"]
    .duplicated()
)


pruefe(
    not doppelte_ags.any(),
    "Keine doppelten AGS im Master",
    "Doppelte AGS im Master gefunden",
)


if doppelte_ags.any():

    print(
        master.loc[
            doppelte_ags,
            ["Kennziffer", "kreisname"]
        ].to_string(index=False)
    )


# ------------------------------------------------------------
# Alle AGS aus Bayern?
# ------------------------------------------------------------

nicht_bayern = master[
    ~master["Kennziffer"]
    .str.startswith("09")
]


pruefe(
    nicht_bayern.empty,
    "Alle AGS beginnen mit 09",
    (
        "AGS außerhalb Bayerns: "
        f"{nicht_bayern['Kennziffer'].tolist()}"
    ),
)


# ============================================================
# 4.2 AGS-Abgleich Master ↔ Kreisliste
# ============================================================

print("\n[2] AGS-Abgleich Master ↔ Kreisliste")


ags_master = set(
    master["Kennziffer"]
)

ags_kreisliste = set(
    kreise["ags"]
)


# AGS im Master, aber nicht in Kreisliste
ags_unbekannt = sorted(
    ags_master - ags_kreisliste
)


# AGS in Kreisliste, aber nicht im Master
ags_fehlend = sorted(
    ags_kreisliste - ags_master
)


pruefe(
    len(ags_unbekannt) == 0,
    "Keine unbekannten AGS",
    (
        "AGS im Master, aber nicht in der "
        f"Kreisliste: {ags_unbekannt}"
    ),
)


pruefe(
    len(ags_fehlend) == 0,
    "Alle Kreise aus der Kreisliste sind im Master",
    (
        "AGS aus der Kreisliste fehlen im Master: "
        f"{ags_fehlend}"
    ),
)


# ============================================================
# 4.3 Kreistyp
# ============================================================

print("\n[3] Kreistyp")


# ------------------------------------------------------------
# Kreistyp aus AGS ableiten
#
# 4. Stelle des AGS:
# 6 = kreisfreie Stadt
# sonst = Landkreis
# ------------------------------------------------------------

kreistyp_abgeleitet = (
    master["Kennziffer"]
    .str[3]
    .map(
        lambda wert:
        "Kreisfreie Stadt"
        if wert == "6"
        else "Landkreis"
    )
)


# ------------------------------------------------------------
# Verteilung prüfen
# ------------------------------------------------------------

anzahl_kreisfrei = (
    kreistyp_abgeleitet
    .eq("Kreisfreie Stadt")
    .sum()
)

anzahl_landkreise = (
    kreistyp_abgeleitet
    .eq("Landkreis")
    .sum()
)


pruefe(
    (
        anzahl_kreisfrei
        == ERWARTET_KREISFREI
        and
        anzahl_landkreise
        == ERWARTET_LANDKREISE
    ),
    (
        f"{ERWARTET_KREISFREI} kreisfreie Städte, "
        f"{ERWARTET_LANDKREISE} Landkreise"
    ),
    (
        "Kreistyp-Verteilung weicht ab: "
        f"{anzahl_kreisfrei} kreisfreie Städte, "
        f"{anzahl_landkreise} Landkreise"
    ),
)


# ------------------------------------------------------------
# Kreistyp Master ↔ Kreisliste
# ------------------------------------------------------------

typ_check = master[
    [
        "Kennziffer",
        "kreistyp"
    ]
].merge(
    kreise[
        [
            "ags",
            "kreistyp"
        ]
    ],
    left_on="Kennziffer",
    right_on="ags",
    how="inner",
    suffixes=(
        "_master",
        "_kreisliste"
    ),
)


abweichend_typ = typ_check[
    typ_check["kreistyp_master"]
    !=
    typ_check["kreistyp_kreisliste"]
]


if abweichend_typ.empty:

    print(
        "  OK       Kreistyp im Master stimmt "
        "mit der Kreisliste überein"
    )

else:

    print(
        "  FEHLER   Kreistyp weicht ab bei:"
    )

    print(
        abweichend_typ[
            [
                "Kennziffer",
                "kreistyp_master",
                "kreistyp_kreisliste"
            ]
        ].to_string(index=False)
    )

    fehler.append(
        "Kreistyp im Master stimmt nicht "
        "mit der Kreisliste überein"
    )


# ============================================================
# 4.4 Kreisnamen
# ============================================================

print(
    "\n[4] Kreisnamen "
    "(Hinweis, kein Abbruch)"
)


def normalisiere_name(name):
    """
    Vereinfachte Vergleichsform für Kreisnamen.
    """

    name = str(name).lower()

    for zeichen in (
        ".",
        " ",
        "-",
        "(",
        ")",
    ):
        name = name.replace(
            zeichen,
            ""
        )

    return name


name_check = master[
    [
        "Kennziffer",
        "kreisname"
    ]
].merge(
    kreise[
        [
            "ags",
            "kreisname"
        ]
    ],
    left_on="Kennziffer",
    right_on="ags",
    how="inner",
    suffixes=(
        "_master",
        "_kreisliste"
    ),
)


name_check[
    "name_master_normalisiert"
] = (
    name_check[
        "kreisname_master"
    ]
    .map(normalisiere_name)
)


name_check[
    "name_kreisliste_normalisiert"
] = (
    name_check[
        "kreisname_kreisliste"
    ]
    .map(normalisiere_name)
)


abweichende_namen = name_check[
    name_check[
        "name_master_normalisiert"
    ]
    !=
    name_check[
        "name_kreisliste_normalisiert"
    ]
]


if abweichende_namen.empty:

    print(
        "  OK       Alle Kreisnamen stimmen "
        "mit der Kreisliste überein"
    )

else:

    print(
        f"  HINWEIS  {len(abweichende_namen)} "
        "Kreisnamen weichen ab:"
    )

    print(
        abweichende_namen[
            [
                "Kennziffer",
                "kreisname_master",
                "kreisname_kreisliste"
            ]
        ].to_string(index=False)
    )

    warnungen.append(
        f"{len(abweichende_namen)} "
        "abweichende Kreisnamen"
    )


# ============================================================
# 4.5 Regierungsbezirk
# ============================================================

print(
    "\n[5] Regierungsbezirk "
    "(Master ↔ StMWi)"
)


regierungsbezirk_check = master[
    [
        "Kennziffer",
        "regierungsbezirk"
    ]
].merge(
    stmwi[
        [
            "ags",
            "regierungsbezirk"
        ]
    ],
    left_on="Kennziffer",
    right_on="ags",
    how="inner",
    suffixes=(
        "_master",
        "_stmwi"
    ),
)


abweichend_rb = (
    regierungsbezirk_check[
        "regierungsbezirk_master"
    ]
    !=
    regierungsbezirk_check[
        "regierungsbezirk_stmwi"
    ]
)


abweichungen_rb = (
    regierungsbezirk_check[
        abweichend_rb
    ]
)


pruefe(
    abweichungen_rb.empty,
    (
        "Regierungsbezirke stimmen mit "
        "der StMWi-Raumstruktur überein"
    ),
    (
        "Regierungsbezirk weicht ab bei: "
        f"{abweichungen_rb['Kennziffer'].tolist()}"
    ),
)


# ============================================================
# 4.6 LEP-Gebietskategorie
#     Master ↔ StMWi
# ============================================================

print(
    "\n[6] LEP-Gebietskategorie"
)


# ------------------------------------------------------------
# Gültige Werte
# ------------------------------------------------------------

ungueltige_lep = master[
    ~master[
        "lep_gebietskategorie"
    ].isin(
        ["LR", "VR"]
    )
]


pruefe(
    ungueltige_lep.empty,
    "LEP enthält nur LR und VR",
    (
        "LEP enthält fehlende oder "
        "unerwartete Werte"
    ),
)


# ------------------------------------------------------------
# Master ↔ StMWi
# ------------------------------------------------------------

lep_check = master[
    [
        "Kennziffer",
        "lep_gebietskategorie"
    ]
].merge(
    stmwi[
        [
            "ags",
            "lep_gebietskategorie"
        ]
    ],
    left_on="Kennziffer",
    right_on="ags",
    how="inner",
    suffixes=(
        "_master",
        "_stmwi"
    ),
)


abweichend_lep = (
    lep_check[
        "lep_gebietskategorie_master"
    ]
    !=
    lep_check[
        "lep_gebietskategorie_stmwi"
    ]
)


abweichungen_lep = (
    lep_check[
        abweichend_lep
    ]
)


pruefe(
    abweichungen_lep.empty,
    (
        "LEP-Zuordnungen stimmen mit "
        "StMWi überein"
    ),
    (
        "LEP weicht ab bei: "
        f"{abweichungen_lep['Kennziffer'].tolist()}"
    ),
)


# ------------------------------------------------------------
# LEP-Verteilung
# ------------------------------------------------------------

print(
    "\n  LEP-Verteilung:"
)

print(
    master[
        "lep_gebietskategorie"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# 4.7 RmbH
#     Master ↔ StMWi
# ============================================================

print(
    "\n[7] RmbH"
)


# ------------------------------------------------------------
# Gültige Werte
# ------------------------------------------------------------

ungueltige_rmbh = master[
    ~master[
        "rmbh"
    ].isin(
        ["Ja", "Nein"]
    )
]


pruefe(
    ungueltige_rmbh.empty,
    "RmbH enthält nur Ja und Nein",
    (
        "RmbH enthält fehlende oder "
        "unerwartete Werte"
    ),
)


# ------------------------------------------------------------
# Master ↔ StMWi
# ------------------------------------------------------------

rmbh_check = master[
    [
        "Kennziffer",
        "rmbh"
    ]
].merge(
    stmwi[
        [
            "ags",
            "rmbh"
        ]
    ],
    left_on="Kennziffer",
    right_on="ags",
    how="inner",
    suffixes=(
        "_master",
        "_stmwi"
    ),
)


abweichend_rmbh = (
    rmbh_check[
        "rmbh_master"
    ]
    !=
    rmbh_check[
        "rmbh_stmwi"
    ]
)


abweichungen_rmbh = (
    rmbh_check[
        abweichend_rmbh
    ]
)


pruefe(
    abweichungen_rmbh.empty,
    (
        "RmbH-Zuordnungen stimmen mit "
        "StMWi überein"
    ),
    (
        "RmbH weicht ab bei: "
        f"{abweichungen_rmbh['Kennziffer'].tolist()}"
    ),
)


# ------------------------------------------------------------
# RmbH-Verteilung
# ------------------------------------------------------------

print(
    "\n  RmbH-Verteilung:"
)

print(
    master[
        "rmbh"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# 4.8 Fehlende wichtige Metadaten
# ============================================================

print(
    "\n[8] Fehlende wichtige Metadaten"
)


wichtige_metadaten = [
    "Kennziffer",
    "kreisname",
    "kreistyp",
    "regierungsbezirk",
    "lep_gebietskategorie",
    "rmbh",
]


fehlende_metadaten = (
    master[
        wichtige_metadaten
    ]
    .isna()
    .sum()
)


fehlende_metadaten = (
    fehlende_metadaten[
        fehlende_metadaten > 0
    ]
)


pruefe(
    fehlende_metadaten.empty,
    (
        "Keine fehlenden Werte in "
        "wichtigen Metadaten"
    ),
    (
        "Fehlende Metadaten: "
        f"{fehlende_metadaten.to_dict()}"
    ),
)


# ============================================================
# 4.9 Fehlende Werte in Indikatoren
# ============================================================

print(
    "\n[9] Fehlende Werte in Indikatorspalten"
)


# Diese Spalten sind Metadaten und
# keine Indikatoren.
meta_spalten = {
    "Kennziffer",
    "Raumeinheit",
    "Aggregat",
    "kreisname",
    "kreistyp",
    "regierungsbezirk",
    "lep_gebietskategorie",
    "rmbh",
}


indikatoren = [
    spalte
    for spalte in master.columns
    if spalte not in meta_spalten
]


fehlende_indikatoren = (
    master[
        indikatoren
    ]
    .isna()
    .sum()
)


fehlende_indikatoren = (
    fehlende_indikatoren[
        fehlende_indikatoren > 0
    ]
)


if fehlende_indikatoren.empty:

    print(
        "  OK       Keine fehlenden Werte "
        "in den Indikatorspalten"
    )

else:

    print(
        f"  HINWEIS  {len(fehlende_indikatoren)} "
        "Indikatorspalten enthalten fehlende Werte:"
    )

    print(
        fehlende_indikatoren
        .sort_values(
            ascending=False
        )
        .to_string()
    )

    warnungen.append(
        f"{len(fehlende_indikatoren)} "
        "Indikatorspalten mit fehlenden Werten"
    )


# ============================================================
# 5. Ergebnis
# ============================================================

print(
    "\n" + "=" * 60
)

print(
    "ERGEBNIS DER VALIDIERUNG"
)

print(
    "=" * 60
)


# ------------------------------------------------------------
# Fehler vorhanden?
# ------------------------------------------------------------

if fehler:

    print(
        f"\nABBRUCH: {len(fehler)} Fehler."
    )

    print(
        "Es wurde KEINE validierte Datei geschrieben."
    )

    print(
        "\nFehler:"
    )

    for fehlertext in fehler:

        print(
            f"  - {fehlertext}"
        )

    sys.exit(1)


# ============================================================
# 6. Validierten Master speichern
# ============================================================

# Metadaten nach vorne
vorne = [
    "Kennziffer",
    "kreisname",
    "kreistyp",
    "regierungsbezirk",
    "lep_gebietskategorie",
    "rmbh",
]


vorne = [
    spalte
    for spalte in vorne
    if spalte in master.columns
]


rest = [
    spalte
    for spalte in master.columns
    if spalte not in vorne
]


master_validiert = master[
    vorne + rest
].copy()


# Nach AGS sortieren
master_validiert = (
    master_validiert
    .sort_values(
        "Kennziffer"
    )
    .reset_index(drop=True)
)


# ------------------------------------------------------------
# Speichern
# ------------------------------------------------------------

master_validiert.to_csv(
    OUTPUT_FILE,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 7. Abschluss
# ============================================================

print(
    "\nVALIDIERUNG BESTANDEN"
)


if warnungen:

    print(
        f"\nHinweise zur manuellen Prüfung "
        f"({len(warnungen)}):"
    )

    for warnung in warnungen:

        print(
            f"  - {warnung}"
        )

else:

    print(
        "\nKeine Warnungen."
    )


print(
    "\nValidierter Master gespeichert unter:"
)

print(
    OUTPUT_FILE
)