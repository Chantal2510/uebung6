# Eigene POI-Vector-Tiles: Cafés in Mainz

## 1. Ziel der Aufgabe

Aus einer vorhandenen GeoJSON-Datei mit Cafés aus Mainz werden eigene XYZ-Vector-Tiles erstellt. Tippecanoe schreibt die Kacheln als statische Dateien. Sie brauchen dafür keinen eigenen Kartenserver. Die fertigen Kacheln können über GitHub Pages in einer Webkarte und in QGIS verwendet werden.

## 2. Datenquelle der Cafés

Verwendet wurde ausschließlich `geodata/cafeExport.geojson`. Die Datei ist ein Overpass-Turbo-Export aus OpenStreetMap und enthält in den Metadaten den Zeitstempel `2026-11-03T14:57:23Z` sowie den ODbL-Lizenzhinweis.

Im Ordner liegt außerdem `geodata/export.geojson`. Diese Datei enthält Punkte bei Rom (ungefähr 12,49° östliche Länge und 41,89° nördliche Breite) und wurde ausdrücklich **nicht** verwendet. Es wurden keine Café-Daten ergänzt oder erfunden.

## 3. Beschreibung der Café-Daten

Die verwendete Datei enthält 82 Punktobjekte. Alle haben `amenity=cafe`, einen Namen und eigene, nicht doppelte Koordinaten. Die geografische Ausdehnung liegt in Mainz:

- Länge: 8,2014261° bis 8,3098061° Ost
- Breite: 49,9399178° bis 50,0223262° Nord

Die bereinigte Datei enthält nur Attribute, die in der Quelldatei vorhanden waren:

| Attribut | Cafés mit Wert |
|---|---:|
| `name` | 82 |
| `amenity` | 82 |
| `opening_hours` | 67 |
| `address` | 62 |
| `outdoor_seating` | 48 |
| `wheelchair` | 46 |
| `website` | 39 |
| `cuisine` | 20 |

Die Straßenadresse wurde aus vorhandenen Adressfeldern zu einem lesbaren Feld zusammengefügt. Eine Website kann auch aus `contact:website` stammen.

## 4. Datenbereinigung und Koordinatensystem

Die Originaldatei bleibt unverändert. Das Skript `tools/prepare_poi.py` liest sie ein, prüft GeoJSON-Struktur, Punktgeometrien, WGS84-Koordinaten und `amenity=cafe`, und schreibt nur die benötigten Attribute nach `data/poi.geojson`.

Die Quelle enthält kein separates `crs`-Feld. Die Koordinaten stehen aber als Längengrad/Breitengrad in der für GeoJSON üblichen Reihenfolge. Das entspricht WGS84 (EPSG:4326); deshalb war keine Transformation nötig. Die Koordinatenwerte und die räumliche Lage in Mainz wurden geprüft.

```bash
python3 tools/prepare_poi.py
```

Das Skript erzeugt die Datei lokal. Sowohl die Quelldateien unter `geodata/` als auch `data/poi.geojson` sind in `.gitignore` eingetragen und sollen nicht veröffentlicht werden.

### Abgleich mit der Rasterkachel

`geodata/Kachel-Mainz.tif` ist 10.000 × 10.000 Pixel groß. Seine GeoTIFF-Metadaten ergeben 0,2 m Pixelgröße und damit eine Ausdehnung von 2 × 2 km in ETRS89 / UTM Zone 32N (EPSG:25832): E 446.000–448.000 m, N 5.536.000–5.538.000 m. Eine Café-Koordinate liegt innerhalb dieser Ausdehnung. Da kein Beschneiden bestätigt wurde, bleiben trotzdem alle 82 Cafés in der Datengrundlage.

## 5. Tippecanoe-Befehle und Parameter

Das Docker-Image verwendet Tippecanoe 2.62.5. Im Ordner `uebung6` bauen:

```bash
docker build -t tippecanoe-uebung6 tools
```

Die wichtigsten Parameter sind:

- `-e tiles_xyz/poi`: Ausgabe als XYZ-Ordner `z/x/y.pbf`
- `-l poi`: interner Vector-Tile-Layername ist `poi`
- `-Z10 -z14`: minimale Zoomstufe 10 und maximale Zoomstufe 14
- `--drop-densest-as-needed`: kann in zu dichten Kacheln Punkte ausdünnen
- `--no-tile-compression`: schreibt unkomprimierte Vector-Tiles
- `--force`: überschreibt eine vorhandene Ausgabe

## 6. Erzeugung der XYZ-Kacheln

Die Befehle im Ordner `uebung6` ausführen:

```bash
mkdir -p tiles_xyz/poi
docker run --rm -v "$PWD":/work -w /work tippecanoe-uebung6 \
  tippecanoe -e tiles_xyz/poi -l poi \
  -Z10 -z14 --drop-densest-as-needed \
  --no-tile-compression --force data/poi.geojson
```

Tippecanoe legt die tatsächlich benötigten Kacheln unter `tiles_xyz/poi/` ab. `--drop-densest-as-needed` kann Punkte nur bei zu hoher Dichte reduzieren; die Ausgangsdatei wird dadurch nicht verändert.

## 7. Tatsächliche Dateigröße

Nach der Kachelerzeugung wurde die Summe aller Dateien unter `tiles_xyz/poi/` gemessen: **31.236 Byte** (0,031236 MB bzw. 0,029789 MiB). Das sind 37 `.pbf`-Kacheln und die von Tippecanoe erzeugte `metadata.json`. Der Layer in den PBF-Dateien heißt `poi`; die Zoomstufen 10 bis 14 sind enthalten. Bei Zoom 14 sind alle 82 verschiedenen Punktpositionen vorhanden. Auf den kleineren Zoomstufen kann Tippecanoe wegen `--drop-densest-as-needed` Punkte ausdünnen. Das Ergebnis liegt deutlich unter dem Ziel von 5 MB.

## 8. Veröffentlichung auf GitHub Pages

Das lokale `uebung6`-Verzeichnis ist selbst das Repository-Root. Das eingetragene GitHub-Remote ist `https://github.com/Chantal2510/uebung6.git`. Wenn GitHub Pages für den Branch `main` und das Repository-Root aktiviert ist, lautet der Projektseiten-Pfad:

```text
https://chantal2510.github.io/uebung6/tiles_xyz/poi/{z}/{x}/{y}.pbf
```

GitHub Pages muss in den Repository-Einstellungen noch aktiviert werden, falls das nicht bereits geschehen ist. Es wurden keine GitHub-Einstellungen geändert.

Für die Veröffentlichung die fertigen Kacheln `tiles_xyz/poi/` auswählen. Die Rohdateien und die bereinigte Quelldatei werden durch `.gitignore` ausgeschlossen. Lokale Bevölkerungskacheln bleiben ebenfalls ausgeschlossen. Nicht alle Dateien eines Projekts werden automatisch durch `.gitignore` von GitHub Pages verborgen, wenn sie bereits versioniert sind; vor einem Commit deshalb die Dateiliste prüfen.

Die Webkarte verwendet einen relativen `BASE`-Pfad und kann lokal (mit Live Server) oder nach der Veröffentlichung im GitHub-Pages-Unterordner geöffnet werden. Für Cafés gibt es einen eigenen Ein-/Ausschalter, gut sichtbare Punkte, Namen ab Zoomstufe 13 und Hover-Informationen. Lokal wird XYZ ausgewählt, weil der einfache Python-Webserver keine PMTiles-HTTP-Range-Requests unterstützt. Auf `*.github.io` wird dagegen PMTiles für Gebäude verwendet; die nicht veröffentlichten Bevölkerungsdaten werden dort ausgeblendet. Die POI-Kacheln werden in beiden Fällen relativ als XYZ geladen.

Die Gebäude- und Bevölkerungsebenen gehören ebenfalls zur Übungsvorlage. Ihre Quelldaten waren im lokalen Ordner zunächst nicht vorhanden. Für die vollständige lokale Karte wurden daher die beiden Beispieldateien aus dem verlinkten offiziellen Übungsmaterial verwendet: `data/buildings.geojson` (6.411 OSM-Gebäude) und `data/population.geojson` (2.982 Zensus-2022-Gitterzellen). Die Dateien bleiben lokal und sind von Git ausgeschlossen. Aus ihnen wurden anschließend Gebäude- und Bevölkerungskacheln nach den Tippecanoe-Vorgaben der Übung erzeugt. Die ursprüngliche MapLibre-Darstellung mit Gebäude-/Bevölkerungsschaltern, Beschriftungen, Popups und 3D-Höhen bleibt erhalten; wenn die Kacheldateien fehlen, blendet die Seite die jeweilige Steuerung aus.

Zum lokalen Erzeugen der Übungsebenen im Ordner `uebung6` (Image vorher mit `docker build -t tippecanoe-uebung6 tools` bauen):

```bash
mkdir -p tiles tiles_xyz
docker run --rm -v "$PWD":/work -w /work tippecanoe-uebung6 \
  tippecanoe -o tiles/buildings.pmtiles -l buildings \
  -Z13 -z16 --no-feature-limit --no-tile-size-limit --force data/buildings.geojson
docker run --rm -v "$PWD":/work -w /work tippecanoe-uebung6 \
  tippecanoe -e tiles_xyz/buildings -l buildings \
  -Z13 -z16 --no-feature-limit --no-tile-size-limit \
  --no-tile-compression --force data/buildings.geojson
docker run --rm -v "$PWD":/work -w /work tippecanoe-uebung6 \
  tippecanoe -o tiles/population.pmtiles -l population \
  -Z8 -z15 --no-tile-size-limit --coalesce-densest-as-needed \
  --force data/population.geojson
docker run --rm -v "$PWD":/work -w /work tippecanoe-uebung6 \
  tippecanoe -e tiles_xyz/population -l population \
  -Z8 -z15 --no-tile-size-limit --coalesce-densest-as-needed \
  --no-tile-compression --force data/population.geojson
```

Diese beiden Zusatz-Layer wurden lokal wiederhergestellt. Gemessene Größen: `tiles/buildings.pmtiles` 1.187.230 Byte, `tiles/population.pmtiles` 1.034.536 Byte, `tiles_xyz/buildings/` 2.285.778 Byte und `tiles_xyz/population/` 2.647.562 Byte. Die Bevölkerungskacheln und Quelldaten sollen nicht mit den POI-Dateien veröffentlicht werden; alle GeoJSON-Quelldateien sind in `.gitignore` ausgeschlossen. Für die lokale Vorschau ist XYZ vorausgewählt, weil `python3 -m http.server` die für PMTiles nötigen HTTP-Byte-Bereichsanfragen nicht unterstützt. Die POI-Darstellung und der Hover wurden bereits mit den Café-Kacheln lokal getestet.

## 9. Einbindung in QGIS

1. **Layer → Layer hinzufügen → Vector-Tiles-Layer → Neu** öffnen und eine generische Verbindung anlegen.
2. Name: `Cafés Mainz`; Typ: **XYZ**.
3. Min. Zoom: **10**, Max. Zoom: **14**.
4. URL:

   ```text
   https://chantal2510.github.io/uebung6/tiles_xyz/poi/{z}/{x}/{y}.pbf
   ```

5. Verbindung speichern, den Layer hinzufügen und auf Mainz zoomen.
6. Optional den Mapbox-Style `qgis/poi_style.json` verwenden. Die URL ist dort bereits eingetragen. Die Cafés werden orange mit weißer Kontur und ab Zoom 13 mit Namen angezeigt.

Für einen lokalen Test mit VS Code Live Server hängt die URL davon ab, welcher Ordner als Webroot dient:

- `uebung6` ist Webroot: `http://127.0.0.1:5500/tiles_xyz/poi/{z}/{x}/{y}.pbf`
- der übergeordnete Ordner ist Webroot: `http://127.0.0.1:5500/uebung6/tiles_xyz/poi/{z}/{x}/{y}.pbf`

Die Geodaten stammen aus OpenStreetMap und stehen unter ODbL. OpenStreetMap-Mitwirkende müssen als Quelle genannt werden.

## 10. Häufige Probleme und Lösungen

| Problem | Lösung |
|---|---|
| Docker meldet `Mounts denied` | Docker Desktop starten und den Ordner `uebung6` als lokalen Projektordner freigeben. |
| `tippecanoe-uebung6` wird nicht gefunden | Zuerst `docker build -t tippecanoe-uebung6 tools` im Ordner `uebung6` ausführen. |
| Die Karte zeigt keine Cafés | Prüfen, ob `tiles_xyz/poi/{z}/{x}/{y}.pbf` existiert und der `poi`-Layername sowie Zoom 10–14 stimmen. Die HTML-Datei über Live Server statt `file://` öffnen. |
| GitHub Pages liefert 404 | Pages-Quelle und Repository-Unterpfad prüfen; Ordnernamen sind im URL-Pfad groß-/kleinschreibungssensitiv. |
| QGIS zeigt keine Kacheln | `{z}/{x}/{y}` genau so stehen lassen, Min./Max. Zoom prüfen und die Verbindung neu laden. |
| Die Kacheln überschreiten 5 MB | Erst unnötige Attribute und die tatsächliche Featurezahl prüfen; danach gegebenenfalls den maximalen Zoom reduzieren und neu erzeugen. |
