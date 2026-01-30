# Offene TODOs (extern zur Bachelorarbeit)

Diese Datei bündelt alle offenen Arbeitsschritte und ist **kein** Teil der Bachelorarbeit.

## Must

- [TODO] Testplan aus `bachelorarbeit/06-test-und-evaluation.md` durchführen und dokumentieren (Backend, Firmware, Frontend).
- [TODO] Hardware-Validierung nach PCB-Lieferung: Sensorpfade, ADC, OneWire, USB-Serial (`sensornode-firmware/src/main.cpp`).
- [TODO] Testprotokolle und Messbeispiele ergänzen (`bachelorarbeit/09-anhang.md`).

## Should

- [TODO] Langzeittest (>= 7 Tage) definieren und durchführen (Backend-Logs, Datenkonsistenz).
- [TODO] Performance-Tests für API und DB-Queries durchführen (`sensorhub-backend/app/api/setups.py`, `sensorhub-backend/app/db.py`).
- [TODO] Kalibrierungs-UI/Wizard spezifizieren und implementieren (`sensorhub-frontend/src/`).
- [TODO] Authentifizierungskonzept definieren und umsetzen (`sensorhub-backend/app/main.py`, `sensorhub-backend/app/api/*`).

## Could

- [TODO] Alarmierung für Offline/Out-of-Range ergänzen (Backend + Frontend).
- [TODO] Deployment-Automation (z.B. Docker/Installer) erstellen (`docs/` + Skripte).
- [TODO] Related-Work/Literaturvergleich ausarbeiten (`bachelorarbeit/02-grundlagen.md`, `bachelorarbeit/08-literaturverzeichnis.md`).
