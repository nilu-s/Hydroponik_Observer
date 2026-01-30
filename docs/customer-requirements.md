# Customer Requirements (Funktionale Anforderungen)

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
- ⚠️ **Teilweise**: Grundfunktionalität vorhanden, aber mit Einschränkungen (z.B. fehlende Langzeittests)
- ❌ **Nicht erfüllt**: Anforderung nicht implementiert

## Hinweise zur Implementierung

- **CR-11 (Langzeitbetrieb)**: Grundlegende Stabilität ist gegeben, aber umfassende Langzeittests über mehrere Wochen stehen noch aus.
- **CR-14 (Fotodokumentation)**: USB-Kameras werden vom Backend verwaltet, nicht von den Sensor-Nodes.
- **CR-16 (Export)**: Export erfolgt als ZIP-Archiv mit CSV-Dateien (nicht nur CSV).
