# 5 Datenmodell und Persistenz

## 5.1 Messdaten- und Metadatenmodell

### Entity-Relationship-Diagramm

[ER-Diagramm der Datenbank]

### Sensoren, Kalibrierung, Zeitreihen

**Setup:** Repräsentiert eine hydroponische Anlage

**Node:** Repräsentiert einen physischen Sensorknoten

**Sensor:** Einzelner Sensor (pH, EC, etc.)

**Reading:** Einzelner Messwert mit Timestamp

**CalibrationData:** Kalibrierungsdaten für Sensoren

## 5.2 Speicherung, Abfragen, Aggregationen

### Historie/Trends

[Wie werden historische Daten effizient abgefragt?]

### Aggregationen

[Durchschnitt, Min/Max über Zeiträume]

## 5.3 Datenqualität: Validierung, Plausibilisierung, Versionierung

### Validierung

[Wertebereichs-Checks, Format-Validierung]

### Plausibilisierung

[Erkennung unrealistischer Werte, Sprünge]

### Versionierung

[Schema-Migration, Kompatibilität]
