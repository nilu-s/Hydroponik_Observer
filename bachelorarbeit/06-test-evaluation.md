# 6 Test, Verifikation und Evaluation

Dieses Kapitel beschreibt die Teststrategie, durchgeführte Tests und die Bewertung des Systems hinsichtlich der definierten Anforderungen.

## 6.1 Teststrategie

### 6.1.1 Testebenen

Das System wurde auf drei Ebenen getestet:

| Ebene | Fokus | Werkzeuge |
|-------|-------|-----------|
| **Unit-Tests** | Einzelne Funktionen/Klassen | pytest |
| **Integration-Tests** | Zusammenspiel mehrerer Komponenten | pytest, manuell |
| **System-Tests** | End-to-End Funktionalität | Manuell |

### 6.1.2 Testumgebung

**Hardware:**
- 2x Raspberry Pi Pico mit HydroponikPlatine
- 2x pH-Elektroden
- 2x EC-Sonden
- 1x USB-Kamera
- 1x Laptop (Windows 11) als Hub

**Software:**
- Python 3.11
- Node.js 20
- pytest 8.x
- Chrome Browser (Frontend-Tests)

---

## 6.2 Unit-Tests

### 6.2.1 Backend Unit-Tests

**Testabdeckung:**

```
tests/
├── test_admin_health.py        # Admin-Endpoints
├── test_camera_worker_manager.py  # Kamera-Worker
├── test_readings_capture_loop.py  # Readings Loop
└── test_security.py            # CSRF-Schutz
```

**Beispiel: CSRF-Schutz-Tests**

```python
def test_csrf_token_required():
    response = client.post("/api/setups", json={"name": "Test"})
    assert response.status_code == 403
    assert response.json()["detail"] == "csrf token required"

def test_csrf_token_valid():
    headers = {"X-CSRF-Token": CSRF_TOKEN}
    response = client.post("/api/setups", json={"name": "Test"}, headers=headers)
    assert response.status_code == 200
```

**Ergebnisse:**
- ✅ 28 Tests passed
- ⏱️ Durchschnittliche Laufzeit: 2.3s
- 📊 Coverage: ~65% (Backend-Code)

### 6.2.2 Firmware Unit-Tests

Firmware-Tests wurden **manuell** durchgeführt, da Embedded Unit-Testing für Arduino/PlatformIO komplex ist:

**Getestete Funktionen:**
- ✅ ADC-Auslesen (12-bit Resolution)
- ✅ Smoothing-Algorithmus (64 Samples, 10s Window)
- ✅ Kalibri erung (3-Punkt pH, 2-Punkt EC)
- ✅ JSON Serialization/Deserialization
- ✅ Hello-Mechanismus & Timeout

---

## 6.3 Integrations-Tests

### 6.3.1 Node-Discovery

**Test-Setup:**
1. Backend starten
2. Node per USB anschließen
3. Beobachten: Node-Discovery-Log

**Erwartetes Verhalten:**
- Node sendet `hello`-Nachricht innerhalb von 2 Sekunden
- Backend registriert Node in Datenbank
- Frontend zeigt Node als "online"

**Ergebnis:**
- ✅ Discovery funktioniert zuverlässig
- ⏱️ Durchschnittliche Discovery-Zeit: 1.8s
- ⚠️ Bei 3+ Nodes gleichzeitig: Gelegentliche Verzögerung (bis 5s)

### 6.3.2 Messwert-Erfassung & Speicherung

**Test-Setup:**
1. Setup mit Node und Intervall=1 Minute erstellen
2. 10 Minuten laufen lassen
3. Messwerte in DB prüfen

**Erwartetes Verhalten:**
- Mindestens 10 Readings in DB
- Readings enthalten Node-ID, Setup-ID, Timestamp
- Werte liegen im plausiblen Bereich

**Ergebnis:**
- ✅ 10/10 Readings erfolgreich gespeichert
- ✅ Alle Timestamps korrekt (Unix-ms)
- ✅ pH-Werte: 6.2-7.1 (plausibel für Leitungswasser)
- ✅ EC-Werte: 0.3-0.5 mS/cm (plausibel)

### 6.3.3 WebSocket Live-Updates

**Test-Setup:**
1. Frontend öffnen
2. Setup erstellen und expandieren
3. "Capture Reading" klicken
4. Beobachten: Live-Update ohne Page-Refresh

**Ergebnis:**
- ✅ Live-Update erfolgt innerhalb von 200ms
- ✅ Keine Verzögerung bei 3 gleichzeitigen Clients
- ❌ Bei WebSocket-Disconnect: Kein Auto-Reconnect (akzeptierte Limitation)

---

## 6.4 System-Tests

### 6.4.1 End-to-End Szenario: Neues Setup erstellen

**Schritte:**
1. Frontend öffnen → "Create Setup"
2. Name eingeben, Node auswählen
3. Intervall auf 5 Minuten setzen
4. Setup speichern
5. 10 Minuten warten
6. History-Chart prüfen

**Erwartetes Verhalten:**
- Setup erscheint in Dashboard
- Nach 5, 10 Minuten: Messwerte in Chart sichtbar

**Ergebnis:**
- ✅ Setup-Erstellung erfolgreich
- ✅ Readings nach 5/10 Min vorhanden
- ✅ Chart zeigt korrekte Zeitreihe

### 6.4.2 Multi-Node-Betrieb

**Test-Setup:**
2 Nodes gleichzeitig, 2 Setups (je 1 Node zugeordnet)

**Erwartetes Verhalten:**
- Beide Nodes erfassen unabhängig
- Keine Kollisionen/Fehler

**Ergebnis:**
- ✅ Beide Nodes arbeiten parallel
- ✅ Keine gegenseitige Beeinflussung
- ⚠️ Bei 3+ Nodes: Discovery-Loop manchmal langsam (siehe 6.3.1)

### 6.4.3 Kamera-Integration

**Test-Setup:**
1. USB-Kamera anschließen
2. Setup mit Kamera-Port verknüpfen
3. Foto-Intervall auf 2 Minuten setzen
4. 10 Minuten warten

**Erwartetes Verhalten:**
- Mindestens 5 Fotos gespeichert
- Fotos haben korrekte Timestamps

**Ergebnis:**
- ✅ 5/5 Fotos erfolgreich
- ✅ Dateigröße: ~300-500 KB (JPEG)
- ❌ Erste Foto-Aufnahme verzögert (C# Worker-Start: ~3s)

### 6.4.4 Datenexport (CSV/ZIP)

**Test-Setup:**
1. Setup mit 100+ Readings erstellen
2. "Export All" klicken
3. ZIP-Datei herunterladen
4. CSV-Datei öffnen

**Erwartetes Verhalten:**
- ZIP enthält `setups/<setup-id>/readings.csv`
- CSV hat Spalten: `id`, `setup_id`, `node_id`, `ts_iso`, `ph`, `ec`, `temp`, `status_json`

**Ergebnis:**
- ✅ ZIP erfolgreich erstellt (2.3 MB für 1000 Readings)
- ✅ CSV korrekt formatiert
- ✅ Timestamps als ISO-8601 (`2026-01-29T14:32:10Z`)

---

## 6.5 Performance-Tests

### 6.5.1 API Response-Zeiten

Gemessen mit `pytest-benchmark`:

| Endpoint | Avg. Response | P95 | P99 |
|----------|---------------|-----|-----|
| `GET /api/setups` | 12ms | 18ms | 24ms |
| `GET /api/nodes` | 8ms | 12ms | 16ms |
| `GET /api/setups/{id}/reading` | 45ms | 78ms | 120ms |
| `GET /api/setups/{id}/history?limit=200` | 23ms | 35ms | 48ms |
| `POST /api/setups/{id}/capture-reading` | 180ms | 250ms | 350ms |

**Interpretation:**
- ✅ Lesende Operationen < 50ms (Anforderung NFR-7)
- ✅ Historie mit 200 Readings: ~23ms (NFR-8 erfüllt)
- ⚠️ Capture-Reading: 180ms (serieller Round-Trip, akzeptabel)

### 6.5.2 Datenbank-Skalierung

**Test-Setup:**
- 1000, 5000, 10000, 50000 Readings generiert
- Query: `SELECT * FROM readings WHERE setup_id = ? ORDER BY ts DESC LIMIT 200`

| Readings in DB | Query-Zeit | Index? |
|----------------|------------|--------|
| 1,000 | 4ms | Nein |
| 5,000 | 18ms | Nein |
| 10,000 | 35ms | Nein |
| 50,000 | 180ms | Nein |
| 50,000 | 12ms | **Ja** |

**Erkenntnisse:**
- ⚠️ Ohne Index: Lineare Skalierung (schlecht)
- ✅ Mit Index auf `(setup_id, ts)`: Konstante Performance

**Maßnahme:**
Index wurde nachträglich hinzugefügt:

```sql
CREATE INDEX IF NOT EXISTS idx_readings_setup_ts 
ON readings(setup_id, ts DESC);
```

---

## 6.6 Robustheit-Tests

### 6.6.1 Node-Disconnect & Reconnect

**Szenario:**
1. Node im Betrieb
2. USB-Kabel ziehen
3. 10 Sekunden warten
4. USB-Kabel wieder einstecken

**Erwartetes Verhalten:**
- Backend erkennt Disconnect (Timeout nach 4s)
- Node als "offline" markiert
- Bei Reconnect: Auto-Discovery, Node wieder "online"

**Ergebnis:**
- ✅ Disconnect-Erkennung: ~4.2s (HELLO_ACK_TIMEOUT)
- ✅ Reconnect: ~2.1s (nächster Discovery-Scan)
- ✅ Keine Datenverluste (Readings werden erst bei Erfolg gespeichert)

### 6.6.2 Backend-Restart

**Szenario:**
1. System läuft
2. Backend beenden (Ctrl+C)
3. Backend neu starten

**Erwartetes Verhalten:**
- Frontend zeigt "WebSocket disconnected"
- Nach Backend-Start: Frontend reconnected automatisch
- Alle Daten persistent (SQLite)

**Ergebnis:**
- ❌ Frontend reconnected **nicht** automatisch (muss Page-Refresh machen)
- ✅ Daten persistent (SQLite DB bleibt erhalten)
- ✅ Nodes reconnecten automatisch (Hello-Loop)

**Verbesserungsvorschlag:**
WebSocket Auto-Reconnect im Frontend implementieren.

### 6.6.3 Fehlerhafte Sensordaten

**Szenario:**
- pH-Elektrode aus Wasser nehmen (trockene Elektrode)
- EC-Sonde kurzschließen

**Erwartetes Verhalten:**
- Unrealistische Werte (z.B. pH < 0 oder > 14)
- Status enthält "warning" oder "error"

**Ergebnis:**
- ⚠️ Firmware liefert unrealistische Werte (z.B. pH = 15.2)
- ❌ Kein automatisches Warning im Status

**Verbesserungsvorschlag:**
Plausibilitäts-Check in Firmware:

```cpp
if (ph < 0.0 || ph > 14.0) {
  status.add("ph_out_of_range");
}
```

---

## 6.7 Anforderungs-Erfüllung

### 6.7.1 Customer Requirements (CR)

| ID | Anforderung | Status | Bemerkung |
|----|-------------|--------|-----------|
| CR-01 | Hydroponik-Überwachung | ✅ Erfüllt | Alle 3 Parameter (pH, EC, Temp) |
| CR-02 | pH-Überwachung | ✅ Erfüllt | 12-bit ADC, 3-Punkt-Kalibrierung |
| CR-03 | EC-Überwachung | ✅ Erfüllt | 2-Punkt-Kalibrierung |
| CR-04 | Temperatur-Überwachung | ✅ Erfüllt | DS18B20, ±0.5°C |
| CR-05 | Kalibrierung | ✅ Erfüllt | Über Backend einstellbar |
| CR-06 | Zyklische Messung | ✅ Erfüllt | Konfigurierbare Intervalle |
| CR-07 | Minimalbetrieb (ohne UI) | ✅ Erfüllt | Backend läuft headless |
| CR-08 | Datenübertragung | ✅ Erfüllt | Serial (Node↔Hub), REST/WS (Hub↔Frontend) |
| CR-09 | Multi-Node | ✅ Erfüllt | Getestet mit 2 Nodes |
| CR-10 | Fehlertoleranz | ✅ Erfüllt | Auto-Reconnect nach 2-4s |
| CR-11 | Langzeitbetrieb | ⚠️ Teilweise | Getestet bis 48h, keine Langzeit-Tests (>1 Woche) |
| CR-12 | Erweiterbarkeit | ✅ Erfüllt | Neue Nodes automatisch erkannt |
| CR-13 | Persistierung | ✅ Erfüllt | SQLite, Daten bleiben nach Restart |
| CR-14 | Fotodokumentation | ✅ Erfüllt | USB-Kameras, automatische Intervalle |
| CR-15 | Visualisierung | ✅ Erfüllt | Web-UI mit Live-Updates & Charts |
| CR-16 | Datenexport | ✅ Erfüllt | ZIP mit CSV |
| CR-17 | Echtzeit-Updates | ✅ Erfüllt | WebSocket, <200ms Latenz |
| CR-18 | Historie | ✅ Erfüllt | Unbegrenzte Speicherung, Charts |

**Erfüllungsgrad**: 17/18 voll erfüllt (94%), 1/18 teilweise (CR-11)

### 6.7.2 Nicht-funktionale Anforderungen (NFR)

| ID | Anforderung | Zielwert | Ist-Wert | Status |
|----|-------------|----------|----------|--------|
| NFR-7 | Response-Zeit Backend | <500ms | 45-180ms | ✅ |
| NFR-8 | UI flüssig bei 10.000+ Datenpunkten | Ja | Chart zeigt 10.000 Punkte flüssig | ✅ |
| NFR-9 | Mehrere Nodes parallel | Ja | Getestet mit 2 Nodes | ✅ |
| NFR-10 | Login-System | Ja | ❌ Nicht implementiert | ❌ |

**Interpretation:**
- Performance-Ziele erfüllt
- Sicherheits-Feature (Login) fehlt (akzeptiert, da System für lokales Netzwerk)

---

## 6.8 Diskussion der Ergebnisse

### 6.8.1 Stärken des Systems

1. **Zuverlässige Kommunikation**: Serial-Protokoll stabiler als WLAN
2. **Schnelle Discovery**: Neue Nodes werden binnen 2-4s erkannt
3. **Gute Performance**: API-Response-Zeiten weit unter Zielvorgabe
4. **Einfaches Deployment**: SQLite + Python/React → keine komplexen Dependencies

### 6.8.2 Schwächen und Limitierungen

1. **Keine Benutzer-Authentifizierung**: System offen für alle im lokalen Netzwerk
2. **WebSocket-Reconnect fehlt**: Frontend muss manuell neu laden nach Backend-Restart
3. **Plausibilitäts-Checks fehlen**: Firmware akzeptiert unrealistische Sensorwerte
4. **Langzeit-Stabilität ungetestet**: Keine Tests >48h

### 6.8.3 Verbesserungspotenzial

| Problem | Lösung | Aufwand |
|---------|--------|---------|
| Fehlende Auth | Passwort-Login + Session-Tokens | 2-3 Tage |
| WS-Reconnect | Exponential Backoff Retry-Logik | 1 Tag |
| Plausibilitäts-Checks | Firmware-Update mit Range-Checks | 0.5 Tage |
| Langzeit-Tests | 1-Wochen-Testlauf überwachen | 1 Woche (parallel) |

---

## 6.9 Zusammenfassung

Das System erfüllt **94% der funktionalen Anforderungen** vollständig. Die wichtigsten Kernfunktionen (Messwerterfassung, Visualisierung, Multi-Node-Betrieb) funktionieren zuverlässig.

**Haupterkenntnisse:**
- Serial-basierte Node-Kommunikation bewährt sich
- Performance-Ziele übererfüllt
- Robustheit gut (Auto-Reconnect, Fehlertoleranz)
- Sicherheit vernachlässigt (akzeptabel für lokales Setup)

**Nächste Schritte für Produktiv-Einsatz:**
1. Langzeit-Stabilitäts-Tests (>1 Woche)
2. Plausibilitäts-Checks in Firmware implementieren
3. WebSocket-Reconnect im Frontend
4. Optional: Login-System für Mehrbenutzer-Szenarien
