# Designentscheidungen

## UID statt Port als Node-ID
**Entscheidung:** Nodes werden über eine eindeutige UID identifiziert, nicht über den aktuell belegten Serial-Port.  
**Alternative:** Port-basierte Zuordnung (COM-Port als ID).  
**Begründung:** Ports sind instabil (USB-Reihenfolge, Neuanschlüsse). Die UID bleibt konstant und erlaubt stabile Zuordnung über Sessions.  
**Tradeoff:** Ein zusätzlicher Handshake-Schritt ist nötig, damit die UID bekannt ist.

## Polling-Loops statt Event-Driven
**Entscheidung:** Discovery, Reading-Capture und Photo-Capture laufen in regelmäßigen Loops.  
**Alternative:** Event-driven Architektur mit OS-Events oder Interrupts.  
**Begründung:** Polling vereinfacht die Plattform-Integration und funktioniert zuverlässig mit Serial-Geräten und externem Worker.  
**Tradeoff:** Zusätzliche Last durch regelmäßige Abfragen, insbesondere bei vielen Setups.

## Camera Worker als separater Prozess
**Entscheidung:** Kamera-Zugriff erfolgt über einen separaten C#-Worker-Prozess.  
**Alternative:** Direkte Integration in den Python-Backend-Prozess.  
**Begründung:** Windows MediaCapture ist in C# stabiler nutzbar; Prozess-Isolation verhindert, dass Kamera-Probleme das Backend blockieren.  
**Tradeoff:** Zusätzliches Prozess-Management und ein eigenes Binärprotokoll.

## SQLite + Dateisystem für Fotos
**Entscheidung:** Messwerte in SQLite, Fotos im Dateisystem.  
**Alternative:** Vollständige Speicherung in einer Datenbank oder einem Objekt-Storage.  
**Begründung:** SQLite ist leichtgewichtig und genügt für lokale Nutzung, Fotos sind als Dateien effizient und leicht exportierbar.  
**Tradeoff:** Dateisystem-Wachstum muss aktiv überwacht und bereinigt werden.
