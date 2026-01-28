# SensorHub Dokumentation

Diese Dokumentation beschreibt das Zusammenspiel von Firmware, Backend und Frontend im SensorHub.
Sie richtet sich an Entwickler:innen und dient als technische Referenz fuer Datenfluss,
Komponenten und Protokolle.

## Inhalt

- `architecture.md` - Systemueberblick, Komponenten und Laufzeitprozesse
- `protocols.md` - Protokolle (Serial, WebSocket, Worker-Frames)
- `api.md` - REST-API und Endpunkte
- `data-model.md` - Datenmodell, Persistenz und Ablage
- `diagrams.md` - Diagramme und Sequenzen

## Kurzueberblick

- **Firmware (RP2040 / Pico)**: Liefert Sensordaten (pH, EC, Temperatur) via Serial-JSON.
- **Backend (FastAPI)**: Erkannt Nodes/Camera-Devices, kapselt Serial/Worker,
  speichert Messwerte und stellt HTTP/WS bereit.
- **Camera Worker (C#)**: Listet Kameras und streamt JPEG Frames via Stdout.
- **Frontend (Vite + React)**: Bedienoberflaeche, ruft REST und Live-WS ab.

## Hauptdatenpfade

- **Livewerte**: Frontend WS -> Backend pollt Node -> Serial JSON -> Backend -> WS Push
- **History**: Backend schreibt Messungen in SQLite -> Frontend liest ueber REST
- **Kamera**: Frontend REST -> Backend startet Worker -> MJPEG Stream

Weitere Details, Beispiele und Diagramme siehe die Dateien im `docs` Ordner.
