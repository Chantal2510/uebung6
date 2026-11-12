#!/usr/bin/env python3
"""Prepare the local Mainz cafe GeoJSON for Tippecanoe without editing its source."""

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geodata" / "cafeExport.geojson"
DESTINATION = ROOT / "data" / "poi.geojson"
PROPERTY_FIELDS = (
    "cuisine",
    "opening_hours",
    "wheelchair",
    "outdoor_seating",
)


def nonempty(properties: dict, *keys: str) -> str | None:
    for key in keys:
        value = properties.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Die Café-Quelldatei wurde nicht gefunden: {SOURCE}")

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if source.get("type") != "FeatureCollection" or not isinstance(source.get("features"), list):
        raise ValueError("Die Quelldatei ist keine gültige GeoJSON-FeatureCollection.")

    cleaned = []
    longitudes = []
    latitudes = []
    for index, feature in enumerate(source["features"], start=1):
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates")
        if geometry.get("type") != "Point" or not isinstance(coordinates, list) or len(coordinates) < 2:
            raise ValueError(f"Feature {index} ist kein gültiger Punkt.")
        longitude, latitude = coordinates[:2]
        if (
            not isinstance(longitude, (int, float))
            or not isinstance(latitude, (int, float))
            or not math.isfinite(longitude)
            or not math.isfinite(latitude)
            or not -180 <= longitude <= 180
            or not -90 <= latitude <= 90
        ):
            raise ValueError(f"Feature {index} enthält keine gültigen WGS84-Koordinaten.")

        properties = feature.get("properties") or {}
        if properties.get("amenity") != "cafe":
            raise ValueError(f"Feature {index} ist nicht als amenity=cafe gekennzeichnet.")

        cleaned_properties = {
            "name": nonempty(properties, "name", "name:de"),
            "amenity": "cafe",
        }
        for field in PROPERTY_FIELDS:
            value = nonempty(properties, field)
            if value is not None:
                cleaned_properties[field] = value

        website = nonempty(properties, "website", "contact:website")
        if website is not None:
            cleaned_properties["website"] = website

        street = nonempty(properties, "addr:street", "contact:street")
        house_number = nonempty(properties, "addr:housenumber", "contact:housenumber")
        postcode = nonempty(properties, "addr:postcode")
        city = nonempty(properties, "addr:city", "contact:city")
        address_parts = []
        street_line = " ".join(part for part in (street, house_number) if part)
        if street_line:
            address_parts.append(street_line)
        locality = " ".join(part for part in (postcode, city) if part)
        if locality:
            address_parts.append(locality)
        if address_parts:
            cleaned_properties["address"] = ", ".join(address_parts)

        cleaned_feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": cleaned_properties,
        }
        cleaned.append(cleaned_feature)
        longitudes.append(longitude)
        latitudes.append(latitude)

    if not cleaned:
        raise ValueError("Die Quelldatei enthält keine Café-Punkte.")

    output = {
        "type": "FeatureCollection",
        "generator": "prepare_poi.py",
        "copyright": source.get("copyright", "© OpenStreetMap-Mitwirkende, ODbL"),
        "timestamp": source.get("timestamp"),
        "features": cleaned,
    }
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    bounds = (
        min(longitudes),
        min(latitudes),
        max(longitudes),
        max(latitudes),
    )
    fields = sorted({key for feature in cleaned for key in feature["properties"]})
    print(f"Features: {len(cleaned)}")
    print(f"WGS84-Ausdehnung (lon/lat): {bounds}")
    print(f"Ausgabeattribute: {', '.join(fields)}")
    print(f"Geschrieben: {DESTINATION}")


if __name__ == "__main__":
    main()
