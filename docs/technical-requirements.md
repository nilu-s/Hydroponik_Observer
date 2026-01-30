# Technical Requirements (Technische Anforderungen)

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

- **Architektur**: Grundlegende Systemstruktur (Node-Hub-Modell)
- **Firmware**: Raspberry Pi Pico (RP2040) Node-Implementierung
- **Backend**: Hub/Server-Implementierung (FastAPI, Python)
- **Frontend**: Web-Benutzeroberfläche (React, TypeScript)
- **Datenmodell**: Datenstrukturen und Persistenz (SQLite)
- **Protokoll**: JSON-basierte serielle Kommunikation
- **Kommunikation**: Serial (Node↔Hub), REST/WebSocket (Hub↔Frontend)
- **Konfiguration**: Setup-, Node- und Intervall-Einstellungen
- **Fehlerbehandlung**: Robustheit, Auto-Reconnect, Status-Tracking
- **Sicherheit**: CSRF-Schutz, Admin-Token

## Wichtige Designentscheidungen

### Raspberry Pi Pico statt ESP32
Die Sensor-Nodes basieren auf **Raspberry Pi Pico** (RP2040), nicht ESP32. Hauptgründe:
- Serielle Kommunikation über USB (einfacher als WLAN)
- Niedrigere Kosten
- Ausreichende Performance für Sensor-Auslesen

### Serielles Protokoll statt WLAN/HTTP
Die Kommunikation zwischen Node und Hub erfolgt über **USB-Serial mit JSON**, nicht über HTTP/WLAN:
- Einfachere Implementierung (kein WLAN-Setup)
- Zuverlässigere Verbindung (kabelgebunden)
- Geringerer Stromverbrauch

### Kamera-Verwaltung im Backend
USB-Kameras werden vom **Hub (Backend)** verwaltet, nicht von den Nodes:
- USB-Bandbreite (Nodes haben nur einen USB-Port für Serial)
- Zentrale Verwaltung und Steuerung
- Automatische Kamera-Discovery

### SQLite statt PostgreSQL
SQLite wurde als Datenbank gewählt:
- Embedded (keine separate Datenbank-Instanz nötig)
- Einfaches Deployment (single-file)
- Ausreichend für typische Anwendungsfälle (1-10 Nodes)
