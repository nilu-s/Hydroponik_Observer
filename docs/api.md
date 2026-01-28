# REST API

Basis: `http://<backend>/api`

Alle JSON-Responses sind UTF-8. Fehler liefern HTTP-Status und eine Textnachricht.

## Setups

- `GET /setups` -> Liste aller Setups
  - Response: `{ setupId, name, port, cameraPort, valueIntervalMinutes, photoIntervalMinutes, createdAt }[]`
- `POST /setups` -> Setup anlegen
  - Body: `{ "name": "Setup A" }`
  - Response: `{ setupId, name, port, cameraPort, valueIntervalMinutes, photoIntervalMinutes, createdAt }`
- `PATCH /setups/{setupId}` -> Setup aktualisieren
  - Body: `{ "name"?, "port"?, "cameraPort"?, "valueIntervalMinutes"?, "photoIntervalMinutes"? }`
  - Response: `{ setupId, name, port, cameraPort, valueIntervalMinutes, photoIntervalMinutes, createdAt }`
- `DELETE /setups/{setupId}` -> Setup loeschen
  - Response: `{ ok, deleted, deletedPhotos }`

## Readings

- `GET /setups/{setupId}/reading` -> Live Messung (ueber Node)
  - Response: `{ ts, ph, ec, temp, status }`
- `POST /setups/{setupId}/capture-reading` -> Messung lesen + speichern
  - Response: `{ ts, ph, ec, temp, status }`
- `GET /setups/{setupId}/history?limit=200` -> Historie (readings + photos)
  - Response: `{ readings, photos }`
  - `readings[]`: `{ id, setup_id, node_id, ts, ph, ec, temp, status_json }`
  - `photos[]`: `{ id, setup_id, camera_id, ts, path }`

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
- `PATCH /cameras/{cameraId}` -> Alias setzen
  - Body: `{ "alias": "Kamera X" }`
  - Response: `{ cameraId, deviceId?, alias?, pnpDeviceId?, containerId?, friendlyName?, status? }`
- `DELETE /cameras/{cameraId}` -> Kamera entfernen
  - Response: `{ ok }`

## Export

- `GET /export/all` -> ZIP Export mit CSV pro Setup

## Admin

- `POST /admin/reset` -> DB und Runtime reset
  - Header: `X-Reset-Token: reset123`
