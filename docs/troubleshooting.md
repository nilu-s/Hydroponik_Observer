# Troubleshooting

Typische Fehlerbilder und Loesungen.

## Node wird nicht erkannt

- USB Kabel pruefen (Datenkabel)
- COM Port in `GET /nodes/ports` sichtbar?
- SensorNode neu anstecken und Backend-Logs pruefen

## Livewerte bleiben leer

- Setup hat keinen Port zugewiesen
- Node ist offline (siehe `GET /nodes`)
- Serial Kommunikation pruefen (Baudrate 115200)

## Kamera offline oder kein Bild

- Kamera in `GET /cameras/devices` sichtbar?
- Kamera im Setup zugewiesen?
- Worker startet? Backend-Logs pruefen

## Frontend zeigt keine Livewerte

- WebSocket erreichbar (`/api/live`)
- Browser Console auf Fehler pruefen
- Backend laeuft und ist erreichbar (CORS/URL)

## Admin Reset funktioniert nicht

- Header `X-Reset-Token` gesetzt?
- Token stimmt mit Konfiguration ueberein?
