# 1 Einleitung

## 1.1 Motivation

Hydroponik-Systeme benötigen stabile Umweltbedingungen, wobei pH-Wert, elektrische Leitfähigkeit (EC) und Temperatur die zentrale Messbasis für die Bewertung des Nährstoffzustands bilden. Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN :: Firmware erfasst pH, EC und Temperatur.

Die Motivation dieser Arbeit liegt in der Bereitstellung einer lokal betriebenen Monitoring-Lösung, die Messwerte zuverlässig erfasst, speichert und visualisiert, ohne eine Cloud-Abhängigkeit zu erzeugen. Evidence: sensorhub-backend/app/main.py :: FastAPI app + StaticFiles :: Lokaler Backend-Server mit Datenpersistenz und UI-Zugriff.

## 1.2 Problemstellung

Typische Herausforderungen sind die Nachvollziehbarkeit der Messhistorie, die Konsistenz der Messdaten über längere Zeiträume und die einfache Erweiterbarkeit um weitere Sensor-Nodes. Evidence: sensorhub-backend/app/db.py :: readings table :: Persistente Speicherung von Zeitreihen.

Ein zusätzlicher Bedarf besteht in einer kompakten, reproduzierbaren Hardwarebasis, die jedoch zum Zeitpunkt dieser Arbeit noch nicht physisch vorliegt. [HARDWARE-NOT-AVAILABLE-YET]

## 1.3 Zielsetzung und Beitrag der Arbeit

Ziel ist die Implementierung eines prototypischen Systems, das Messwerte von Sensor-Nodes über eine serielle JSON-Schnittstelle entgegennimmt, in einer lokalen SQLite-Datenbank speichert und über REST sowie WebSocket ausliefert. Evidence: sensorhub-backend/app/nodes.py :: NodeClient.send_command :: Serial JSON-Kommunikation; Evidence: sensorhub-backend/app/db.py :: readings table :: SQLite-Persistenz; Evidence: sensorhub-backend/app/main.py :: /api/live :: WebSocket-Endpunkt.

Der Beitrag umfasst die Integration von Sensor-Firmware, Backend-Services, Web-UI sowie einer Kamera-Erweiterung für Fotodokumentation. Evidence: sensornode-firmware/src/main.cpp :: handleGetAll :: Sensorwerte werden bereitgestellt; Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: Web-UI Live-Daten; Evidence: sensorhub-backend/app/camera_streaming.py :: capture_photo_now :: Fotoaufnahme im Backend.

## 1.4 Abgrenzung

**Scope:** Beobachtung/Monitoring vs. Regelung/Automatisierung

Diese Arbeit fokussiert sich auf die Erfassung, Speicherung und Visualisierung von Sensordaten. Die automatische Regelung (z.B. automatische pH-Anpassung, Dosierung) ist explizit nicht Teil des Scopes.
Evidence: sensorhub-backend/app/api/setups.py :: capture_reading :: API erfasst Messwerte, keine Regel- oder Aktor-Endpoints vorhanden.

## 1.5 Aufbau der Arbeit

Kapitel 2 stellt die für das implementierte System relevanten Grundlagen vor. Kapitel 3 definiert Anforderungen und Randbedingungen. Kapitel 4 beschreibt Architektur, Datenmodell und Protokolle. Kapitel 5 dokumentiert die Implementierung der Software und den Hardwarestatus. Kapitel 6 beschreibt den Validierungsansatz, da formale Tests noch ausstehen. Kapitel 7 diskutiert Grenzen und zukünftige Arbeiten. Evidence: bachelorarbeit/00-README.md :: Struktur :: Kapitelstruktur der Arbeit.
# 1 Einleitung

## 1.1 Motivation

Hydroponik-Systeme benötigen stabile Umweltbedingungen, wobei pH-Wert, elektrische Leitfähigkeit (EC) und Temperatur die zentrale Messbasis für die Bewertung des Nährstoffzustands bilden. Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN :: Firmware erfasst pH, EC und Temperatur.

Die Motivation dieser Arbeit liegt in der Bereitstellung einer lokal betriebenen Monitoring-Lösung, die Messwerte zuverlässig erfasst, speichert und visualisiert, ohne eine Cloud-Abhängigkeit zu erzeugen. Evidence: sensorhub-backend/app/main.py :: FastAPI app + StaticFiles :: Lokaler Backend-Server mit Datenpersistenz und UI-Zugriff.

## 1.2 Problemstellung

Typische Herausforderungen sind die Nachvollziehbarkeit der Messhistorie, die Konsistenz der Messdaten über längere Zeiträume und die einfache Erweiterbarkeit um weitere Sensor-Nodes. Evidence: sensorhub-backend/app/db.py :: readings table :: Persistente Speicherung von Zeitreihen.

Ein zusätzlicher Bedarf besteht in einer kompakten, reproduzierbaren Hardwarebasis, die jedoch zum Zeitpunkt dieser Arbeit noch nicht physisch vorliegt. [HARDWARE-NOT-AVAILABLE-YET]

## 1.3 Zielsetzung und Beitrag der Arbeit

Ziel ist die Implementierung eines prototypischen Systems, das Messwerte von Sensor-Nodes über eine serielle JSON-Schnittstelle entgegennimmt, in einer lokalen SQLite-Datenbank speichert und über REST sowie WebSocket ausliefert. Evidence: sensorhub-backend/app/nodes.py :: NodeClient.send_command :: Serial JSON-Kommunikation; Evidence: sensorhub-backend/app/db.py :: readings table :: SQLite-Persistenz; Evidence: sensorhub-backend/app/main.py :: /api/live :: WebSocket-Endpunkt.

Der Beitrag umfasst die Integration von Sensor-Firmware, Backend-Services, Web-UI sowie einer Kamera-Erweiterung für Fotodokumentation. Evidence: sensornode-firmware/src/main.cpp :: handleGetAll :: Sensorwerte werden bereitgestellt; Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: Web-UI Live-Daten; Evidence: sensorhub-backend/app/camera_streaming.py :: capture_photo_now :: Fotoaufnahme im Backend.

## 1.4 Abgrenzung

**Scope:** Beobachtung/Monitoring vs. Regelung/Automatisierung

Diese Arbeit fokussiert sich auf die Erfassung, Speicherung und Visualisierung von Sensordaten. Die automatische Regelung (z.B. automatische pH-Anpassung, Dosierung) ist explizit nicht Teil des Scopes.
Evidence: sensorhub-backend/app/api/setups.py :: capture_reading :: API erfasst Messwerte, keine Regel- oder Aktor-Endpoints vorhanden.

## 1.5 Aufbau der Arbeit

Kapitel 2 stellt die für das implementierte System relevanten Grundlagen vor. Kapitel 3 definiert Anforderungen und Randbedingungen. Kapitel 4 beschreibt Architektur, Datenmodell und Protokolle. Kapitel 5 dokumentiert die Implementierung der Software und den Hardwarestatus. Kapitel 6 beschreibt den Validierungsansatz, da formale Tests noch ausstehen. Kapitel 7 diskutiert Grenzen und zukünftige Arbeiten. Evidence: bachelorarbeit/00-README.md :: Struktur :: Kapitelstruktur der Arbeit.
# 1 Einleitung

## 1.1 Motivation

Hydroponik-Systeme benötigen stabile Umweltbedingungen, wobei pH-Wert, elektrische Leitfähigkeit (EC) und Temperatur die zentrale Messbasis für die Bewertung des Nährstoffzustands bilden. Evidence: sensornode-firmware/src/main.cpp :: PH_PIN/EC_PIN/TEMP_PIN :: Firmware erfasst pH, EC und Temperatur.

Die Motivation dieser Arbeit liegt in der Bereitstellung einer lokal betriebenen Monitoring-Lösung, die Messwerte zuverlässig erfasst, speichert und visualisiert, ohne eine Cloud-Abhängigkeit zu erzeugen. Evidence: sensorhub-backend/app/main.py :: FastAPI app + StaticFiles :: Lokaler Backend-Server mit Datenpersistenz und UI-Zugriff.

## 1.2 Problemstellung

Typische Herausforderungen sind die Nachvollziehbarkeit der Messhistorie, die Konsistenz der Messdaten über längere Zeiträume und die einfache Erweiterbarkeit um weitere Sensor-Nodes. Evidence: sensorhub-backend/app/db.py :: readings table :: Persistente Speicherung von Zeitreihen.

Ein zusätzlicher Bedarf besteht in einer kompakten, reproduzierbaren Hardwarebasis, die jedoch zum Zeitpunkt dieser Arbeit noch nicht physisch vorliegt. [HARDWARE-NOT-AVAILABLE-YET]

## 1.3 Zielsetzung und Beitrag der Arbeit

Ziel ist die Implementierung eines prototypischen Systems, das Messwerte von Sensor-Nodes über eine serielle JSON-Schnittstelle entgegennimmt, in einer lokalen SQLite-Datenbank speichert und über REST sowie WebSocket ausliefert. Evidence: sensorhub-backend/app/nodes.py :: NodeClient.send_command :: Serial JSON-Kommunikation; Evidence: sensorhub-backend/app/db.py :: readings table :: SQLite-Persistenz; Evidence: sensorhub-backend/app/main.py :: /api/live :: WebSocket-Endpunkt.

Der Beitrag umfasst die Integration von Sensor-Firmware, Backend-Services, Web-UI sowie einer Kamera-Erweiterung für Fotodokumentation. Evidence: sensornode-firmware/src/main.cpp :: handleGetAll :: Sensorwerte werden bereitgestellt; Evidence: sensorhub-frontend/src/services/ws.ts :: LiveWsClient :: Web-UI Live-Daten; Evidence: sensorhub-backend/app/camera_streaming.py :: capture_photo_now :: Fotoaufnahme im Backend.

## 1.4 Abgrenzung

**Scope:** Beobachtung/Monitoring vs. Regelung/Automatisierung

Diese Arbeit fokussiert sich auf die Erfassung, Speicherung und Visualisierung von Sensordaten. Die automatische Regelung (z.B. automatische pH-Anpassung, Dosierung) ist explizit nicht Teil des Scopes.
Evidence: sensorhub-backend/app/api/setups.py :: capture_reading :: API erfasst Messwerte, keine Regel- oder Aktor-Endpoints vorhanden.

## 1.5 Aufbau der Arbeit

Kapitel 2 stellt die für das implementierte System relevanten Grundlagen vor. Kapitel 3 definiert Anforderungen und Randbedingungen. Kapitel 4 beschreibt Architektur, Datenmodell und Protokolle. Kapitel 5 dokumentiert die Implementierung der Software und den Hardwarestatus. Kapitel 6 beschreibt den Validierungsansatz, da formale Tests noch ausstehen. Kapitel 7 diskutiert Grenzen und zukünftige Arbeiten. Evidence: bachelorarbeit/README.md :: Struktur :: Kapitelstruktur der Arbeit.
