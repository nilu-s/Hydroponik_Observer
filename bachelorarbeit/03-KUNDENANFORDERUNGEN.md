# 3.1 Kundenanforderungen (Funktionale Anforderungen)

Diese Anforderungen beschreiben die funktionalen Eigenschaften des Systems aus Anwendersicht.

## Übersicht

| ID | Beschreibung | Priorität | Requirement | Status |
|----|--------------|-----------|-------------|--------|
| CR-01 | Das System soll Hydroponik-Versuchsaufbauten überwachen | MUSS | Gesamtsystem | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-02 | Der pH-Wert der Nährlösung soll überwacht werden | MUSS | pH-Überwachung | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-03 | Die elektrische Leitfähigkeit der Nährlösung soll überwacht werden | MUSS | EC-Überwachung | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-04 | Die Temperatur der Nährlösung soll überwacht werden | MUSS | Temperaturüberwachung | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-05 | Alle Messwerte sollen kalibriert erfasst werden | MUSS | Messgenauigkeit | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-06 | Messwerte sollen automatisch zyklisch erfasst werden | MUSS | Zyklische Messung | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-07 | Das System soll ohne Benutzeroberfläche funktionsfähig sein | SOLL | Minimalbetrieb | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-08 | Messdaten sollen an eine zentrale Einheit übertragen werden | MUSS | Datenübertragung | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-09 | Das System muss mindestens zwei Sensor Nodes parallel betreiben können | MUSS | Multi-Node | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-10 | Kurzzeitige Ausfälle sollen toleriert werden (Auto-Reconnect) | SOLL | Fehlertoleranz | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-11 | Das System soll über längere Zeiträume stabil betrieben werden können | SOLL | Langzeitbetrieb | [NOT-TESTED-YET] |
| CR-12 | Das System soll um weitere Sensor Nodes erweiterbar sein | SOLL | Erweiterbarkeit | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-13 | Messdaten sollen dauerhaft gespeichert werden (persistent) | MUSS | Persistierung | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-14 | Pflanzenzustand soll visuell dokumentiert werden (Kamera) | SOLL | Fotodokumentation | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-15 | Messdaten sollen visuell dargestellt werden (Web-UI) | SOLL | Visualisierung | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-16 | Messdaten sollen exportiert werden können (CSV/ZIP) | MUSS | Datenexport | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-17 | Live-Messwerte sollen in Echtzeit angezeigt werden | SOLL | Echtzeit-Updates | [CODE-ALIGNED] [NOT-TESTED-YET] |
| CR-18 | Das System soll historische Messwerte anzeigen können | SOLL | Historie | [CODE-ALIGNED] [NOT-TESTED-YET] |

## Prioritäten

- **MUSS**: Kritische Anforderungen, die zwingend erfüllt werden müssen
- **SOLL**: Wichtige Anforderungen, die nach Möglichkeit erfüllt werden sollten

## Erfüllungsstatus

- ✅ **Erfüllt**: Anforderung implementiert und getestet
- ⚠️ **Teilweise**: Grundfunktionalität vorhanden, aber mit Einschränkungen
- ❌ **Nicht erfüllt**: Anforderung nicht implementiert
- **[NOT-TESTED-YET]**: Implementiert, aber noch nicht formell verifiziert

## Detaillierte Beschreibung

### CR-01: Überwachung von Hydroponik-Versuchsaufbauten
Das System erfasst Messwerte (pH, EC, Temperatur), speichert sie und stellt sie für Auswertung bereit. Evidence: sensornode-firmware/src/main.cpp :: handleGetAll :: Messwerte werden erzeugt; Evidence: sensorhub-backend/app/db.py :: insert_reading :: Speicherung in SQLite.

### CR-02, CR-03, CR-04: Messwert-Überwachung
Die Firmware erfasst pH, EC und Temperatur und stellt diese Werte dem Hub bereit. Evidence: sensornode-firmware/src/main.cpp :: readPhRaw/readEcRaw/readTempC :: Sensorwerte werden gelesen.

### CR-05: Kalibrierte Messung
Die Firmware unterstützt Kalibrierpunkte für pH (3) und EC (2). Evidence: sensornode-firmware/src/main.cpp :: applyPhCalibration/applyEcCalibration :: Kalibrierfunktionen implementiert.

### CR-06: Automatische zyklische Erfassung
Das Backend erfasst Messwerte zyklisch anhand der pro Setup konfigurierten Intervalle. Evidence: sensorhub-backend/app/realtime_updates.py :: readings_capture_loop :: Intervallbasierte Speicherung.

### CR-07: Minimalbetrieb (ohne UI)
Das Backend kann ohne Web-UI betrieben werden; die Loops laufen serverseitig unabhängig vom Frontend. Evidence: sensorhub-backend/app/main.py :: on_startup :: Hintergrund-Loops starten beim Backend-Start.

### CR-08: Datenübertragung zur zentralen Einheit
Messwerte werden über serielle JSON-Nachrichten an den Hub übertragen. Evidence: sensorhub-backend/app/nodes.py :: NodeClient.send_command :: Serial JSON-Kommunikation.

### CR-09: Multi-Node-Betrieb
Das Backend verwaltet mehrere Nodes parallel über eine serielle Discovery und einen Client-Pool. Evidence: sensorhub-backend/app/nodes.py :: NODE_CLIENTS/node_discovery_loop :: Mehrere Nodes werden parallel verwaltet.

### CR-10: Fehlertoleranz
Die Node sendet bei Verbindungsverlust wiederholt `hello`-Nachrichten, um die Verbindung neu aufzubauen. Evidence: sensornode-firmware/src/main.cpp :: HELLO_RETRY_INTERVAL_MS/sendHello :: Hello-Retry implementiert.

### CR-11: Langzeitbetrieb
Langzeitbetrieb ist vorgesehen, wurde jedoch nicht formell getestet. [NOT-TESTED-YET] Evidence: NONE.

### CR-12: Erweiterbarkeit
Neue Nodes werden über die Discovery erkannt und in der Datenbank registriert. Evidence: sensorhub-backend/app/nodes.py :: _scan_nodes_once/upsert_node :: Automatische Registrierung neuer Nodes.

### CR-13: Persistente Speicherung
Messwerte werden in einer SQLite-Datenbank gespeichert. Evidence: sensorhub-backend/app/db.py :: readings table :: Persistente Speicherung in SQLite.

### CR-14: Fotodokumentation
USB-Kameras können Setups zugeordnet werden; das Backend speichert Fotos in Intervallen. Evidence: sensorhub-backend/app/camera_streaming.py :: photo_capture_loop/_save_frame :: Intervallgesteuerte Fotoablage.

### CR-15: Visualisierung
Eine React-basierte Web-UI visualisiert Live-Daten und Historie. Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: Live-Daten; Evidence: sensorhub-backend/app/api/setups.py :: get_history :: Historien-Endpoint.

### CR-16: Datenexport
Messdaten können als ZIP-Archiv mit CSV-Dateien exportiert werden. Evidence: sensorhub-backend/app/api/setups.py :: export_all :: CSV/ZIP Export.

### CR-17: Echtzeit-Updates
Live-Messwerte werden per WebSocket an das Frontend gesendet. Evidence: sensorhub-backend/app/realtime_updates.py :: LiveManager._build_reading_payload :: WebSocket-Payload; Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: WebSocket-Client.

### CR-18: Historische Daten
Das System stellt historische Messwerte über einen API-Endpoint bereit. Evidence: sensorhub-backend/app/api/setups.py :: get_history :: Historien-Endpoint.
