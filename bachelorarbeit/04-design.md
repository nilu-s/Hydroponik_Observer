# 4 System-Design

Dieses Kapitel beschreibt die architektonischen Entscheidungen, das Datenmodell und die Kommunikationsprotokolle des SensorHUB-Systems.

## 4.1 Systemarchitektur

### 4.1.1 Architekturübersicht

Das System folgt einer **Node-Hub-Architektur**:

- **Sensor-Nodes**: Erfassen Messwerte lokal (pH, EC, Temperatur)
- **Hub (Backend)**: Zentrale Koordinations- und Datenverwaltungsinstanz
- **Frontend**: Web-basierte Benutzeroberfläche

```
┌─────────────┐         Serial/USB         ┌──────────────┐
│ Sensor Node │◄─────────────────────────►│              │
│  (Pico)     │                            │              │
└─────────────┘                            │              │
                                           │   Backend    │
┌─────────────┐         Serial/USB         │   (FastAPI)  │
│ Sensor Node │◄─────────────────────────►│              │
│  (Pico)     │                            │              │
└─────────────┘                            └──────┬───────┘
                                                  │
┌─────────────┐              USB                 │
│ USB Kamera  │◄────────────────────────────────►│
└─────────────┘                                   │
                                                  │ REST/WebSocket
                                           ┌──────▼───────┐
                                           │   Frontend   │
                                           │   (React)    │
                                           └──────────────┘
```

### 4.1.2 Komponenten

#### Sensor-Node (Firmware)
- **Plattform**: Raspberry Pi Pico (RP2040)
- **Kommunikation**: Serielles JSON-Protokoll über USB
- **Funktionen**: Sensor-Auslesen, Kalibrierung, Smoothing, Debug-Modus

#### Hub (Backend)
- **Framework**: FastAPI (Python)
- **Datenbank**: SQLite
- **Funktionen**: 
  - Automatische Node-Discovery
  - Automatische Kamera-Discovery
  - Zyklische Messwerterfassung
  - REST API + WebSocket
  - Foto-Capture und -Speicherung

#### Frontend
- **Framework**: React (TypeScript)
- **Funktionen**: Live-Visualisierung, historische Daten, Setup-Verwaltung

### 4.1.3 Designentscheidungen

#### Warum Raspberry Pi Pico statt ESP32?
- **USB-Serial vs. WLAN**: Einfachere, zuverlässigere Kommunikation
- **Kosten**: Günstiger (~4€ vs. ~8€)
- **Stromverbrauch**: Geringer bei reiner Serial-Kommunikation

#### Warum lokales System ohne Cloud?
- **Datenhoheit**: Alle Messdaten bleiben lokal
- **Keine Abhängigkeit**: Funktioniert ohne Internetverbindung
- **Latenz**: Sofortige Anzeige ohne Cloud-Roundtrip

#### Warum SQLite statt PostgreSQL?
- **Embedded**: Keine separate Datenbankinstanz nötig
- **Einfaches Deployment**: Single-File Datenbank
- **Ausreichend**: Für 1-10 Nodes und 10.000+ Messwerte/Tag

---

## 4.2 Datenmodell

### 4.2.1 Entity-Relationship-Diagramm

```
┌─────────────┐
│   Setup     │
│─────────────│
│ setup_id    │◄──────┐
│ name        │       │
│ node_id     │       │ 1:N
│ camera_id   │       │
│ intervals   │       │
└─────────────┘       │
                      │
┌─────────────┐       │
│    Node     │       │
│─────────────│       │
│ node_id     │───────┤
│ name        │       │
│ kind        │       │
│ fw          │       │
│ cap_json    │       │
│ mode        │       │
│ status      │       │
└─────────────┘       │
        │             │
        │ 1:1         │
        ▼             │
┌─────────────┐       │
│ Calibration │       │
│─────────────│       │
│ node_id     │       │
│ payload_json│       │
│ calib_hash  │       │
└─────────────┘       │
                      │
                      │
                ┌─────▼──────┐
                │  Reading   │
                │────────────│
                │ id         │
                │ setup_id   │
                │ node_id    │
                │ ts         │
                │ ph         │
                │ ec         │
                │ temp       │
                │ status_json│
                └────────────┘
```

### 4.2.2 Datenbank-Schema

#### Setup
Repräsentiert eine hydroponische Anlage.

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `setup_id` | TEXT | Eindeutige UUID |
| `name` | TEXT | Anzeigename |
| `node_id` | TEXT | Zugeordnete Node (optional) |
| `camera_id` | TEXT | Zugeordnete Kamera (optional) |
| `value_interval_minutes` | INTEGER | Messintervall |
| `photo_interval_minutes` | INTEGER | Foto-Intervall |
| `created_at` | INTEGER | Erstellungszeitpunkt (Unix-ms) |

#### Node
Repräsentiert einen physischen Sensorknoten.

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `node_id` | TEXT | Hardware-UID (aus Flash) |
| `name` | TEXT | Alias (optional) |
| `kind` | TEXT | Node-Typ (`real`, `virtual`) |
| `fw` | TEXT | Firmware-Version |
| `cap_json` | TEXT | Capabilities (JSON) |
| `mode` | TEXT | `real` oder `debug` |
| `status` | TEXT | `online`, `offline`, `error` |
| `last_seen_at` | INTEGER | Letzter Kontakt (Unix-ms) |
| `last_error` | TEXT | Letzte Fehlermeldung |

#### Reading
Einzelner Messwert.

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | INTEGER | Auto-Increment |
| `setup_id` | TEXT | Zugehöriges Setup |
| `node_id` | TEXT | Sensor-Node |
| `ts` | INTEGER | Zeitstempel (Unix-ms) |
| `ph` | REAL | pH-Wert |
| `ec` | REAL | Leitfähigkeit (mS/cm) |
| `temp` | REAL | Temperatur (°C) |
| `status_json` | TEXT | Status-Array (JSON) |

#### Calibration
Kalibrierungsdaten für Nodes.

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `node_id` | TEXT | Node-ID (Primary Key) |
| `calib_version` | INTEGER | Kalibrierungsversion |
| `calib_hash` | TEXT | Hash der Kalibrierungsdaten |
| `payload_json` | TEXT | Vollständige Kalibrierdaten (JSON) |
| `updated_at` | INTEGER | Letztes Update (Unix-ms) |

**Kalibrierungsdaten-Format (JSON):**

```json
{
  "ph": {
    "points": [
      { "raw": 0.0, "val": 0.0 },
      { "raw": 1.65, "val": 7.0 },
      { "raw": 3.3, "val": 14.0 }
    ]
  },
  "ec": {
    "points": [
      { "raw": 0.0, "val": 0.0 },
      { "raw": 3.3, "val": 5.0 }
    ]
  }
}
```

---

## 4.3 Kommunikationsprotokolle

### 4.3.1 Node ↔ Hub Protokoll

**Medium**: Serielles USB (JSON-Nachrichten, newline-delimited)

#### Nachrichtentypen

**1. Hello (Node → Hub)**

Node kündigt sich beim Start an:

```json
{
  "t": "hello",
  "raw": "probe",
  "fw": "pico-0.1.0",
  "uid": "e6614103e7696a25",
  "cap": {
    "ph": true,
    "ec": true,
    "temp": true,
    "debug": true,
    "calib": true,
    "pins": {
      "ph": "adc2",
      "ec": "adc0",
      "temp": "gpio17"
    }
  },
  "calibHash": "default"
}
```

**2. Hello Acknowledgement (Hub → Node)**

Hub bestätigt Node-Registration:

```json
{
  "t": "hello_ack",
  "raw": "{...original hello message...}",
  "fw": "pico-0.1.0",
  "uid": "e6614103e7696a25",
  "cap": {...},
  "calibHash": "default"
}
```

**3. Get All (Hub → Node)**

Hub fordert aktuelle Messwerte an:

```json
{
  "t": "get_all"
}
```

**Response (Node → Hub):**

```json
{
  "t": "all",
  "raw": "{...request...}",
  "ts": 1234567890,
  "mode": "real",
  "status": ["ok"],
  "ph": 6.8,
  "ec": 1.2,
  "temp": 21.5
}
```

**4. Set Mode (Hub → Node)**

Wechsel zwischen Real- und Debug-Modus:

```json
{
  "t": "set_mode",
  "mode": "debug"
}
```

**5. Set Values (Hub → Node, nur Debug-Modus)**

Manuelle Wert-Setzung:

```json
{
  "t": "set_values",
  "ph": 7.0,
  "ec": 1.5,
  "temp": 22.0
}
```

**6. Set Calibration (Hub → Node)**

Neue Kalibrierungsdaten übertragen:

```json
{
  "t": "set_calib",
  "payload": {
    "ph": {
      "points": [...]
    },
    "ec": {
      "points": [...]
    },
    "calibHash": "abc123"
  }
}
```

**Response:**

```json
{
  "t": "set_calib_ack",
  "raw": "{...request...}"
}
```

### 4.3.2 Hub ↔ Frontend Protokoll

#### REST API

**Base URL**: `http://localhost:8000/api`

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/setups` | GET | Liste aller Setups |
| `/setups` | POST | Neues Setup erstellen |
| `/setups/{id}` | PATCH | Setup aktualisieren |
| `/setups/{id}` | DELETE | Setup löschen |
| `/setups/{id}/reading` | GET | Aktuellen Messwert abrufen |
| `/setups/{id}/capture-reading` | POST | Messwert erfassen & speichern |
| `/setups/{id}/history` | GET | Historische Daten |
| `/nodes` | GET | Liste aller Nodes |
| `/nodes/{id}` | PATCH | Node-Alias ändern |
| `/nodes/{id}` | DELETE | Node entfernen |
| `/nodes/{id}/command` | POST | Kommando an Node senden |
| `/cameras` | GET | Liste aller Kameras |
| `/export/all` | GET | Alle Daten als ZIP exportieren |

#### WebSocket

**Endpoint**: `ws://localhost:8000/api/live`

**Subscribe zu Setup-Updates:**

```json
{
  "t": "sub",
  "setupId": "setup-uuid"
}
```

**Live-Reading-Nachricht:**

```json
{
  "t": "reading",
  "setupId": "setup-uuid",
  "ts": 1234567890,
  "ph": 6.8,
  "ec": 1.2,
  "temp": 21.5,
  "status": ["ok"]
}
```

---

## 4.4 Sicherheitskonzept

### CSRF-Schutz

- **Token-basiert**: `X-CSRF-Token` Header erforderlich für mutating Requests
- **Origin-Check**: Nur vertrauenswürdige Origins erlaubt

### Admin-Funktionen

- **Reset-Endpoint**: Erfordert `X-Reset-Token` Header
- **Token aus Environment-Variable**: `ADMIN_RESET_TOKEN`

### Limitierungen

- ⚠️ **Keine Benutzer-Authentifizierung**: System ist für lokales Netzwerk gedacht
- ⚠️ **Keine Verschlüsselung**: HTTP (nicht HTTPS)
- ⚠️ **Keine Autorisierung**: Alle Clients haben vollen Zugriff
