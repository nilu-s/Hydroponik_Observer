# REST API

Basis: `http://<sensorhub-backend>/api` (z.B. `http://localhost:8000/api`)

Alle JSON-Responses sind UTF-8. Fehler liefern HTTP-Status und eine JSON-Response
im FastAPI-Standard: `{ "detail": "..." }`.

## Hinweise

- Zeitstempel (`ts`, `createdAt`, `lastSeenAt`) sind Unix Epoch in Millisekunden.
- `status_json` ist ein JSON-String, der ein Array enthaelt (z.B. `["ok"]`).
- Nullable Felder koennen `null` sein (z.B. `cameraPort`, `port`).
- Auth: Alle Endpunkte benoetigen `Authorization: Bearer <JWT>`.
  - Der JWT muss eine `role` oder `roles`-Claim enthalten (`viewer`, `operator`, `admin`).
  - Schreiboperationen benoetigen mind. `operator`, gefaehrliche Loeschungen `admin`.
- CSRF: Für `POST/PUT/PATCH/DELETE` wird bei fehlendem `Origin` ein Header
  `X-CSRF-Token` erwartet.

## Setups

- `GET /setups` -> Liste aller Setups
  - Response: `{ setupId, name, port, cameraPort, valueIntervalMinutes, photoIntervalMinutes, createdAt }[]`
  - `valueIntervalMinutes` und `photoIntervalMinutes` sind Minutenwerte (Defaults aus Backend).
- `POST /setups` -> Setup anlegen
  - Body: `{ "name": "Setup A" }`
  - Response: `{ setupId, name, port, cameraPort, valueIntervalMinutes, photoIntervalMinutes, createdAt }`
- `PATCH /setups/{setupId}` -> Setup aktualisieren
  - Body: `{ "name"?, "port"?, "cameraPort"?, "valueIntervalMinutes"?, "photoIntervalMinutes"? }`
  - Response: `{ setupId, name, port, cameraPort, valueIntervalMinutes, photoIntervalMinutes, createdAt }`
  - Fehler: `400` wenn `cameraPort` gesetzt wird, die Kamera aber nicht existiert.
- `DELETE /setups/{setupId}` -> Setup loeschen
  - Response: `{ ok, deleted, deletedPhotos }`
  - `deleted` ist `false`, wenn das Setup nicht existiert.

## Readings

- `GET /setups/{setupId}/reading` -> Live Messung (ueber Node)
  - Response: `{ ts, ph, ec, temp, status }`
- `POST /setups/{setupId}/capture-reading` -> Messung lesen + speichern
  - Response: `{ ts, ph, ec, temp, status }`
- `GET /setups/{setupId}/history?limit=200` -> Historie (readings + photos)
  - Response: `{ readings, photos }`
  - `readings[]`: `{ id, setup_id, node_id, ts, ph, ec, temp, status_json }`
  - `photos[]`: `{ id, setup_id, camera_id, ts, path }`
  - Sortierung: `readings` nach `ts` absteigend, `photos` nach `ts` aufsteigend.

## Photos / Camera

- `POST /setups/{setupId}/capture-photo` -> Foto aufnehmen + speichern
  - Response: `{ ok, photo }`
  - `photo`: `{ ts, path, cameraId }`
- `GET /setups/{setupId}/camera/snapshot` -> Einzelsnapshot (JPEG)
- `GET /setups/{setupId}/camera/stream` -> MJPEG Stream

## Nodes

- `GET /nodes` -> Liste erkannter Nodes
  - Response: `{ port, alias, kind, fw, capJson, mode, lastSeenAt, status, lastError }[]`
- `GET /nodes/ports` -> Serial Port Kandidaten (RP2040)
  - Response: `{ device, name, description, hwid, manufacturer, serial_number, vid, pid, location, interface }[]`
- `PATCH /nodes/{port}` -> Alias setzen
  - Body: `{ "alias": "Node A" }`
  - Response: `{ port, alias, kind, fw, capJson, mode, lastSeenAt, status, lastError }`
- `DELETE /nodes/{port}` -> Node loeschen
  - Response: `{ ok, affectedSetups, deletedPhotos }`
  - Fehler: `404` wenn Node nicht existiert.
- `POST /nodes/{port}/command` -> Serial Command
  - Body je nach `t`:
    - `{ "t": "hello" }`
    - `{ "t": "get_all" }`
    - `{ "t": "set_mode", "mode": "real" | "debug" }`
    - `{ "t": "set_sim", "simPh"?, "simEc"?, "simTemp"? }`
  - Response: `{ ok }` oder Node-Antwort, je nach Command

## Cameras

- `GET /cameras/devices` -> Kamera-Liste (Worker Scan)
  - Response: `{ cameraId, deviceId, alias?, pnpDeviceId?, containerId?, friendlyName?, status? }[]`
  - `status` ist typischerweise `online` oder `offline`.
- `PATCH /cameras/{cameraId}` -> Alias setzen
  - Body: `{ "alias": "Kamera X" }`
  - Response: `{ cameraId, deviceId?, alias?, pnpDeviceId?, containerId?, friendlyName?, status? }`
- `DELETE /cameras/{cameraId}` -> Kamera entfernen
  - Response: `{ ok }`

## Export

- `GET /export/all` -> ZIP Export mit CSV pro Setup
  - Struktur: `setups/<setupId>/readings.csv` und `setups/<setupId>/meta.txt`

## Admin

- `POST /admin/reset` -> DB und Runtime reset
  - Header: `X-Reset-Token: <ADMIN_RESET_TOKEN>`

## WebSocket Live

- `WS /live` -> Live Updates
  - Auth per `Authorization: Bearer <JWT>` oder Query `?token=<JWT>`

## Beispiele

### Setup anlegen

Request Body:
```json
{ "name": "Setup A" }
```

Response:
```json
{
  "setupId": "S1a2b3c4d",
  "name": "Setup A",
  "port": null,
  "cameraPort": null,
  "valueIntervalMinutes": 10,
  "photoIntervalMinutes": 30,
  "createdAt": 1769608113000
}
```

### Setup aktualisieren (Intervalle + Kamera)

Request Body:
```json
{ "cameraPort": "usb1234", "valueIntervalMinutes": 5, "photoIntervalMinutes": 15 }
```

Response:
```json
{
  "setupId": "S1a2b3c4d",
  "name": "Setup A",
  "port": "COM4",
  "cameraPort": "usb1234",
  "valueIntervalMinutes": 5,
  "photoIntervalMinutes": 15,
  "createdAt": 1769608113000
}
```

### History abrufen

Response:
```json
{
  "readings": [
    { "id": 12, "setup_id": "S1a2b3c4d", "node_id": "COM4", "ts": 1769608113000, "ph": 6.4, "ec": 1.6, "temp": 22.1, "status_json": "[\"ok\"]" }
  ],
  "photos": [
    { "id": 1769608113123, "setup_id": "S1a2b3c4d", "camera_id": "usb1234", "ts": 1769608113123, "path": "/data/photos/S1a2b3c4d/S1a2b3c4d_2026-01-28_14-48-33.jpg" }
  ]
}
```

### Kamera Devices (GET /cameras/devices)

Response:
```json
[
  {
    "cameraId": "usb1234",
    "deviceId": "usb1234",
    "alias": "Kamera USB",
    "pnpDeviceId": "USB\\VID_046D&PID_0825",
    "friendlyName": "Logitech HD",
    "containerId": "{...}",
    "status": "online"
  }
]
```

### Nodes (GET /nodes)

Response:
```json
[
  {
    "port": "COM4",
    "alias": "Node A",
    "kind": "real",
    "fw": "pico-0.1.0",
    "capJson": "{\"ph\":true,\"ec\":true,\"temp\":true}",
    "mode": "real",
    "lastSeenAt": 1769608113000,
    "status": "online",
    "lastError": null
  }
]
```

### Fehlerbeispiel

Response:
```json
{ "detail": "setup not found" }
```

### Node Command (set_mode)

Request Body:
```json
{ "t": "set_mode", "mode": "debug" }
```

Response:
```json
{ "ok": true }
```

### Kamera Snapshot

Response:
- Status: `200`
- Content-Type: `image/jpeg`

### Foto aufnehmen (POST /setups/{setupId}/capture-photo)

Response:
```json
{
  "ok": true,
  "photo": {
    "ts": 1769608113123,
    "path": "/data/photos/S1a2b3c4d/S1a2b3c4d_2026-01-28_14-48-33.jpg",
    "cameraId": "usb1234"
  }
}
```

### Node Command (get_all)

Request Body:
```json
{ "t": "get_all" }
```

Response (Beispiel):
```json
{
  "t": "all",
  "ts": 1769608113000,
  "mode": "real",
  "status": ["ok"],
  "ph": 6.5,
  "ec": 1.7,
  "temp": 22.1
}
```

### Kamera Stream

Response:
- Status: `200`
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
