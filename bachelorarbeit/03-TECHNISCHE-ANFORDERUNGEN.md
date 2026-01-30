# 3.2 Technische Anforderungen

Diese Anforderungen beschreiben die technische Umsetzung des Systems. Jede Anforderung verweist auf eine Kundenanforderung (CR) oder ist als Constraint gekennzeichnet.

## Übersicht

| ID | Technische Anforderung | Prio | Trace (CR-xx oder Constraint) | Fit Criterion | Verifikationsart | Notes |
|---|---|---|---|---|---|---|
| TR-01 | Das System muss aus Sensor-Nodes und einem zentralen Hub bestehen. | MUSS | CR-01 | Erfüllt, wenn Node- und Hub-Komponenten eindeutig identifizierbar sind. | Inspektion | - |
| TR-02 | Der Hub muss Messwerte von Nodes empfangen und verarbeiten können. | MUSS | CR-01, CR-08 | Erfüllt, wenn eingehende Messdaten übernommen und weiterverarbeitet werden. | Test | - |
| TR-03 | Der Hub muss mehrere Nodes gleichzeitig verwalten können. | MUSS | CR-09, CR-12 | Erfüllt, wenn parallele Verbindungen mehrerer Nodes aktiv sind. | Test | - |
| TR-04 | Jede Node muss eine eindeutige, stabile ID besitzen. | MUSS | CR-12 | Erfüllt, wenn jede Node mit einer eindeutigen Kennung erkannt wird. | Inspektion | - |
| TR-05 | Die Kommunikation zwischen Node und Hub muss über serielle JSON-Nachrichten erfolgen. | MUSS | CR-08 | Erfüllt, wenn Nachrichten als JSON über eine serielle Verbindung ausgetauscht werden. | Inspektion | Protokollbindung an Serial-JSON. |
| TR-06 | Die Node muss pH-, EC- und Temperaturwerte lokal erfassen. | MUSS | CR-02, CR-03, CR-04 | Erfüllt, wenn alle drei Messgrößen in einem Messzyklus verfügbar sind. | Test | - |
| TR-07 | Kalibrierungsdaten müssen vom Hub an die Node übertragen und angewendet werden können. | MUSS | CR-05 | Erfüllt, wenn eine Kalibrierung übertragen wird und sich die Messwerte entsprechend ändern. | Test | - |
| TR-08 | Die Node muss eine 3-Punkt-pH-Kalibrierung unterstützen. | MUSS | CR-05 | Erfüllt, wenn drei Kalibrierpunkte gespeichert und genutzt werden können. | Inspektion | - |
| TR-09 | Die Node muss eine 2-Punkt-EC-Kalibrierung unterstützen. | MUSS | CR-05 | Erfüllt, wenn zwei Kalibrierpunkte gespeichert und genutzt werden können. | Inspektion | - |
| TR-10 | Das Backend muss Messwerte in konfigurierbaren Intervallen erfassen. | MUSS | CR-06 | Erfüllt, wenn das Intervall angepasst werden kann und die Erfassung dem Intervall folgt. | Test | - |
| TR-11 | Mess- und Foto-Intervalle müssen pro Setup konfigurierbar sein. | SOLL | CR-06, CR-14 | Erfüllt, wenn Änderungen pro Setup wirksam werden. | Test | - |
| TR-12 | Messwerte müssen persistent mit Zeitstempel, Node-ID und Setup-ID gespeichert werden. | MUSS | CR-13 | Erfüllt, wenn gespeicherte Datensätze diese Felder enthalten und nach Neustart verfügbar sind. | Inspektion | - |
| TR-13 | Das Backend muss historische Messwerte abrufbar bereitstellen. | SOLL | CR-18 | Erfüllt, wenn historische Daten nach Zeitraum oder Limit abrufbar sind. | Test | - |
| TR-14 | Das Backend muss Messdaten als CSV/ZIP exportieren können. | MUSS | CR-16 | Erfüllt, wenn ein Exportformat erzeugt und heruntergeladen werden kann. | Test | - |
| TR-15 | Das Backend muss aktuelle Messwerte als Live-Stream bereitstellen können. | SOLL | CR-17 | Erfüllt, wenn aktuelle Werte ohne manuelle Aktualisierung bereitgestellt werden. | Test | - |
| TR-16 | Der Hub muss Fotos in konfigurierbaren Intervallen aufnehmen und speichern können. | SOLL | CR-14 | Erfüllt, wenn Fotos automatisch gespeichert und abrufbar sind. | Demonstration | Kamera-Hardware erforderlich. |
| TR-17 | Nodes müssen für die automatische Wiedererkennung regelmäßige Hello-Nachrichten senden. | SOLL | CR-10, CR-12 | Erfüllt, wenn Hello-Nachrichten zyklisch gesendet werden. | Test | - |
| TR-18 | Der Hub muss neue Nodes automatisch erkennen und registrieren. | SOLL | CR-12 | Erfüllt, wenn eine neue Node ohne manuelle Konfiguration erscheint. | Test | - |
| TR-19 | Der Hub muss Offline-Status von Nodes erkennen und kennzeichnen. | SOLL | CR-10 | Erfüllt, wenn fehlende Node-Kommunikation als Offline-Status markiert wird. | Test | - |
| TR-20 | Das System muss nach kurzen Verbindungsunterbrechungen die Datenerfassung fortsetzen können. | SOLL | CR-10 | Erfüllt, wenn nach Wiederherstellung der Verbindung Messdaten weiter erfasst werden. | Test | - |
| TR-21 | Der Minimalbetrieb muss ohne UI möglich sein, ohne dass Datenfluss und Speicherung entfallen. | MUSS | CR-07 | Erfüllt, wenn Messdaten ohne gestartete UI erfasst und gespeichert werden. | Test | - |
| TR-22 | Der Langzeitbetrieb muss durch kontinuierliche Hintergrundprozesse im Backend unterstützt werden. | SOLL | CR-11 | Erfüllt, wenn Capture- und Verarbeitungsprozesse ohne UI dauerhaft laufen. | Analyse | - |
| TR-23 | Eine Web-UI muss Messwerte und Status visuell darstellen können. | SOLL | CR-15 | Erfüllt, wenn UI aktuelle und historische Werte sichtbar macht. | Demonstration | UI optional. |
| TR-24 | Die UI muss historische Messwerte anzeigen können. | SOLL | CR-18 | Erfüllt, wenn historische Daten in der UI abrufbar und darstellbar sind. | Demonstration | UI optional. |
| TR-25 | Das System muss lokal ohne externe Cloud-Abhängigkeit betrieben werden. | MUSS | Constraint | Erfüllt, wenn keine externen Cloud-Dienste für den Betrieb erforderlich sind. | Analyse | Constraint aus Randbedingungen. |
| TR-26 | Die Sensor-Nodes müssen auf der Mikrocontroller-Plattform RP2040 basieren. | MUSS | Constraint | Erfüllt, wenn die Firmware auf RP2040 lauffähig ist. | Inspektion | Constraint aus Randbedingungen. |
| TR-27 | Das Backend muss auf einem Standard-PC ausführbar sein; Windows wird unterstützt. | MUSS | Constraint | Erfüllt, wenn das Backend unter Windows startfähig ist. | Demonstration | Constraint aus Randbedingungen. |
| TR-28 | Der Betrieb muss ohne Internetverbindung möglich sein. | MUSS | Constraint | Erfüllt, wenn alle Kernfunktionen offline verfügbar sind. | Demonstration | Constraint aus Randbedingungen. |

## Traceability-Matrix (CR → TR)

| CR-ID | Zugeordnete TR-IDs | Kommentar |
|---|---|---|
| CR-01 | TR-01, TR-02, TR-12 | - |
| CR-02 | TR-06 | - |
| CR-03 | TR-06 | - |
| CR-04 | TR-06 | - |
| CR-05 | TR-07, TR-08, TR-09 | - |
| CR-06 | TR-10, TR-11 | - |
| CR-07 | TR-21 | - |
| CR-08 | TR-02, TR-05 | - |
| CR-09 | TR-03 | - |
| CR-10 | TR-17, TR-19, TR-20 | - |
| CR-11 | TR-22 | - |
| CR-12 | TR-03, TR-04, TR-18 | - |
| CR-13 | TR-12 | - |
| CR-14 | TR-16 | - |
| CR-15 | TR-23 | - |
| CR-16 | TR-14 | - |
| CR-17 | TR-15 | - |
| CR-18 | TR-13, TR-24 | - |

## Hinweise für spätere Test & Evaluation

- Messgenauigkeit und Kalibrierung (pH/EC/Temperatur) sind hardwareabhängig und müssen mit realen Sensoren verifiziert werden.
- Fotoqualität und Aufnahmerhythmus sind nach Verfügbarkeit der Kamerahardware zu prüfen.
- Langzeitbetrieb ist als separater Dauerlauf zu verifizieren.
- Multi-Node-Betrieb und Reconnect-Verhalten sind unter Lastbedingungen zu testen.
- Offline-Betrieb ohne Internet und ohne UI ist als Systemtest nachzuweisen.
