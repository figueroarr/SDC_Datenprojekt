from pathlib import Path

# ============================================================
# PROJEKTPFADE
# ============================================================

# config.py liegt in:
# DatenProjekt/DatenProjekt_Report/scripts/
#
# parents[2] führt zurück zu:
# DatenProjekt/

PROJEKT_DIR = Path(__file__).resolve().parents[2]

REPORT_DIR = PROJEKT_DIR / "DatenProjekt_Report"

DATA_DIR = REPORT_DIR / "data"

PROCESSED_DIR = DATA_DIR / "processed"

METADATA_DIR = DATA_DIR / "metadata"

RAW_DIR = PROJEKT_DIR / "RawData"