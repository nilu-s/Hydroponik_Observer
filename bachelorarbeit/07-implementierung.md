# 7 Implementierung

## 7.1 Repository-/Projektstruktur und Build/Tooling

### Repository-Struktur

```
Hydroponik_Observer/
├── sensornode-firmware/    (PlatformIO, C++)
├── sensorhub-backend/       (FastAPI, Python)
├── sensorhub-frontend/      (React, TypeScript)
├── HydroponikPlatine/       (KiCad PCB)
└── docs/                    (Dokumentation)
```

### Build/Tooling

- **Firmware:** PlatformIO
- **Backend:** Poetry / pip, pytest
- **Frontend:** npm, Vite, React

## 7.2 Sensornode-Firmware

### Sensoranbindung

[Wie werden Sensoren ausgelesen? ADC, Digital, I2C/SPI?]

### Sampling

[Sampling-Rate, Averaging, Filtering]

### Kalibrierung

[Wie wird Kalibrierung auf dem Node durchgeführt/gespeichert?]

### Kommunikation

[HTTP POST an Backend, Error-Handling, Retry-Logik]

## 7.3 Sensorhub-Backend

### Datenannahme

[POST /api/nodes/{id}/readings Endpoint]

### Verarbeitung

[Validierung, Plausibilisierung, Transformation]

### Persistenz

[SQLAlchemy ORM, Transactions]

### API

[FastAPI Routers, Dependency Injection]

## 7.4 Sensorhub-Frontend

### Visualisierung

[Charts, Live-Updates, Komponenten-Struktur]

### Dashboards

[HomePage: Übersicht über alle Nodes/Setups]

### Zustände/Fehler

[Anzeige von Node-Status, Fehlermeldungen]

## 7.5 Logging, Monitoring, Fehlerbehandlung

### Logging

[Python logging, Log-Levels, strukturierte Logs]

### Monitoring

[Health-Checks, Metriken]

### Fehlerbehandlung

[Exception-Handling, User-Feedback]
