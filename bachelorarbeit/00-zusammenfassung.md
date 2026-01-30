# Zusammenfassung

## Deutsche Zusammenfassung

Diese Arbeit beschreibt ein lokales Hydroponik-Monitoring-System, das Messwerte erfasst, speichert und visualisiert, ohne eine automatische Regelung vorzunehmen. Evidence: sensorhub-backend/app/api/setups.py :: capture_reading :: Messwert-Erfassung ohne Steuerungs-Endpunkte.

Die Sensor-Nodes basieren auf dem Raspberry Pi Pico (RP2040) und erfassen pH, EC und Temperatur. Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN :: Firmware liest pH, EC und Temperatur über definierte Pins.

Die Kommunikation zwischen Node und Hub erfolgt über newline-delimited JSON via USB-Serial. Evidence: sensornode-firmware/src/main.cpp :: sendJson/handleMessage :: Firmware sendet/empfängt JSON per Serial.

Das Backend ist als FastAPI-Anwendung implementiert, speichert Messwerte in einer SQLite-Datenbank und stellt REST- sowie WebSocket-Schnittstellen bereit. Evidence: sensorhub-backend/app/main.py :: FastAPI app + /api/live :: FastAPI-App mit WebSocket-Endpoint; Datenzugriff in db.py.

Die Web-Oberfläche ist eine React/TypeScript-Anwendung mit Live-Updates per WebSocket. Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: Frontend implementiert WebSocket-Verbindung und Subscriptions.

Für die Fotodokumentation wird ein externer Windows-C#-Worker verwendet, der JPEG-Frames an das Backend streamt. Evidence: sensorhub-backend/worker/Program.cs :: StreamDevice/WriteFrame :: Worker erzeugt JPEG-Frames und sendet sie im FRAM-Protokoll.

Der aktuelle Stand ist ein funktionsfähiger Software-Prototyp; formale Tests wurden noch nicht durchgeführt [NOT-TESTED-YET].

Die physische PCB ist noch nicht verfügbar; Hardware-Validierung und vollständiges Deployment sind ausstehend [HARDWARE-NOT-AVAILABLE-YET].

---

## Abstract (English)

This thesis presents a local hydroponics monitoring system that captures, stores, and visualizes sensor data without closed-loop control. Evidence: sensorhub-backend/app/api/setups.py :: capture_reading :: Data capture endpoints only, no control endpoints.

Sensor nodes are based on the Raspberry Pi Pico (RP2040) and measure pH, EC, and temperature. Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN :: Firmware reads pH/EC/temperature.

Node–hub communication uses newline-delimited JSON over USB serial. Evidence: sensornode-firmware/src/main.cpp :: sendJson/handleMessage :: JSON via Serial.

The backend is implemented with FastAPI, persists data in SQLite, and exposes REST and WebSocket endpoints. Evidence: sensorhub-backend/app/main.py :: FastAPI app + /api/live :: FastAPI app with WebSocket endpoint; persistence in db.py.

The web UI is a React/TypeScript frontend with live updates via WebSocket. Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: Frontend WebSocket client.

Photo documentation relies on a Windows C# worker that streams JPEG frames to the backend. Evidence: sensorhub-backend/worker/Program.cs :: StreamDevice/WriteFrame :: Worker streams JPEG frames.

Formal testing has not been executed yet [NOT-TESTED-YET].

The custom PCB is not yet available; hardware validation and full deployment are pending [HARDWARE-NOT-AVAILABLE-YET].

---

## Stichworte / Keywords

**Deutsch:** Hydroponik, Sensor-Monitoring, RP2040, Serial JSON, FastAPI, SQLite, WebSocket

**English:** Hydroponics, Sensor Monitoring, RP2040, Serial JSON, FastAPI, SQLite, WebSocket
