# Konfiguration

Diese Seite beschreibt wichtige Konfigurationspunkte im Backend und Betrieb.

## Backend Konfiguration

Die Backend-Konfiguration wird in `sensorhub-backend/app/config.py` gepflegt.

Typische Parameter:

- DB Pfad (SQLite)
- Foto-Verzeichnis
- Default-Intervalle fuer Messungen und Fotos
- Reset-Token fuer Admin-Reset
- Pfad/Location fuer den Camera Worker

## Kamera Worker

Der Camera Worker wird vom Backend gestartet. Falls der Worker nicht gefunden wird,
pruefe den Worker-Pfad in der Konfiguration sowie die vorhandenen Dateien in
`sensorhub-backend/worker/`.

## Reset Token

Der Admin-Reset Endpunkt verlangt einen Header `X-Reset-Token`. Stelle sicher,
dass der Token nicht oeffentlich geteilt wird, wenn das System erreichbar ist.
