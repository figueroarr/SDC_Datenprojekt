from pathlib import Path
import pandas as pd


# ============================================================
# 1. PFADE
# ============================================================

# Hauptordner DatenProjekt
projekt = Path(__file__).resolve().parents[2]

# Bereinigte INKAR-Datei
inkar_datei = (
    projekt
    / "DatenProjekt_Report"
    / "data"
    / "processed"
    / "inkar_bayern_2023_bereinigt.csv"
)

# Ordner für Metadaten
metadata_ordner = (
    projekt
    / "DatenProjekt_Report"
    / "data"
    / "metadata"
)

# Ausgabedateien
indikatoren_datei = metadata_ordner / "indikatorenliste.csv"
kreise_datei = metadata_ordner / "kreisliste.csv"


# ============================================================
# 2. DATEI PRÜFEN
# ============================================================

if not inkar_datei.exists():
    raise FileNotFoundError(
        f"""
Die bereinigte INKAR-Datei wurde nicht gefunden:

{inkar_datei}

Führe zuerst 01_bereinige_inkar.py aus.
"""
    )


# ============================================================
# 3. INKAR-DATEN EINLESEN
# ============================================================

daten = pd.read_csv(
    inkar_datei,
    dtype={"Kennziffer": "string"},
)

daten["Kennziffer"] = (
    daten["Kennziffer"]
    .str.strip()
    .str.zfill(5)
)


# ============================================================
# 4. INDIKATORENLISTE ERSTELLEN
# ============================================================

# Diese Spalten sind keine Indikatoren.
schluesselspalten = {
    "Kennziffer",
    "Raumeinheit",
    "Aggregat",
}

indikatoren = [
    spalte
    for spalte in daten.columns
    if spalte not in schluesselspalten
]


# ------------------------------------------------------------
# Dimensionen definieren
# ------------------------------------------------------------

def bestimme_dimension(indikator):

    indikator_klein = indikator.lower()

    if (
        "schulabgänger" in indikator_klein
        or "auszubildende" in indikator_klein
    ):
        return "Bildung und Ausbildung"

    elif (
        "wanderung" in indikator_klein
        or "zuzug" in indikator_klein
        or "fortzug" in indikator_klein
    ):
        return "Wanderung und Mobilität"

    elif (
        "frauenanteil" in indikator_klein
        or "bevölkerung weiblich" in indikator_klein
        or "bevölkerung männlich" in indikator_klein
    ):
        return "Geschlechterstruktur"

    elif (
        "bevölkerung" in indikator_klein
        or "einwohner von" in indikator_klein
    ):
        return "Bevölkerung und Demografie"

    elif (
        "ländlichkeit" in indikator_klein
        or "einwohnerdichte" in indikator_klein
        or "mittelzentren" in indikator_klein
        or "oberzentren" in indikator_klein
        or "bodenfläche" in indikator_klein
        or "arbeitsplatz-dichte" in indikator_klein
    ):
        return "Raumstruktur"

    else:
        return "Sonstige"


# ------------------------------------------------------------
# Bezug zur Hypothese
# ------------------------------------------------------------

def bestimme_bezug(indikator):

    indikator_klein = indikator.lower()

    if (
        "frauen" in indikator_klein
        or "weiblich" in indikator_klein
        or "männlich" in indikator_klein
    ):
        return (
            "Ermöglicht die Untersuchung geschlechtsspezifischer "
            "Unterschiede und ist damit unmittelbar für die "
            "Gender-Perspektive des Projekts relevant."
        )

    elif (
        "wanderung" in indikator_klein
        or "zuzug" in indikator_klein
        or "fortzug" in indikator_klein
    ):
        return (
            "Zeigt Wanderungsbewegungen und ermöglicht die Analyse, "
            "ob bestimmte Regionen Bevölkerung beziehungsweise "
            "bestimmte Bevölkerungsgruppen verlieren oder gewinnen."
        )

    elif (
        "schulabgänger" in indikator_klein
        or "auszubildende" in indikator_klein
    ):
        return (
            "Bildungs- und Ausbildungsstrukturen können regionale "
            "Zukunftschancen sowie Unterschiede zwischen Frauen "
            "und Männern sichtbar machen."
        )

    elif (
        "bevölkerung" in indikator_klein
        or "einwohner von" in indikator_klein
    ):
        return (
            "Beschreibt die demografische Struktur der Region und "
            "dient als Grundlage zur Einordnung regionaler "
            "Unterschiede."
        )

    elif (
        "ländlichkeit" in indikator_klein
        or "einwohnerdichte" in indikator_klein
        or "mittelzentren" in indikator_klein
        or "oberzentren" in indikator_klein
        or "arbeitsplatz-dichte" in indikator_klein
    ):
        return (
            "Beschreibt die räumliche Struktur und ermöglicht den "
            "Vergleich zwischen ländlich und stärker urban "
            "geprägten Regionen."
        )

    elif "bodenfläche" in indikator_klein:

        return (
            "Dient vor allem als strukturelle Kontextvariable und "
            "zur räumlichen Einordnung der untersuchten Kreise."
        )

    else:

        return (
            "Der konkrete Bezug zur Hypothese muss im weiteren "
            "Projektverlauf geprüft werden."
        )


# ------------------------------------------------------------
# Tabelle erzeugen
# ------------------------------------------------------------

indikatorenliste = pd.DataFrame({
    "indikator": indikatoren
})

indikatorenliste["dimension"] = (
    indikatorenliste["indikator"]
    .apply(bestimme_dimension)
)

indikatorenliste["einheit"] = ""

indikatorenliste["im_dashboard"] = ""

indikatorenliste["begruendung_bezug_hypothese"] = (
    indikatorenliste["indikator"]
    .apply(bestimme_bezug)
)

indikatorenliste["quelle"] = "INKAR"

indikatorenliste["jahr"] = 2023


# Spalten sinnvoll sortieren
indikatorenliste = indikatorenliste[
    [
        "dimension",
        "indikator",
        "einheit",
        "jahr",
        "quelle",
        "im_dashboard",
        "begruendung_bezug_hypothese",
    ]
]


# ============================================================
# 5. KREISLISTE ERSTELLEN
# ============================================================

kreisliste = daten[
    [
        "Kennziffer",
        "Raumeinheit",
        "Aggregat",
    ]
].copy()


# Verständlichere Namen
kreisliste = kreisliste.rename(
    columns={
        "Kennziffer": "ags",
        "Raumeinheit": "kreisname",
        "Aggregat": "aggregat",
    }
)


# ------------------------------------------------------------
# Kreistyp bestimmen
# ------------------------------------------------------------

# 4. Stelle der AGS:
# 6 = kreisfreie Stadt
# sonst = Landkreis

kreisliste["kreistyp"] = (
    kreisliste["ags"]
    .astype(str)
    .str.zfill(5)
    .str[3]
    .map(
        lambda x:
        "Kreisfreie Stadt"
        if x == "6"
        else "Landkreis"
    )
)

# ------------------------------------------------------------
# Regierungsbezirk
# ------------------------------------------------------------

# Wird später über eine Referenztabelle ergänzt.
kreisliste["regierungsbezirk"] = ""


# ------------------------------------------------------------
# Strukturwandelregion
# ------------------------------------------------------------

kreisliste["strukturwandelregion"] = ""


# ------------------------------------------------------------
# Untersuchungsgebiet
# ------------------------------------------------------------

# Ja / Nein wird später anhand der finalen Auswahl gesetzt.

kreisliste["im_untersuchungsgebiet"] = ""


# ------------------------------------------------------------
# Sortieren
# ------------------------------------------------------------

kreisliste = kreisliste.sort_values(
    by="ags"
).reset_index(drop=True)


# ============================================================
# 6. AUSGABEORDNER ERSTELLEN
# ============================================================

metadata_ordner.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# 7. DATEIEN SPEICHERN
# ============================================================

indikatorenliste.to_csv(
    indikatoren_datei,
    index=False,
    encoding="utf-8-sig",
)

kreisliste.to_csv(
    kreise_datei,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 8. QUALITÄTSKONTROLLE
# ============================================================

print("=" * 60)
print("METADATEN ERSTELLT")
print("=" * 60)


print("\nINDIKATORENLISTE")
print("-" * 60)

print("Anzahl Indikatoren:")
print(len(indikatorenliste))

print("\nDimensionen:")
print(
    indikatorenliste["dimension"]
    .value_counts()
    .to_string()
)


print("\n\nKREISLISTE")
print("-" * 60)

print("Anzahl Kreise:")
print(len(kreisliste))

print("\nDoppelte AGS:")
print(
    kreisliste["ags"]
    .duplicated()
    .sum()
)


print("\n\nGESPEICHERT")
print("-" * 60)

print("\nIndikatorenliste:")
print(indikatoren_datei)

print("\nKreisliste:")
print(kreise_datei)