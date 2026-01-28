# Kamera, History, Export, Admin

## Kamera

### Snapshot / Stream

```mermaid
flowchart TB
  subgraph Top[" "]
    direction LR
    UI[SensorHub Frontend]
    API[SensorHub Backend API]
  end

  subgraph Bottom[" "]
    direction LR
    Worker[Camera Worker]
  end

  UI -->|GET /api/setups/<setupId>/camera/snapshot| API
  API -->|start --device <id>| Worker
  Worker -->|FRAM + JPEG payload| API
  API -->|image/jpeg| UI

  UI -->|GET /api/setups/<setupId>/camera/stream| API
  API -->|start --device <id>| Worker
  Worker -->|FRAM + JPEG payload loop| API
  API -->|multipart/x-mixed-replace| UI

  style UI fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1
  style API fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style Worker fill:#FFF3E0,stroke:#FB8C00,color:#E65100
```

### Photo Capture Loop (Persistenz)

```mermaid
flowchart TB
  subgraph Top[" "]
    direction LR
    API[SensorHub Backend Loop]
  end

  subgraph Bottom[" "]
    direction LR
    Worker[Camera Worker]
    FS[(Photos Dir)]
  end

  API -->|start --device <id>| Worker
  Worker -->|FRAM + JPEG payload| API
  API -->|write /data/photos/<setup_id>/<setup_id>_<yyyy-mm-dd_HH-MM-SS>.jpg| FS

  style API fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style Worker fill:#FFF3E0,stroke:#FB8C00,color:#E65100
  style FS fill:#FCE4EC,stroke:#D81B60,color:#880E4F
```

### Kamera Discovery

```mermaid
flowchart TB
  subgraph Top[" "]
    direction LR
    UI[SensorHub Frontend]
    WS[SensorHub Backend WS]
    API[SensorHub Backend Camera Discovery]
  end

  subgraph Bottom[" "]
    direction LR
    Worker[Camera Worker]
    DB[(SQLite)]
  end

  API -->|--list| Worker
  Worker -->|JSON devices| API
  API -->|upsert cameras + mark offline| DB
  API -->|broadcast cameraDevices| WS
  WS -->|cameraDevices payload| UI

  style API fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style Worker fill:#FFF3E0,stroke:#FB8C00,color:#E65100
  style DB fill:#FFEBEE,stroke:#E53935,color:#B71C1C
  style WS fill:#FFF8E1,stroke:#F9A825,color:#8D6E63
  style UI fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1
```

### Kamera Entfernen

```mermaid
flowchart TB
  subgraph Top[" "]
    direction LR
    UI[SensorHub Frontend]
    API[SensorHub Backend API]
    WS[SensorHub Backend WS]
  end

  subgraph Bottom[" "]
    direction LR
    DB[(SQLite)]
  end

  UI -->|DELETE /api/cameras/<cameraId>| API
  API -->|delete camera| DB
  API -->|broadcast cameraDevices| WS
  WS -->|cameraDevices payload| UI

  style UI fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1
  style API fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style DB fill:#FFEBEE,stroke:#E53935,color:#B71C1C
  style WS fill:#FFF8E1,stroke:#F9A825,color:#8D6E63
```

### Manuelles Foto speichern

```mermaid
flowchart TB
  subgraph Top[" "]
    direction LR
    UI[SensorHub Frontend]
    API[SensorHub Backend API]
  end

  subgraph Bottom[" "]
    direction LR
    Worker[Camera Worker]
    FS[(Photos Dir)]
  end

  UI -->|POST /api/setups/<setupId>/capture-photo| API
  API -->|start --device <id>| Worker
  Worker -->|FRAM + JPEG payload| API
  API -->|write photo file| FS
  API -->|ok + photo| UI

  style UI fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1
  style API fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style Worker fill:#FFF3E0,stroke:#FB8C00,color:#E65100
  style FS fill:#FCE4EC,stroke:#D81B60,color:#880E4F
```

## History, Export, Admin

### Setup History (Readings + Photos)

```mermaid
flowchart TB
  subgraph Top[" "]
    direction LR
    UI[SensorHub Frontend]
    API[SensorHub Backend API]
  end

  subgraph Bottom[" "]
    direction LR
    DB[(SQLite)]
    FS[(Photos Dir)]
  end

  UI -->|GET /api/setups/<setupId>/history?limit=200| API
  API -->|SELECT readings| DB
  API -->|list /data/photos/<setup_id>/| FS
  API -->|readings + photos| UI

  style UI fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1
  style API fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style DB fill:#FFEBEE,stroke:#E53935,color:#B71C1C
  style FS fill:#FCE4EC,stroke:#D81B60,color:#880E4F
```

### Export (ZIP mit CSV)

```mermaid
flowchart TB
  subgraph Top[" "]
    direction LR
    UI[SensorHub Frontend]
    API[SensorHub Backend API]
  end

  subgraph Bottom[" "]
    direction LR
    DB[(SQLite)]
    FS[(Temp File)]
  end

  UI -->|GET /api/export/all| API
  API -->|SELECT setups + readings| DB
  API -->|create ZIP with CSV| FS
  API -->|sensorhub-export.zip| UI

  style UI fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1
  style API fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style DB fill:#FFEBEE,stroke:#E53935,color:#B71C1C
  style FS fill:#FCE4EC,stroke:#D81B60,color:#880E4F
```

### Admin Reset

```mermaid
flowchart TB
  subgraph Top[" "]
    direction LR
    UI[SensorHub Frontend]
    API[SensorHub Backend Admin]
    WS[SensorHub Backend WS]
  end

  subgraph Bottom[" "]
    direction LR
    DB[(SQLite)]
    FS[(Photos Dir)]
  end

  UI -->|POST /api/admin/reset, X-Reset-Token| API
  API -->|init_db reset true| DB
  API -->|delete photos| FS
  API -->|broadcast reset reason db-reset| WS
  WS -->|reset event| UI

  style UI fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1
  style API fill:#E8F5E9,stroke:#43A047,color:#1B5E20
  style DB fill:#FFEBEE,stroke:#E53935,color:#B71C1C
  style FS fill:#FCE4EC,stroke:#D81B60,color:#880E4F
  style WS fill:#FFF8E1,stroke:#F9A825,color:#8D6E63
```
