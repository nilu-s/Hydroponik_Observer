# Konfiguration

Diese Seite beschreibt wichtige Konfigurationspunkte im Backend und Betrieb.

## Backend Konfiguration

Die Backend-Konfiguration wird in `sensorhub-backend/app/config.py` gepflegt.

Typische Parameter:

- DB Pfad (SQLite)
- Foto-Verzeichnis
- Default-Intervalle fuer Messungen und Fotos
- Reset-Token fuer Admin-Reset (ENV `ADMIN_RESET_TOKEN`)
- Pfad/Location fuer den Camera Worker
- Worker-Limits fuer Kamera-Streams (ENV `CAMERA_WORKER_MAX_PER_DEVICE`, `CAMERA_WORKER_MAX_TOTAL`)
- Poll-Intervalle (ENV `NODE_SCAN_INTERVAL_SEC`, `CAMERA_SCAN_INTERVAL_SEC`, `LIVE_POLL_INTERVAL_SEC`, `PHOTO_CAPTURE_POLL_INTERVAL_SEC`)
- JWT Konfiguration (ENV `JWT_SECRET`, optional `JWT_ISSUER`, `JWT_AUDIENCE`)
- CORS/CSRF (ENV `CORS_ALLOW_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `CSRF_TOKEN`)

## Kamera Worker

Der Camera Worker wird vom Backend gestartet. Falls der Worker nicht gefunden wird,
pruefe den Worker-Pfad in der Konfiguration sowie die vorhandenen Dateien in
`sensorhub-backend/worker/`.

## Reset Token

Der Admin-Reset Endpunkt verlangt einen Header `X-Reset-Token`. Stelle sicher,
dass der Token nicht oeffentlich geteilt wird, wenn das System erreichbar ist.
Der Token wird ueber die Umgebungsvariable `ADMIN_RESET_TOKEN` gesetzt.

## Auth

Alle API-Routen benoetigen ein JWT im Header `Authorization: Bearer <JWT>`.
Der JWT muss eine `role` oder `roles`-Claim enthalten. Erlaubte Rollen:
`viewer`, `operator`, `admin`.

## CORS/CSRF

Die erlaubten Origins kommen aus `CORS_ALLOW_ORIGINS` (kommasepariert).
CSRF kann ueber `CSRF_TRUSTED_ORIGINS` (kommasepariert) oder `CSRF_TOKEN`
abgesichert werden.
