# Datenprojekt: Strukturwandelregionen und Geschlechterverhältnisse

Dieses Projekt untersucht Geschlechterverhältnisse in bayerischen Strukturwandelregionen. Im Mittelpunkt steht die Frage, welche Unterschiede sich in regionalen Daten zu Arbeit, Bevölkerung und Raumstruktur zeigen – und welche Perspektiven in diesen Daten möglicherweise nicht sichtbar werden.

## Projektordner

- `RawData/` – unveränderte Ausgangsdaten und zugehörige Dokumentation
- `DatenProjekt_Report/scripts/` – Skripte zur Bereinigung, Ergänzung, Prüfung und Aufbereitung der Daten
- `DatenProjekt_Report/data/metadata/` – Metadaten, Indikatoren und Zuordnungstabellen
- `DatenProjekt_Report/data/processed/` – verarbeitete Datensätze und GeoJSON-Datei
- `DatenProjekt_Report/` – Quarto-Bericht und Midterm-Präsentation
- `Dokumentation/` und `Studien/` – Projektunterlagen, Fachliteratur und Quellen

## Verwendete Ausgangsdaten

Die Rohdaten liegen im Ordner `RawData/`. Dazu gehören unter anderem INKAR-Tabellen, Bevölkerungs- und Ausländerzahlen, eine Tabelle zur Raumstruktur sowie das Verwaltungsgebiets-Geopaket `DE_VG250.gpkg`. Die Dateien wurden für das Projekt ausgewählt, weil sie regionale Vergleiche für bayerische Kreise und die Betrachtung von Strukturwandel und Geschlechterverhältnissen ermöglichen. Die Dokumentation und Lizenzhinweise der jeweiligen Quelle liegen ebenfalls bei den Daten.

Die Originaldateien in `RawData/` sollten bei der Verarbeitung unverändert bleiben. Bereinigte und abgeleitete Dateien werden unter `DatenProjekt_Report/data/` abgelegt.

## Verarbeitungsschritte

Die nummerierten Skripte in `DatenProjekt_Report/scripts/` bilden die Verarbeitungskette:

1. `01_bereinige_inkar.py` bereinigt die INKAR-Daten.
2. `02_erstelle_metadaten.py` erstellt Metadaten für die verwendeten Indikatoren.
3. `02b_ergaenze_indikatorenliste.py` ergänzt die Indikatorenliste.
4. `03_erstelle_stmwi_raumstruktur.py` bereitet die Raumstruktur-Daten des STM​​WI auf.
5. `04_erstelle_master.py` führt die aufbereiteten Daten in einem gemeinsamen Datensatz zusammen.
6. `05_validieren_master.py` prüft den zusammengeführten Datensatz.
7. `06_erstelle_geojson.py` erstellt die räumliche GeoJSON-Datei für Karten und Analysen.

Die Skripte werden in der Reihenfolge ihrer Nummerierung ausgeführt. Pfade und Einstellungen stehen in `DatenProjekt_Report/scripts/config.py`. Vor einem erneuten Lauf bitte die dort hinterlegten Pfade und die benötigten Python-Pakete prüfen.

## Benötigte Programme

### Quarto

Quarto wird benötigt, um den Bericht und die Präsentation aus den `.qmd`-Dateien zu erstellen. Quarto wird als Programm auf dem eigenen Computer installiert; es gehört **nicht** in den Projektordner. Die Projektdateien liegen anschließend weiterhin in `DatenProjekt_Report/`.

Im Terminal im Projektordner:

```bash
quarto preview DatenProjekt_Report/midterm.qmd
```

Für den Bericht entsprechend:

```bash
quarto preview DatenProjekt_Report/report.qmd
```

### Git LFS

Git LFS wird benötigt, weil das Geopaket `DE_VG250.gpkg` größer als 100 MB ist. Git LFS wird ebenfalls als Programm auf dem Computer installiert – **nicht** in `RawData/` und nicht in einem anderen Projektordner. Die Datei `.gitattributes` im Projekt legt fest, welche großen Dateien Git LFS verwaltet.

Nach der Installation einmalig im Terminal:

```bash
git lfs install
```

Wer das Repository neu herunterlädt, braucht Git und Git LFS. Git LFS muss installiert sein, damit große Dateien wie das Geopaket korrekt geladen werden.

### Python

Für die Verarbeitungsskripte wird Python 3 benötigt. Die Skripte verwenden zusätzliche Python-Bibliotheken. Die konkrete Paketliste sollte aus den Imports der Skripte beziehungsweise aus `config.py` entnommen werden; falls im Projekt eine `requirements.txt` ergänzt wird, kann die Installation daraus erfolgen:

```bash
python3 -m pip install -r DatenProjekt_Report/requirements.txt
```

## Repository herunterladen

Git, Git LFS, Quarto und Python werden auf dem Computer installiert. Sie werden nicht in den Projektordner kopiert. Danach kann das Repository in einen beliebigen Arbeitsordner geklont werden:

```bash
git clone https://github.com/figuerrarr/SDC_Datenprojekt.git
cd SDC_Datenprojekt
git lfs install
```

> Hinweis: Bitte den Repository-Link oben prüfen. Im Gespräch wurde als Adresse `https://github.com/figuerrarr/SDC_Datenprojekt.git` genannt; falls der GitHub-Benutzername oder Repository-Name anders geschrieben ist, muss die URL entsprechend angepasst werden.

## Hinweise

- Rohdaten, Studien und Dokumentation können Lizenz- oder Namensnennungspflichten haben. Die jeweiligen Lizenzdateien und Quellenangaben sind zu beachten.
- Vor dem Veröffentlichen prüfen, ob alle enthaltenen Dateien und personenbezogenen Informationen öffentlich geteilt werden dürfen.
- Generierte Vorschauen und Cache-Ordner sind nicht die Quelldateien; maßgeblich für die Präsentation ist `DatenProjekt_Report/midterm.qmd`.
