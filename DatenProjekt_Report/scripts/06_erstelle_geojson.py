from pathlib import Path

import geopandas as gpd
import pandas as pd


# ============================================================
# 1. PFADE
# ============================================================

PROJEKT_DIR = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJEKT_DIR / "DatenProjekt_Report"

PROCESSED_DIR = REPORT_DIR / "data" / "processed"
RAW_DIR = PROJEKT_DIR / "RawData"

VG250_FILE = (
    RAW_DIR
    / "vg250_01-01.utm32s.gpkg.ebenen"
    / "vg250_ebenen_0101"
    / "DE_VG250.gpkg"
)

MASTER_FILE = (
    PROCESSED_DIR
    / "inkar_bayern_2023_master_validiert.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "bayern_kreise_2023.geojson"
)


# ============================================================
# 2. DATEIEN LADEN
# ============================================================

print("=" * 60)
print("VG250 → GEOJSON")
print("=" * 60)

print("\nDateien werden geladen ...")

if not VG250_FILE.exists():
    raise FileNotFoundError(
        f"VG250-Datei nicht gefunden:\n{VG250_FILE}"
    )

if not MASTER_FILE.exists():
    raise FileNotFoundError(
        f"Master-Datei nicht gefunden:\n{MASTER_FILE}"
    )


# ============================================================
# 3. VG250 KREISE LADEN
# ============================================================

print("\nVG250-Ebene 'vg250_krs' wird geladen ...")

kreise = gpd.read_file(
    VG250_FILE,
    layer="vg250_krs"
)

print(f"VG250 insgesamt: {len(kreise)} Kreise")


# ============================================================
# 4. BAYERN FILTERN
# ============================================================

kreise["AGS"] = (
    kreise["AGS"]
    .astype(str)
    .str.zfill(5)
)

bayern = kreise[
    kreise["AGS"].str.startswith("09")
].copy()

print(f"Bayern: {len(bayern)} Kreise")


# ============================================================
# 5. MASTER LADEN
# ============================================================

master = pd.read_csv(
    MASTER_FILE,
    sep=";",
    dtype={"Kennziffer": "string"}
)

master["Kennziffer"] = (
    master["Kennziffer"]
    .astype("string")
    .str.zfill(5)
)

print(f"Master: {len(master)} Kreise")


# ============================================================
# 6. MASTER UND VG250 ÜBER AGS VERGLEICHEN
# ============================================================

print("\n" + "=" * 60)
print("AGS-VALIDIERUNG")
print("=" * 60)

ags_vg250 = set(bayern["AGS"])
ags_master = set(master["Kennziffer"])

fehlend_im_vg250 = sorted(
    ags_master - ags_vg250
)

fehlend_im_master = sorted(
    ags_vg250 - ags_master
)

print(
    f"AGS im Master:  {len(ags_master)}"
)

print(
    f"AGS in VG250:   {len(ags_vg250)}"
)


if fehlend_im_vg250:
    print(
        "\nWARNUNG: Diese AGS aus dem Master fehlen in VG250:"
    )
    print(fehlend_im_vg250)

if fehlend_im_master:
    print(
        "\nWARNUNG: Diese AGS aus VG250 fehlen im Master:"
    )
    print(fehlend_im_master)


if not fehlend_im_vg250 and not fehlend_im_master:
    print("\nOK: Alle 96 AGS stimmen überein.")


# ============================================================
# 7. MASTER MIT GEOMETRIEN VERBINDEN
# ============================================================

print("\nMaster und Geometrien werden verbunden ...")

geojson = bayern.merge(
    master,
    left_on="AGS",
    right_on="Kennziffer",
    how="inner",
    validate="one_to_one"
)

print(
    f"Ergebnis: {len(geojson)} Kreise"
)


# ============================================================
# 8. GEOMETRIE PRÜFEN
# ============================================================

print("\n" + "=" * 60)
print("GEOMETRIE-VALIDIERUNG")
print("=" * 60)

fehlende_geometrien = geojson.geometry.isna().sum()

print(
    f"Fehlende Geometrien: {fehlende_geometrien}"
)

if fehlende_geometrien > 0:
    raise ValueError(
        "Mindestens eine Geometrie fehlt."
    )


if len(geojson) != 96:
    raise ValueError(
        f"Es wurden {len(geojson)} statt 96 Kreise erzeugt."
    )

print("OK: 96 Kreise mit Geometrie vorhanden.")


# ============================================================
# 9. GEOJSON SPEICHERN
# ============================================================

# Nur Schlüssel, Name und Geometrie behalten; die Daten bleiben im Master
geojson = geojson[["Kennziffer", "kreisname", "geometry"]].copy()

# Vereinfachen (Toleranz in Metern, daher VOR der Umrechnung)
geojson["geometry"] = geojson.geometry.simplify(200, preserve_topology=True)

# Für plotly / Web-Karten nach WGS84 umrechnen
geojson = geojson.to_crs(4326)

geojson.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)

print("\n" + "=" * 60)
print("ERFOLG")
print("=" * 60)

print(
    f"GeoJSON gespeichert unter:\n{OUTPUT_FILE}"
)

print(
    f"Dateigröße: {OUTPUT_FILE.stat().st_size / 1e6:.2f} MB"
)