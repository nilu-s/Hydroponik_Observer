# 6 Protokolle und API-Design

## 6.1 Kommunikationsprotokolle Sensornode ↔ Hub

### Format

[JSON-Format der Sensordaten]

```json
{
  "node_id": "node-1",
  "timestamp": "2025-01-29T10:30:00Z",
  "readings": [
    {
      "sensor_type": "ph",
      "value": 6.5
    }
  ]
}
```

### Fehlerfälle

[Timeout, Verbindungsabbruch, ungültige Daten]

## 6.2 REST API des Backends

### Ressourcen

- `/api/setups` - Verwaltung von Anlagen
- `/api/nodes` - Verwaltung von Nodes
- `/api/sensors` - Sensor-Konfiguration
- `/api/readings` - Messwerte abrufen
- `/api/calibration` - Kalibrierung

### Endpunkte

[Detaillierte Beschreibung der wichtigsten Endpoints]

### Beispiel-Flows

[Typische Request/Response-Flows]

## 6.3 Konfiguration

### Nodes, Sensoren, Grenzwerte

[Wie werden Konfigurationen verwaltet und persistent gespeichert?]
