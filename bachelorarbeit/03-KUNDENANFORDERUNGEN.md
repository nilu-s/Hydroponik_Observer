# 3.1 Kundenanforderungen (Funktionale Anforderungen)

Diese Anforderungen beschreiben die funktionalen Eigenschaften des Systems aus Anwendersicht. Die Formulierungen sind bewusst technologieunabhängig. Der Minimalbetrieb des Systems muss ohne Benutzeroberfläche möglich sein; eine UI ist optional und darf den Minimalbetrieb nicht voraussetzen.

## Übersicht

| ID | Kundenanforderung | Prio | Fit Criterion | Notes |
|---|---|---|---|---|
| CR-01 | Das System muss Hydroponik-Versuchsaufbauten überwachen. | MUSS | Erfüllt, wenn Messwerte erfasst, gespeichert und für Auswertung bereitgestellt werden. | - |
| CR-02 | Das System muss den pH-Wert der Nährlösung überwachen. | MUSS | Erfüllt, wenn pH-Messwerte zyklisch erfasst und gespeichert werden. | - |
| CR-03 | Das System muss die elektrische Leitfähigkeit der Nährlösung überwachen. | MUSS | Erfüllt, wenn EC-Messwerte zyklisch erfasst und gespeichert werden. | - |
| CR-04 | Das System muss die Temperatur der Nährlösung überwachen. | MUSS | Erfüllt, wenn Temperaturmesswerte zyklisch erfasst und gespeichert werden. | - |
| CR-05 | Das System muss Messwerte kalibriert erfassen. | MUSS | Erfüllt, wenn Kalibrierparameter angewendet werden und die erfassten Werte darauf basieren. | Kalibrierung hardwareabhängig. |
| CR-06 | Das System muss Messwerte automatisch zyklisch erfassen. | MUSS | Erfüllt, wenn Messwerte in konfigurierbaren Intervallen ohne manuellen Trigger erfasst werden. | - |
| CR-07 | Das System muss im Minimalbetrieb ohne Benutzeroberfläche funktionsfähig sein. | MUSS | Erfüllt, wenn Messwert-Erfassung und -Speicherung ohne UI möglich sind. | UI ist optional. |
| CR-08 | Das System muss Messdaten an eine zentrale Einheit übertragen. | MUSS | Erfüllt, wenn erfasste Daten zuverlässig beim zentralen System ankommen. | - |
| CR-09 | Das System muss mindestens zwei Sensor-Nodes parallel betreiben können. | MUSS | Erfüllt, wenn zwei Nodes gleichzeitig Messdaten liefern und verarbeitet werden. | - |
| CR-10 | Das System muss kurzzeitige Ausfälle tolerieren. | SOLL | Erfüllt, wenn die Datenerfassung nach kurzen Unterbrechungen ohne manuelle Eingriffe fortgesetzt wird. | - |
| CR-11 | Das System muss über längere Zeiträume stabil betrieben werden können. | SOLL | Erfüllt, wenn ein definierter Langzeitbetrieb ohne manuelle Neustarts möglich ist. | Langzeittest in Kapitel 06. |
| CR-12 | Das System muss um weitere Sensor-Nodes erweiterbar sein. | SOLL | Erfüllt, wenn zusätzliche Nodes ohne Systemumbau integriert werden können. | - |
| CR-13 | Das System muss Messdaten dauerhaft speichern. | MUSS | Erfüllt, wenn Messwerte nach Neustart weiterhin verfügbar sind. | - |
| CR-14 | Das System muss den Pflanzenzustand visuell dokumentieren können. | SOLL | Erfüllt, wenn Fotos in festgelegten Intervallen gespeichert werden. | Kamera-Hardware erforderlich. |
| CR-15 | Das System muss Messdaten visuell darstellen können. | SOLL | Erfüllt, wenn aktuelle und historische Werte für Nutzer sichtbar sind. | UI optional. |
| CR-16 | Das System muss Messdaten exportieren können. | MUSS | Erfüllt, wenn Messdaten in einem offenen Dateiformat bereitgestellt werden. | - |
| CR-17 | Das System muss Live-Messwerte in Echtzeit anzeigen können. | SOLL | Erfüllt, wenn aktuelle Werte ohne manuelle Aktualisierung sichtbar sind. | UI optional. |
| CR-18 | Das System muss historische Messwerte anzeigen können. | SOLL | Erfüllt, wenn archivierte Werte abrufbar und darstellbar sind. | UI optional. |
