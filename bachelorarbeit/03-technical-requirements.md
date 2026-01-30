# 3.2 Technical Requirements (Technische Anforderungen)

Diese Anforderungen beschreiben die technische Umsetzung des Systems.

## Übersicht

| ID | Beschreibung | Kategorie |
|----|--------------|-----------|
| TR-01 | Das System besteht aus mindestens einem Sensor Node | Architektur |
| TR-02 | Der Hub empfängt Messwerte von den Nodes | Architektur |
| TR-03 | Der Hub unterstützt mehrere Sensor Nodes gleichzeitig | Architektur |
| TR-04 | Jede Node besitzt eine eindeutige ID (Hardware-UID) | Architektur |
| TR-05 | Nodes kommunizieren via serieller Schnittstelle mit dem Hub | Kommunikation |
| TR-08 | Die Sensor Node erfasst Messwerte lokal | Firmware |
| TR-09 | Die Firmware läuft auf einem Raspberry Pi Pico (RP2040) | Firmware |
| TR-10 | USB-Kameras werden vom Hub verwaltet (nicht von Nodes) | Backend |
| TR-11 | Messwerte werden mit Zeitstempel versehen | Datenmodell |
| TR-12 | Mess- und Foto-Intervalle können konfiguriert werden | Konfiguration |
| TR-13 | Kalibrierungsdaten werden vom Hub an die Node gesendet und lokal angewendet | Firmware |
| TR-14 | Die Firmware unterstützt pH, EC und Temperatur-Sensoren | Firmware |
| TR-15 | Die Node unterstützt einen Debug-Modus mit simulierten Werten | Firmware |
| TR-16 | Die Sensor Nodes ermöglichen lokale Fehlerdiagnose | Fehlerbehandlung |
| TR-17 | Kommunikation erfolgt via JSON-Nachrichten über Serial | Protokoll |
| TR-18 | Messdaten enthalten Node-ID, Zeitstempel, pH, EC, Temp, Status | Protokoll, Datenmodell |
| TR-19 | Der Hub empfängt und speichert Messwerte | Backend |
| TR-20 | Der Hub führt automatische Node-Discovery durch | Backend |
| TR-21 | Der Hub führt automatische Kamera-Discovery durch | Backend |
| TR-22 | Die Node sendet regelmäßig "hello"-Nachrichten für Auto-Discovery | Protokoll |
| TR-23 | Messdaten werden mit Metadaten (Setup, Node, Status) versehen | Datenmodell |
| TR-24 | Die Firmware verwendet Glättung (Smoothing) über mehrere Samples | Firmware |
| TR-25 | Kalibrierdaten sind im Datenmodell enthalten | Datenmodell |
| TR-26 | Die Node unterstützt 3-Punkt-Kalibrierung für pH | Firmware |
| TR-27 | Die Node unterstützt 2-Punkt-Kalibrierung für EC | Firmware |
| TR-29 | Messwerte werden in einer SQLite-Datenbank gespeichert | Backend |
| TR-30 | Es gibt eine REST API zur Abfrage von Messwerten | Backend |
| TR-31 | Eine Web-UI visualisiert Messwerte und Status | Frontend |
| TR-32 | Messdaten können nach Setup und Zeitraum gefiltert werden | Backend |
| TR-33 | Das Backend stellt CSRF-Schutz bereit | Backend, Sicherheit |
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
Grundlegende Systemstruktur mit Node-Hub-Modell. Jede Node erfasst Messwerte und sendet sie via seriellem Protokoll an einen zentralen Hub.

### Firmware
**Raspberry Pi Pico (RP2040)** basierte Implementierung für die Sensor-Nodes. Unterstützt pH, EC und Temperatur-Sensoren mit 3-Punkt (pH) bzw. 2-Punkt (EC) Kalibrierung. Beinhaltet Debug-Modus und automatische Hello-Discovery.

### Backend
Hub-/Server-Implementierung mit **FastAPI (Python)**. Empfängt Messwerte über serielle Schnittstelle, speichert sie persistent in einer **SQLite-Datenbank** und stellt eine REST API bereit. Verwaltet automatische Node-Discovery, Kamera-Discovery und zyklische Messwerterfassung.

### Frontend
**React (TypeScript)** basierte Web-Benutzeroberfläche zur Visualisierung von Live- und historischen Messwerten sowie zur Verwaltung von Nodes, Setups und Kameras.

### Datenmodell
Strukturierung von Messwerten mit Metadaten (Setup-ID, Node-ID, Zeitstempel, Status) und Kalibrierungsdaten (3-Punkt für pH, 2-Punkt für EC).

### Protokoll
JSON-basiertes Nachrichtenformat über serielle Schnittstelle (USB). Nachrichten-Typen: `hello`, `hello_ack`, `get_all`, `set_mode`, `set_values`, `set_calib`.

### Kommunikation
- **Node ↔ Hub**: Serielles Protokoll (USB/UART) mit JSON-Nachrichten
- **Hub ↔ Frontend**: REST API (HTTP) und WebSocket für Live-Updates

### Konfiguration
Konfigurierbare Mess- und Foto-Intervalle pro Setup. Node-Modus (real/debug) über API steuerbar.

### Fehlerbehandlung
- Node: Automatisches Hello-Retry bei Verbindungsverlust
- Hub: Timeout-Detection, Node-Status-Tracking, Fehler-Logging

### Sicherheit
CSRF-Schutz via Token/Origin-Check. Admin-Reset-Endpoint mit Token-Authentifizierung.

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
Die Sensor-Nodes basieren auf **Raspberry Pi Pico** (RP2040), NICHT auf ESP32. Der Pico kommuniziert über USB-Serial mit dem Hub.

### Kommunikationsprotokoll
Die Kommunikation zwischen Node und Hub erfolgt über ein **JSON-basiertes serielles Protokoll**. Es gibt KEIN HTTP/WLAN auf der Node-Ebene.

### Kamera-Verwaltung
USB-Kameras werden vom **Hub (Backend)** verwaltet, nicht von den Sensor-Nodes. Das Backend führt automatische Kamera-Discovery durch und steuert Foto-Capture und Video-Streaming.

### Kalibrierung
- **pH**: 3-Punkt-Kalibrierung (0V→0pH, 1.65V→7pH, 3.3V→14pH)
- **EC**: 2-Punkt-Kalibrierung (linear)
- Kalibrierungsdaten werden vom Hub an die Node gesendet und dort persistent angewendet.

### Auto-Discovery
Nodes senden automatisch `hello`-Nachrichten beim Start und bei Verbindungsverlust. Der Hub erkennt neue Nodes automatisch und registriert sie in der Datenbank.
