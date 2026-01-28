# Grenzen und Ausblick

## Grenzen
- **Polling-Last:** Mehr Setups erhöhen die Anzahl der Serial- und Kamera-Abfragen.
- **Skalierung:** Architektur ist auf einen Host-PC ausgelegt, nicht auf verteilte Systeme.
- **Datenwachstum:** Readings und Fotos wachsen linear mit der Laufzeit.
- **Robustheit der Peripherie:** USB-Disconnects oder Kamera-Timeouts erfordern manuelle Wiederherstellung.
- **Kalibrierungs-Workflows:** Der Prozess ist technisch vorhanden, aber operativ nicht vollständig geführt.

## Konkrete Next Steps
1. Konfigurierbare Archivierung/Löschung alter Readings und Fotos.
2. Health-Dashboard für Nodes/Kameras (Uptime, letzte Werte, Fehler).
3. Event-basierte Kamera- und Node-Erkennung als Ergänzung zum Polling.
4. Batch-Export mit Zeitfenster und Filteroptionen.
5. Optionaler Cloud-Upload für Fotos und Historien.
6. Automatisiertes Recovery bei Serial-Disconnects.
7. Erweiterung des Kalibrierungs-UI mit Validierung und Historie.
