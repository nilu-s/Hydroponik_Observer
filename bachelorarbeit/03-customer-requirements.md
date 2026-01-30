# 3.1 Customer Requirements (Funktionale Anforderungen)

Diese Anforderungen beschreiben die funktionalen Eigenschaften des Systems aus Anwendersicht.

## Übersicht

| ID | Beschreibung | Priorität | Requirement | Status |
|----|--------------|-----------|-------------|--------|
| CR-01 | Das System soll Hydroponik-Versuchsaufbauten überwachen | MUSS | Gesamtsystem | ✅ Erfüllt |
| CR-02 | Der pH-Wert der Nährlösung soll überwacht werden | MUSS | pH-Überwachung | ✅ Erfüllt |
| CR-03 | Die elektrische Leitfähigkeit der Nährlösung soll überwacht werden | MUSS | EC-Überwachung | ✅ Erfüllt |
| CR-04 | Die Temperatur der Nährlösung soll überwacht werden | MUSS | Temperaturüberwachung | ✅ Erfüllt |
| CR-05 | Alle Messwerte sollen kalibriert erfasst werden | MUSS | Messgenauigkeit | ✅ Erfüllt |
| CR-06 | Messwerte sollen automatisch zyklisch erfasst werden | MUSS | Zyklische Messung | ✅ Erfüllt |
| CR-07 | Das System soll ohne Benutzeroberfläche funktionsfähig sein | SOLL | Minimalbetrieb | ✅ Erfüllt |
| CR-08 | Messdaten sollen an eine zentrale Einheit übertragen werden | MUSS | Datenübertragung | ✅ Erfüllt |
| CR-09 | Das System muss mindestens zwei Sensor Nodes parallel betreiben können | MUSS | Multi-Node | ✅ Erfüllt |
| CR-10 | Kurzzeitige Ausfälle sollen toleriert werden (Auto-Reconnect) | SOLL | Fehlertoleranz | ✅ Erfüllt |
| CR-11 | Das System soll über längere Zeiträume stabil betrieben werden können | SOLL | Langzeitbetrieb | ⚠️ Teilweise |
| CR-12 | Das System soll um weitere Sensor Nodes erweiterbar sein | SOLL | Erweiterbarkeit | ✅ Erfüllt |
| CR-13 | Messdaten sollen dauerhaft gespeichert werden (persistent) | MUSS | Persistierung | ✅ Erfüllt |
| CR-14 | Pflanzenzustand soll visuell dokumentiert werden (Kamera) | SOLL | Fotodokumentation | ✅ Erfüllt |
| CR-15 | Messdaten sollen visuell dargestellt werden (Web-UI) | SOLL | Visualisierung | ✅ Erfüllt |
| CR-16 | Messdaten sollen exportiert werden können (CSV/ZIP) | MUSS | Datenexport | ✅ Erfüllt |
| CR-17 | Live-Messwerte sollen in Echtzeit angezeigt werden | SOLL | Echtzeit-Updates | ✅ Erfüllt |
| CR-18 | Das System soll historische Messwerte anzeigen können | SOLL | Historie | ✅ Erfüllt |

## Prioritäten

- **MUSS**: Kritische Anforderungen, die zwingend erfüllt werden müssen
- **SOLL**: Wichtige Anforderungen, die nach Möglichkeit erfüllt werden sollten

## Erfüllungsstatus

- ✅ **Erfüllt**: Anforderung vollständig implementiert und getestet
- ⚠️ **Teilweise**: Grundfunktionalität vorhanden, aber mit Einschränkungen
- ❌ **Nicht erfüllt**: Anforderung nicht implementiert

## Detaillierte Beschreibung

### CR-01: Überwachung von Hydroponik-Versuchsaufbauten
Das System dient der kontinuierlichen Überwachung hydroponischer Anlagen. Es erfasst relevante Messwerte und ermöglicht deren Auswertung.

### CR-02, CR-03, CR-04: Messwert-Überwachung
Die drei wichtigsten Parameter für hydroponische Systeme (pH-Wert, elektrische Leitfähigkeit, Temperatur) müssen kontinuierlich überwacht werden.

### CR-05: Kalibrierte Messung
Alle Sensoren müssen kalibrierbar sein, um genaue und reproduzierbare Messwerte zu gewährleisten.

### CR-06: Automatische zyklische Erfassung
Das System arbeitet autonom und erfasst Messwerte in konfigurierbaren Intervallen ohne manuelle Eingriffe.

### CR-09: Multi-Node-Betrieb
Das System muss mindestens zwei Sensor-Nodes parallel unterstützen, um mehrere Anlagen oder Messpunkte gleichzeitig überwachen zu können. Implementiert durch automatische Node-Discovery über serielle Schnittstellen.

### CR-10: Fehlertoleranz
Bei kurzem Verbindungsverlust zwischen Node und Hub sendet die Node automatisch `hello`-Nachrichten (Retry) und stellt die Verbindung wieder her.

### CR-11: Langzeitbetrieb
Das System soll über Tage/Wochen stabil laufen. Implementiert durch Smoothing (Glättung von Messwerten), persistente SQLite-Datenbank und automatische Messwerterfassung in Intervallen. Status: Teilweise erfüllt - Langzeittests stehen noch aus.

### CR-13: Persistente Speicherung
Alle Messwerte werden in einer SQLite-Datenbank persistent gespeichert und bleiben auch nach Neustart verfügbar.

### CR-14: Fotodokumentation
USB-Kameras können Setups zugeordnet werden. Das Backend erfasst automatisch Fotos in konfigurierbaren Intervallen und speichert sie lokal.

### CR-15: Visualisierung
Eine React-basierte Web-UI zeigt Live-Messwerte, historische Daten (Charts) und Status-Informationen (Node online/offline, Fehler).

### CR-16: Datenexport
Messdaten können als **ZIP-Archiv mit CSV-Dateien** exportiert werden für weitere Analysen mit externen Tools (z.B. Excel, Python, R).

### CR-17: Echtzeit-Updates
Live-Messwerte werden via WebSocket an das Frontend gesendet und automatisch aktualisiert (ohne Page-Refresh).

### CR-18: Historische Daten
Das System speichert alle Messwerte dauerhaft und stellt sie als Zeitreihen dar. Die Web-UI zeigt historische Daten als Charts.
