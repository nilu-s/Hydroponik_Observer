# SensorHub Dokumentation

Diese Dokumentation beschreibt das Zusammenspiel von SensorNode, SensorHub Backend und SensorHub Frontend.
Sie richtet sich an Entwickler:innen und dient als technische Referenz fuer Datenfluss,
Komponenten und Protokolle.

## Inhalt

- `architecture.md` - Systemueberblick, Komponenten und Laufzeitprozesse
- `protocols.md` - Protokolle (Serial, WebSocket, Worker-Frames)
- `api.md` - REST-API und Endpunkte
- `data-model.md` - Datenmodell, Persistenz und Ablage
- `setup.md` - Installation, Voraussetzungen, erste Schritte
- `deployment.md` - Betrieb, Startreihenfolge, Autostart
- `config.md` - Konfiguration, Tokens, Pfade
- `troubleshooting.md` - Fehlerbilder und Loesungen
- `faq.md` - Kurzantworten
- `diagramme/README.md` - Diagramme und Sequenzen

## Schnellzugriff

- Architektur: `architecture.md`
- API: `api.md`
- Protokolle: `protocols.md`
- Datenmodell: `data-model.md`
- Setup: `setup.md`
- Betrieb: `deployment.md`
- Konfiguration: `config.md`
- Troubleshooting: `troubleshooting.md`
- Diagramme (voll): `diagramme/README.md`

## Kurzueberblick

- **SensorNode (RP2040 / Pico)**: Liefert Sensordaten (pH, EC, Temperatur) via Serial-JSON.
- **SensorHub Backend (FastAPI)**: Erkennt Nodes/Camera-Devices, kapselt Serial/Worker,
  speichert Messwerte und stellt HTTP/WS bereit.
- **Camera Worker (C#)**: Listet Kameras und streamt JPEG Frames via Stdout.
- **SensorHub Frontend (Vite + React)**: Bedienoberflaeche, ruft REST und Live-WS ab.

## Hauptdatenpfade

- **Livewerte**: SensorHub Frontend WS -> SensorHub Backend -> Serial JSON -> SensorNode -> Backend -> WS Push
- **History**: SensorHub Backend schreibt Messungen in SQLite -> SensorHub Frontend liest ueber REST
- **Kamera**: SensorHub Frontend REST -> SensorHub Backend startet Worker -> MJPEG Stream

## Verzeichnisuebersicht

- `sensorhub-backend/` - FastAPI Backend, DB und Worker-Ansteuerung
- `sensorhub-frontend/` - Vite + React UI
- `sensornode-firmware/` - Pico Firmware (PlatformIO)
- `data/` - SQLite DB und Fotos
- `docs/` - Dokumentation und Diagramme

## Diagramme (Kurzansicht)

Systemuebersicht:
```mermaid
flowchart LR
  subgraph SensorHub_Frontend
    UI[SensorHub Frontend]
  end

  subgraph SensorHub_Backend
    API[SensorHub Backend API]
    WS[SensorHub Backend WS]
  end

  subgraph Storage
    DB[(SQLite)]
    Photos[(Photos Dir)]
  end

  subgraph SensorNode
    Node[SensorNode RP2040]
  end

  subgraph Camera_Worker
    Worker[Camera Worker]
  end

  UI --> API
  UI --> WS
  WS --> API
  API --> DB
  API --> Photos
  API <--> Node
  API <--> Worker

  style UI fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1
  style API fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style WS fill:#FFF8E1,stroke:#F9A825,color:#8D6E63
  style DB fill:#FFEBEE,stroke:#E53935,color:#B71C1C
  style Photos fill:#FCE4EC,stroke:#D81B60,color:#880E4F
  style Node fill:#F3E5F5,stroke:#8E24AA,color:#4A148C
  style Worker fill:#FFF3E0,stroke:#FB8C00,color:#E65100
```

Deployment (lokal):
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

Weitere Diagramme und Sequenzen: `diagramme/README.md`.

## Startbefehle (lokal)

### SensorHub Backend

```powershell
cd "sensorhub-backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### SensorHub Frontend

```powershell
cd "sensorhub-frontend"
npm install
npm run dev
```

### SensorNode Firmware

```powershell
cd "sensornode-firmware"
pio run
pio run -t upload
```

Optionaler Upload-Port:

```powershell
pio run -t upload --upload-port COM3
```

Hinweis: Das Board ist in `sensornode-firmware/platformio.ini` als `board = pico` konfiguriert.

Weitere Details, Beispiele und Diagramme siehe die Dateien im `docs` Ordner.
