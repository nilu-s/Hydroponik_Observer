# Konfiguration

Diese Datei beschreibt relevante Konfigurationsoptionen des Backends.

## Environment Variablen

- `ADMIN_RESET_TOKEN` (string): Pflicht-Token fuer `POST /api/admin/reset`.
  Wenn nicht gesetzt oder leer, ist der Reset deaktiviert (HTTP 403).
- `CSRF_TOKEN` (string): Optionaler CSRF-Token fuer Requests ohne `Origin`.
- `CORS_ALLOW_ORIGINS` (csv): Kommagetrennte Liste der erlaubten Origins.
- `CSRF_TRUSTED_ORIGINS` (csv): Wenn gesetzt, wird `Origin` gegen diese Liste geprueft.
- `NODE_SCAN_INTERVAL_SEC` (float): Discovery-Intervall fuer Nodes.
- `CAMERA_SCAN_INTERVAL_SEC` (float): Discovery-Intervall fuer Kameras.
- `LIVE_POLL_INTERVAL_SEC` (float): Polling-Intervall fuer Live-Readings.
- `PHOTO_CAPTURE_POLL_INTERVAL_SEC` (float): Polling-Intervall fuer automatische Fotos.
- `CAMERA_WORKER_PATH` (string): Optionaler Pfad zum Camera-Worker-Binary.
- `CAMERA_WORKER_MAX_PER_DEVICE` (int): Max. Worker pro Kamera.
- `CAMERA_WORKER_MAX_TOTAL` (int): Max. Worker gesamt.

## Feste Konstanten (nicht per ENV konfigurierbar)

- `DEFAULT_VALUE_INTERVAL_MINUTES` = 30
- `DEFAULT_PHOTO_INTERVAL_MINUTES` = 720
- `SERIAL_BAUDRATE` = 115200
- `SERIAL_TIMEOUT_SEC` = 1.5
- `SERIAL_OPEN_DELAY_SEC` = 0.4
- `SERIAL_HANDSHAKE_TIMEOUT_SEC` = 4.0
- `LIVE_MIN_FPS` = 5
- `LIVE_MAX_FPS` = 10
- `CAMERA_WORKER_TIMEOUT_SEC` = 10
