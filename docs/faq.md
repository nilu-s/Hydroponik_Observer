# FAQ

## Wo liegen die Messdaten?

In der SQLite Datenbank unter `data/sensorhub.db`.

## Wo liegen die Fotos?

Unter `data/photos/<setup_id>/`.

## Welche Ports nutzt das System?

- Backend: 8000 (Standard)
- Frontend: Vite Dev Server (Standard 5173)

## Wie exportiere ich alle Daten?

`GET /api/export/all` liefert ein ZIP mit CSV pro Setup.

## Welche Sensoren werden erfasst?

pH, EC und Temperatur (siehe SensorNode Firmware).
