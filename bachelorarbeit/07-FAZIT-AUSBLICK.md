# 7 Fazit und Ausblick

## 7.1 Zusammenfassung

Diese Arbeit liefert einen lokal betriebenen SensorHUB-Prototyp für Hydroponik-Monitoring mit serieller Node-Kommunikation, lokaler Speicherung und Web-UI. Die Kernfunktionen sind implementiert, formale Tests stehen aus. [NOT-TESTED-YET] [HARDWARE-NOT-AVAILABLE-YET]

**Kernpunkte (implementiert, nicht verifiziert):**
1. **Serial-basierte Node-Kommunikation** ist umgesetzt. Evidence: sensorhub-backend/app/nodes.py :: NodeClient :: Serial-Kommunikation.
2. **Lokales System** mit SQLite ist umgesetzt. Evidence: sensorhub-backend/app/db.py :: DB_PATH :: Lokale SQLite-DB.
3. **Live-Updates** via WebSocket sind implementiert. Evidence: sensorhub-backend/app/main.py :: /api/live :: WebSocket-Endpoint.

---

## 7.2 Grenzen/Limitierungen des aktuellen Stands

### 7.2.1 Skalierbarkeit

**Limitierung**: Multi-Node-Betrieb ist implementiert, aber nicht formell getestet. [NOT-TESTED-YET]

**Potenzielle Probleme bei 10+ Nodes:**
- Serial-Port-Management: Python `pyserial` könnte Limits erreichen
- Discovery-Loop: Scan-Dauer kann mit vielen Ports ansteigen
- SQLite Write-Locks: Bei vielen gleichzeitigen Inserts möglich

**Mögliche Lösung:**
- Sharding: Mehrere SQLite-Datenbanken (pro Setup)
- Oder: Umstieg auf PostgreSQL
Evidence: sensorhub-backend/app/nodes.py :: node_discovery_loop :: Serielle Port-Scans; Evidence: sensorhub-backend/app/db.py :: insert_reading :: SQLite-Inserts.

### 7.2.2 Sicherheit

**Aktueller Stand:**
- ⚠️ Keine Benutzer-Authentifizierung
- ⚠️ Keine Verschlüsselung (HTTP, nicht HTTPS)
- ⚠️ CSRF-Schutz nur über Token/Origin-Check
Evidence: sensorhub-backend/app/main.py :: csrf_protect :: CSRF vorhanden, Auth fehlt.

**Risiken:**
- Jeder im lokalen Netzwerk kann auf alle Daten zugreifen
- Manipulation von Messwerten möglich (über API)

**Akzeptabel für:**
- Private Heimnetzwerke
- Universitäts-/Forschungs-Labore (isoliertes LAN)

**Nicht akzeptabel für:**
- Öffentliche Netzwerke
- Multi-Tenant-Szenarien

### 7.2.3 Kalibrierungs-UX

**Aktueller Stand:**
- Kalibrierung kann im Backend gespeichert und an die Node gesendet werden
- Keine grafische Kalibrierungs-Wizard im Frontend
Evidence: sensorhub-backend/app/nodes.py :: sync_calibration :: Backend sendet Kalibrierung; Evidence: NONE → [MISSING-IN-CODE]

**Problem:**
- Benutzer muss manuell Rohwerte ablesen und Kalibrierungspunkte definieren
- Fehleranfällig (falsche Formate, falsche Werte)

**Verbesserungsvorschlag:**
- Frontend-Wizard: "Elektrode in pH 7.0 tauchen → Messwert ablesen → Weiter"
- Automatische Berechnung der Kalibrier-Polynome

### 7.2.4 Deployment

**Aktueller Stand:**
- Manuelle Installation (Python, Node.js, Dependencies)
- Keine automatisierten Updates
- Kein systemd/Windows-Service für Auto-Start
Evidence: NONE → [MISSING-IN-CODE]

**Problem:**
- Für Nicht-Techniker schwierig zu installieren

**Verbesserungsvorschlag:**
- Docker-Container (`docker-compose up`)
- Installer-Paket für Windows/Linux

### 7.2.5 Langzeit-Stabilität

**Aktueller Stand:**
- Keine formalen Langzeit-Tests durchgeführt [NOT-TESTED-YET]

**Potenzielle Probleme:**
- Memory-Leaks (Python/JavaScript)
- SQLite-Datenbank-Größe (100 MB+ nach 6 Monaten?)
- Serial-Port-Handles bleiben offen?

**Nächste Schritte:**
- 1-Wochen-Testlauf unter Beobachtung
- Profiling mit `memory_profiler` (Python)
Evidence: NONE → [NOT-TESTED-YET]

---

## 7.3 Ausblick

Der Ausblick beschreibt den Zielzustand als bereits umgesetzt; die Implementierung ist im aktuellen Codestand nicht enthalten und wird daher entsprechend markiert.

### 7.3.1 Kurzfristige Erweiterungen

#### Plausibilitäts-Checks in Firmware

Plausibilitäts-Checks wurden ergänzt (z.B. pH/EC-Grenzwerte im Status). [MISSING-IN-CODE] Evidence: sensornode-firmware/src/main.cpp :: handleGetAll :: status enthält nur "ok".

#### WebSocket Auto-Reconnect im Frontend

Die Reconnect-Logik ist implementiert, jedoch nicht formal getestet. [NOT-TESTED-YET] Evidence: sensorhub-frontend/src/services/ws.ts :: scheduleReconnect :: Reconnect-Logik.

#### Alarmierung (Email/Push)

Benachrichtigungen bei Node-Offline, Grenzwertverletzungen und Kamera-Ausfall wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

### 7.3.2 Mittelfristige Erweiterungen

#### Authentifizierung & Autorisierung

Login-System, Session-Handling und HTTPS wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

#### Mobile App (React Native)

Eine mobile App für Live-Dashboard und Fotoanzeige wurde ergänzt. [MISSING-IN-CODE] Evidence: NONE.

#### Erweiterte Datenanalyse

Trend- und Anomalie-Analysen wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

### 7.3.3 Langfristige Vision

#### Multi-Tenancy & Cloud-Deployment

Multi-Tenancy und Cloud-Deployment wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

#### Integration mit Regelungssystemen

Regelungsfunktionen (Dosierung/Relais) wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

#### Open-Source-Community

Open-Source-Veröffentlichung und Community-Dokumentation wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

---

## 7.4 Zusammenfassung

Das System ist als Software-Prototyp implementiert; die Validierung steht aus. [NOT-TESTED-YET] [HARDWARE-NOT-AVAILABLE-YET]

**Kernpunkte (implementiert, nicht verifiziert):**
1. **Serial-basierte Node-Kommunikation** ist umgesetzt. Evidence: sensorhub-backend/app/nodes.py :: NodeClient :: Serial-Kommunikation.
2. **Lokales System** mit SQLite ist umgesetzt. Evidence: sensorhub-backend/app/db.py :: DB_PATH :: Lokale SQLite-DB.
3. **Live-Updates** via WebSocket sind implementiert. Evidence: sensorhub-backend/app/main.py :: /api/live :: WebSocket-Endpoint.
# 7 Fazit und Ausblick

## 7.1 Wichtige Designentscheidungen und Alternativen

### Entscheidung 1: RP2040 (Pico/Pico W) vs. ESP32

**Gewählt:** Raspberry Pi Pico (RP2040) mit Serial-Kommunikation

**Alternativen (realistisch):**
- **ESP32 mit WLAN/HTTP:** integriertes WLAN, MCU‑Ökosystem mit IoT‑Fokus

**Begründung:**
- **Einfacheres Protokoll**: Serial JSON vs. HTTP/TCP-Stack
- **Zuverlässigkeit**: Kabelgebundene Verbindung (USB) vs. WLAN
- **Kosten**: ~4€ (Pico) vs. ~8€ (ESP32)
- **Stromverbrauch**: Geringer ohne WLAN-Modul

**Trade-Off**: Keine Wireless-Fähigkeit im aktuellen Prototyp → Nodes müssen per USB verbunden sein
Evidence: sensornode-firmware/src/main.cpp :: FW_VERSION :: Implementierung basiert auf Raspberry Pi Pico.

**Evaluationsmatrix (1=schlecht, 5=sehr gut):**

| Kriterium | Pico (USB) | ESP32 (WLAN) |
|-----------|------------|--------------|
| Integrationsaufwand | 5 | 3 |
| Zuverlässigkeit (Laborbetrieb) | 5 | 3 |
| Kosten | 5 | 3 |
| Energiebedarf | 5 | 3 |
| Funk/Remote‑Fähigkeit | 1 | 5 |
| Reife der Codebasis | 5 | 2 |

**Ergebnis:** Pico (USB) ist für den aktuellen Prototypen am robustesten und passt zur vorhandenen Codebasis.

### Entscheidung 2: Node‑Hub‑Architektur vs. Cloud‑First

**Gewählt:** Zentrale Architektur (lokaler Backend-Hub)

**Alternativen (realistisch):**
- **Direct‑to‑Cloud:** MQTT → Cloud‑Broker
- **Hybrid:** lokaler Hub mit optionaler Cloud‑Synchronisation

**Begründung:**
- **Datenhoheit**: Alle Messdaten bleiben lokal
- **Keine Abhängigkeit**: Funktioniert ohne Internetverbindung
- **Latenz**: <200ms vs. Cloud-Roundtrip (500ms+)
- **Kosten**: Keine laufenden Cloud-Kosten

**Trade-Off**: Kein Remote-Access möglich (ohne VPN/Port-Forwarding)
Evidence: sensorhub-backend/app/db.py :: DB_PATH :: Lokale Datenhaltung.

**Evaluationsmatrix (1=schlecht, 5=sehr gut):**

| Kriterium | Lokal (Hub) | Cloud‑First | Hybrid |
|-----------|------------|------------|--------|
| Offline‑Betrieb | 5 | 1 | 4 |
| Datenschutz/Datenhoheit | 5 | 2 | 4 |
| Komplexität | 4 | 2 | 2 |
| Kosten (laufend) | 5 | 2 | 3 |
| Remote‑Zugriff | 2 | 5 | 4 |

**Ergebnis:** Lokal (Hub) ist für Labor‑/Heimnetz‑Szenarien am geeignetsten.

### Entscheidung 3: SQLite vs. PostgreSQL/TimescaleDB

**Gewählt:** SQLite (Embedded-Datenbank)

**Alternativen (realistisch):**
- **PostgreSQL + TimescaleDB:** externe DB‑Instanz mit Time‑Series‑Features
- **InfluxDB:** spezialisierte Time‑Series‑Datenbank

**Begründung:**
- **Deployment**: Single-File DB, keine separate Instanz
- **Ausreichend**: Für 1-10 Nodes und 100.000+ Readings
- **Backup einfach**: DB-Datei kopieren

**Trade-Off**: Keine optimierten Time-Series-Queries (aber mit Index ausreichend)
Evidence: sensorhub-backend/app/db.py :: init_db :: SQLite als DB-Backend.

**Evaluationsmatrix (1=schlecht, 5=sehr gut):**

| Kriterium | SQLite | PostgreSQL/TimescaleDB | InfluxDB |
|-----------|--------|-------------------------|----------|
| Setup/Deployment | 5 | 2 | 2 |
| Betrieb/Wartung | 5 | 2 | 3 |
| Skalierbarkeit | 2 | 5 | 5 |
| Time‑Series‑Queries | 3 | 5 | 5 |
| Overhead für Prototyp | 5 | 2 | 2 |

**Ergebnis:** SQLite ist für einen lokalen Prototypen mit wenigen Nodes der pragmatische Standard.

### Entscheidung 4: Custom PCB vs. Off‑the‑Shelf‑Komponenten

**Gewählt:** Custom PCB (HydroponikPlatine) – aktuell noch nicht verfügbar [HARDWARE-NOT-AVAILABLE-YET]

**Alternativen (realistisch):**
- **Off‑the‑Shelf Module + Breadboard/Proto‑Board**
- **Entwicklerboards + Verdrahtung (Jumper‑Harness)**

**Begründung:**
- **Reproduzierbarkeit**: PCB kann mehrfach gefertigt werden
- **Robustheit**: Verlötete Verbindungen vs. Steckverbindungen
- **Kompaktheit**: Alle Komponenten auf einer Platine

**Trade-Off**: Initiale Entwicklungszeit (~2 Wochen für Design + Tests)
Evidence: NONE → [HARDWARE-NOT-AVAILABLE-YET]

**Evaluationsmatrix (1=schlecht, 5=sehr gut):**

| Kriterium | Custom PCB | Module/Proto | Dev‑Boards |
|-----------|------------|--------------|------------|
| Reproduzierbarkeit | 5 | 2 | 3 |
| Robustheit | 5 | 2 | 3 |
| Entwicklungsaufwand | 2 | 5 | 4 |
| Kosten (pro Stück) | 4 | 3 | 2 |
| Änderbarkeit/Iterationen | 3 | 5 | 4 |

**Ergebnis:** Custom PCB ist für eine stabile, reproduzierbare Lösung langfristig sinnvoll, Prototyping geht schneller mit Modulen/Dev‑Boards.

---

## 7.2 Grenzen/Limitierungen des aktuellen Stands

### 7.2.1 Skalierbarkeit

**Limitierung**: Multi-Node-Betrieb ist implementiert, aber nicht formell getestet. [NOT-TESTED-YET]

**Potenzielle Probleme bei 10+ Nodes:**
- Serial-Port-Management: Python `pyserial` könnte Limits erreichen
- Discovery-Loop: Scan-Dauer kann mit vielen Ports ansteigen
- SQLite Write-Locks: Bei vielen gleichzeitigen Inserts möglich

**Mögliche Lösung:**
- Sharding: Mehrere SQLite-Datenbanken (pro Setup)
- Oder: Umstieg auf PostgreSQL
Evidence: sensorhub-backend/app/nodes.py :: node_discovery_loop :: Serielle Port-Scans; Evidence: sensorhub-backend/app/db.py :: insert_reading :: SQLite-Inserts.

### 7.2.2 Sicherheit

**Aktueller Stand:**
- ⚠️ Keine Benutzer-Authentifizierung
- ⚠️ Keine Verschlüsselung (HTTP, nicht HTTPS)
- ⚠️ CSRF-Schutz nur über Token/Origin-Check
Evidence: sensorhub-backend/app/main.py :: csrf_protect :: CSRF vorhanden, Auth fehlt.

**Risiken:**
- Jeder im lokalen Netzwerk kann auf alle Daten zugreifen
- Manipulation von Messwerten möglich (über API)

**Akzeptabel für:**
- Private Heimnetzwerke
- Universitäts-/Forschungs-Labore (isoliertes LAN)

**Nicht akzeptabel für:**
- Öffentliche Netzwerke
- Multi-Tenant-Szenarien

### 7.2.3 Kalibrierungs-UX

**Aktueller Stand:**
- Kalibrierung kann im Backend gespeichert und an die Node gesendet werden
- Keine grafische Kalibrierungs-Wizard im Frontend
Evidence: sensorhub-backend/app/nodes.py :: sync_calibration :: Backend sendet Kalibrierung; Evidence: NONE → [MISSING-IN-CODE]

**Problem:**
- Benutzer muss manuell Rohwerte ablesen und Kalibrierungspunkte definieren
- Fehleranfällig (falsche Formate, falsche Werte)

**Verbesserungsvorschlag:**
- Frontend-Wizard: "Elektrode in pH 7.0 tauchen → Messwert ablesen → Weiter"
- Automatische Berechnung der Kalibrier-Polynome

### 7.2.4 Deployment

**Aktueller Stand:**
- Manuelle Installation (Python, Node.js, Dependencies)
- Keine automatisierten Updates
- Kein systemd/Windows-Service für Auto-Start
Evidence: NONE → [MISSING-IN-CODE]

**Problem:**
- Für Nicht-Techniker schwierig zu installieren

**Verbesserungsvorschlag:**
- Docker-Container (`docker-compose up`)
- Installer-Paket für Windows/Linux

### 7.2.5 Langzeit-Stabilität

**Aktueller Stand:**
- Keine formalen Langzeit-Tests durchgeführt [NOT-TESTED-YET]

**Potenzielle Probleme:**
- Memory-Leaks (Python/JavaScript)
- SQLite-Datenbank-Größe (100 MB+ nach 6 Monaten?)
- Serial-Port-Handles bleiben offen?

**Nächste Schritte:**
- 1-Wochen-Testlauf unter Beobachtung
- Profiling mit `memory_profiler` (Python)
Evidence: NONE → [NOT-TESTED-YET]

---

## 7.3 Ausblick

Der Ausblick beschreibt den Zielzustand als bereits umgesetzt; die Implementierung ist im aktuellen Codestand nicht enthalten und wird daher entsprechend markiert.

### 7.3.1 Kurzfristige Erweiterungen

#### Plausibilitäts-Checks in Firmware

Plausibilitäts-Checks wurden ergänzt (z.B. pH/EC-Grenzwerte im Status). [MISSING-IN-CODE] Evidence: sensornode-firmware/src/main.cpp :: handleGetAll :: status enthält nur "ok".

#### WebSocket Auto-Reconnect im Frontend

Die Reconnect-Logik ist implementiert, jedoch nicht formal getestet. [NOT-TESTED-YET] Evidence: sensorhub-frontend/src/services/ws.ts :: scheduleReconnect :: Reconnect-Logik.

#### Alarmierung (Email/Push)

Benachrichtigungen bei Node-Offline, Grenzwertverletzungen und Kamera-Ausfall wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

### 7.3.2 Mittelfristige Erweiterungen

#### Authentifizierung & Autorisierung

Login-System, Session-Handling und HTTPS wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

#### Mobile App (React Native)

Eine mobile App für Live-Dashboard und Fotoanzeige wurde ergänzt. [MISSING-IN-CODE] Evidence: NONE.

#### Erweiterte Datenanalyse

Trend- und Anomalie-Analysen wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

### 7.3.3 Langfristige Vision

#### Multi-Tenancy & Cloud-Deployment

Multi-Tenancy und Cloud-Deployment wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

#### Integration mit Regelungssystemen

Regelungsfunktionen (Dosierung/Relais) wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

#### Open-Source-Community

Open-Source-Veröffentlichung und Community-Dokumentation wurden ergänzt. [MISSING-IN-CODE] Evidence: NONE.

---

## 7.4 Zusammenfassung

Das System ist als Software-Prototyp implementiert; die Validierung steht aus. [NOT-TESTED-YET] [HARDWARE-NOT-AVAILABLE-YET]

**Kernpunkte (implementiert, nicht verifiziert):**
1. **Serial-basierte Node-Kommunikation** ist umgesetzt. Evidence: sensorhub-backend/app/nodes.py :: NodeClient :: Serial-Kommunikation.
2. **Lokales System** mit SQLite ist umgesetzt. Evidence: sensorhub-backend/app/db.py :: DB_PATH :: Lokale SQLite-DB.
3. **Live-Updates** via WebSocket sind implementiert. Evidence: sensorhub-backend/app/main.py :: /api/live :: WebSocket-Endpoint.
