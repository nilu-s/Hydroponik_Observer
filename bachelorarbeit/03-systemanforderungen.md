# 3 Systemanforderungen

## 3.0 Stakeholder & Use-Cases

### Stakeholder

Das System richtet sich primär an:
- **Forscher/Wissenschaftler:** Benötigen präzise, kalibrierte Messwerte für Experimente
- **Hobbygärtner/Enthusiasten:** Möchten ihre Hydroponik-Anlagen überwachen
- **Studierende:** Nutzen das System für Lehrprojekte und Abschlussarbeiten

### Use-Cases

- **UC1:** Live-Überblick über aktuelle Messwerte aller Sensor-Nodes
- **UC2:** Historische Datenanalyse (Trends, Zeitreihen)
- **UC3:** Erkennung von Fehlerzuständen (Node offline, Sensor defekt)
- **UC4:** Konfiguration von Sensoren und Kalibrierung
- **UC5:** Export von Messdaten für externe Analysen (CSV)
- **UC6:** Visuelle Dokumentation des Pflanzenwachstums (Fotos)

---

Die detaillierten Anforderungen sind in separate Dateien ausgelagert:

- [3.1 Customer Requirements (Funktionale Anforderungen)](./03-customer-requirements.md)
- [3.2 Technical Requirements (Technische Anforderungen)](./03-technical-requirements.md)

---

## 3.3 Nicht-funktionale Anforderungen

### Zuverlässigkeit

- **NFR-1:** Das System soll bei kurzzeitigen Netzwerkausfällen weiterarbeiten
- **NFR-2:** Node-Ausfälle sollen erkannt und gemeldet werden
- **NFR-3:** Messdaten dürfen nicht verloren gehen (Persistenz, Dateiformat)

### Wartbarkeit

- **NFR-4:** Der Code soll modular strukturiert sein
- **NFR-5:** Zentrale Komponenten sollen mit Unit-Tests abgedeckt sein
- **NFR-6:** Das System soll gut dokumentiert sein (API, Architektur, Deployment)

### Performance

- **NFR-7:** Das Backend soll Messwerte mit <500ms Response-Zeit verarbeiten
- **NFR-8:** Die UI soll auch bei historischen Abfragen mit 10.000+ Datenpunkten flüssig bleiben
- **NFR-9:** Mehrere Nodes sollen gleichzeitig Daten senden können ohne Blockierung

### Sicherheit

- **NFR-10:** Das Backend soll ein Login-System besitzen (Passwort-basiert)
- **NFR-11:** Sensible Konfigurationsdaten (z.B. Passwörter) sollen nicht im Code stehen
- **NFR-12:** Die API soll Input-Validierung durchführen (SQL-Injection, XSS-Schutz)

## 3.4 Randbedingungen

### Hardware/Netzwerk/Deployment

- **RB-1:** Das System läuft in einem lokalen Netzwerk (WLAN)
- **RB-2:** Die Sensor-Nodes basieren auf ESP32-Mikrocontrollern
- **RB-3:** Das Backend läuft auf einem Raspberry Pi oder Standard-PC
- **RB-4:** Die Nodes müssen Zugriff auf den Hub via HTTP haben
- **RB-5:** Das System benötigt keine Internetverbindung (vollständig lokal)

## 3.5 Akzeptanzkriterien

Eine Anforderung gilt als erfüllt, wenn:

1. **Für MUSS-Anforderungen:**
   - Die Funktionalität ist implementiert
   - Manuelle Tests bestätigen die korrekte Funktion
   - Die Dokumentation beschreibt die Umsetzung

2. **Für SOLL-Anforderungen:**
   - Die Funktionalität ist weitgehend implementiert
   - Bekannte Einschränkungen sind dokumentiert

3. **Für KANN-Anforderungen:**
   - Optional implementiert
   - Falls nicht umgesetzt: Begründung im Ausblick

## 3.3 Nicht-funktionale Anforderungen

### Zuverlässigkeit

[Anforderungen an Uptime, Fehlertoleranz]

### Wartbarkeit

[Code-Qualität, Dokumentation, Testabdeckung]

### Performance

[Response-Zeiten, Datenverarbeitungsraten]

### Sicherheit

[Authentifizierung, Zugriffskontrolle, Datenschutz]

## 3.4 Randbedingungen

### Hardware/Netzwerk/Deployment

[Technische Rahmenbedingungen, Einschränkungen]

## 3.5 Akzeptanzkriterien

[Wann gilt eine Anforderung als erfüllt?]
