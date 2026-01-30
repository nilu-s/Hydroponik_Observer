# 7 Diskussion und Ausblick

## 7.1 Wichtige Designentscheidungen und Alternativen

### Entscheidung 1: Raspberry Pi Pico vs. ESP32

**Gewählt:** Raspberry Pi Pico (RP2040) mit Serial-Kommunikation

**Alternative:** ESP32 mit WLAN/HTTP

**Begründung:**
- **Einfacheres Protokoll**: Serial JSON vs. HTTP/TCP-Stack
- **Zuverlässigkeit**: Kabelgebundene Verbindung (USB) vs. WLAN
- **Kosten**: ~4€ (Pico) vs. ~8€ (ESP32)
- **Stromverbrauch**: Geringer ohne WLAN-Modul

**Trade-Off**: Keine Wireless-Fähigkeit → Nodes müssen per USB verbunden sein

### Entscheidung 2: Node-Hub-Architektur vs. Cloud-First

**Gewählt:** Zentrale Architektur (lokaler Backend-Hub)

**Alternative:** Direct-to-Cloud (MQTT → Cloud-Broker)

**Begründung:**
- **Datenhoheit**: Alle Messdaten bleiben lokal
- **Keine Abhängigkeit**: Funktioniert ohne Internetverbindung
- **Latenz**: <200ms vs. Cloud-Roundtrip (500ms+)
- **Kosten**: Keine laufenden Cloud-Kosten

**Trade-Off**: Kein Remote-Access möglich (ohne VPN/Port-Forwarding)

### Entscheidung 3: SQLite vs. PostgreSQL/TimescaleDB

**Gewählt:** SQLite (Embedded-Datenbank)

**Alternative:** PostgreSQL mit TimescaleDB-Extension

**Begründung:**
- **Deployment**: Single-File DB, keine separate Instanz
- **Ausreichend**: Für 1-10 Nodes und 100.000+ Readings
- **Backup einfach**: DB-Datei kopieren

**Trade-Off**: Keine optimierten Time-Series-Queries (aber mit Index ausreichend)

### Entscheidung 4: Custom PCB vs. Off-the-Shelf-Komponenten

**Gewählt:** Custom PCB (HydroponikPlatine)

**Alternative:** Breadboard/Prototype-Board mit Modulen

**Begründung:**
- **Reproduzierbarkeit**: PCB kann mehrfach gefertigt werden
- **Robustheit**: Verlötete Verbindungen vs. Steckverbindungen
- **Kompaktheit**: Alle Komponenten auf einer Platine

**Trade-Off**: Initiale Entwicklungszeit (~2 Wochen für Design + Tests)

---

## 7.2 Grenzen/Limitierungen des aktuellen Stands

### 7.2.1 Skalierbarkeit

**Limitierung**: Getestet mit maximal 2 Nodes gleichzeitig.

**Potenzielle Probleme bei 10+ Nodes:**
- Serial-Port-Management: Python `pyserial` könnte Limits erreichen
- Discovery-Loop: Bei 20+ Ports dauert Scan >10 Sekunden
- SQLite Write-Locks: Bei vielen gleichzeitigen Inserts (>100/s)

**Mögliche Lösung:**
- Sharding: Mehrere SQLite-Datenbanken (pro Setup)
- Oder: Umstieg auf PostgreSQL

### 7.2.2 Sicherheit

**Aktueller Stand:**
- ⚠️ Keine Benutzer-Authentifizierung
- ⚠️ Keine Verschlüsselung (HTTP, nicht HTTPS)
- ⚠️ CSRF-Schutz nur über Token/Origin-Check

**Risiken:**
- Jeder im lokalen Netzwerk kann auf alle Daten zugreifen
- Manipulation von Messwerten möglich (über API)

**Akzeptabel für:**
- Private Heimnetzwerke
- Universitäts-/Forschungs-Labore (isoliertes LAN)

**Nicht akzeptabel für:**
- Öffentliche Netzwerke
- Multi-Tenant-Szenarien

### 7.2.3 Kalibrierungs-UX

**Aktueller Stand:**
- Kalibrierung erfolgt über JSON-Payload in API-Request
- Keine grafische Kalibrierungs-Wizard im Frontend

**Problem:**
- Benutzer muss manuell Rohwerte ablesen und Kalibrierungspunkte definieren
- Fehleranfällig (falsche Formate, falsche Werte)

**Verbesserungsvorschlag:**
- Frontend-Wizard: "Elektrode in pH 7.0 tauchen → Messwert ablesen → Weiter"
- Automatische Berechnung der Kalibrier-Polynome

### 7.2.4 Deployment

**Aktueller Stand:**
- Manuelle Installation (Python, Node.js, Dependencies)
- Keine automatisierten Updates
- Kein systemd/Windows-Service für Auto-Start

**Problem:**
- Für Nicht-Techniker schwierig zu installieren

**Verbesserungsvorschlag:**
- Docker-Container (`docker-compose up`)
- Installer-Paket für Windows/Linux

### 7.2.5 Langzeit-Stabilität

**Aktueller Stand:**
- Getestet bis 48 Stunden Dauerbetrieb
- Keine Tests >1 Woche

**Potenzielle Probleme:**
- Memory-Leaks (Python/JavaScript)
- SQLite-Datenbank-Größe (100 MB+ nach 6 Monaten?)
- Serial-Port-Handles bleiben offen?

**Nächste Schritte:**
- 1-Wochen-Testlauf unter Beobachtung
- Profiling mit `memory_profiler` (Python)

---

## 7.3 Ausblick

### 7.3.1 Kurzfristige Erweiterungen (1-3 Monate)

#### Plausibilitäts-Checks in Firmware

```cpp
if (ph < 0.0 || ph > 14.0) {
  status.add("ph_out_of_range");
}
if (ec < 0.0 || ec > 10.0) {
  status.add("ec_out_of_range");
}
```

**Aufwand**: 1 Tag

#### WebSocket Auto-Reconnect im Frontend

```typescript
class LiveWsClient {
  connect() {
    this.ws = new WebSocket(url);
    this.ws.onerror = () => {
      setTimeout(() => this.connect(), 2000);  // Retry nach 2s
    };
  }
}
```

**Aufwand**: 1 Tag

#### Alarmierung (Email/Push)

Benachrichtigung bei:
- Node offline >5 Minuten
- Messwerte außerhalb Grenzwerte
- Kamera nicht verfügbar

**Technologie**: SMTP (Email), Firebase Cloud Messaging (Push)

**Aufwand**: 3-5 Tage

### 7.3.2 Mittelfristige Erweiterungen (3-6 Monate)

#### Authentifizierung & Autorisierung

- **Login-System**: Passwort-Hash (bcrypt)
- **Session-Tokens**: JWT oder HTTP-only Cookies
- **HTTPS**: Let's Encrypt Zertifikate

**Aufwand**: 5-7 Tage

#### Mobile App (React Native)

- **Plattformen**: iOS + Android
- **Features**: Live-Dashboard, Push-Notifications, Photo-View

**Aufwand**: 3-4 Wochen

#### Erweiterte Datenanalyse

- **Trends**: Lineare Regression für pH/EC über Zeit
- **Prognosen**: "EC wird in 2 Tagen kritisch niedrig"
- **Anomalie-Erkennung**: Automatische Warnung bei ungewöhnlichen Mustern

**Technologie**: Python `scikit-learn`, `prophet`

**Aufwand**: 2-3 Wochen

### 7.3.3 Langfristige Vision (6-12 Monate)

#### Multi-Tenancy & Cloud-Deployment

- **Mehrere Benutzer**: Jeder mit eigenen Setups/Nodes
- **SaaS-Modell**: Gehostete Instanz mit Subscriptions
- **Cloud-Backend**: AWS Lambda + DynamoDB

**Trade-Off**: Höhere Komplexität, laufende Kosten

#### Integration mit Regelungssystemen

- **Automatische Dosierung**: pH-Dosierung basierend auf Messwerten
- **Hardware-Integration**: Relais-Steuerung (Pumpen, Ventile)
- **PID-Controller**: Regelkreise für optimale Bedingungen

**Achtung**: Übergang von "Monitoring" zu "Automation" → höhere Sicherheitsanforderungen!

#### Open-Source-Community

- **GitHub**: Code veröffentlichen (MIT-Lizenz)
- **Dokumentation**: Umfassendes Wiki, Video-Tutorials
- **Hardware**: PCB-Design veröffentlichen (Open Hardware)

**Ziel**: Community-Beiträge, Plugins, alternative Sensoren

---

## 7.4 Zusammenfassung

Das entwickelte System erfüllt die Kern-Anforderungen eines **Hydroponik-Monitoring-Systems** erfolgreich. Die gewählte Architektur (Node-Hub mit Serial-Kommunikation) hat sich als **robust und einfach zu warten** erwiesen.

**Haupterkenntnisse:**
1. **Serial > WLAN** für Zuverlässigkeit in Embedded-Szenarien
2. **Lokales System** bietet Datenhoheit ohne Cloud-Abhängigkeit
3. **SQLite** ausreichend für Kleinanlagen (1-10 Nodes)
4. **Custom PCB** erhöht Reproduzierbarkeit und Robustheit

**Nächste Schritte für Produktiv-Einsatz:**
- Langzeit-Stabilitäts-Tests (1+ Woche)
- Plausibilitäts-Checks implementieren
- WebSocket-Reconnect
- Docker-Deployment

**Potenzial für Weiterentwicklung:**
- Mobile App
- Erweiterte Analyse & Prognosen
- Open-Source-Community
