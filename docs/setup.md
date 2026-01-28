# Setup und Installation

Diese Seite beschreibt die lokalen Voraussetzungen und den Start der Komponenten.

## Voraussetzungen

- Python 3.11+ fuer das Backend
- Node.js 18+ fuer das Frontend
- PlatformIO Core fuer die Firmware
- USB Zugriff auf den RP2040 (Pico)

## Backend starten

```powershell
cd "sensorhub-backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend starten

```powershell
cd "sensorhub-frontend"
npm install
npm run dev
```

## Firmware bauen und flashen

```powershell
cd "sensornode-firmware"
pio run
pio run -t upload
```

Optionaler Upload-Port:

```powershell
pio run -t upload --upload-port COM3
```

## Erste Schritte

1. Backend starten.
2. Frontend starten.
3. SensorNode anschliessen und kurz warten, bis die Node erkannt wird.
4. Im Frontend ein Setup anlegen und Port/Kamera zuweisen.
