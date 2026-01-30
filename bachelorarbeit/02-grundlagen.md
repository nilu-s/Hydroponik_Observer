# 2 Grundlagen

## 2.1 Domänen-Grundlagen

### Hydroponik: relevante Messgrößen & Bedeutung

Für das implementierte System werden pH-Wert, elektrische Leitfähigkeit (EC) und Temperatur als zentrale Messgrößen betrachtet. Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN :: Firmware erfasst genau diese drei Größen.

Weitere Größen wie Wasserstand oder Lichtintensität sind in der aktuellen Implementierung nicht enthalten. [MISSING-IN-CODE] Evidence: NONE.

## 2.2 IoT-/Sensornetz-Grundlagen

### Nodes, Gateway/Hub, Datenpipeline

Das System folgt einer Node–Hub-Struktur mit serieller Anbindung der Nodes an einen zentralen Hub. Evidence: sensorhub-backend/app/nodes.py :: node_discovery_loop :: Backend scannt serielle Ports und verwaltet Nodes.

Eine Cloud-Architektur ist nicht implementiert; alle Daten verbleiben lokal. Evidence: sensorhub-backend/app/db.py :: DB_PATH :: Lokale SQLite-Datei im Projektverzeichnis.

## 2.3 Web-/Backend-Grundlagen

### REST, Persistenz, Visualisierung

Das Backend stellt REST-Endpunkte für Setups, Nodes und Export bereit. Evidence: sensorhub-backend/app/api/setups.py :: router.get/post/patch/delete :: Implementierte REST-API.

Persistenz erfolgt über eine SQLite-Datenbank. Evidence: sensorhub-backend/app/db.py :: init_db/DB_PATH :: SQLite-Initialisierung und Datenpfad.

Live-Visualisierung erfolgt über WebSocket-Kommunikation zwischen Backend und Frontend. Evidence: sensorhub-backend/app/main.py :: /api/live :: WebSocket-Endpoint; Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: WebSocket-Client.

## 2.4 Qualitätsanforderungen

### Kalibrierung, Ausfalltoleranz, Datenintegrität

Kalibrierung ist in der Firmware über definierte Kalibrierpunkte implementiert (pH: 3 Punkte, EC: 2 Punkte). Evidence: sensornode-firmware/src/main.cpp :: applyPhCalibration/applyEcCalibration :: Stückweise lineare Kalibrierung.

Ausfalltoleranz ist auf Node-Ebene durch Hello-Retry vorgesehen; eine explizite Wiederverbindung im Frontend ist implementiert. Evidence: sensornode-firmware/src/main.cpp :: HELLO_RETRY_INTERVAL_MS :: Node sendet Hello-Retries; Evidence: sensorhub-frontend/src/services/ws.ts :: scheduleReconnect :: Frontend Reconnect-Logik.

## 2.5 Stand der Technik / Related Work

### Existierende Hydroponiksysteme

Diese Arbeit fokussiert sich auf die Implementierung des eigenen Systems; ein systematischer Vergleich mit kommerziellen oder Open-Source-Lösungen wird nicht durchgeführt. [OPEN-TOPIC]

### Vergleichbare IoT-Lösungen

Der Vergleich mit Monitoring-Systemen anderer Domänen ist bislang nicht ausgearbeitet. [OPEN-TOPIC]
# 2 Grundlagen

## 2.1 Domänen-Grundlagen

### Hydroponik: relevante Messgrößen & Bedeutung

Für das implementierte System werden pH-Wert, elektrische Leitfähigkeit (EC) und Temperatur als zentrale Messgrößen betrachtet. Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN :: Firmware erfasst genau diese drei Größen.

Weitere Größen wie Wasserstand oder Lichtintensität sind in der aktuellen Implementierung nicht enthalten. [MISSING-IN-CODE] Evidence: NONE.

## 2.2 IoT-/Sensornetz-Grundlagen

### Nodes, Gateway/Hub, Datenpipeline

Das System folgt einer Node–Hub-Struktur mit serieller Anbindung der Nodes an einen zentralen Hub. Evidence: sensorhub-backend/app/nodes.py :: node_discovery_loop :: Backend scannt serielle Ports und verwaltet Nodes.

Eine Cloud-Architektur ist nicht implementiert; alle Daten verbleiben lokal. Evidence: sensorhub-backend/app/db.py :: DB_PATH :: Lokale SQLite-Datei im Projektverzeichnis.

## 2.3 Web-/Backend-Grundlagen

### REST, Persistenz, Visualisierung

Das Backend stellt REST-Endpunkte für Setups, Nodes und Export bereit. Evidence: sensorhub-backend/app/api/setups.py :: router.get/post/patch/delete :: Implementierte REST-API.

Persistenz erfolgt über eine SQLite-Datenbank. Evidence: sensorhub-backend/app/db.py :: init_db/DB_PATH :: SQLite-Initialisierung und Datenpfad.

Live-Visualisierung erfolgt über WebSocket-Kommunikation zwischen Backend und Frontend. Evidence: sensorhub-backend/app/main.py :: /api/live :: WebSocket-Endpoint; Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: WebSocket-Client.

## 2.4 Qualitätsanforderungen

### Kalibrierung, Ausfalltoleranz, Datenintegrität

Kalibrierung ist in der Firmware über definierte Kalibrierpunkte implementiert (pH: 3 Punkte, EC: 2 Punkte). Evidence: sensornode-firmware/src/main.cpp :: applyPhCalibration/applyEcCalibration :: Stückweise lineare Kalibrierung.

Ausfalltoleranz ist auf Node-Ebene durch Hello-Retry vorgesehen; eine explizite Wiederverbindung im Frontend ist implementiert. Evidence: sensornode-firmware/src/main.cpp :: HELLO_RETRY_INTERVAL_MS :: Node sendet Hello-Retries; Evidence: sensorhub-frontend/src/services/ws.ts :: scheduleReconnect :: Frontend Reconnect-Logik.

## 2.5 Stand der Technik / Related Work

### Existierende Hydroponiksysteme

Diese Arbeit fokussiert sich auf die Implementierung des eigenen Systems; ein systematischer Vergleich mit kommerziellen oder Open-Source-Lösungen wird nicht durchgeführt. [OPEN-TOPIC]

### Vergleichbare IoT-Lösungen

Der Vergleich mit Monitoring-Systemen anderer Domänen ist bislang nicht ausgearbeitet. [OPEN-TOPIC]
# 2 Grundlagen

## 2.1 Domänen-Grundlagen

### Hydroponik: relevante Messgrößen & Bedeutung

Für das implementierte System werden pH-Wert, elektrische Leitfähigkeit (EC) und Temperatur als zentrale Messgrößen betrachtet. Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN :: Firmware erfasst genau diese drei Größen.

Weitere Größen wie Wasserstand oder Lichtintensität sind in der aktuellen Implementierung nicht enthalten. [MISSING-IN-CODE] Evidence: NONE.

## 2.2 IoT-/Sensornetz-Grundlagen

### Nodes, Gateway/Hub, Datenpipeline

Das System folgt einer Node–Hub-Struktur mit serieller Anbindung der Nodes an einen zentralen Hub. Evidence: sensorhub-backend/app/nodes.py :: node_discovery_loop :: Backend scannt serielle Ports und verwaltet Nodes.

Eine Cloud-Architektur ist nicht implementiert; alle Daten verbleiben lokal. Evidence: sensorhub-backend/app/db.py :: DB_PATH :: Lokale SQLite-Datei im Projektverzeichnis.

## 2.3 Web-/Backend-Grundlagen

### REST, Persistenz, Visualisierung

Das Backend stellt REST-Endpunkte für Setups, Nodes und Export bereit. Evidence: sensorhub-backend/app/api/setups.py :: router.get/post/patch/delete :: Implementierte REST-API.

Persistenz erfolgt über eine SQLite-Datenbank. Evidence: sensorhub-backend/app/db.py :: init_db/DB_PATH :: SQLite-Initialisierung und Datenpfad.

Live-Visualisierung erfolgt über WebSocket-Kommunikation zwischen Backend und Frontend. Evidence: sensorhub-backend/app/main.py :: /api/live :: WebSocket-Endpoint; Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: WebSocket-Client.

## 2.4 Qualitätsanforderungen

### Kalibrierung, Ausfalltoleranz, Datenintegrität

Kalibrierung ist in der Firmware über definierte Kalibrierpunkte implementiert (pH: 3 Punkte, EC: 2 Punkte). Evidence: sensornode-firmware/src/main.cpp :: applyPhCalibration/applyEcCalibration :: Stückweise lineare Kalibrierung.

Ausfalltoleranz ist auf Node-Ebene durch Hello-Retry vorgesehen; eine explizite Wiederverbindung im Frontend ist implementiert. Evidence: sensornode-firmware/src/main.cpp :: HELLO_RETRY_INTERVAL_MS :: Node sendet Hello-Retries; Evidence: sensorhub-frontend/src/services/ws.ts :: scheduleReconnect :: Frontend Reconnect-Logik.

## 2.5 Stand der Technik / Related Work

### Existierende Hydroponiksysteme

Diese Arbeit fokussiert sich auf die Implementierung des eigenen Systems; ein systematischer Vergleich mit kommerziellen oder Open-Source-Lösungen wird nicht durchgeführt. [OPEN-TOPIC]

### Vergleichbare IoT-Lösungen

Der Vergleich mit Monitoring-Systemen anderer Domänen ist bislang nicht ausgearbeitet. [OPEN-TOPIC]
