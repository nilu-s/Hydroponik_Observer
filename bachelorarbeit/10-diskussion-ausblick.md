# 10 Diskussion und Ausblick

## 10.1 Wichtige Designentscheidungen und Alternativen

### Entscheidung 1: Zentrale vs. Dezentrale Architektur

**Gewählt:** Zentrale Architektur (Backend als Hub)

**Alternative:** Dezentral mit Peer-to-Peer

**Begründung:** [...]

### Entscheidung 2: REST vs. MQTT

**Gewählt:** REST API

**Alternative:** MQTT Broker

**Begründung:** [...]

### Entscheidung 3: SQLite vs. PostgreSQL

**Gewählt:** SQLite

**Alternative:** PostgreSQL, TimescaleDB

**Begründung:** [...]

## 10.2 Grenzen/Limitierungen des aktuellen Stands

### Skalierbarkeit

[Limitierungen bei sehr vielen Nodes/hoher Frequenz]

### Sicherheit

[Keine Authentifizierung, keine Verschlüsselung]

### Kalibrierungs-UX

[Verbesserungspotenzial in der Benutzerführung]

### Deployment

[Manuelle Installation, keine Container/Docker]

## 10.3 Ausblick

### Roadmap

#### Kurzfristig

- Implementierung von Alarmierung (Email/Push)
- Verbesserte Kalibrierungs-UX
- Docker-Container für einfaches Deployment

#### Mittelfristig

- Authentifizierung und Zugriffskontrolle
- Mobile App (React Native)
- Erweiterte Datenanalyse (Trends, Prognosen)

#### Langfristig

- Multi-Tenancy (mehrere Benutzer/Anlagen)
- Cloud-Deployment
- Integration mit Regelungssystemen
