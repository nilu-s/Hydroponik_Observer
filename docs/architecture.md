# Architektur und Komponenten

## Systemuebersicht

SensorHub besteht aus drei Hauptschichten:

1. **SensorNode** auf dem RP2040 (Pico) sammelt Sensordaten.
2. **SensorHub Backend** (FastAPI) orchestriert Nodes, speichert Daten und stellt APIs bereit.
3. **SensorHub Frontend** (Vite + React) zeigt Daten und steuert Setups.

Zusaetzlich existiert ein **Camera Worker** (C#), der das Betriebssystem fuer
Kameralisten und Frame-Streaming nutzt.

## Komponenten

### SensorNode (RP2040)

- Datei: `sensornode-firmware/src/main.cpp`
- Sensoren: pH (ADC2), EC (ADC0), Temperatur (OneWire GPIO17)
- Protokoll: JSON Lines ueber Serial (115200 Baud)
- Modi: `real` und `debug` (simulierte Werte)
- Kalibrierung: pH (3 Punkte), EC (2 Punkte), Hash fuer Sync

### SensorHub Backend (FastAPI)

- Einstieg: `sensorhub-backend/app/main.py`
- Aufgaben:
  - Node-Scan und Handshake
  - Serial Requests fuer Messwerte
  - Speicherung in SQLite
  - REST-API und WebSocket Live-Feed
  - Kamera-Management und Snapshot/Stream
- Persistenz: `data/sensorhub.db` + `data/photos/<setup_id>/`

### Camera Worker (C#)

- Datei: `sensorhub-backend/worker/Program.cs`
- Modus `--list`: Gibt JSON-Liste von Kameras aus
- Modus `--device <id>`: Streamt Frames als Binary-Stream
- Protokoll: Eigener Frame-Header + JPEG Payload

### SensorHub Frontend (Vite + React)

- Einstieg: `sensorhub-frontend/src/main.tsx`
- API-Client: `sensorhub-frontend/src/services/api.ts`
- WebSocket: `sensorhub-frontend/src/services/ws.ts`
- Hauptseiten: `sensorhub-frontend/src/pages/HomePage.tsx`, `SettingsPage.tsx`

## Laufzeitprozesse (SensorHub Backend)

Beim Start werden mehrere Loops gestartet:

- `node_discovery`: Scannt Serial Ports und erkennt RP2040 Nodes.
- `readings_capture`: Periodisches Speichern von Messwerten (Setup-Intervall).
- `camera_discovery`: Scan per Worker fuer Kamera-Devices.
- `photo_capture`: Periodische Fotoaufnahme pro Setup.

## Komponentendiagramm

```mermaid
flowchart LR
  subgraph SensorNode
    Node[SensorNode RP2040]
  end

  subgraph SensorHub_Backend
    API[SensorHub Backend API]
    WS[SensorHub Backend WS]
    Serial[SensorHub Serial NodeClient]
    DB[(SQLite)]
    Photos[(Photos Dir)]
    CamCtl[SensorHub Camera Streaming]
    WorkerCtl[SensorHub Camera Worker Host]
  end

  subgraph SensorHub_Frontend
    UI[SensorHub Frontend]
  end

  subgraph Camera_Worker
    CamWorker[Camera Worker]
  end

  UI -->|HTTP JSON| API
  UI -->|WS JSON| WS
  API --> DB
  API --> Photos
  WS --> Serial
  Serial <--> Node
  CamCtl --> WorkerCtl
  WorkerCtl --> CamWorker
  CamWorker --> CamCtl
  API --> CamCtl

  %% Farbcode (Flowchart, kompatibel mit Mermaid Preview)
  style UI fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1
  style API fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style WS fill:#FFF8E1,stroke:#F9A825,color:#8D6E63
  style Serial fill:#E0F2F1,stroke:#00897B,color:#004D40
  style CamCtl fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style WorkerCtl fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style DB fill:#FFEBEE,stroke:#E53935,color:#B71C1C
  style Photos fill:#FCE4EC,stroke:#D81B60,color:#880E4F
  style Node fill:#F3E5F5,stroke:#8E24AA,color:#4A148C
  style CamWorker fill:#FFF3E0,stroke:#FB8C00,color:#E65100
```

## Deployment (lokal)

```mermaid
flowchart TB
  Host[Windows Host]
  Backend[SensorHub Backend]
  Frontend[SensorHub Frontend]
  Worker[Camera Worker]
  DB[(SQLite)]
  Photos[(Photos Dir)]
  Node[SensorNode RP2040]

  Frontend -->|HTTP| Backend
  Frontend -->|WS| Backend
  Backend --> DB
  Backend --> Photos
  Backend --> Worker
  Backend <--> Node
  Host --> Backend
  Host --> Frontend
  Host --> Worker

  style Frontend fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1
  style Backend fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style Worker fill:#FFF3E0,stroke:#FB8C00,color:#E65100
  style DB fill:#FFEBEE,stroke:#E53935,color:#B71C1C
  style Photos fill:#FCE4EC,stroke:#D81B60,color:#880E4F
  style Node fill:#F3E5F5,stroke:#8E24AA,color:#4A148C
```

## Datenfluss (High Level)

1. SensorHub Frontend abonniert ein Setup per WebSocket.
2. SensorHub Backend pollt den SensorNode ueber Serial (`get_all`).
3. SensorNode antwortet mit Messwerten, SensorHub Backend pusht via WS.
4. In Intervallen werden Messungen in SQLite gespeichert.
5. Kamera-Streams werden on-demand ueber den Worker erzeugt.

## Weiterfuehrend

- Protokolle: `protocols.md`
- Datenmodell: `data-model.md`
- Diagramme (Detail): `diagramme/README.md`
