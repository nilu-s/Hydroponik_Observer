# Betrieb und Deployment

Diese Seite beschreibt den Betrieb im lokalen Setup und Hinweise zur Dauerlauf-Umgebung.

## Startreihenfolge (lokal)

1. Backend starten.
2. Frontend starten.
3. SensorNode anschliessen.
4. Kamera anschliessen (falls genutzt).

## Datenpfade

- SQLite: `data/sensorhub.db`
- Fotos: `data/photos/<setup_id>/`

## Autostart (Windows)

Moegliche Optionen:

- Task Scheduler mit zwei Tasks (Backend, Frontend)
- Batch/PowerShell Skript, das beide Prozesse startet

Beispiel (PowerShell, manuell):

```powershell
cd "sensorhub-backend"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

```powershell
cd "sensorhub-frontend"
npm run dev
```

## Backup

- Datenbank regelmaessig sichern (`data/sensorhub.db`)
- Fotos nach Bedarf kopieren (`data/photos/`)
