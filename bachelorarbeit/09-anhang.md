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
| `/api/setups/{id}/capture-photo` | POST | - | Erfasstes Foto |
| `/api/setups/{id}/history?limit=200` | GET | - | `{"readings": [...], "photos": [...]}` |
| `/api/setups/{id}/camera/stream` | GET | - | MJPEG-Stream |
| `/api/setups/{id}/camera/snapshot` | GET | - | JPEG-Snapshot |

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
| `/api/cameras/devices` | GET | Kamera-Geräte (Discovery) |
| `/api/cameras/{id}` | PATCH | Kamera-Alias ändern |
| `/api/cameras/{id}` | DELETE | Kamera entfernen |

#### Admin

| Endpoint | Method | Headers | Response |
|----------|--------|---------|----------|
| `/api/admin/health` | GET | - | System-Health-Status |
| `/api/admin/reset` | POST | `X-Reset-Token: <token>` | `{"ok": true}` |

#### Export

| Endpoint | Method | Response |
|----------|--------|----------|
| `/api/export/all` | GET | ZIP-Datei mit allen Messdaten (CSV) |
Evidence: sensorhub-backend/app/api/setups.py :: router endpoints :: Setup-API; Evidence: sensorhub-backend/app/api/nodes.py :: router endpoints :: Node-API; Evidence: sensorhub-backend/app/api/cameras.py :: router endpoints :: Kamera-API; Evidence: sensorhub-backend/app/api/admin.py :: router endpoints :: Admin-API; Evidence: sensorhub-backend/app/main.py :: camera_stream/camera_snapshot :: Kamera-Endpoints.

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
Evidence: sensorhub-backend/app/realtime_updates.py :: _build_reading_payload :: Reading-Payload; Evidence: sensorhub-backend/app/camera_devices.py :: broadcast_camera_devices :: cameraDevices-Message; Evidence: sensorhub-backend/app/realtime_updates.py :: broadcast_system_reset :: reset-Message.

---

## B Schaltpläne und PCB-Layout

### B.1 Schaltplan (Auszug)

![Schaltplan HydroponikPlatine](../HydroponikPlatine.pdf)
[HARDWARE-NOT-AVAILABLE-YET] Evidence: NONE.

**Kernkomponenten:**
- Raspberry Pi Pico (RP2040) (Mikrocontroller)
- TL081 (Operationsverstärker für pH)
- TC1121COA (DC/DC Inverter, +5V → -5V)
- DS18B20 (Temperatur-Sensor, OneWire)
Evidence: NONE → [HARDWARE-NOT-AVAILABLE-YET]

### B.2 PCB-Layout

- **Größe**: A3
- **Layer**: 2-Layer
- **Fertigung**: JLCPCB, PCBWay
Evidence: NONE → [HARDWARE-NOT-AVAILABLE-YET]

**Dateien**:
- Gerber-Files: `HydroponikPlatine/production/*.gbr`
- BOM: `HydroponikPlatine/production/bom.csv`

---

## C Konfigurationsdateien

### C.1 Backend-Konfiguration

**Datei**: `sensorhub-backend/app/config.py`

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"

# Datenbank
DB_PATH = DATA_DIR / "sensorhub.db"

# CORS
CORS_ALLOW_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8081",
    "http://localhost:19006",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]

# CSRF
CSRF_TOKEN = os.getenv("CSRF_TOKEN", "")
CSRF_TRUSTED_ORIGINS = CORS_ALLOW_ORIGINS

# Admin
ADMIN_RESET_TOKEN = os.getenv("ADMIN_RESET_TOKEN", "")

# Intervalle
DEFAULT_VALUE_INTERVAL_MINUTES = 30
DEFAULT_PHOTO_INTERVAL_MINUTES = 720

# Verzeichnisse
DATA_DIR = PROJECT_DIR / "data"
PHOTOS_DIR = DATA_DIR / "photos"
```
Evidence: sensorhub-backend/app/config.py :: DEFAULT_CORS_ORIGINS/DEFAULT_VALUE_INTERVAL_MINUTES :: Konfigurationen.

### C.2 Frontend-Konfiguration

**Datei**: `sensorhub-frontend/src/services/backend-url.ts`

```typescript
export const getBackendBaseUrl = () => {
  const { protocol, hostname, port } = window.location;
  return `${protocol}//${hostname}:${resolveBackendPort(port)}`;
};
```
Evidence: sensorhub-frontend/src/services/backend-url.ts :: getBackendBaseUrl :: Dynamische Backend-URL.

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
Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN/FW_VERSION :: Firmware-Konstanten.

---

## D Messergebnisse und Logs
Messergebnisse und Logs liegen derzeit nicht vor. [NOT-TESTED-YET] Evidence: NONE.

---

## E Test-Protokolle
Test-Protokolle wurden noch nicht erstellt. [NOT-TESTED-YET] Evidence: NONE.

---

## F Eidesstattliche Erklärung

Hiermit versichere ich, dass ich die vorliegende Arbeit selbstständig verfasst und keine anderen als die angegebenen Quellen und Hilfsmittel benutzt habe. Wörtlich oder dem Sinn nach aus anderen Werken entnommene Stellen sind unter Angabe der Quellen kenntlich gemacht.

---

**Ort, Datum**

**Unterschrift**
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
| `/api/setups/{id}/capture-photo` | POST | - | Erfasstes Foto |
| `/api/setups/{id}/history?limit=200` | GET | - | `{"readings": [...], "photos": [...]}` |
| `/api/setups/{id}/camera/stream` | GET | - | MJPEG-Stream |
| `/api/setups/{id}/camera/snapshot` | GET | - | JPEG-Snapshot |

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
| `/api/cameras/devices` | GET | Kamera-Geräte (Discovery) |
| `/api/cameras/{id}` | PATCH | Kamera-Alias ändern |
| `/api/cameras/{id}` | DELETE | Kamera entfernen |

#### Admin

| Endpoint | Method | Headers | Response |
|----------|--------|---------|----------|
| `/api/admin/health` | GET | - | System-Health-Status |
| `/api/admin/reset` | POST | `X-Reset-Token: <token>` | `{"ok": true}` |

#### Export

| Endpoint | Method | Response |
|----------|--------|----------|
| `/api/export/all` | GET | ZIP-Datei mit allen Messdaten (CSV) |
Evidence: sensorhub-backend/app/api/setups.py :: router endpoints :: Setup-API; Evidence: sensorhub-backend/app/api/nodes.py :: router endpoints :: Node-API; Evidence: sensorhub-backend/app/api/cameras.py :: router endpoints :: Kamera-API; Evidence: sensorhub-backend/app/api/admin.py :: router endpoints :: Admin-API; Evidence: sensorhub-backend/app/main.py :: camera_stream/camera_snapshot :: Kamera-Endpoints.

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
Evidence: sensorhub-backend/app/realtime_updates.py :: _build_reading_payload :: Reading-Payload; Evidence: sensorhub-backend/app/camera_devices.py :: broadcast_camera_devices :: cameraDevices-Message; Evidence: sensorhub-backend/app/realtime_updates.py :: broadcast_system_reset :: reset-Message.

---

## B Schaltpläne und PCB-Layout

### B.1 Schaltplan (Auszug)

![Schaltplan HydroponikPlatine](../HydroponikPlatine.pdf)
[HARDWARE-NOT-AVAILABLE-YET] Evidence: NONE.

**Kernkomponenten:**
- Raspberry Pi Pico (RP2040) (Mikrocontroller)
- TL081 (Operationsverstärker für pH)
- TC1121COA (DC/DC Inverter, +5V → -5V)
- DS18B20 (Temperatur-Sensor, OneWire)
Evidence: NONE → [HARDWARE-NOT-AVAILABLE-YET]

### B.2 PCB-Layout

- **Größe**: A3
- **Layer**: 2-Layer
- **Fertigung**: JLCPCB, PCBWay
Evidence: NONE → [HARDWARE-NOT-AVAILABLE-YET]

**Dateien**:
- Gerber-Files: `HydroponikPlatine/production/*.gbr`
- BOM: `HydroponikPlatine/production/bom.csv`

---

## C Konfigurationsdateien

### C.1 Backend-Konfiguration

**Datei**: `sensorhub-backend/app/config.py`

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"

# Datenbank
DB_PATH = DATA_DIR / "sensorhub.db"

# CORS
CORS_ALLOW_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8081",
    "http://localhost:19006",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]

# CSRF
CSRF_TOKEN = os.getenv("CSRF_TOKEN", "")
CSRF_TRUSTED_ORIGINS = CORS_ALLOW_ORIGINS

# Admin
ADMIN_RESET_TOKEN = os.getenv("ADMIN_RESET_TOKEN", "")

# Intervalle
DEFAULT_VALUE_INTERVAL_MINUTES = 30
DEFAULT_PHOTO_INTERVAL_MINUTES = 720

# Verzeichnisse
DATA_DIR = PROJECT_DIR / "data"
PHOTOS_DIR = DATA_DIR / "photos"
```
Evidence: sensorhub-backend/app/config.py :: DEFAULT_CORS_ORIGINS/DEFAULT_VALUE_INTERVAL_MINUTES :: Konfigurationen.

### C.2 Frontend-Konfiguration

**Datei**: `sensorhub-frontend/src/services/backend-url.ts`

```typescript
export const getBackendBaseUrl = () => {
  const { protocol, hostname, port } = window.location;
  return `${protocol}//${hostname}:${resolveBackendPort(port)}`;
};
```
Evidence: sensorhub-frontend/src/services/backend-url.ts :: getBackendBaseUrl :: Dynamische Backend-URL.

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
Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN/FW_VERSION :: Firmware-Konstanten.

---

## D Messergebnisse und Logs
Messergebnisse und Logs liegen derzeit nicht vor. [NOT-TESTED-YET] Evidence: NONE.

---

## E Test-Protokolle
Test-Protokolle wurden noch nicht erstellt. [NOT-TESTED-YET] Evidence: NONE.

---

## F Eidesstattliche Erklärung

Hiermit versichere ich, dass ich die vorliegende Arbeit selbstständig verfasst und keine anderen als die angegebenen Quellen und Hilfsmittel benutzt habe. Wörtlich oder dem Sinn nach aus anderen Werken entnommene Stellen sind unter Angabe der Quellen kenntlich gemacht.

---

**Ort, Datum**

**Unterschrift**
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
| `/api/setups/{id}/capture-photo` | POST | - | Erfasstes Foto |
| `/api/setups/{id}/history?limit=200` | GET | - | `{"readings": [...], "photos": [...]}` |
| `/api/setups/{id}/camera/stream` | GET | - | MJPEG-Stream |
| `/api/setups/{id}/camera/snapshot` | GET | - | JPEG-Snapshot |

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
| `/api/cameras/devices` | GET | Kamera-Geräte (Discovery) |
| `/api/cameras/{id}` | PATCH | Kamera-Alias ändern |
| `/api/cameras/{id}` | DELETE | Kamera entfernen |

#### Admin

| Endpoint | Method | Headers | Response |
|----------|--------|---------|----------|
| `/api/admin/health` | GET | - | System-Health-Status |
| `/api/admin/reset` | POST | `X-Reset-Token: <token>` | `{"ok": true}` |

#### Export

| Endpoint | Method | Response |
|----------|--------|----------|
| `/api/export/all` | GET | ZIP-Datei mit allen Messdaten (CSV) |
Evidence: sensorhub-backend/app/api/setups.py :: router endpoints :: Setup-API; Evidence: sensorhub-backend/app/api/nodes.py :: router endpoints :: Node-API; Evidence: sensorhub-backend/app/api/cameras.py :: router endpoints :: Kamera-API; Evidence: sensorhub-backend/app/api/admin.py :: router endpoints :: Admin-API; Evidence: sensorhub-backend/app/main.py :: camera_stream/camera_snapshot :: Kamera-Endpoints.

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
Evidence: sensorhub-backend/app/realtime_updates.py :: _build_reading_payload :: Reading-Payload; Evidence: sensorhub-backend/app/camera_devices.py :: broadcast_camera_devices :: cameraDevices-Message; Evidence: sensorhub-backend/app/realtime_updates.py :: broadcast_system_reset :: reset-Message.

---

## B Schaltpläne und PCB-Layout

### B.1 Schaltplan (Auszug)

![Schaltplan HydroponikPlatine](../HydroponikPlatine.pdf)
[HARDWARE-NOT-AVAILABLE-YET] Evidence: NONE.

**Kernkomponenten:**
- Raspberry Pi Pico (RP2040) (Mikrocontroller)
- TL081 (Operationsverstärker für pH)
- TC1121COA (DC/DC Inverter, +5V → -5V)
- DS18B20 (Temperatur-Sensor, OneWire)
Evidence: NONE → [HARDWARE-NOT-AVAILABLE-YET]

### B.2 PCB-Layout

- **Größe**: A3
- **Layer**: 2-Layer
- **Fertigung**: JLCPCB, PCBWay
Evidence: NONE → [HARDWARE-NOT-AVAILABLE-YET]

**Dateien**:
- Gerber-Files: `HydroponikPlatine/production/*.gbr`
- BOM: `HydroponikPlatine/production/bom.csv`

---

## C Konfigurationsdateien

### C.1 Backend-Konfiguration

**Datei**: `sensorhub-backend/app/config.py`

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"

# Datenbank
DB_PATH = DATA_DIR / "sensorhub.db"

# CORS
CORS_ALLOW_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8081",
    "http://localhost:19006",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]

# CSRF
CSRF_TOKEN = os.getenv("CSRF_TOKEN", "")
CSRF_TRUSTED_ORIGINS = CORS_ALLOW_ORIGINS

# Admin
ADMIN_RESET_TOKEN = os.getenv("ADMIN_RESET_TOKEN", "")

# Intervalle
DEFAULT_VALUE_INTERVAL_MINUTES = 30
DEFAULT_PHOTO_INTERVAL_MINUTES = 720

# Verzeichnisse
DATA_DIR = PROJECT_DIR / "data"
PHOTOS_DIR = DATA_DIR / "photos"
```
Evidence: sensorhub-backend/app/config.py :: DEFAULT_CORS_ORIGINS/DEFAULT_VALUE_INTERVAL_MINUTES :: Konfigurationen.

### C.2 Frontend-Konfiguration

**Datei**: `sensorhub-frontend/src/services/backend-url.ts`

```typescript
export const getBackendBaseUrl = () => {
  const { protocol, hostname, port } = window.location;
  return `${protocol}//${hostname}:${resolveBackendPort(port)}`;
};
```
Evidence: sensorhub-frontend/src/services/backend-url.ts :: getBackendBaseUrl :: Dynamische Backend-URL.

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
Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN/FW_VERSION :: Firmware-Konstanten.

---

## D Messergebnisse und Logs
Messergebnisse und Logs liegen derzeit nicht vor. [NOT-TESTED-YET] Evidence: NONE.

---

## E Test-Protokolle
Test-Protokolle wurden noch nicht erstellt. [NOT-TESTED-YET] Evidence: NONE.

---

## F Eidesstattliche Erklärung

Hiermit versichere ich, dass ich die vorliegende Arbeit selbstständig verfasst und keine anderen als die angegebenen Quellen und Hilfsmittel benutzt habe. Wörtlich oder dem Sinn nach aus anderen Werken entnommene Stellen sind unter Angabe der Quellen kenntlich gemacht.

---

**Ort, Datum**

**Unterschrift**
