# Architektur

## Systemübersicht
SensorHUB besteht aus einem Web-Frontend, einer FastAPI-Backend-API, einem Live-Layer für WebSockets, einem Serial-NodeClient für RP2040-SensorNodes und einem separaten Camera Worker für Bilddaten. Daten werden in SQLite persistiert, Fotos werden im Dateisystem gespeichert.

Dieses Diagramm zeigt die Hauptkomponenten und ihre Kommunikationswege, um die Systemgrenzen und Datenflüsse auf einen Blick zu verstehen.

```mermaid
flowchart LR
    Frontend["SensorHub Frontend"]
    BackendAPI["SensorHub Backend API"]
    LiveLayer["WebSocket / Live Layer"]
    SerialNodeClient["Serial / NodeClient"]
    SensorNode["SensorNode (RP2040)"]
    CameraWorker["Camera Worker (C#)"]
    Database["Datenbank (SQLite)"]
    PhotoFS["Dateisystem / Photos"]

    Frontend -->|REST| BackendAPI
    Frontend <-->|WS| LiveLayer
    LiveLayer --> BackendAPI
    BackendAPI --> Database
    BackendAPI --> PhotoFS
    BackendAPI --> SerialNodeClient
    SerialNodeClient <-->|JSON Lines| SensorNode
    BackendAPI <-->|Frames| CameraWorker
    BackendAPI -->|Snapshots| PhotoFS

    classDef frontend fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1;
    classDef backend fill:#E8F5E9,stroke:#43A047,color:#1B5E20;
    classDef live fill:#FFF8E1,stroke:#F9A825,color:#8D6E63;
    classDef serial fill:#E0F2F1,stroke:#00897B,color:#004D40;
    classDef node fill:#F3E5F5,stroke:#8E24AA,color:#4A148C;
    classDef worker fill:#FFF3E0,stroke:#FB8C00,color:#E65100;
    classDef db fill:#FFEBEE,stroke:#E53935,color:#B71C1C;
    classDef photos fill:#FCE4EC,stroke:#D81B60,color:#880E4F;

    class Frontend frontend;
    class BackendAPI backend;
    class LiveLayer live;
    class SerialNodeClient serial;
    class SensorNode node;
    class CameraWorker worker;
    class Database db;
    class PhotoFS photos;
```

- Das Frontend kommuniziert per REST und erhält Live-Daten über WebSockets.
- Der Backend-API-Prozess bündelt alle Zugriffe auf Serial, Kamera-Worker, DB und Dateisystem.
- SensorNodes sprechen ausschließlich das JSON-Line-Protokoll über Serial.
- Bilddaten werden als Frames vom Worker geliefert und als Fotos im Dateisystem abgelegt.

## Komponenten
- **SensorHub Frontend**: Benutzeroberfläche für Setups, Live-Werte, Timeline und Kamera-Preview.
- **SensorHub Backend API**: REST-API für Setups, Nodes, Kameras und Historie, plus WebSocket-Endpunkt `/api/live`.
- **WebSocket / Live Layer**: Verwaltung von Subscriptions und Push von Live-Readings.
- **Serial / NodeClient**: Discovery, Handshake und Abfrage von Sensordaten über JSON Lines.
- **SensorNode (RP2040)**: Sensorabfragen, Glättung, Kalibrierung und Debug-Modus.
- **Camera Worker (C#)**: Zugriff auf Windows MediaCapture und Ausgabe von JPEG-Frames.
- **Datenbank (SQLite)**: Persistenz für Setups, Nodes, Readings, Cameras und Calibration.
- **Dateisystem / Photos**: Ablage von Fotos pro Setup.

## Laufzeitprozesse und Loops
Die Backend-Logik basiert auf mehreren zyklischen Loops, die Discovery, Readings und Fotos unabhängig voneinander ausführen. Das Diagramm zeigt, welche Loop welche Komponente ansteuert.

```mermaid
flowchart LR
    BackendAPI["SensorHub Backend API"]
    LiveLayer["WebSocket / Live Layer"]
    SerialNodeClient["Serial / NodeClient"]
    SensorNode["SensorNode (RP2040)"]
    CameraWorker["Camera Worker (C#)"]
    Database["Datenbank (SQLite)"]
    PhotoFS["Dateisystem / Photos"]

    NodeDiscoveryLoop["Node Discovery Loop"]
    ReadingsCaptureLoop["Readings Capture Loop"]
    CameraDiscoveryLoop["Camera Discovery Loop"]
    PhotoCaptureLoop["Photo Capture Loop"]

    NodeDiscoveryLoop --> SerialNodeClient
    SerialNodeClient <-->|hello/ack| SensorNode
    NodeDiscoveryLoop --> Database

    ReadingsCaptureLoop --> SerialNodeClient
    ReadingsCaptureLoop --> Database
    ReadingsCaptureLoop --> LiveLayer

    CameraDiscoveryLoop --> CameraWorker
    CameraDiscoveryLoop --> Database
    CameraDiscoveryLoop --> LiveLayer

    PhotoCaptureLoop --> CameraWorker
    PhotoCaptureLoop --> PhotoFS
    PhotoCaptureLoop --> Database

    BackendAPI --> NodeDiscoveryLoop
    BackendAPI --> ReadingsCaptureLoop
    BackendAPI --> CameraDiscoveryLoop
    BackendAPI --> PhotoCaptureLoop

    classDef frontend fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1;
    classDef backend fill:#E8F5E9,stroke:#43A047,color:#1B5E20;
    classDef live fill:#FFF8E1,stroke:#F9A825,color:#8D6E63;
    classDef serial fill:#E0F2F1,stroke:#00897B,color:#004D40;
    classDef node fill:#F3E5F5,stroke:#8E24AA,color:#4A148C;
    classDef worker fill:#FFF3E0,stroke:#FB8C00,color:#E65100;
    classDef db fill:#FFEBEE,stroke:#E53935,color:#B71C1C;
    classDef photos fill:#FCE4EC,stroke:#D81B60,color:#880E4F;

    class BackendAPI backend;
    class LiveLayer live;
    class SerialNodeClient serial;
    class SensorNode node;
    class CameraWorker worker;
    class Database db;
    class PhotoFS photos;
```

- Discovery und Capture-Loops laufen getrennt, damit Ausfälle isoliert bleiben.
- Live-Readings werden sowohl gespeichert als auch per WebSocket gepusht.
- Kamera-Discovery aktualisiert die Geräteliste und versorgt das Frontend mit Status.
- Fotos werden getrennt von Live-Frames im Dateisystem persistiert.

## Lokales Deployment
SensorHUB läuft lokal auf einem Host-PC. Backend und Frontend sind getrennte Prozesse, der Camera Worker wird bei Bedarf gestartet. Die SensorNodes hängen per USB am Host.

```mermaid
flowchart TB
    HostMachine["Host-PC (Windows)"]
    Frontend["SensorHub Frontend"]
    BackendAPI["SensorHub Backend API"]
    LiveLayer["WebSocket / Live Layer"]
    CameraWorker["Camera Worker (C#)"]
    Database["Datenbank (SQLite)"]
    PhotoFS["Dateisystem / Photos"]
    SerialNodeClient["Serial / NodeClient"]
    SensorNode["SensorNode (RP2040)"]

    subgraph HostMachine["Host-PC (Windows)"]
        Frontend
        BackendAPI
        LiveLayer
        CameraWorker
        Database
        PhotoFS
        SerialNodeClient
    end

    SensorNode <-->|USB Serial| SerialNodeClient
    Frontend --> BackendAPI
    Frontend <-->|WS| LiveLayer
    BackendAPI --> Database
    BackendAPI --> PhotoFS
    BackendAPI --> CameraWorker

    classDef frontend fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1;
    classDef backend fill:#E8F5E9,stroke:#43A047,color:#1B5E20;
    classDef live fill:#FFF8E1,stroke:#F9A825,color:#8D6E63;
    classDef serial fill:#E0F2F1,stroke:#00897B,color:#004D40;
    classDef node fill:#F3E5F5,stroke:#8E24AA,color:#4A148C;
    classDef worker fill:#FFF3E0,stroke:#FB8C00,color:#E65100;
    classDef db fill:#FFEBEE,stroke:#E53935,color:#B71C1C;
    classDef photos fill:#FCE4EC,stroke:#D81B60,color:#880E4F;

    class Frontend frontend;
    class BackendAPI backend;
    class LiveLayer live;
    class SerialNodeClient serial;
    class SensorNode node;
    class CameraWorker worker;
    class Database db;
    class PhotoFS photos;
```

- Frontend und Backend teilen sich denselben Host, sind aber logisch getrennt.
- Der Camera Worker ist ein eigener Prozess, der bei Bedarf gestartet wird.
- SensorNodes kommunizieren nur über die Serial-Verbindung zum Host-PC.
