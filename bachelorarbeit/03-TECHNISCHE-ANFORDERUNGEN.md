# 3.2 Technische Anforderungen

Diese Anforderungen beschreiben die technische Umsetzung des Systems.

## Übersicht

| ID | Beschreibung | Kategorie |
|----|--------------|-----------|
| TR-01 | Das System besteht aus mindestens einem Sensor-Node | Architektur |
| TR-02 | Der Hub empfängt Messwerte von den Nodes | Architektur |
| TR-03 | Der Hub unterstützt mehrere Sensor-Nodes gleichzeitig | Architektur |
| TR-04 | Jede Node besitzt eine eindeutige ID (Hardware-UID) | Architektur |
| TR-05 | Nodes kommunizieren via serieller Schnittstelle mit dem Hub | Kommunikation |
| TR-08 | Die Sensor-Node erfasst Messwerte lokal | Firmware |
| TR-09 | Die Firmware läuft auf der vorgesehenen Mikrocontroller-Plattform der Sensor-Node | Firmware |
| TR-10 | USB-Kameras werden vom Hub verwaltet (nicht von Nodes) | Backend |
| TR-11 | Messwerte werden mit Zeitstempel versehen | Datenmodell |
| TR-12 | Mess- und Foto-Intervalle sind konfigurierbar | Konfiguration |
| TR-13 | Kalibrierungsdaten werden vom Hub an die Node gesendet und zur Laufzeit angewendet | Firmware |
| TR-14 | Die Firmware unterstützt pH-, EC- und Temperatur-Sensoren | Firmware |
| TR-15 | Die Node unterstützt einen Debug-Modus mit simulierten Werten | Firmware |
| TR-16 | Die Node sendet einen Status-Array im Messpayload (derzeit „ok“) | Fehlerbehandlung |
| TR-17 | Kommunikation erfolgt via JSON-Nachrichten über Serial | Protokoll |
| TR-18 | Messdaten werden im Backend mit Node-ID, Setup-ID, Zeitstempel, pH/EC/Temp und Status gespeichert | Protokoll/Datenmodell |
| TR-19 | Der Hub empfängt und speichert Messwerte | Backend |
| TR-20 | Der Hub führt automatische Node-Discovery durch | Backend |
| TR-21 | Der Hub führt automatische Kamera-Discovery durch | Backend |
| TR-22 | Die Node sendet „hello“-Nachrichten für Auto-Discovery | Protokoll |
| TR-23 | Messdaten werden mit Metadaten (Setup, Node, Status) versehen | Datenmodell |
| TR-24 | Die Firmware verwendet Glättung über mehrere Samples | Firmware |
| TR-25 | Kalibrierdaten sind im Datenmodell enthalten | Datenmodell |
| TR-26 | Die Node unterstützt 3-Punkt-Kalibrierung für pH | Firmware |
| TR-27 | Die Node unterstützt 2-Punkt-Kalibrierung für EC | Firmware |
| TR-29 | Messwerte werden in einer SQLite-Datenbank gespeichert | Backend |
| TR-30 | Es gibt eine REST API zur Abfrage von Messwerten | Backend |
| TR-31 | Eine Web-UI visualisiert Messwerte und Status | Frontend |
| TR-32 | Messdaten können nach Setup und Limit abgefragt werden | Backend |
| TR-33 | Das Backend stellt CSRF-Schutz bereit | Backend/Sicherheit |
| TR-34 | Der Hub verwaltet Kamera-Worker für Video-Streaming | Backend |
| TR-35 | Setups können angelegt/bearbeitet/gelöscht werden (CRUD) | Backend |
| TR-36 | Messwerte können als ZIP mit CSV exportiert werden | Backend |
| TR-37 | Fotos werden automatisch in konfigurierbaren Intervallen gespeichert | Backend |
| TR-38 | Der Hub kann mehrere Setups parallel verwalten | Backend |
| TR-39 | Live-Daten werden über WebSocket an Frontend gesendet | Backend |
| TR-40 | Das Backend führt automatische Readings-Capture in Intervallen durch | Backend |
| TR-41 | Das Backend bietet einen Admin-Reset-Endpoint | Backend |

## Kategorien

### Architektur
Grundlegende Systemstruktur mit Node-Hub-Modell und serieller Kommunikation.

### Firmware
Firmware mit pH/EC/Temperatur, Kalibrierung und Debug-Modus.

### Backend
Backend mit SQLite, REST und WebSocket.

### Frontend
Web-UI für Live-Daten.

### Datenmodell
Messwerte und Kalibrierung sind im Schema modelliert.

### Protokoll
JSON-basiertes Serial-Protokoll mit `hello`, `get_all`, `set_mode`, `set_values`, `set_calib`.

### Kommunikation
- **Node ↔ Hub**: Serielles Protokoll (USB/UART) mit JSON-Nachrichten
- **Hub ↔ Frontend**: REST API (HTTP) und WebSocket für Live-Updates

### Konfiguration
Konfigurierbare Mess- und Foto-Intervalle pro Setup; Node-Modus über API steuerbar.

### Fehlerbehandlung
- Node: Automatisches Hello-Retry bei Verbindungsverlust.
- Hub: Node-Status-Tracking und Fehler-Logging.

### Sicherheit
CSRF-Schutz via Token/Origin-Check; Admin-Reset mit Token.

## Trace-Matrix: CR → TR

Diese Matrix zeigt, welche technischen Anforderungen welche funktionalen Anforderungen umsetzen:

| Customer Requirement | Technical Requirements |
|---------------------|------------------------|
| CR-01 (Gesamtsystem) | TR-01, TR-02, TR-03, TR-04, TR-20, TR-38 |
| CR-02 (pH-Überwachung) | TR-08, TR-09, TR-14, TR-18, TR-26, TR-29 |
| CR-03 (EC-Überwachung) | TR-08, TR-09, TR-14, TR-18, TR-27, TR-29 |
| CR-04 (Temperatur) | TR-08, TR-09, TR-14, TR-18, TR-29 |
| CR-05 (Kalibrierung) | TR-13, TR-25, TR-26, TR-27 |
| CR-06 (Zyklische Messung) | TR-08, TR-12, TR-40 |
| CR-07 (Minimalbetrieb) | TR-19, TR-29, TR-40 |
| CR-08 (Datenübertragung) | TR-05, TR-17, TR-18, TR-22 |
| CR-09 (Multi-Node) | TR-03, TR-20 |
| CR-10 (Fehlertoleranz) | TR-16, TR-22 |
| CR-11 (Langzeitbetrieb) | TR-24, TR-29, TR-40 |
| CR-12 (Erweiterbarkeit) | TR-03, TR-04, TR-20, TR-22 |
| CR-13 (Persistenz) | TR-29 |
| CR-14 (Fotos) | TR-10, TR-21, TR-34, TR-37 |
| CR-15 (Visualisierung) | TR-31, TR-39 |
| CR-16 (Export) | TR-36 |
| CR-17 (Echtzeit-Updates) | TR-39 |
| CR-18 (Historie) | TR-29, TR-32 |
*** End of File

Diese Anforderungen beschreiben die technische Umsetzung des Systems.

## Übersicht

| ID | Beschreibung | Kategorie |
|----|--------------|-----------|
| TR-01 | Das System besteht aus mindestens einem Sensor-Node | Architektur |
| TR-02 | Der Hub empfängt Messwerte von den Nodes | Architektur |
| TR-03 | Der Hub unterstützt mehrere Sensor-Nodes gleichzeitig | Architektur |
| TR-04 | Jede Node besitzt eine eindeutige ID (Hardware-UID) | Architektur |
| TR-05 | Nodes kommunizieren via serieller Schnittstelle mit dem Hub | Kommunikation |
| TR-08 | Die Sensor-Node erfasst Messwerte lokal | Firmware |
| TR-09 | Die Firmware läuft auf der vorgesehenen Mikrocontroller-Plattform der Sensor-Node | Firmware |
| TR-10 | USB-Kameras werden vom Hub verwaltet (nicht von Nodes) | Backend |
| TR-11 | Messwerte werden mit Zeitstempel versehen | Datenmodell |
| TR-12 | Mess- und Foto-Intervalle sind konfigurierbar | Konfiguration |
| TR-13 | Kalibrierungsdaten werden vom Hub an die Node gesendet und zur Laufzeit angewendet | Firmware |
| TR-14 | Die Firmware unterstützt pH-, EC- und Temperatur-Sensoren | Firmware |
| TR-15 | Die Node unterstützt einen Debug-Modus mit simulierten Werten | Firmware |
| TR-16 | Die Node sendet einen Status-Array im Messpayload (derzeit „ok“) | Fehlerbehandlung |
| TR-17 | Kommunikation erfolgt via JSON-Nachrichten über Serial | Protokoll |
| TR-18 | Messdaten werden im Backend mit Node-ID, Setup-ID, Zeitstempel, pH/EC/Temp und Status gespeichert | Protokoll/Datenmodell |
| TR-19 | Der Hub empfängt und speichert Messwerte | Backend |
| TR-20 | Der Hub führt automatische Node-Discovery durch | Backend |
| TR-21 | Der Hub führt automatische Kamera-Discovery durch | Backend |
| TR-22 | Die Node sendet „hello“-Nachrichten für Auto-Discovery | Protokoll |
| TR-23 | Messdaten werden mit Metadaten (Setup, Node, Status) versehen | Datenmodell |
| TR-24 | Die Firmware verwendet Glättung über mehrere Samples | Firmware |
| TR-25 | Kalibrierdaten sind im Datenmodell enthalten | Datenmodell |
| TR-26 | Die Node unterstützt 3-Punkt-Kalibrierung für pH | Firmware |
| TR-27 | Die Node unterstützt 2-Punkt-Kalibrierung für EC | Firmware |
| TR-29 | Messwerte werden in einer SQLite-Datenbank gespeichert | Backend |
| TR-30 | Es gibt eine REST API zur Abfrage von Messwerten | Backend |
| TR-31 | Eine Web-UI visualisiert Messwerte und Status | Frontend |
| TR-32 | Messdaten können nach Setup und Limit abgefragt werden | Backend |
| TR-33 | Das Backend stellt CSRF-Schutz bereit | Backend/Sicherheit |
| TR-34 | Der Hub verwaltet Kamera-Worker für Video-Streaming | Backend |
| TR-35 | Setups können angelegt/bearbeitet/gelöscht werden (CRUD) | Backend |
| TR-36 | Messwerte können als ZIP mit CSV exportiert werden | Backend |
| TR-37 | Fotos werden automatisch in konfigurierbaren Intervallen gespeichert | Backend |
| TR-38 | Der Hub kann mehrere Setups parallel verwalten | Backend |
| TR-39 | Live-Daten werden über WebSocket an Frontend gesendet | Backend |
| TR-40 | Das Backend führt automatische Readings-Capture in Intervallen durch | Backend |
| TR-41 | Das Backend bietet einen Admin-Reset-Endpoint | Backend |

## Kategorien

### Architektur
Grundlegende Systemstruktur mit Node-Hub-Modell und serieller Kommunikation.

### Firmware
Firmware mit pH/EC/Temperatur, Kalibrierung und Debug-Modus.

### Backend
Backend mit SQLite, REST und WebSocket.

### Frontend
Web-UI für Live-Daten.

### Datenmodell
Messwerte und Kalibrierung sind im Schema modelliert.

### Protokoll
JSON-basiertes Serial-Protokoll mit `hello`, `get_all`, `set_mode`, `set_values`, `set_calib`.

### Kommunikation
- **Node ↔ Hub**: Serielles Protokoll (USB/UART) mit JSON-Nachrichten
- **Hub ↔ Frontend**: REST API (HTTP) und WebSocket für Live-Updates

### Konfiguration
Konfigurierbare Mess- und Foto-Intervalle pro Setup; Node-Modus über API steuerbar.

### Fehlerbehandlung
- Node: Automatisches Hello-Retry bei Verbindungsverlust.
- Hub: Node-Status-Tracking und Fehler-Logging.

### Sicherheit
CSRF-Schutz via Token/Origin-Check; Admin-Reset mit Token.

## Trace-Matrix: CR → TR

Diese Matrix zeigt, welche technischen Anforderungen welche funktionalen Anforderungen umsetzen:

| Customer Requirement | Technical Requirements |
|---------------------|------------------------|
| CR-01 (Gesamtsystem) | TR-01, TR-02, TR-03, TR-04, TR-20, TR-38 |
| CR-02 (pH-Überwachung) | TR-08, TR-09, TR-14, TR-18, TR-26, TR-29 |
| CR-03 (EC-Überwachung) | TR-08, TR-09, TR-14, TR-18, TR-27, TR-29 |
| CR-04 (Temperatur) | TR-08, TR-09, TR-14, TR-18, TR-29 |
| CR-05 (Kalibrierung) | TR-13, TR-25, TR-26, TR-27 |
| CR-06 (Zyklische Messung) | TR-08, TR-12, TR-40 |
| CR-07 (Minimalbetrieb) | TR-19, TR-29, TR-40 |
| CR-08 (Datenübertragung) | TR-05, TR-17, TR-18, TR-22 |
| CR-09 (Multi-Node) | TR-03, TR-20 |
| CR-10 (Fehlertoleranz) | TR-16, TR-22 |
| CR-11 (Langzeitbetrieb) | TR-24, TR-29, TR-40 |
| CR-12 (Erweiterbarkeit) | TR-03, TR-04, TR-20, TR-22 |
| CR-13 (Persistenz) | TR-29 |
| CR-14 (Fotos) | TR-10, TR-21, TR-34, TR-37 |
| CR-15 (Visualisierung) | TR-31, TR-39 |
| CR-16 (Export) | TR-36 |
| CR-17 (Echtzeit-Updates) | TR-39 |
| CR-18 (Historie) | TR-29, TR-32 |
*** End of File

## Übersicht

| ID | Beschreibung | Kategorie |
|----|--------------|-----------|
| TR-01 | Das System besteht aus mindestens einem Sensor-Node | Architektur |
| TR-02 | Der Hub empfängt Messwerte von den Nodes | Architektur |
| TR-03 | Der Hub unterstützt mehrere Sensor-Nodes gleichzeitig | Architektur |
| TR-04 | Jede Node besitzt eine eindeutige ID (Hardware-UID) | Architektur |
| TR-05 | Nodes kommunizieren via serieller Schnittstelle mit dem Hub | Kommunikation |
| TR-08 | Die Sensor-Node erfasst Messwerte lokal | Firmware |
| TR-09 | Die Firmware läuft auf der vorgesehenen Mikrocontroller-Plattform der Sensor-Node | Firmware |
| TR-10 | USB-Kameras werden vom Hub verwaltet (nicht von Nodes) | Backend |
| TR-11 | Messwerte werden mit Zeitstempel versehen | Datenmodell |
| TR-12 | Mess- und Foto-Intervalle sind konfigurierbar | Konfiguration |
| TR-13 | Kalibrierungsdaten werden vom Hub an die Node gesendet und zur Laufzeit angewendet | Firmware |
| TR-14 | Die Firmware unterstützt pH-, EC- und Temperatur-Sensoren | Firmware |
| TR-15 | Die Node unterstützt einen Debug-Modus mit simulierten Werten | Firmware |
| TR-16 | Die Node sendet einen Status-Array im Messpayload (derzeit „ok“) | Fehlerbehandlung |
| TR-17 | Kommunikation erfolgt via JSON-Nachrichten über Serial | Protokoll |
| TR-18 | Messdaten werden im Backend mit Node-ID, Setup-ID, Zeitstempel, pH/EC/Temp und Status gespeichert | Protokoll/Datenmodell |
| TR-19 | Der Hub empfängt und speichert Messwerte | Backend |
| TR-20 | Der Hub führt automatische Node-Discovery durch | Backend |
| TR-21 | Der Hub führt automatische Kamera-Discovery durch | Backend |
| TR-22 | Die Node sendet „hello“-Nachrichten für Auto-Discovery | Protokoll |
| TR-23 | Messdaten werden mit Metadaten (Setup, Node, Status) versehen | Datenmodell |
| TR-24 | Die Firmware verwendet Glättung über mehrere Samples | Firmware |
| TR-25 | Kalibrierdaten sind im Datenmodell enthalten | Datenmodell |
| TR-26 | Die Node unterstützt 3-Punkt-Kalibrierung für pH | Firmware |
| TR-27 | Die Node unterstützt 2-Punkt-Kalibrierung für EC | Firmware |
| TR-29 | Messwerte werden in einer SQLite-Datenbank gespeichert | Backend |
| TR-30 | Es gibt eine REST API zur Abfrage von Messwerten | Backend |
| TR-31 | Eine Web-UI visualisiert Messwerte und Status | Frontend |
| TR-32 | Messdaten können nach Setup und Limit abgefragt werden | Backend |
| TR-33 | Das Backend stellt CSRF-Schutz bereit | Backend/Sicherheit |
| TR-34 | Der Hub verwaltet Kamera-Worker für Video-Streaming | Backend |
| TR-35 | Setups können angelegt/bearbeitet/gelöscht werden (CRUD) | Backend |
| TR-36 | Messwerte können als ZIP mit CSV exportiert werden | Backend |
| TR-37 | Fotos werden automatisch in konfigurierbaren Intervallen gespeichert | Backend |
| TR-38 | Der Hub kann mehrere Setups parallel verwalten | Backend |
| TR-39 | Live-Daten werden über WebSocket an Frontend gesendet | Backend |
| TR-40 | Das Backend führt automatische Readings-Capture in Intervallen durch | Backend |
| TR-41 | Das Backend bietet einen Admin-Reset-Endpoint | Backend |

## Kategorien

### Architektur
Grundlegende Systemstruktur mit Node-Hub-Modell und serieller Kommunikation.

### Firmware
Firmware mit pH/EC/Temperatur, Kalibrierung und Debug-Modus.

### Backend
FastAPI-Backend mit SQLite, REST und WebSocket.

### Frontend
React/TypeScript UI für Live-Daten.

### Datenmodell
Messwerte und Kalibrierung sind im SQLite-Schema modelliert.

### Protokoll
JSON-basiertes Serial-Protokoll mit `hello`, `get_all`, `set_mode`, `set_values`, `set_calib`.

### Kommunikation
- **Node ↔ Hub**: Serielles Protokoll (USB/UART) mit JSON-Nachrichten
- **Hub ↔ Frontend**: REST API (HTTP) und WebSocket für Live-Updates

### Konfiguration
Konfigurierbare Mess- und Foto-Intervalle pro Setup; Node-Modus über API steuerbar.

### Fehlerbehandlung
- Node: Automatisches Hello-Retry bei Verbindungsverlust.
- Hub: Node-Status-Tracking und Fehler-Logging.

### Sicherheit
CSRF-Schutz via Token/Origin-Check; Admin-Reset mit Token.

## Trace-Matrix: CR → TR

Diese Matrix zeigt, welche technischen Anforderungen welche funktionalen Anforderungen umsetzen:

| Customer Requirement | Technical Requirements |
|---------------------|------------------------|
| CR-01 (Gesamtsystem) | TR-01, TR-02, TR-03, TR-04, TR-20, TR-38 |
| CR-02 (pH-Überwachung) | TR-08, TR-09, TR-14, TR-18, TR-26, TR-29 |
| CR-03 (EC-Überwachung) | TR-08, TR-09, TR-14, TR-18, TR-27, TR-29 |
| CR-04 (Temperatur) | TR-08, TR-09, TR-14, TR-18, TR-29 |
| CR-05 (Kalibrierung) | TR-13, TR-25, TR-26, TR-27 |
| CR-06 (Zyklische Messung) | TR-08, TR-12, TR-40 |
| CR-07 (Minimalbetrieb) | TR-19, TR-29, TR-40 |
| CR-08 (Datenübertragung) | TR-05, TR-17, TR-18, TR-22 |
| CR-09 (Multi-Node) | TR-03, TR-20 |
| CR-10 (Fehlertoleranz) | TR-16, TR-22 |
| CR-11 (Langzeitbetrieb) | TR-24, TR-29, TR-40 |
| CR-12 (Erweiterbarkeit) | TR-03, TR-04, TR-20, TR-22 |
| CR-13 (Persistenz) | TR-29 |
| CR-14 (Fotos) | TR-10, TR-21, TR-34, TR-37 |
| CR-15 (Visualisierung) | TR-31, TR-39 |
| CR-16 (Export) | TR-36 |
| CR-17 (Echtzeit-Updates) | TR-39 |
| CR-18 (Historie) | TR-29, TR-32 |

# 3.2 Technische Anforderungen

Diese Anforderungen beschreiben die technische Umsetzung des Systems.

## Übersicht

| ID | Beschreibung | Kategorie | Status | Evidence |
|----|--------------|-----------|--------|----------|
| TR-01 | Das System besteht aus mindestens einem Sensor-Node | Architektur | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: NODE_CLIENTS :: Node-Verwaltung im Backend. |
| TR-02 | Der Hub empfängt Messwerte von den Nodes | Architektur | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: fetch_node_reading :: Messwerte werden vom Node angefordert. |
| TR-03 | Der Hub unterstützt mehrere Sensor-Nodes gleichzeitig | Architektur | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: NODE_CLIENTS :: Mehrere Clients parallel. |
| TR-04 | Jede Node besitzt eine eindeutige ID (Hardware-UID) | Architektur | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: readBoardUid :: UID aus Flash. |
| TR-05 | Nodes kommunizieren via serieller Schnittstelle mit dem Hub | Kommunikation | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: serial.Serial :: USB-Serial-Kommunikation. |
| TR-08 | Die Sensor-Node erfasst Messwerte lokal | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: readPhRaw/readEcRaw/readTempC :: Lokale Messwerterfassung. |
| TR-09 | Die Firmware läuft auf der vorgesehenen Mikrocontroller-Plattform der Sensor-Node | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: FW_VERSION :: Firmware-Version "pico-0.1.0". |
| TR-10 | USB-Kameras werden vom Hub verwaltet (nicht von Nodes) | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/camera_devices.py :: camera_discovery_loop :: Kamera-Discovery im Backend. |
| TR-11 | Messwerte werden mit Zeitstempel versehen | Datenmodell | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: _request_node_reading :: Backend ergänzt ts in ms. |
| TR-12 | Mess- und Foto-Intervalle sind konfigurierbar | Konfiguration | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: update_setup :: valueIntervalMinutes/photoIntervalMinutes. |
| TR-13 | Kalibrierungsdaten werden vom Hub an die Node gesendet und zur Laufzeit angewendet | Firmware | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: sync_calibration :: set_calib an Node; Firmware: handleSetCalib. |
| TR-14 | Die Firmware unterstützt pH-, EC- und Temperatur-Sensoren | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: readPhRaw/readEcRaw/readTempC :: Sensorfunktionen. |
| TR-15 | Die Node unterstützt einen Debug-Modus mit simulierten Werten | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: handleSetMode/updateDebugValues :: Debug-Modus. |
| TR-16 | Die Node sendet einen Status-Array im Messpayload (derzeit „ok“) | Fehlerbehandlung | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: handleGetAll :: status=["ok"]. |
| TR-17 | Kommunikation erfolgt via JSON-Nachrichten über Serial | Protokoll | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: send_command :: JSON-Line über Serial. |
| TR-18 | Messdaten werden im Backend mit Node-ID, Setup-ID, Zeitstempel, pH/EC/Temp und Status gespeichert | Protokoll/Datenmodell | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: insert_reading :: Speicherung mit setup_id/node_id/ts/ph/ec/temp/status. |
| TR-19 | Der Hub empfängt und speichert Messwerte | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/api/setups.py :: capture_reading :: Lesen und Speichern. |
| TR-20 | Der Hub führt automatische Node-Discovery durch | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: node_discovery_loop :: Periodischer Scan. |
| TR-21 | Der Hub führt automatische Kamera-Discovery durch | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/camera_devices.py :: camera_discovery_loop :: Periodischer Scan. |
| TR-22 | Die Node sendet „hello“-Nachrichten für Auto-Discovery | Protokoll | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: sendHello/HELLO_RETRY_INTERVAL_MS :: Hello-Retry. |
| TR-23 | Messdaten werden mit Metadaten (Setup, Node, Status) versehen | Datenmodell | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: readings table :: setup_id/node_id/status_json. |
| TR-24 | Die Firmware verwendet Glättung über mehrere Samples | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: computeSmoothed :: Smoothing-Funktion. |
| TR-25 | Kalibrierdaten sind im Datenmodell enthalten | Datenmodell | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: calibration table :: Kalibrierung in SQLite. |
| TR-26 | Die Node unterstützt 3-Punkt-Kalibrierung für pH | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: calibration.phPoints[3] :: 3-Punkt pH. |
| TR-27 | Die Node unterstützt 2-Punkt-Kalibrierung für EC | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: calibration.ecPoints[2] :: 2-Punkt EC. |
| TR-29 | Messwerte werden in einer SQLite-Datenbank gespeichert | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: init_db/readings :: SQLite. |
| TR-30 | Es gibt eine REST API zur Abfrage von Messwerten | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/api/setups.py :: get_reading/get_history :: REST-Endpunkte. |
| TR-31 | Eine Web-UI visualisiert Messwerte und Status | Frontend | [CODE-ALIGNED] | Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: Live-Daten für UI. |
| TR-32 | Messdaten können nach Setup und Limit abgefragt werden | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: list_readings(limit) :: Setup-Filter mit Limit. |
| TR-33 | Das Backend stellt CSRF-Schutz bereit | Backend/Sicherheit | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/main.py :: csrf_protect :: CSRF-Token/Origin-Check. |
| TR-34 | Der Hub verwaltet Kamera-Worker für Video-Streaming | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/camera_worker_manager.py :: CameraWorkerManager :: Worker-Verwaltung. |
| TR-35 | Setups können angelegt/bearbeitet/gelöscht werden (CRUD) | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/api/setups.py :: get/post/patch/delete :: CRUD-Endpunkte. |
| TR-36 | Messwerte können als ZIP mit CSV exportiert werden | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/api/setups.py :: export_all :: CSV/ZIP Export. |
| TR-37 | Fotos werden automatisch in konfigurierbaren Intervallen gespeichert | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/camera_streaming.py :: photo_capture_loop :: Intervall-Fotoaufnahme. |
| TR-38 | Der Hub kann mehrere Setups parallel verwalten | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: list_setups :: Mehrere Setups. |
| TR-39 | Live-Daten werden über WebSocket an Frontend gesendet | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/realtime_updates.py :: LiveManager :: WebSocket-Broadcast. |
| TR-40 | Das Backend führt automatische Readings-Capture in Intervallen durch | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/realtime_updates.py :: readings_capture_loop :: Intervall-Capture. |
| TR-41 | Das Backend bietet einen Admin-Reset-Endpoint | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/api/admin.py :: reset_db :: Reset-Endpoint. |

## Kategorien

### Architektur
Grundlegende Systemstruktur mit Node-Hub-Modell und serieller Kommunikation. Evidence: sensorhub-backend/app/nodes.py :: NodeClient :: Serial-Node-Kommunikation.

### Firmware
Firmware mit pH/EC/Temperatur, Kalibrierung und Debug-Modus. Evidence: sensornode-firmware/src/main.cpp :: applyPhCalibration/applyEcCalibration/handleSetMode :: Kalibrierung und Debug-Modus.

### Backend
FastAPI-Backend mit SQLite, REST und WebSocket. Evidence: sensorhub-backend/app/main.py :: FastAPI app + /api/live :: API und WebSocket.

### Frontend
React/TypeScript UI für Live-Daten. Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: WebSocket-Client.

### Datenmodell
Messwerte und Kalibrierung sind im SQLite-Schema modelliert. Evidence: sensorhub-backend/app/db.py :: readings/calibration tables :: Datenmodell-Tabellen.

### Protokoll
JSON-basiertes Serial-Protokoll mit `hello`, `get_all`, `set_mode`, `set_values`, `set_calib`. Evidence: sensornode-firmware/src/main.cpp :: handleMessage :: Nachrichten-Typen implementiert.

### Kommunikation
- **Node ↔ Hub**: Serielles Protokoll (USB/UART) mit JSON-Nachrichten
- **Hub ↔ Frontend**: REST API (HTTP) und WebSocket für Live-Updates
Evidence: sensorhub-backend/app/nodes.py :: serial.Serial :: Node ↔ Hub; Evidence: sensorhub-backend/app/main.py :: /api/live :: Hub ↔ Frontend.

### Konfiguration
Konfigurierbare Mess- und Foto-Intervalle pro Setup; Node-Modus über API steuerbar. Evidence: sensorhub-backend/app/api/setups.py :: patch_setup :: Intervalle; Evidence: sensorhub-backend/app/api/nodes.py :: post_node_command :: set_mode.

### Fehlerbehandlung
- Node: Automatisches Hello-Retry bei Verbindungsverlust. Evidence: sensornode-firmware/src/main.cpp :: HELLO_RETRY_INTERVAL_MS :: Retry-Mechanismus.
- Hub: Node-Status-Tracking und Fehler-Logging. Evidence: sensorhub-backend/app/nodes.py :: mark_nodes_offline/log_event :: Offline-Markierung und Logging.

### Sicherheit
CSRF-Schutz via Token/Origin-Check; Admin-Reset mit Token. Evidence: sensorhub-backend/app/main.py :: csrf_protect :: CSRF; Evidence: sensorhub-backend/app/api/admin.py :: reset_db :: Reset-Token.

## Trace-Matrix: CR → TR

Diese Matrix zeigt, welche technischen Anforderungen welche funktionalen Anforderungen umsetzen:

| Customer Requirement | Technical Requirements |
|---------------------|------------------------|
| CR-01 (Gesamtsystem) | TR-01, TR-02, TR-03, TR-04, TR-20, TR-38 |
| CR-02 (pH-Überwachung) | TR-08, TR-09, TR-14, TR-18, TR-26, TR-29 |
| CR-03 (EC-Überwachung) | TR-08, TR-09, TR-14, TR-18, TR-27, TR-29 |
| CR-04 (Temperatur) | TR-08, TR-09, TR-14, TR-18, TR-29 |
| CR-05 (Kalibrierung) | TR-13, TR-25, TR-26, TR-27 |
| CR-06 (Zyklische Messung) | TR-08, TR-12, TR-40 |
| CR-07 (Minimalbetrieb) | TR-19, TR-29, TR-40 |
| CR-08 (Datenübertragung) | TR-05, TR-17, TR-18, TR-22 |
| CR-09 (Multi-Node) | TR-03, TR-20 |
| CR-10 (Fehlertoleranz) | TR-16, TR-22 |
| CR-11 (Langzeitbetrieb) | TR-24, TR-29, TR-40 |
| CR-12 (Erweiterbarkeit) | TR-03, TR-04, TR-20, TR-22 |
| CR-13 (Persistenz) | TR-29 |
| CR-14 (Fotos) | TR-10, TR-21, TR-34, TR-37 |
| CR-15 (Visualisierung) | TR-31, TR-39 |
| CR-16 (Export) | TR-36 |
| CR-17 (Echtzeit-Updates) | TR-39 |
| CR-18 (Historie) | TR-29, TR-32 |

## Wichtige Implementierungshinweise

### Hardware-Plattform
Die Sensor-Nodes basieren auf der vorgesehenen Mikrocontroller-Plattform und kommunizieren über USB-Serial mit dem Hub.
Evidence: sensornode-firmware/src/main.cpp :: FW_VERSION :: Pico-Firmware; Evidence: sensorhub-backend/app/nodes.py :: serial.Serial :: USB-Serial-Kommunikation.

### Kommunikationsprotokoll
Die Kommunikation zwischen Node und Hub erfolgt über ein **JSON-basiertes serielles Protokoll**. Es gibt KEIN HTTP/WLAN auf der Node-Ebene.
Evidence: sensornode-firmware/src/main.cpp :: sendJson/handleMessage :: JSON-Serial-Protokoll.

### Kamera-Verwaltung
USB-Kameras werden vom **Hub (Backend)** verwaltet, nicht von den Sensor-Nodes. Das Backend führt automatische Kamera-Discovery durch und steuert Foto-Capture und Video-Streaming.
Evidence: sensorhub-backend/app/camera_devices.py :: camera_discovery_loop :: Kamera-Discovery; Evidence: sensorhub-backend/app/camera_streaming.py :: stream_camera/capture_photo_now :: Streaming und Foto-Capture.

### Kalibrierung
- **pH**: 3-Punkt-Kalibrierung (0V→0pH, 1.65V→7pH, 3.3V→14pH)
- **EC**: 2-Punkt-Kalibrierung (linear)
- Kalibrierungsdaten werden vom Hub an die Node gesendet und zur Laufzeit angewendet.
Evidence: sensornode-firmware/src/main.cpp :: applyPhCalibration/applyEcCalibration :: Kalibrierung in Firmware; Evidence: sensorhub-backend/app/nodes.py :: sync_calibration :: Übertragung der Kalibrierung.

### Auto-Discovery
Nodes senden automatisch `hello`-Nachrichten beim Start und bei Verbindungsverlust. Der Hub erkennt neue Nodes automatisch und registriert sie in der Datenbank.
Evidence: sensornode-firmware/src/main.cpp :: sendHello :: Hello-Mechanismus; Evidence: sensorhub-backend/app/nodes.py :: _scan_nodes_once/upsert_node :: Registrierung in DB.
# 3.2 Technische Anforderungen

Diese Anforderungen beschreiben die technische Umsetzung des Systems.

## Übersicht

| ID | Beschreibung | Kategorie | Status | Evidence |
|----|--------------|-----------|--------|----------|
| TR-01 | Das System besteht aus mindestens einem Sensor-Node | Architektur | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: NODE_CLIENTS :: Node-Verwaltung im Backend. |
| TR-02 | Der Hub empfängt Messwerte von den Nodes | Architektur | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: fetch_node_reading :: Messwerte werden vom Node angefordert. |
| TR-03 | Der Hub unterstützt mehrere Sensor-Nodes gleichzeitig | Architektur | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: NODE_CLIENTS :: Mehrere Clients parallel. |
| TR-04 | Jede Node besitzt eine eindeutige ID (Hardware-UID) | Architektur | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: readBoardUid :: UID aus Flash. |
| TR-05 | Nodes kommunizieren via serieller Schnittstelle mit dem Hub | Kommunikation | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: serial.Serial :: USB-Serial-Kommunikation. |
| TR-08 | Die Sensor-Node erfasst Messwerte lokal | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: readPhRaw/readEcRaw/readTempC :: Lokale Messwerterfassung. |
| TR-09 | Die Firmware läuft auf der vorgesehenen Mikrocontroller-Plattform der Sensor-Node | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: FW_VERSION :: Firmware-Version "pico-0.1.0". |
| TR-10 | USB-Kameras werden vom Hub verwaltet (nicht von Nodes) | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/camera_devices.py :: camera_discovery_loop :: Kamera-Discovery im Backend. |
| TR-11 | Messwerte werden mit Zeitstempel versehen | Datenmodell | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: _request_node_reading :: Backend ergänzt ts in ms. |
| TR-12 | Mess- und Foto-Intervalle sind konfigurierbar | Konfiguration | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: update_setup :: valueIntervalMinutes/photoIntervalMinutes. |
| TR-13 | Kalibrierungsdaten werden vom Hub an die Node gesendet und zur Laufzeit angewendet | Firmware | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: sync_calibration :: set_calib an Node; Firmware: handleSetCalib. |
| TR-14 | Die Firmware unterstützt pH-, EC- und Temperatur-Sensoren | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: readPhRaw/readEcRaw/readTempC :: Sensorfunktionen. |
| TR-15 | Die Node unterstützt einen Debug-Modus mit simulierten Werten | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: handleSetMode/updateDebugValues :: Debug-Modus. |
| TR-16 | Die Node sendet einen Status-Array im Messpayload (derzeit „ok“) | Fehlerbehandlung | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: handleGetAll :: status=["ok"]. |
| TR-17 | Kommunikation erfolgt via JSON-Nachrichten über Serial | Protokoll | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: send_command :: JSON-Line über Serial. |
| TR-18 | Messdaten werden im Backend mit Node-ID, Setup-ID, Zeitstempel, pH/EC/Temp und Status gespeichert | Protokoll/Datenmodell | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: insert_reading :: Speicherung mit setup_id/node_id/ts/ph/ec/temp/status. |
| TR-19 | Der Hub empfängt und speichert Messwerte | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/api/setups.py :: capture_reading :: Lesen und Speichern. |
| TR-20 | Der Hub führt automatische Node-Discovery durch | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/nodes.py :: node_discovery_loop :: Periodischer Scan. |
| TR-21 | Der Hub führt automatische Kamera-Discovery durch | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/camera_devices.py :: camera_discovery_loop :: Periodischer Scan. |
| TR-22 | Die Node sendet „hello“-Nachrichten für Auto-Discovery | Protokoll | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: sendHello/HELLO_RETRY_INTERVAL_MS :: Hello-Retry. |
| TR-23 | Messdaten werden mit Metadaten (Setup, Node, Status) versehen | Datenmodell | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: readings table :: setup_id/node_id/status_json. |
| TR-24 | Die Firmware verwendet Glättung über mehrere Samples | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: computeSmoothed :: Smoothing-Funktion. |
| TR-25 | Kalibrierdaten sind im Datenmodell enthalten | Datenmodell | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: calibration table :: Kalibrierung in SQLite. |
| TR-26 | Die Node unterstützt 3-Punkt-Kalibrierung für pH | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: calibration.phPoints[3] :: 3-Punkt pH. |
| TR-27 | Die Node unterstützt 2-Punkt-Kalibrierung für EC | Firmware | [CODE-ALIGNED] | Evidence: sensornode-firmware/src/main.cpp :: calibration.ecPoints[2] :: 2-Punkt EC. |
| TR-29 | Messwerte werden in einer SQLite-Datenbank gespeichert | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: init_db/readings :: SQLite. |
| TR-30 | Es gibt eine REST API zur Abfrage von Messwerten | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/api/setups.py :: get_reading/get_history :: REST-Endpunkte. |
| TR-31 | Eine Web-UI visualisiert Messwerte und Status | Frontend | [CODE-ALIGNED] | Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: Live-Daten für UI. |
| TR-32 | Messdaten können nach Setup und Limit abgefragt werden | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: list_readings(limit) :: Setup-Filter mit Limit. |
| TR-33 | Das Backend stellt CSRF-Schutz bereit | Backend/Sicherheit | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/main.py :: csrf_protect :: CSRF-Token/Origin-Check. |
| TR-34 | Der Hub verwaltet Kamera-Worker für Video-Streaming | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/camera_worker_manager.py :: CameraWorkerManager :: Worker-Verwaltung. |
| TR-35 | Setups können angelegt/bearbeitet/gelöscht werden (CRUD) | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/api/setups.py :: get/post/patch/delete :: CRUD-Endpunkte. |
| TR-36 | Messwerte können als ZIP mit CSV exportiert werden | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/api/setups.py :: export_all :: CSV/ZIP Export. |
| TR-37 | Fotos werden automatisch in konfigurierbaren Intervallen gespeichert | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/camera_streaming.py :: photo_capture_loop :: Intervall-Fotoaufnahme. |
| TR-38 | Der Hub kann mehrere Setups parallel verwalten | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/db.py :: list_setups :: Mehrere Setups. |
| TR-39 | Live-Daten werden über WebSocket an Frontend gesendet | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/realtime_updates.py :: LiveManager :: WebSocket-Broadcast. |
| TR-40 | Das Backend führt automatische Readings-Capture in Intervallen durch | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/realtime_updates.py :: readings_capture_loop :: Intervall-Capture. |
| TR-41 | Das Backend bietet einen Admin-Reset-Endpoint | Backend | [CODE-ALIGNED] | Evidence: sensorhub-backend/app/api/admin.py :: reset_db :: Reset-Endpoint. |

## Kategorien

### Architektur
Grundlegende Systemstruktur mit Node-Hub-Modell und serieller Kommunikation. Evidence: sensorhub-backend/app/nodes.py :: NodeClient :: Serial-Node-Kommunikation.

### Firmware
Firmware mit pH/EC/Temperatur, Kalibrierung und Debug-Modus. Evidence: sensornode-firmware/src/main.cpp :: applyPhCalibration/applyEcCalibration/handleSetMode :: Kalibrierung und Debug-Modus.

### Backend
FastAPI-Backend mit SQLite, REST und WebSocket. Evidence: sensorhub-backend/app/main.py :: FastAPI app + /api/live :: API und WebSocket.

### Frontend
React/TypeScript UI für Live-Daten. Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: WebSocket-Client.

### Datenmodell
Messwerte und Kalibrierung sind im SQLite-Schema modelliert. Evidence: sensorhub-backend/app/db.py :: readings/calibration tables :: Datenmodell-Tabellen.

### Protokoll
JSON-basiertes Serial-Protokoll mit `hello`, `get_all`, `set_mode`, `set_values`, `set_calib`. Evidence: sensornode-firmware/src/main.cpp :: handleMessage :: Nachrichten-Typen implementiert.

### Kommunikation
- **Node ↔ Hub**: Serielles Protokoll (USB/UART) mit JSON-Nachrichten
- **Hub ↔ Frontend**: REST API (HTTP) und WebSocket für Live-Updates
Evidence: sensorhub-backend/app/nodes.py :: serial.Serial :: Node ↔ Hub; Evidence: sensorhub-backend/app/main.py :: /api/live :: Hub ↔ Frontend.

### Konfiguration
Konfigurierbare Mess- und Foto-Intervalle pro Setup; Node-Modus über API steuerbar. Evidence: sensorhub-backend/app/api/setups.py :: patch_setup :: Intervalle; Evidence: sensorhub-backend/app/api/nodes.py :: post_node_command :: set_mode.

### Fehlerbehandlung
- Node: Automatisches Hello-Retry bei Verbindungsverlust. Evidence: sensornode-firmware/src/main.cpp :: HELLO_RETRY_INTERVAL_MS :: Retry-Mechanismus.
- Hub: Node-Status-Tracking und Fehler-Logging. Evidence: sensorhub-backend/app/nodes.py :: mark_nodes_offline/log_event :: Offline-Markierung und Logging.

### Sicherheit
CSRF-Schutz via Token/Origin-Check; Admin-Reset mit Token. Evidence: sensorhub-backend/app/main.py :: csrf_protect :: CSRF; Evidence: sensorhub-backend/app/api/admin.py :: reset_db :: Reset-Token.

## Trace-Matrix: CR → TR

Diese Matrix zeigt, welche technischen Anforderungen welche funktionalen Anforderungen umsetzen:

| Customer Requirement | Technical Requirements |
|---------------------|------------------------|
| CR-01 (Gesamtsystem) | TR-01, TR-02, TR-03, TR-04, TR-20, TR-38 |
| CR-02 (pH-Überwachung) | TR-08, TR-09, TR-14, TR-18, TR-26, TR-29 |
| CR-03 (EC-Überwachung) | TR-08, TR-09, TR-14, TR-18, TR-27, TR-29 |
| CR-04 (Temperatur) | TR-08, TR-09, TR-14, TR-18, TR-29 |
| CR-05 (Kalibrierung) | TR-13, TR-25, TR-26, TR-27 |
| CR-06 (Zyklische Messung) | TR-08, TR-12, TR-40 |
| CR-07 (Minimalbetrieb) | TR-19, TR-29, TR-40 |
| CR-08 (Datenübertragung) | TR-05, TR-17, TR-18, TR-22 |
| CR-09 (Multi-Node) | TR-03, TR-20 |
| CR-10 (Fehlertoleranz) | TR-16, TR-22 |
| CR-11 (Langzeitbetrieb) | TR-24, TR-29, TR-40 |
| CR-12 (Erweiterbarkeit) | TR-03, TR-04, TR-20, TR-22 |
| CR-13 (Persistenz) | TR-29 |
| CR-14 (Fotos) | TR-10, TR-21, TR-34, TR-37 |
| CR-15 (Visualisierung) | TR-31, TR-39 |
| CR-16 (Export) | TR-36 |
| CR-17 (Echtzeit-Updates) | TR-39 |
| CR-18 (Historie) | TR-29, TR-32 |

## Wichtige Implementierungshinweise

### Hardware-Plattform
Die Sensor-Nodes basieren auf der vorgesehenen Mikrocontroller-Plattform und kommunizieren über USB-Serial mit dem Hub.
Evidence: sensornode-firmware/src/main.cpp :: FW_VERSION :: Pico-Firmware; Evidence: sensorhub-backend/app/nodes.py :: serial.Serial :: USB-Serial-Kommunikation.

### Kommunikationsprotokoll
Die Kommunikation zwischen Node und Hub erfolgt über ein **JSON-basiertes serielles Protokoll**. Es gibt KEIN HTTP/WLAN auf der Node-Ebene.
Evidence: sensornode-firmware/src/main.cpp :: sendJson/handleMessage :: JSON-Serial-Protokoll.

### Kamera-Verwaltung
USB-Kameras werden vom **Hub (Backend)** verwaltet, nicht von den Sensor-Nodes. Das Backend führt automatische Kamera-Discovery durch und steuert Foto-Capture und Video-Streaming.
Evidence: sensorhub-backend/app/camera_devices.py :: camera_discovery_loop :: Kamera-Discovery; Evidence: sensorhub-backend/app/camera_streaming.py :: stream_camera/capture_photo_now :: Streaming und Foto-Capture.

### Kalibrierung
- **pH**: 3-Punkt-Kalibrierung (0V→0pH, 1.65V→7pH, 3.3V→14pH)
- **EC**: 2-Punkt-Kalibrierung (linear)
- Kalibrierungsdaten werden vom Hub an die Node gesendet und zur Laufzeit angewendet.
Evidence: sensornode-firmware/src/main.cpp :: applyPhCalibration/applyEcCalibration :: Kalibrierung in Firmware; Evidence: sensorhub-backend/app/nodes.py :: sync_calibration :: Übertragung der Kalibrierung.

### Auto-Discovery
Nodes senden automatisch `hello`-Nachrichten beim Start und bei Verbindungsverlust. Der Hub erkennt neue Nodes automatisch und registriert sie in der Datenbank.
Evidence: sensornode-firmware/src/main.cpp :: sendHello :: Hello-Mechanismus; Evidence: sensorhub-backend/app/nodes.py :: _scan_nodes_once/upsert_node :: Registrierung in DB.
