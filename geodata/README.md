# Geodaten für GeoServer

Legen Sie hier Ihre eigenen Daten ab:
- `*.tif`/`*.tiff` (GeoTIFF) → WMS-Layer `uebung:<Dateiname>`
- table-safe `*.geojson` (Buchstaben, Ziffern, Unterstriche; mit Buchstaben
  beginnend) → WFS-Layer `uebung:<Dateiname>`, SRS=EPSG:4326

`mainz.tif` ist der verpflichtende Raster-Layer `uebung:mainz`. Neue oder
geänderte Dateien werden automatisch vom laufenden `geodata-watcher`
importiert/veröffentlicht und danach automatisch in der Karte angezeigt.
Bindestriche in GeoTIFF-Dateinamen werden im Layernamen durch Unterstriche
ersetzt.

Hinweise:
- Dateien werden read-only in den GeoServer-Container gemountet (`/data`).
- Das Löschen einer Quelldatei entfernt den publizierten Layer bzw. die
  importierte Tabelle nicht automatisch.
- Achten Sie auf das Koordinatenbezugssystem. Für Vektor (WFS) wird EPSG:4326 erwartet.
- Große Raster (> 200 MB) können initial langsamer sein. Bei Bedarf können Sie vorab mit `gdal_translate` Pyramiden und Kompression (z. B. LZW/DEFLATE) anwenden.
