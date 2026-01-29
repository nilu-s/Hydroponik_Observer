# 8 Laufzeitverhalten und Robustheit

## 8.1 Datenfluss End-to-End

### Messung → Transport → Speicherung → Anzeige

[Sequenzdiagramm des kompletten Datenflusses]

1. Sensor-Node erfasst Messwert
2. Node sendet JSON via HTTP POST
3. Backend validiert und speichert
4. Backend sendet WebSocket-Update
5. Frontend aktualisiert UI

## 8.2 Parallelbetrieb mehrerer Nodes

### Skalierung

[Wie viele Nodes können gleichzeitig betrieben werden?]

### Konflikte

[Gibt es Race-Conditions? Lock-Mechanismen?]

### Timing

[Synchronisation, Clock-Drift]

## 8.3 Ausfalltoleranz

### Disconnects

[Was passiert bei Verbindungsabbruch?]

### Restart

[Recovery nach Backend-/Frontend-Restart]

### Datenlücken

[Wie werden fehlende Messwerte behandelt?]

### Recovery

[Wiederherstellung nach Fehlern]
