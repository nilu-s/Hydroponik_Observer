# Protokolle

Diese Datei beschreibt die genutzten Protokolle zwischen Firmware, Backend,
Frontend und Camera Worker.

## 1) Serial JSON Line Protocol (Firmware <-> Backend)

Transport: UART/USB Serial, 115200 Baud. Jede Nachricht ist eine JSON-Zeile
(`\n`-terminiert).

### Handshake

**Node -> Backend**
```json
{"t":"hello","fw":"pico-0.1.0","cap":{"ph":true,"ec":true,"temp":true,"debug":true,"calib":true,"pins":{"ph":"adc2","ec":"adc0","temp":"gpio17"}},"calibHash":"default"}
```

**Backend -> Node**
```json
{"t":"hello_ack","fw":"pico-0.1.0","cap":{...},"calibHash":"default"}
```

### Messwerte

**Backend -> Node**
```json
{"t":"get_all"}
```

**Node -> Backend**
```json
{"t":"all","ts":123456,"mode":"real","status":["ok"],"ph":6.5,"ec":1.7,"temp":22.1}
```

### Node Modus

**Backend -> Node**
```json
{"t":"set_mode","mode":"debug"}
```

### Debug Simulation

**Backend -> Node**
```json
{"t":"set_sim","ph":6.4,"ec":1.5,"temp":21.8}
```

### Kalibrierung

**Backend -> Node**
```json
{"t":"set_calib","version":1,"payload":{"ph":{"points":[{"raw":0.0,"val":0.0},{"raw":1.65,"val":7.0},{"raw":3.3,"val":14.0}]},"ec":{"points":[{"raw":0.0,"val":0.0},{"raw":3.3,"val":5.0}]},"calibHash":"abc123"}}
```

**Node -> Backend**
```json
{"t":"set_calib_ack"}
```

## 2) WebSocket Protocol (Frontend <-> Backend)

Endpoint: `ws://<backend>/api/live`

### Frontend -> Backend
```json
{"t":"sub","setupId":"S12345678"}
{"t":"unsub","setupId":"S12345678"}
```

### Backend -> Frontend
```json
{"t":"reading","setupId":"S12345678","ts":123456,"ph":6.5,"ec":1.7,"temp":22.1,"status":["ok"]}
{"t":"cameraDevices","devices":[{"cameraId":"usb1234","deviceId":"usb1234","alias":"Kamera USB","pnpDeviceId":"USB\\VID_046D&PID_0825","friendlyName":"Logitech HD","containerId":"{...}","status":"online"}]}
{"t":"reset","reason":"db-reset"}
{"t":"error","setupId":"S12345678","msg":"setup missing"}
{"t":"error","msg":"unknown message"}
```

## 3) Camera Worker Protocol (Backend <-> Worker)

Der Camera Worker liefert zwei Modi:

- `--list` gibt JSON mit Kamera-Infos auf Stdout aus.
- `--device <id>` streamt Frames als Binary-Stream.

### Frame Header (Binary)

Header-Len: 32 Bytes. Reihenfolge (Little Endian):

- Magic: 4 Bytes (`FRAM`)
- Version: 2 Bytes
- HeaderLen: 2 Bytes
- Sequence: 8 Bytes
- TimestampMs: 8 Bytes
- DeviceIdLen: 2 Bytes
- MimeLen: 2 Bytes
- PayloadLen: 4 Bytes

Danach folgen:

1. DeviceId UTF-8 Bytes
2. MIME UTF-8 Bytes (z.B. `image/jpeg`)
3. JPEG Payload

## 4) HTTP REST (Frontend <-> Backend)

REST nutzt JSON ueber HTTP. Details siehe `api.md`.
