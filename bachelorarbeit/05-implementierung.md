# 5 Implementierung

Dieses Kapitel beschreibt die konkrete Umsetzung des Systems, aufgeteilt in Hardware und Software.

## 5.1 Hardware-Entwicklung

### 5.1.1 PCB-Design

Das System verwendet eine custom PCB (HydroponikPlatine), entwickelt mit **KiCad 9.0**.

#### Hauptkomponenten

| Komponente | Funktion | Spezifikation |
|------------|----------|---------------|
| **Raspberry Pi Pico W** | Mikrocontroller | RP2040, Dual-Core ARM Cortex-M0+ @ 133MHz |
| **TL081** | Operationsverstärker | pH-Signal-Konditionierung |
| **TC1121COA** | DC/DC Converter | +5V → -5V Inverter für OP-Amp |
| **DS18B20** | Temperatur-Sensor | OneWire Digital, ±0.5°C |
| **Screw Terminals** | Sensor-Anschlüsse | pH-Sonde (BNC), EC-Sonde |

#### Schaltplan-Übersicht

**pH-Messkanal:**
- Eingang: BNC-Anschluss für pH-Elektrode (hochohmig)
- Verstärkung: TL081 als Non-Inverting Amplifier (Gain=1)
- ADC: GPIO28 (ADC2) des Pico
- Spannungsbereich: 0-3.3V → pH 0-14

**EC-Messkanal:**
- Eingang: Schraubklemme für EC-Sonde
- Widerstandsteiler: 4.7kΩ + Sonde
- ADC: GPIO26 (ADC0) des Pico
- Spannungsbereich: 0-3.3V → EC 0-5 mS/cm

**Temperatur-Messkanal:**
- Sensor: DS18B20 (OneWire)
- GPIO: GPIO17
- Pull-Up: 4.7kΩ

**Stromversorgung:**
- USB-Eingang: 5V vom Pico
- Positive Rail: +5V (direkt)
- Negative Rail: -5V (TC1121COA Inverter)
- Analog Rail: +3.3V (Pico internal LDO)
- GND + AGND: Getrennte analog/digital Grounds

#### Layout-Eigenschaften

- **Größe**: A3 (DIN-Format)
- **Layer**: 2-Layer PCB
- **Trace-Breite**: 0.25mm (Signal), 0.5mm (Power)
- **Via-Größe**: 0.8mm Drill, 1.5mm Pad

### 5.1.2 Sensor-Kalibrierung

#### pH-Sensor (3-Punkt-Kalibrierung)

Verwendet Pufferlösungen bei pH 4.0, 7.0 und 10.0:

| Pufferlösung | Erwartete ADC-Spannung | Erwarteter pH |
|--------------|------------------------|---------------|
| pH 4.0 | ~0.86V | 4.0 |
| pH 7.0 | ~1.65V | 7.0 |
| pH 10.0 | ~2.44V | 10.0 |

**Kalibrierungsablauf:**

1. Elektrode in pH 7.0 Puffer tauchen
2. Rohwert auslesen (z.B. 1.68V)
3. Offset berechnen: `offset = 1.65V - 1.68V = -0.03V`
4. Weitere Puffer messen für Linearitätsprüfung

**Lineare Interpolation:**

Zwischen zwei Kalibrierpunkten $(x_1, y_1)$ und $(x_2, y_2)$:

$$
y = y_1 + \frac{(y_2 - y_1)}{(x_2 - x_1)} \cdot (x - x_1)
$$

Wobei $x$ = ADC-Rohwert, $y$ = kalibrierter pH-Wert.

#### EC-Sensor (2-Punkt-Kalibrierung)

Verwendet Standardlösungen bei 0 mS/cm und 2.76 mS/cm (z.B. 1413 µS/cm):

| Lösung | ADC-Spannung | EC |
|--------|--------------|-----|
| Destilliertes Wasser | ~0V | 0 mS/cm |
| 1413 µS/cm Lösung | ~1.5V | 1.413 mS/cm |

---

## 5.2 Firmware-Implementierung (Sensor-Node)

### 5.2.1 Projekt-Setup

**Entwicklungsumgebung:**
- **Framework**: Arduino (mit Pico-Board-Package)
- **Build-Tool**: PlatformIO
- **Sprache**: C++ (Arduino-API)

**Wichtige Libraries:**
- `ArduinoJson` (v7): JSON Parsing/Serialization
- `OneWire` + `DallasTemperature`: DS18B20 Temperatur-Sensor
- `hardware/flash.h`: Pico Flash-UID Auslesen

### 5.2.2 Hauptkomponenten

#### Sensor-Auslesen

**ADC-Konfiguration:**

```cpp
static const int PH_PIN = 28;   // ADC2 (GPIO28)
static const int EC_PIN = 26;   // ADC0 (GPIO26)
static const int TEMP_PIN = 17; // GPIO17 (OneWire)

void setup() {
  analogReadResolution(12);  // 12-bit ADC (0-4095)
  pinMode(PH_PIN, INPUT);
  pinMode(EC_PIN, INPUT);
  tempSensor.begin();
}
```

**Rohwert-Messung:**

```cpp
static float readPhRaw() {
  const int raw = analogRead(PH_PIN);
  return (static_cast<float>(raw) / 4095.0f) * 3.3f;  // → Volt
}
```

#### Smoothing (Glättung)

Um Messrauschen zu reduzieren, werden **64 Samples** über ein **10-Sekunden-Fenster** gemittelt:

```cpp
static const size_t MAX_SAMPLES = 64;
static const uint32_t SMOOTHING_WINDOW_MS = 10000;
static const uint32_t SAMPLE_INTERVAL_MS = 250;  // Alle 250ms ein Sample

static Sample computeSmoothed(uint32_t now) {
  float sumPh = 0.0f, sumEc = 0.0f, sumTemp = 0.0f;
  size_t count = 0;
  
  for (size_t i = 0; i < sampleCount; i++) {
    const Sample &s = samples[i];
    if (now - s.ts <= SMOOTHING_WINDOW_MS) {
      sumPh += s.ph;
      sumEc += s.ec;
      sumTemp += s.temp;
      count++;
    }
  }
  
  return {
    now,
    sumPh / count,
    sumEc / count,
    sumTemp / count
  };
}
```

#### Auto-Discovery (Hello-Mechanismus)

Die Node sendet automatisch `hello`-Nachrichten:

- **Beim Start**: Sofort nach `setup()`
- **Bei Disconnected**: Alle 1.2 Sekunden Retry

```cpp
static const uint32_t HELLO_RETRY_INTERVAL_MS = 1200;
static const uint32_t HELLO_ACK_TIMEOUT_MS = 4000;

void loop() {
  // ... Message-Handling ...
  
  const uint32_t now = millis();
  
  // Timeout-Check
  if (nodeConnected && now - lastHelloAckAt > HELLO_ACK_TIMEOUT_MS) {
    nodeConnected = false;
  }
  
  // Auto-Announce bei Disconnect
  if (!nodeConnected && now - lastAnnounceAt >= HELLO_RETRY_INTERVAL_MS) {
    lastAnnounceAt = now;
    sendHello("probe");
  }
}
```

#### Debug-Modus

Simuliert Messwerte für Tests ohne echte Sensoren:

```cpp
static NodeMode nodeMode = MODE_REAL;  // oder MODE_DEBUG

static void handleSetMode(JsonObject payload) {
  const char *mode = payload["mode"];
  if (mode && String(mode) == "debug") {
    nodeMode = MODE_DEBUG;
    resetDebugValues();  // Startwerte setzen
    return;
  }
  nodeMode = MODE_REAL;
}
```

**Debug-Werte** werden alle 5 Sekunden inkrementiert (z.B. pH 6.0 → 6.1 → ... → 6.9 → 6.0):

```cpp
static void updateDebugValues(uint32_t now) {
  if (now - lastDebugUpdate < 5000) return;
  
  lastDebugUpdate = now;
  debugPh = advanceTenths(debugPh, 6.0f, 6.9f);
  debugEc = advanceTenths(debugEc, 1.0f, 1.9f);
  debugTemp = advanceTenths(debugTemp, 20.0f, 20.9f);
}
```

---

## 5.3 Backend-Implementierung

### 5.3.1 Projekt-Setup

**Framework & Technologien:**
- **Web-Framework**: FastAPI 0.115+
- **Datenbank**: SQLite (via `sqlite3` built-in)
- **ASGI-Server**: Uvicorn
- **ORM**: Eigene SQL-Funktionen (kein SQLAlchemy)

**Projekt-Struktur:**

```
sensorhub-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI App + Startup
│   ├── config.py            # Konfiguration
│   ├── db.py                # Datenbank-Layer
│   ├── models.py            # Pydantic Models
│   ├── nodes.py             # Node-Management
│   ├── scheduler.py         # Loop-Registry
│   ├── realtime_updates.py  # WebSocket-Manager
│   ├── camera_devices.py    # Kamera-Discovery
│   ├── camera_streaming.py  # Foto-Capture
│   ├── camera_worker_manager.py  # C# Worker Verwaltung
│   ├── api/
│   │   ├── __init__.py
│   │   ├── admin.py         # Admin-Endpoints
│   │   ├── nodes.py         # Node-Endpoints
│   │   ├── setups.py        # Setup-Endpoints
│   │   └── cameras.py       # Kamera-Endpoints
│   └── utils/
│       ├── csv_export.py
│       ├── datetime_utils.py
│       └── paths.py
├── requirements.txt
└── tests/
```

### 5.3.2 Node-Discovery Loop

Automatisches Erkennen neuer Nodes über serielle Schnittstellen:

```python
async def node_discovery_loop():
    while True:
        ports = list_serial_ports()  # pyserial
        
        for port in ports:
            port_name = port["port"]
            
            # Node bereits bekannt?
            if get_node_client(port_name):
                continue
            
            # Versuche Node zu öffnen
            try:
                client = SerialNodeClient(port_name)
                if client.probe_hello():
                    register_node_client(client)
                    log_event("node.discovered", node_id=client.node_id)
            except Exception as e:
                log_event("node.discovery_failed", port=port_name, error=str(e))
        
        await asyncio.sleep(2)  # Alle 2 Sekunden scannen
```

### 5.3.3 Readings-Capture Loop

Zyklisches Erfassen von Messwerten basierend auf Setup-Intervallen:

```python
async def readings_capture_loop():
    while True:
        setups = list_setups()
        
        for setup in setups:
            interval = setup["value_interval_minutes"]
            last_reading = get_last_reading(setup["setup_id"])
            
            if should_capture(last_reading, interval):
                try:
                    node_id, reading = await fetch_setup_reading(setup["setup_id"])
                    insert_reading(
                        setup_id=setup["setup_id"],
                        node_id=node_id,
                        ts=reading["ts"],
                        ph=reading["ph"],
                        ec=reading["ec"],
                        temp=reading["temp"],
                        status=reading["status"]
                    )
                except Exception as e:
                    log_event("reading.capture_failed", setup_id=setup["setup_id"], error=str(e))
        
        await asyncio.sleep(10)
```

### 5.3.4 WebSocket Live-Updates

```python
class LiveManager:
    def __init__(self):
        self.subscriptions: dict[str, set[WebSocket]] = defaultdict(set)
    
    async def subscribe(self, setup_id: str, ws: WebSocket):
        self.subscriptions[setup_id].add(ws)
    
    async def broadcast_reading(self, setup_id: str, reading: dict):
        sockets = self.subscriptions.get(setup_id, set())
        
        for ws in sockets:
            try:
                await ws.send_json({
                    "t": "reading",
                    "setupId": setup_id,
                    **reading
                })
            except Exception:
                await self.remove_ws(ws)
```

---

## 5.4 Frontend-Implementierung

### 5.4.1 Projekt-Setup

**Framework & Tools:**
- **Framework**: React 18
- **Build-Tool**: Vite
- **Sprache**: TypeScript
- **Styling**: CSS (kein Framework)

**Projekt-Struktur:**

```
sensorhub-frontend/
├── src/
│   ├── main.tsx             # Entry Point
│   ├── styles.css           # Global Styles
│   ├── types/
│   │   └── index.ts         # TypeScript Types
│   ├── services/
│   │   ├── api.ts           # REST API Client
│   │   ├── ws.ts            # WebSocket Client
│   │   └── backend-url.ts   # Config
│   ├── pages/
│   │   ├── HomePage.tsx     # Dashboard
│   │   └── SettingsPage.tsx # Settings
│   └── components/
│       ├── setup/
│       │   ├── SetupCard.tsx
│       │   ├── CreateSetupForm.tsx
│       │   └── HistoryChart.tsx
│       └── node/
│           └── NodeCard.tsx
├── index.html
├── package.json
└── vite.config.ts
```

### 5.4.2 WebSocket-Integration

```typescript
export class LiveWsClient {
  private ws: WebSocket | null = null;
  
  constructor(
    private onMessage: (msg: WsServerMsg) => void,
    private onStatusChange: (status: "connected" | "disconnected" | "connecting") => void
  ) {}
  
  connect() {
    this.onStatusChange("connecting");
    this.ws = new WebSocket(`ws://${BACKEND_URL}/api/live`);
    
    this.ws.onopen = () => {
      this.onStatusChange("connected");
    };
    
    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      this.onMessage(msg);
    };
    
    this.ws.onerror = () => {
      this.onStatusChange("disconnected");
    };
  }
  
  subscribe(setupId: string) {
    this.ws?.send(JSON.stringify({ t: "sub", setupId }));
  }
  
  unsubscribe(setupId: string) {
    this.ws?.send(JSON.stringify({ t: "unsub", setupId }));
  }
}
```

### 5.4.3 Live-Visualisierung

```typescript
const HomePage = () => {
  const [liveReadings, setLiveReadings] = useState<Record<string, Reading>>({});
  
  const handleWsMsg = (msg: WsServerMsg) => {
    if (msg.t === "reading") {
      setLiveReadings(prev => ({
        ...prev,
        [msg.setupId]: msg
      }));
    }
  };
  
  useEffect(() => {
    const client = new LiveWsClient(handleWsMsg, setWsStatus);
    client.connect();
    
    setups.forEach(setup => {
      client.subscribe(setup.setupId);
    });
    
    return () => client.close();
  }, [setups]);
  
  // ... Rendering ...
};
```

---

## 5.5 Kamera-Integration

### 5.5.1 C# Worker für DirectShow

USB-Kameras werden über einen externen **C# Worker** gesteuert (weil Python-Bibliotheken wie `opencv-python` nicht zuverlässig mit Windows DirectShow funktionieren):

**Architektur:**
- Backend (Python) spawnt C# Worker-Prozess pro Kamera
- Kommunikation via **stdin/stdout** (JSON-Line-Protocol)
- Worker captured Fotos und speichert sie direkt

**Worker-Kommandos:**

| Command | Beschreibung |
|---------|--------------|
| `snapshot` | Einzelfoto aufnehmen |
| `start_stream` | Video-Stream starten |
| `stop_stream` | Video-Stream stoppen |
| `exit` | Worker beenden |

### 5.5.2 Automatische Foto-Capture

```python
async def photo_capture_loop():
    while True:
        setups = list_setups()
        
        for setup in setups:
            camera_id = setup.get("camera_id")
            if not camera_id:
                continue
            
            interval = setup["photo_interval_minutes"]
            last_photo = get_last_photo_time(setup["setup_id"])
            
            if should_capture_photo(last_photo, interval):
                try:
                    await capture_photo_now(setup["setup_id"])
                except Exception as e:
                    log_event("photo.capture_failed", setup_id=setup["setup_id"], error=str(e))
        
        await asyncio.sleep(30)  # Alle 30 Sekunden prüfen
```

---

## 5.6 Fehlerbehandlung & Logging

### 5.6.1 Strukturiertes Logging

```python
def log_event(event_type: str, **kwargs):
    log_entry = {
        "ts": datetime.utcnow().isoformat(),
        "event": event_type,
        **kwargs
    }
    print(json.dumps(log_entry), file=sys.stderr)
```

**Beispiel-Events:**
- `node.discovered`
- `node.disconnected`
- `reading.captured`
- `photo.captured`
- `error.sensor_timeout`

### 5.6.2 Node-Timeout-Erkennung

```python
HELLO_ACK_TIMEOUT_MS = 4000

def check_node_timeouts():
    now = int(time.time() * 1000)
    
    for client in list_node_clients():
        if now - client.last_hello_ack > HELLO_ACK_TIMEOUT_MS:
            mark_node_offline(client.node_id)
            log_event("node.timeout", node_id=client.node_id)
```
