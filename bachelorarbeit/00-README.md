# Bachelorarbeit: SensorHUB für Hydroponik-Monitoring

## Struktur (Construction Type Thesis)

Diese Dateien bilden die Kapitelstruktur der Bachelorarbeit gemäß "Construction type of work" Vorgabe:
**Anforderungen → Konzeption/Entwurf → Implementierung → Test/Evaluation → Fazit/Ausblick**

### Vorspann

- `00-DECKBLATT.md` - Titelseite
- `00-ZUSAMMENFASSUNG.md` - Zusammenfassung (DE) + Abstract (EN) + Keywords
- `00-VERZEICHNISSE.md` - Inhalts-, Abbildungs-, Tabellen-, Abkürzungsverzeichnis

### Hauptkapitel

- `01-EINLEITUNG.md` - **Kapitel 1: Einleitung**
  - Motivation, Problemstellung, Zielsetzung, Abgrenzung, Aufbau
  
- `02-GRUNDLAGEN.md` - **Kapitel 2: Grundlagen (Theory)**
  - Domänen-Grundlagen (Hydroponik)
  - IoT-/Sensornetz-Grundlagen
  - Web-/Backend-Grundlagen
  - Stand der Technik

- `03-ANFORDERUNGEN.md` - **Kapitel 3: Anforderungen**
  - Stakeholder & Use-Cases
  - Kundenanforderungen (CR) → `03-KUNDENANFORDERUNGEN.md`
  - Technische Anforderungen (TR) → `03-TECHNISCHE-ANFORDERUNGEN.md`
  - Nicht-funktionale Anforderungen
  - Randbedingungen

- `04-KONZEPTION-ENTWURF.md` - **Kapitel 4: Konzeption und Entwurf**
  - Systemarchitektur (Node-Hub-Modell)
  - Datenmodell (ER-Diagramm, Datenbank-Schema)
  - Kommunikationsprotokolle (Serial, REST, WebSocket)
  - Sicherheitskonzept

- `05-IMPLEMENTIERUNG.md` - **Kapitel 5: Implementierung**
  - Hardware-Entwicklung (PCB-Design, Sensoren)
  - Firmware-Implementierung (Pico/Arduino)
  - Backend-Implementierung (FastAPI)
  - Frontend-Implementierung (React)
  - Kamera-Integration (C# Worker)

- `06-TEST-UND-EVALUATION.md` - **Kapitel 6: Test und Evaluation**
  - Teststrategie (Unit/Integration/System)
  - Testszenarien & Ergebnisse
  - Performance-Tests
  - Robustheit-Tests
  - Anforderungs-Erfüllung

- `07-FAZIT-AUSBLICK.md` - **Kapitel 7: Fazit und Ausblick**
  - Wichtige Designentscheidungen
  - Grenzen & Limitierungen
  - Ausblick & Roadmap

### Nachspann

- `08-LITERATURVERZEICHNIS.md` - Literaturverzeichnis
- `09-ANHANG.md` - Anhang
  - API-Dokumentation
  - Schaltpläne & PCB-Layout
  - Konfigurationsdateien
  - Test-Protokolle
  - Eidesstattliche Erklärung

---

## Änderungen gegenüber ursprünglicher Struktur

### Zusammengeführte Kapitel

**Alt**: Kapitel 4-6 waren fragmentiert
- `04-gesamtarchitektur.md`
- `05-datenmodell.md`
- `06-protokolle-api.md`

**Neu**: Kapitel 4 (Design) vereint alle Design-Aspekte
- Architektur + Datenmodell + Protokolle in einem Kapitel

### Umbenannte/Erweiterte Kapitel

**Alt**: 
- `07-implementierung.md` (nur Software)
- `08-laufzeitverhalten.md`

**Neu**:
- `05-IMPLEMENTIERUNG.md` (Hardware + Software + Laufzeitverhalten)

**Alt**:
- `09-test-evaluation.md` (Platzhalter)

**Neu**:
- `06-TEST-UND-EVALUATION.md` (Testkapitel ausgearbeitet, Tests ausstehend)

### Begründung

Die neue Struktur folgt der **"Construction type of work"** Vorgabe aus der Thesis-Vorlage:

1. **Introduction** (Kap. 1)
2. **Theory** (Kap. 2)
3. **Requirements** (Kap. 3)
4. **Design** (Kap. 4)
5. **Implementation** (Kap. 5)
6. **Test** (Kap. 6)
7. **Discussion/Conclusion** (Kap. 7)

Dies ist die **Standard-Struktur für Software-Entwicklungs-Theses** und macht die Arbeit übersichtlicher als die ursprüngliche 10-Kapitel-Struktur.

---

## Verwendung

### Markdown-Workflow

1. **Direkt bearbeiten** für die Rohfassung
2. **Diagramme** mit Mermaid oder Draw.io erstellen
3. **Literaturverzeichnis** mit Zotero/BibTeX verwalten

### LaTeX-Export (optional)

```bash
# Mit Pandoc konvertieren
pandoc --from markdown --to latex \
  01-EINLEITUNG.md \
  02-GRUNDLAGEN.md \
  03-ANFORDERUNGEN.md \
  04-KONZEPTION-ENTWURF.md \
  05-IMPLEMENTIERUNG.md \
  06-TEST-UND-EVALUATION.md \
  07-FAZIT-AUSBLICK.md \
  -o thesis.tex
```

### Abgabeformat

Je nach Hochschul-Anforderungen:
- **PDF**: Via Pandoc oder LaTeX
- **Word**: Via Pandoc (`--to docx`)
- **HTML**: Via Pandoc (`--to html --standalone`)

---

## Nächste Schritte

Offene TODOs stehen in `../todo.md` und sind **kein** Teil der Bachelorarbeit.

### Inhaltlich

- [ ] Kapitel 1-2: Platzhalter mit Inhalten füllen
- [ ] Kapitel 4-5: Diagramme/Schaltpläne einfügen
- [ ] Kapitel 7: Fazit & Ausblick vervollständigen
- [ ] Literaturverzeichnis: Quellen recherchieren
- [ ] Anhang: API-Docs + Schaltpläne ergänzen

### Formal

- [ ] Abstract (EN) schreiben
- [ ] Abbildungsverzeichnis erstellen
- [ ] Tabellenverzeichnis erstellen
- [ ] Abkürzungsverzeichnis vervollständigen
- [ ] Formatierung für finale Abgabe festlegen
- [ ] Rechtschreibung & Grammatik prüfen
