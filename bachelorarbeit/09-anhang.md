# Anhang

## A Vollständige API-Dokumentation

### A.1 REST API Endpoints

#### Setups

| Endpoint | Method | Request Body | Response |
|----------|--------|--------------|----------|
| `/api/setups` | GET | - | Liste aller Setups |
| `/api/setups` | POST | `{"name": str}` | Erstelltes Setup |
| `/api/setups/{id}` | PATCH | `{"name": str, "nodeId": str, ...}` | Aktualisiertes Setup |
| `/api/setups/{id}` | DELETE | - | `{"ok": true, "deleted": bool}` |
| `/api/setups/{id}/reading` | GET | - | Aktueller Messwert |
| `/api/setups/{id}/capture-reading` | POST | - | Erfasster Messwert |
| `/api/setups/{id}/history?limit=200` | GET | - | `{"readings": [...], "photos": [...]}` |

#### Nodes

| Endpoint | Method | Request Body | Response |
|----------|--------|--------------|----------|
| `/api/nodes` | GET | - | Liste aller Nodes |
| `/api/nodes/{id}` | PATCH | `{"alias": str}` | Aktualisierte Node |
| `/api/nodes/{id}` | DELETE | - | `{"ok": true, "affectedSetups": int}` |
| `/api/nodes/{id}/command` | POST | `{"t": "get_all"}` | Node-Response |
| `/api/nodes/ports` | GET | - | Liste verfügbarer Serial-Ports |

#### Kameras

| Endpoint | Method | Response |
|----------|--------|----------|
| `/api/cameras` | GET | Liste aller Kameras |

#### Admin

| Endpoint | Method | Headers | Response |
|----------|--------|---------|----------|
| `/api/admin/health` | GET | - | System-Health-Status |
| `/api/admin/reset` | POST | `X-Reset-Token: <token>` | `{"ok": true}` |

#### Export

| Endpoint | Method | Response |
|----------|--------|----------|
| `/api/export/all` | GET | ZIP-Datei mit allen Messdaten (CSV) |

### A.2 WebSocket API

**Endpoint**: `ws://localhost:8000/api/live`

**Subscribe-Nachricht:**

```json
{
  "t": "sub",
  "setupId": "setup-uuid"
}
```

**Server-Nachrichten:**

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

```json
{
  "t": "cameraDevices",
  "devices": [...]
}
```

```json
{
  "t": "reset",
  "reason": "db-reset"
}
```

---

## B Schaltpläne und PCB-Layout

### B.1 Schaltplan (Auszug)

![Schaltplan HydroponikPlatine](../HydroponikPlatine.pdf)

**Kernkomponenten:**
- Raspberry Pi Pico W (Mikrocontroller)
- TL081 (Operationsverstärker für pH)
- TC1121COA (DC/DC Inverter, +5V → -5V)
- DS18B20 (Temperatur-Sensor, OneWire)

### B.2 PCB-Layout

- **Größe**: A3
- **Layer**: 2-Layer
- **Fertigung**: JLCPCB, PCBWay

**Dateien**:
- Gerber-Files: `HydroponikPlatine/production/*.gbr`
- BOM: `HydroponikPlatine/production/bom.csv`

---

## C Konfigurationsdateien

### C.1 Backend-Konfiguration

**Datei**: `sensorhub-backend/app/config.py`

```python
import os

# Datenbank
DB_PATH = Path("data/sensorhub.db")

# CORS
CORS_ALLOW_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# CSRF
CSRF_TOKEN = os.getenv("CSRF_TOKEN", "dev-token-12345")
CSRF_TRUSTED_ORIGINS = CORS_ALLOW_ORIGINS

# Admin
ADMIN_RESET_TOKEN = os.getenv("ADMIN_RESET_TOKEN", "")

# Intervalle
DEFAULT_VALUE_INTERVAL_MINUTES = 5
DEFAULT_PHOTO_INTERVAL_MINUTES = 15

# Verzeichnisse
DATA_DIR = Path("data")
PHOTOS_DIR = DATA_DIR / "photos"
```

### C.2 Frontend-Konfiguration

**Datei**: `sensorhub-frontend/src/services/backend-url.ts`

```typescript
export const BACKEND_URL = "localhost:8000";
```

### C.3 Firmware-Konfiguration

**Datei**: `sensornode-firmware/src/main.cpp`

```cpp
// Pins
static const int PH_PIN = 28;   // ADC2
static const int EC_PIN = 26;   // ADC0
static const int TEMP_PIN = 17; // OneWire

// Timing
static const uint32_t SAMPLE_INTERVAL_MS = 250;
static const uint32_t SMOOTHING_WINDOW_MS = 10000;
static const uint32_t HELLO_RETRY_INTERVAL_MS = 1200;
static const uint32_t HELLO_ACK_TIMEOUT_MS = 4000;

// Firmware-Version
static const char *FW_VERSION = "pico-0.1.0";
```

---

## D Messergebnisse und Logs

### D.1 Beispiel: Readings-Capture-Log

```json
{"ts": "2026-01-29T10:15:23Z", "event": "reading.captured", "setup_id": "setup-abc123", "node_id": "e6614103e7696a25", "ph": 6.8, "ec": 1.2, "temp": 21.5}
{"ts": "2026-01-29T10:20:23Z", "event": "reading.captured", "setup_id": "setup-abc123", "node_id": "e6614103e7696a25", "ph": 6.7, "ec": 1.3, "temp": 21.6}
```

### D.2 Beispiel: Node-Discovery-Log

```json
{"ts": "2026-01-29T10:00:05Z", "event": "node.discovered", "node_id": "e6614103e7696a25", "port": "COM3", "fw": "pico-0.1.0"}
{"ts": "2026-01-29T10:00:07Z", "event": "node.registered", "node_id": "e6614103e7696a25", "kind": "real"}
```

### D.3 Beispiel: CSV-Export

**Datei**: `readings.csv`

```csv
id,setup_id,node_id,ts_iso,ph,ec,temp,status_json
1,setup-abc123,e6614103e7696a25,2026-01-29T10:15:23Z,6.8,1.2,21.5,"[""ok""]"
2,setup-abc123,e6614103e7696a25,2026-01-29T10:20:23Z,6.7,1.3,21.6,"[""ok""]"
```

---

## E Test-Protokolle

### E.1 Unit-Test-Ergebnisse

```
$ pytest tests/
============================= test session starts =============================
platform win32 -- Python 3.11.5, pytest-8.0.0
collected 28 items

tests/test_admin_health.py ..                                          [  7%]
tests/test_camera_worker_manager.py ......                             [ 28%]
tests/test_readings_capture_loop.py .........                          [ 60%]
tests/test_security.py ...........                                     [100%]

============================== 28 passed in 2.34s ==============================
```

### E.2 Performance-Test-Ergebnisse

| Endpoint | Avg | P50 | P95 | P99 |
|----------|-----|-----|-----|-----|
| GET /api/setups | 12ms | 10ms | 18ms | 24ms |
| GET /api/nodes | 8ms | 7ms | 12ms | 16ms |
| GET /api/setups/{id}/reading | 45ms | 42ms | 78ms | 120ms |
| POST /api/setups/{id}/capture-reading | 180ms | 175ms | 250ms | 350ms |

---

## F Eidesstattliche Erklärung

Hiermit versichere ich, dass ich die vorliegende Arbeit selbstständig verfasst und keine anderen als die angegebenen Quellen und Hilfsmittel benutzt habe. Wörtlich oder dem Sinn nach aus anderen Werken entnommene Stellen sind unter Angabe der Quellen kenntlich gemacht.

---

**Ort, Datum**

**Unterschrift**
