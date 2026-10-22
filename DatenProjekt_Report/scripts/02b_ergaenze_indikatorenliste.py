import re
import sys

import pandas as pd

from config import RAW_DIR, METADATA_DIR


# ============================================================
# 1. PFADE
# ============================================================

# Zentrale INKAR-Datendatei
DATEN_DATEI = RAW_DIR / "Tabelle 20261007.csv"

# INKAR-Datei mit den ausführlichen Metadaten
METADATEN_DATEI = RAW_DIR / "inkar-2.xls"

# Ausgabe
OUTPUT_FILE = METADATA_DIR / "indikatorenliste_final.csv"

# Warnungen und Fehler sammeln
warnungen = []
fehler = []

# ============================================================
# 2. Dimensionen (explizit, keine Schlüsselwortsuche)
# ============================================================

RAUM = "Raumstruktur"
DEMO = "Bevölkerung und Demografie"
GESCHL = "Geschlechterstruktur"
WANDER = "Wanderung und Mobilität"
BILDUNG = "Bildung und Ausbildung"

DIMENSION = {
    "Bodenfläche gesamt qkm": RAUM,
    "Bevölkerung gesamt": DEMO,
    "Bevölkerung männlich": DEMO,
    "Bevölkerung weiblich": DEMO,
    "Einwohner von 18 bis unter 25 Jahren": DEMO,
    "Einwohner von 25 bis unter 30 Jahren": DEMO,
    "Einwohner von 30 bis unter 50 Jahren": DEMO,
    "Einwohner von 50 bis unter 65 Jahren": DEMO,
    "Einwohner von 65 bis unter 75 Jahren": DEMO,
    "Frauenanteil": GESCHL,
    "Frauenanteil 20 bis unter 40 Jahre": GESCHL,
    "Bevölkerungsentwicklung (10 Jahre)": DEMO,
    "Bevölkerungsentwicklung (5 Jahre)": DEMO,
    "Außenwanderungssaldo Frauen": WANDER,
    "Außenwanderungssaldo Männer": WANDER,
    "Binnenwanderungssaldo": WANDER,
    "Binnenwanderungssaldo Frauen": WANDER,
    "Binnenwanderungssaldo Männer": WANDER,
    "Fortzugsrate": WANDER,
    "Zuzugsrate Frauen": WANDER,
    "Zuzugsrate Männer": WANDER,
    "Fortzugsrate Frauen": WANDER,
    "Fortzugsrate Männer": WANDER,
    "Schulabgänger mit allgemeiner Hochschulreife": BILDUNG,
    "Weibliche Schulabgänger mit allgemeiner Hochschulreife": BILDUNG,
    "Männliche Schulabgänger mit allgemeiner Hochschulreife": BILDUNG,
    "Schulabgänger mit mittlerem Abschluss": BILDUNG,
    "Weibliche Schulabgänger mit mittlerem Abschluss": BILDUNG,
    "Männliche Schulabgänger mit mittlerem Abschluss": BILDUNG,
    "Schulabgänger mit Hauptschulabschluss": BILDUNG,
    "Weibliche Schulabgänger mit Hauptschulabschluss": BILDUNG,
    "Männliche Schulabgänger mit Hauptschulabschluss": BILDUNG,
    "Schulabgänger ohne Abschluss": BILDUNG,
    "Weibliche Schulabgänger ohne Abschluss": BILDUNG,
    "Männliche Schulabgänger ohne Abschluss": BILDUNG,
    "Auszubildende": BILDUNG,
    "Weibliche Auszubildende": BILDUNG,
    "Männliche Auszubildende": BILDUNG,
    "Ländlichkeit": RAUM,
    "Bevölkerung in Mittelzentren": RAUM,
    "Bevölkerung in Oberzentren": RAUM,
    "Einwohnerdichte": RAUM,
    "Einwohner-Arbeitsplatz-Dichte": RAUM,
}


# ============================================================
# 3. Bekannte Datenhinweise (Vorbelegung)
# ============================================================

HINWEIS_WANDERUNG = (
    "INKAR: Asylbewerber in zentralen Aufnahmestellen erscheinen als "
    "Außenwanderungsgewinn, spätere Fortzüge als Binnenwanderungsverlust. "
    "Einzelne Kreise sind dadurch verzerrt."
)

HINWEIS_ABITUR = (
    "Rohdaten enthalten 0,0 bei Landkreis Bamberg (09471) und Landkreis "
    "Schweinfurt (09678). Ursache laut INKAR-Metadaten nicht erklärt; "
    "im Dashboard als 'keine Daten' behandeln."
)

HINWEIS_AZUBI_GESAMT = (
    "Auszubildende je 1.000 SV-Beschäftigte, bezogen auf den Arbeitsort. "
    "Nicht vergleichbar mit den Anteilswerten der Spalten für Frauen/Männer."
)

HINWEIS_AZUBI_GESCHLECHT = (
    "Anteil an allen Auszubildenden in %, Arbeitsort. "
    "Frauen- und Männeranteil summieren sich auf 100."
)

HINWEIS_BEVOELKERUNG = (
    "INKAR: Personen mit Geschlecht 'divers' oder 'unbekannt' werden per "
    "Umschlüsselungsverfahren auf männlich und weiblich verteilt."
)


def vorbelegter_hinweis(indikator):
    """Gibt einen bekannten Datenhinweis zurück oder einen leeren Text."""

    if "wanderungssaldo" in indikator.lower():
        return HINWEIS_WANDERUNG

    if "Hochschulreife" in indikator:
        return HINWEIS_ABITUR

    if indikator == "Auszubildende":
        return HINWEIS_AZUBI_GESAMT

    if indikator in ("Weibliche Auszubildende", "Männliche Auszubildende"):
        return HINWEIS_AZUBI_GESCHLECHT

    if indikator in (
        "Bevölkerung männlich",
        "Bevölkerung weiblich",
        "Frauenanteil",
        "Frauenanteil 20 bis unter 40 Jahre",
    ):
        return HINWEIS_BEVOELKERUNG

    return ""


# ============================================================
# 4. Hilfsfunktionen
# ============================================================

def leite_einheit_ab(langname, berechnung):
    """Leitet die Einheit aus Langname und Berechnungsformel ab."""

    langname = str(langname) if pd.notna(langname) else ""
    berechnung = str(berechnung) if pd.notna(berechnung) else ""

    # 1. "je 1.000 ..."
    treffer = re.search(r"je 1\.000 .*$", langname)
    if treffer:
        return treffer.group(0).strip()

    # 2. "... je km²"
    treffer = re.search(r"([A-Za-zÄÖÜäöüß ]+ je km²)\s*$", langname)
    if treffer:
        return treffer.group(1).strip()

    # 3. "in km²"
    if re.search(r"in km²\s*$", langname):
        return "km²"

    # 4. Prozent
    if re.search(r"in %\s*$", langname) or "x 100" in berechnung:
        return "%"

    # 5. absolute Zahl
    if langname.startswith("Zahl der"):
        return "Personen"

    return "PRÜFEN"


def bestimme_geschlechtsbezug(indikator):
    """Frauen, Männer, Frauenanteil oder gesamt."""

    if indikator.startswith("Frauenanteil"):
        return "Geschlechterverhältnis"

    if (
        indikator.startswith("Weibliche ")
        or indikator.endswith(" Frauen")
        or indikator.endswith(" weiblich")
    ):
        return "Frauen"

    if (
        indikator.startswith("Männliche ")
        or indikator.endswith(" Männer")
        or indikator.endswith(" männlich")
    ):
        return "Männer"

    return "gesamt"


def bestimme_familie(indikator):
    """Entfernt das Geschlechtswort aus dem Indikatornamen."""

    name = indikator

    for praefix in ("Weibliche ", "Männliche "):
        if name.startswith(praefix):
            # "Weibliche Schulabgänger mit ..." -> "Schulabgänger mit ..."
            name = name[len(praefix):]
            name = name[0].upper() + name[1:]

    for suffix in (" Frauen", " Männer", " weiblich", " männlich", " gesamt"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]

    return name.strip()


# ============================================================
# 5. Rohdaten und Metadaten einlesen
# ============================================================

print("=" * 60)
print("INDIKATORENLISTE ERGÄNZEN")
print("=" * 60)

if not DATEN_DATEI.exists():
    raise FileNotFoundError(
        f"INKAR-Datendatei nicht gefunden: {DATEN_DATEI}"
    )

if not METADATEN_DATEI.exists():
    raise FileNotFoundError(
        f"INKAR-Metadatendatei nicht gefunden: {METADATEN_DATEI}"
    )

try:

    # --------------------------------------------------------
    # INKAR-Daten aus Tabelle 20261007.csv
    # --------------------------------------------------------

    daten = pd.read_csv(
        DATEN_DATEI,
        sep=";",
        encoding="utf-8-sig",
        header=None
    )

    # --------------------------------------------------------
    # INKAR-Metadaten aus inkar-2.xls
    # --------------------------------------------------------

    metadaten = pd.read_excel(
        METADATEN_DATEI,
        sheet_name="Metadaten",
        header=1,
        engine="xlrd"
    )

except ImportError:
    raise ImportError(
        "Bitte installieren: pip install xlrd"
    )


# Zeile 0 = Spaltennamen
# Zeile 1 = Jahr
# Ab Spalte 4 beginnen die Indikatoren

indikatoren_daten = (
    daten.iloc[0, 3:]
    .astype(str)
    .tolist()
)

jahre = daten.iloc[1, 3:].tolist()

jahr_je_indikator = dict(
    zip(indikatoren_daten, jahre)
)

print(
    f"Indikatoren in 'Tabelle 20261007.csv': {len(indikatoren_daten)}"
)

print(
    f"Indikatoren im Blatt 'Metadaten':      {len(metadaten)}"
)

# ============================================================
# 6. Prüfungen
# ============================================================

# 6.1 Mengenvergleich Daten <-> Metadaten
nur_daten = sorted(set(indikatoren_daten) - set(metadaten["Indikator"]))
nur_meta = sorted(set(metadaten["Indikator"]) - set(indikatoren_daten))

if nur_daten:
    fehler.append(f"Nur in 'Daten', nicht in 'Metadaten': {nur_daten}")
if nur_meta:
    fehler.append(f"Nur in 'Metadaten', nicht in 'Daten': {nur_meta}")

# 6.2 Dimensionen vollständig?
ohne_dimension = [i for i in indikatoren_daten if i not in DIMENSION]
if ohne_dimension:
    fehler.append(
        "Keine Dimension im Dictionary für: " f"{ohne_dimension}"
    )

# 6.3 Jahre
einzigartige_jahre = sorted({str(j) for j in jahre})
if len(einzigartige_jahre) > 1:
    warnungen.append(
        f"Unterschiedliche Bezugsjahre in den Daten: {einzigartige_jahre}"
    )

if fehler:
    print("\nABBRUCH:")
    for f in fehler:
        print(f"  - {f}")
    sys.exit(1)


# ============================================================
# 7. Katalog aufbauen
# ============================================================

katalog = pd.DataFrame({"indikator": indikatoren_daten})

katalog = katalog.merge(
    metadaten[
        [
            "Indikator",
            "Langname",
            "Quelle",
            "Berechnungsgrundlage",
            "Anmerkungen",
        ]
    ].rename(
        columns={
            "Indikator": "indikator",
            "Langname": "langname",
            "Quelle": "quelle_original",
            "Berechnungsgrundlage": "berechnung",
            "Anmerkungen": "anmerkung",
        }
    ),
    on="indikator",
    how="left",
    validate="one_to_one",
)

katalog["dimension"] = katalog["indikator"].map(DIMENSION)

katalog["jahr"] = (
    katalog["indikator"]
    .map(jahr_je_indikator)
    .astype(float)
    .astype("Int64")
)

katalog["einheit"] = katalog.apply(
    lambda z: leite_einheit_ab(z["langname"], z["berechnung"]), axis=1
)

katalog["geschlechtsbezug"] = katalog["indikator"].map(
    bestimme_geschlechtsbezug
)

katalog["indikator_familie"] = katalog["indikator"].map(bestimme_familie)

katalog["quelle"] = "INKAR 07/2025 (BBSR)"


# ============================================================
# 8. Abgeleitete Familien-Eigenschaften
# ============================================================

# Gap F-M ist berechenbar, wenn es in der Familie Frauen- UND
# Männerwerte gibt.
def gap_berechenbar(gruppe):
    bezuege = set(gruppe["geschlechtsbezug"])
    return "Frauen" in bezuege and "Männer" in bezuege


# Einheiten innerhalb einer Familie einheitlich?
def einheit_konsistent(gruppe):
    # "je 1.000 weibliche Einwohner" und "je 1.000 Einwohner" gelten als
    # gleiche Einheit (Bezugsgruppe ist jeweils die eigene Gruppe).
    normalisiert = (
        gruppe["einheit"]
        .str.replace("weibliche ", "", regex=False)
        .str.replace("männliche ", "", regex=False)
    )
    return normalisiert.nunique() == 1


gap_map = katalog.groupby("indikator_familie").apply(
    gap_berechenbar, include_groups=False
)
einheit_map = katalog.groupby("indikator_familie").apply(
    einheit_konsistent, include_groups=False
)

katalog["gap_berechenbar"] = (
    katalog["indikator_familie"].map(gap_map).map({True: "ja", False: "nein"})
)
katalog["einheit_konsistent_in_familie"] = (
    katalog["indikator_familie"]
    .map(einheit_map)
    .map({True: "ja", False: "nein"})
)

inkonsistente = sorted(
    katalog.loc[
        (katalog["einheit_konsistent_in_familie"] == "nein")
        & (katalog["gap_berechenbar"] == "ja"),
        "indikator_familie",
    ].unique()
)
if inkonsistente:
    warnungen.append(
        "Familien mit gemischten Einheiten (Gesamtwert nicht mit "
        f"Frauen/Männerwert vergleichbar): {inkonsistente}"
    )

unklare_einheit = katalog.loc[katalog["einheit"] == "PRÜFEN", "indikator"]
if not unklare_einheit.empty:
    warnungen.append(
        f"Einheit nicht erkannt bei: {unklare_einheit.tolist()}"
    )


# ============================================================
# 9. Manuelle Spalten (bei erneutem Lauf nicht überschreiben)
# ============================================================

katalog["im_dashboard"] = ""
katalog["datenhinweis"] = katalog["indikator"].map(vorbelegter_hinweis)

if OUTPUT_FILE.exists():

    alt = pd.read_csv(
        OUTPUT_FILE, sep=";", encoding="utf-8-sig", dtype=str
    ).fillna("")

    alt = alt.set_index("indikator")

    for spalte in ("im_dashboard", "datenhinweis"):

        if spalte not in alt.columns:
            continue

        bisher = katalog["indikator"].map(alt[spalte])
        katalog[spalte] = bisher.where(
            bisher.notna() & (bisher != ""), katalog[spalte]
        )

    print("\nBestehende manuelle Einträge wurden übernommen.")


# ============================================================
# 10. Spalten ordnen und speichern
# ============================================================

katalog = katalog[
    [
        "dimension",
        "indikator",
        "indikator_familie",
        "geschlechtsbezug",
        "gap_berechenbar",
        "einheit",
        "einheit_konsistent_in_familie",
        "jahr",
        "quelle",
        "quelle_original",
        "langname",
        "berechnung",
        "anmerkung",
        "im_dashboard",
        "datenhinweis",
    ]
].sort_values(["dimension", "indikator_familie", "geschlechtsbezug"])

METADATA_DIR.mkdir(parents=True, exist_ok=True)

katalog.to_csv(
    OUTPUT_FILE, sep=";", index=False, encoding="utf-8-sig"
)


# ============================================================
# 11. Zusammenfassung
# ============================================================

print("\n" + "=" * 60)
print("ERGEBNIS")
print("=" * 60)

print(f"\nIndikatoren im Katalog: {len(katalog)}")

print("\nDimensionen:")
print(katalog["dimension"].value_counts().to_string())

print("\nGeschlechtsbezug:")
print(katalog["geschlechtsbezug"].value_counts().to_string())

print("\nEinheiten:")
print(katalog["einheit"].value_counts().to_string())

print(
    "\nFamilien mit Gap-Berechnung (Frauen und Männer vorhanden): "
    f"{katalog.loc[katalog['gap_berechenbar'] == 'ja', 'indikator_familie'].nunique()}"
)

if warnungen:
    print(f"\nHinweise ({len(warnungen)}):")
    for w in warnungen:
        print(f"  - {w}")

print(f"\nGespeichert: {OUTPUT_FILE}")
