# 4 Gesamtarchitektur des SensorHUB-Systems

## 4.1 Systemübersicht und Komponenten

### Sensornode-Firmware

[ESP32-basierte Firmware für Sensorerfassung]

### Backend

[FastAPI-Backend für Datenverwaltung und API]

### Frontend

[React-Frontend für Visualisierung]

## 4.2 Schnittstellen- und Kommunikationsübersicht

[Diagramm: Node → Backend → Frontend, Protokolle]

## 4.3 Laufzeit- und Deployment-Sicht

### Lokale Services

[Wie werden die Komponenten deployed?]

### Netzwerk-Topologie

[WLAN, lokales Netzwerk, Port-Konfiguration]

## 4.4 Begründung zentraler Architekturentscheidungen

### Warum FastAPI?

[Performance, async, Type-Safety]

### Warum React?

[Komponenten-basiert, Ecosystem, WebSocket-Support]

### Warum SQLite?

[Embedded, einfaches Deployment, ausreichend für Use-Case]

## 4.5 Hardware-Design

### PCB-Design (KiCad)

[Schaltplan, Layout, Komponenten]

### Sensorauswahl

[pH, EC/TDS, Temperatur, Wasserstand - Begründung der Wahl]

### Mikrocontroller (ESP32)

[Technische Spezifikationen, GPIO-Belegung]
