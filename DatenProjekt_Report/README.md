# Datenprojekt: Strukturwandelregionen und Geschlechterverhältnisse

Dieses Projekt untersucht Geschlechterverhältnisse in bayerischen Kreisen aus einer datenfeministischen Perspektive. Im Mittelpunkt steht die Frage, welche geschlechtsspezifischen Unterschiede sich in regionalen Daten zeigen — und welche Gleichstellungsdimensionen in diesen Daten systematisch fehlen.

Bezugsjahr der Daten: **2023**. Untersuchungsraum: **96 bayerische Kreise** (25 kreisfreie Städte, 71 Landkreise).

---

## Projektordner

- `RawData/` — unveränderte Ausgangsdaten und zugehörige Dokumentation
- `DatenProjekt_Report/scripts/` — Skripte zur Bereinigung, Analyse und Aufbereitung
- `DatenProjekt_Report/data/processed/` — verarbeitete Datensätze und GeoJSON
- `DatenProjekt_Report/data/metadata/` — Metadaten, Indikatoren- und Zuordnungstabellen
- `DatenProjekt_Report/report.qmd` — Quarto-Bericht (HTML)
- `DatenProjekt_Report/midterm.qmd` — Quarto-Midterm-Präsentation (Reveal.js)
- `Dokumentation/`, `Studien/` — Projektunterlagen, Fachliteratur, Quellen

---

## Verwendete Ausgangsdaten

Alle Rohdaten liegen in `RawData/` und bleiben dort unverändert. Verarbeitete und abgeleitete Dateien werden in `DatenProjekt_Report/data/` abgelegt.

### INKAR — Indikatoren und Karten zur Raum- und Stadtentwicklung

- Quelle: Bundesinstitut für Bau-, Stadt- und Raumforschung (BBSR), Ausgabe 07/2025
- Dateien: `Tabelle 20261007.csv`, `inkar-2.xls`
- Liefert: **43 Indikatoren** pro Kreis zu Bevölkerung, Wanderung, Bildung, Ausbildung und Raumstruktur, teils geschlechterdifferenziert.
- Die CSV enthält die Werte, die `.xls` enthält die Metadaten (Langnamen, Einheiten, Berechnungsgrundlagen, Anmerkungen).

### VG250 — Verwaltungsgebiete 1:250 000

- Quelle: Bundesamt für Kartographie und Geodäsie (BKG)
- Datei: `vg250_01-01.utm32s.gpkg.ebenen/vg250_ebenen_0101/DE_VG250.gpkg`
- Liefert: die **Kreisgrenzen** als Geometrien, bundesweit 430 Kreise, davon 96 in Bayern.

### StMWi — Raumstruktur nach LEP-Gebietskategorien

- Quelle: Bayerisches Staatsministerium für Wirtschaft, Landesentwicklung und Energie, Stand 1. Juni 2023
- Liefert pro Kreis: **Regierungsbezirk**, **LEP-Gebietskategorie** (LR = Ländlicher Raum, VR = Verdichtungsraum) und **RmbH-Status** (Raum mit besonderem Handlungsbedarf).
- Die Zuordnung ist im Skript `03_erstelle_stmwi_raumstruktur.py` dokumentiert; die beiden Excel-Dateien `Tab_1.1.1_...xlsx` und `Tab_1.1.4_...xlsx` dienen als Referenz.

Die drei Quellen werden über die **AGS** (Amtliche Gemeindekennziffer, 5-stellig) zusammengeführt.

---

## Verarbeitungskette

Die nummerierten Skripte in `DatenProjekt_Report/scripts/` werden in dieser Reihenfolge ausgeführt.

| Skript | Aufgabe | Ausgabe |
|---|---|---|
| `01_bereinige_inkar.py` | Liest die INKAR-CSV, vereinheitlicht AGS, wandelt deutsche Zahlenformate, prüft auf doppelte AGS und fehlende Werte | `processed/inkar_bayern_2023_bereinigt.csv` |
| `02_erstelle_metadaten.py` | Erstellt Indikatoren- und Kreisliste aus den bereinigten Daten | `metadata/indikatorenliste.csv`, `metadata/kreisliste.csv` |
| `02b_ergaenze_indikatorenliste.py` | Gleicht CSV und INKAR-Metadaten ab, ergänzt Einheit, Geschlechtsbezug, Berechnung, Datenhinweise | `metadata/indikatorenliste_final.csv` |
| `03_erstelle_stmwi_raumstruktur.py` | Ordnet jedem Kreis Regierungsbezirk, LEP-Kategorie (LR/VR) und RmbH-Status zu | `metadata/stmwi_raumstruktur_2023.csv` |
| `04_erstelle_master.py` | Führt INKAR, Kreisliste und Raumstruktur über den AGS zusammen | `processed/inkar_bayern_2023_master.csv` |
| `05_validieren_master.py` | Prüft 96 Kreise, AGS-Eindeutigkeit, Kreistyp, Metadaten-Vollständigkeit | `processed/inkar_bayern_2023_master_validiert.csv` |
| `06_erstelle_geojson.py` | Verbindet Master mit VG250-Geometrien, vereinfacht Grenzen, exportiert nach WGS84 | `processed/bayern_kreise_2023.geojson` |
| `07_analysiere_gender_gaps.py` | Berechnet Gender Gaps (Frauen − Männer) pro Kreis und Regionstyp | `processed/analyse_gaps_kreise.csv`, `analyse_gaps_regionen.csv`, `analyse_rankings.csv` |
| `08_analysiere_datenluecken.py` | Quantifiziert, welche Gleichstellungsdimensionen in den Daten vorliegen und welche fehlen | `processed/analyse_datenluecken.csv` |

Skript `05` muss am Ende **`VALIDIERUNG BESTANDEN`** ausgeben, bevor mit `06` und den Analysen weitergearbeitet wird. Skript `06` muss **`OK: 96 Kreise mit Geometrie vorhanden.`** ausgeben.

Pfade und Ordnerstruktur sind in `config.py` gebündelt.

---

## Bericht und Präsentation rendern

### Quarto

Quarto wird als Programm auf dem Rechner installiert (nicht in den Projektordner). Im Terminal im Ordner `DatenProjekt_Report/`:

```bash
quarto render report.qmd        # Bericht
quarto render midterm.qmd       # Midterm-Präsentation
```

Die `.qmd`-Dateien sind die Quellen, die `.html`-Dateien die gerenderten Fassungen. Inhaltliche Änderungen immer in der `.qmd` vornehmen, nie in der HTML.

### Speaker-Notes in der Midterm

Die Midterm enthält für jede Folie Sprechnotizen. Sichtbar werden sie im **Speaker View**: `midterm.html` im Browser öffnen, Taste `s` drücken.

---

## Benötigte Programme

### Python 3

Für alle Skripte. Zusätzliche Bibliotheken: `pandas`, `geopandas`, `numpy`, `plotly`, `openpyxl`, `xlrd`.

Installation:

```bash
python3 -m pip install pandas geopandas numpy plotly openpyxl xlrd
```

Für die Karten wird zusätzlich `pyogrio` oder `fiona` als Geometrie-Engine benötigt (kommt mit `geopandas`).

### Quarto

Für Bericht und Präsentation. Installation: <https://quarto.org/docs/get-started/>

### Git LFS

Wird benötigt, weil das Geopaket `DE_VG250.gpkg` größer als 100 MB ist. Git LFS wird auf dem Rechner installiert (nicht im Projektordner). Die Datei `.gitattributes` legt fest, welche Dateien über LFS laufen.

```bash
git lfs install
```

Wer das Repository neu klont, braucht Git und Git LFS.

---

## Repository herunterladen

```bash
git clone https://github.com/figueroarr/SDC_Datenprojekt.git
cd SDC_Datenprojekt
git lfs install
```

Falls der Repository-Name oder der GitHub-Benutzername anders lautet, muss die URL entsprechend angepasst werden.

---

## Hinweise

- Rohdaten, Studien und Dokumentation können Lizenz- oder Namensnennungspflichten haben. Die jeweiligen Lizenzdateien und Quellenangaben sind zu beachten (siehe `RawData/`).
- Vor dem Veröffentlichen prüfen, ob alle enthaltenen Dateien und Informationen öffentlich geteilt werden dürfen.
- Generierte Vorschauen und Cache-Ordner (`__pycache__/`, `*_files/`) sind nicht die Quelldateien. Maßgeblich sind die `.qmd`-Dateien und die Skripte.