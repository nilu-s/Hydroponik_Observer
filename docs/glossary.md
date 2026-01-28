# Glossar

- **Node**: Physischer SensorNode (RP2040) mit pH/EC/Temperatur-Sensorik.
- **Setup**: Logische Zuordnung von Node, optionaler Kamera und Intervallen.
- **UID**: Eindeutige Gerätekennung des SensorNode, stabil über USB-Wechsel.
- **Reading**: Einzelner Messwertsatz (pH, EC, Temperatur, Zeitstempel).
- **Snapshot**: Einzelbildaufnahme von einer Kamera.
- **Worker**: Externer Prozess für Kamera-Zugriff und Frame-Streaming.
- **Live Reading**: Echtzeit-Messwerte, die per WebSocket an Clients gesendet werden.
