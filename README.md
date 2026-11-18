# Vier Cinis für Anno 117

Experimentelle Kartenmod für **Anno 117: Pax Romana**: je eine Cinis-Insel im Norden, Osten, Süden und Westen, mit den übrigen Latium-Inseln in der Mitte.

```text
                   Cinis Nord
                       |
    Cinis West —     Latium     — Cinis Ost
                       |
                   Cinis Süd
```

## Entwicklungsstand

**Version 0.3.3 – Baugrenzen an die aktuelle Original-Cinis angeglichen.** Statisch geprüft gegen **Anno 117 Patch 3.0.1, Steam-Build 26607411**, am 18.11.2026. Veröffentlichung als **Vorabversion**, da Spieltest, Mehrspieler-Synchronisation und Vulkanzyklen mit dieser Version noch nicht bestätigt sind.

Patch 1.6.1 vergrößerte die Baufläche der Original-Cinis. Alle vier Modinstanzen referenzieren dieselbe installierte Originalinsel und übernehmen deren Patchänderungen bereits. Die zusätzliche Spielgrenze der Mod schnitt jedoch an jeder Ecke 20 Felder mehr ab als das Original. 0.3.3 korrigiert sie von `268..3828` auf `248..3848`: Innerhalb der Grenze liegen nun je Cinis **116.963 statt 114.074 Landrasterfelder**, also **2.889 mehr**, sowie unverändert 964 Küstenfelder. Landrasterfelder sind wegen zusätzlicher Bauhindernisse nicht gleichbedeutend mit frei bebaubaren Feldern. Einzelheiten und Patchnachweise: [Patch-Kompatibilität](docs/PATCH-KOMPATIBILITAET.md).

- Standard/Default-Latium in allen drei Inselgrößenvarianten; Vulkan-DLC erforderlich, keine Kampagnenunterstützung.
- Karte von 2688 × 2688 auf 4096 × 4096 Felder erweitert; Latium bleibt in der Mitte.
- Neue Spiele: vier Cinis bündig in den Ecken, mit den Küsten zur Mitte gedreht. Alle vier haben die gleiche aktuelle Inseldefinition und dieselbe Land-/Küstenmaske innerhalb der Spielgrenze.
- Kontinent- und Vulkanterrain, Positionen, Drehungen, Horizontinseln und GUIDs bleiben erhalten. Die Terrainkorrektur aus 0.3.0 wurde damals im Spiel geprüft.
- Das alte Layout für 0.2.0-Spielstände bleibt bytegleich zu 0.3.2 enthalten. Bestehende Spielstände werden nicht bearbeitet.
- Die sechs Obsidian-Korrekturen aus 0.3.2 bleiben erhalten: gleiche Zuteilung bei gleichem Forschungs-/Übersteuerungsstand und Phasenfaktor, begrenzt durch die freie Kapazität. Sie wirken auch auf andere Latium-Inseln. Siehe [Obsidian-Fix](docs/OBSIDIAN-FIX.md).
- Grundmengen, Vorratsobergrenzen, Ausbruchszeiten und Queststeuerung bleiben unverändert. Vier unabhängige Ausbruchszyklen sind nicht nachgewiesen.
- Mehrspieler in den Metadaten aktiviert: Alle Teilnehmer brauchen dasselbe ZIP und dieselbe Spielversion. Dies ersetzt keinen gemeinsamen Spieltest.

[Layoutvorschau](docs/layout.html) · [Installation und Testablauf](docs/TESTANLEITUNG.md) · [Änderungen](CHANGELOG.md) · [Technischer Stand](research/STATUS.md)

Die HTML-Vorschau lokal herunterladen und im Browser öffnen; GitHub zeigt die Datei als Quelltext an.

## Download

Das vollständige Modpaket liegt im **[Release v0.3.3](https://github.com/insidi/Anno-117-four-cinis-mod/releases/tag/v0.3.3)**: **[ZIP herunterladen](https://github.com/insidi/Anno-117-four-cinis-mod/releases/download/v0.3.3/cinis-four-directions-v0.3.3.zip)**. Daneben liegt eine `.zip.sha256`-Prüfsumme. Die automatisch von GitHub angebotenen „Source code“-Archive sind kein installierbares Modpaket.

Das Repository enthält Quellcode und Dokumentation; die Kartendateien werden als Release-Assets bereitgestellt.

## Installation

1. Anno 117 schließen und das Mod-ZIP entpacken.
2. Den Ordner `cinis-four-directions` nach `Dokumente/Anno 117 - Pax Romana/mods/` kopieren.
3. Prüfen, dass `modinfo.json` direkt im Modordner liegt, und die Mod im Spiel aktivieren.
4. Für die korrigierten Baugrenzen ein **neues freies Spiel mit Standard/Default-Latium** und aktiviertem Vulkan-DLC starten.

Beim Update den bisherigen Modordner vollständig ersetzen, keine zweite Modkopie daneben behalten. Vorhandene Spielstände behalten ihr Layout und können auch ihre gespeicherte Spielgrenze behalten. Ob ein bestehender Spielstand die neue Grenze übernimmt, ist noch nicht bestätigt. Die Mod bearbeitet keine Save-Dateien und setzt keine Vorräte beim Laden zurück. Ein mit der Mod erzeugtes Spiel weiterhin mit der Mod laden.

Für Mehrspieler installiert jeder Teilnehmer dasselbe ZIP und startet das Spiel neu. Die SHA256-Prüfsumme muss auf allen Rechnern gleich sein. Zunächst einen separaten Testspielstand verwenden; Bauflächen, Ausbruch, Obsidian sowie gemeinsames Speichern/Laden prüfen. Die vollständigen Schritte und Grenzen stehen in der [Testanleitung](docs/TESTANLEITUNG.md).

## Repository-Struktur

| Pfad | Inhalt |
| --- | --- |
| `config/modinfo.json` | Version, Mod-ID und Mehrspielerfreigabe |
| `config/release.json` | Geprüfte Spielversion, Baugrenzen und SHA256 des Basis-Pakets |
| `config/obsidian-modops.xml` | Gemeinsame Quelle der sechs Obsidian-Korrekturen |
| `scripts/build_release.py` | Vollständiges Release-ZIP aus dem festgelegten Basis-Paket |
| `scripts/audit_cinis.py` | Vergleich aller Instanzen mit den aktuell installierten Spieldaten |
| `scripts/test_release.py` | Paket-, Karten-, Metadaten- und Regressionsprüfungen |
| `scripts/Validate-Cinis.ps1`, `scripts/test_obsidian_balance.py` | Echter ModOp-Test und Obsidian-Rechenmodell |
| `scripts/cinis_v2/` | FileDB-/RDA-Werkzeuge und historische Kartenpipeline ([Beschreibung](scripts/cinis_v2/README.md)) |
| `.github/workflows/release.yml` | Build, Prüfung und Veröffentlichung bei Versionstags |
| `docs/`, `CHANGELOG.md`, `research/STATUS.md` | Anleitungen, Änderungen und Untersuchungsergebnisse |
| `research/` außer `STATUS.md`, `tools/`, `dist/` | Lokale Spieldaten, Werkzeuge und Build-Ausgaben; von Git ausgeschlossen |

## Lokal bauen

**Python 3.11 oder neuer**, keine Zusatzpakete und keine lokale Spielinstallation für den Paket-Build erforderlich:

```powershell
python scripts/build_release.py
python scripts/test_release.py
```

Der Build lädt das veröffentlichte vollständige 0.3.2-Paket und prüft dessen festgelegten SHA256-Wert aus `config/release.json`. Dieses Basis-Asset muss verfügbar bleiben. Für einen lokalen Build ohne Download:

```powershell
python scripts/build_release.py --base-zip dist/cinis-four-directions-v0.3.2.zip --tag v0.3.3
python scripts/test_release.py --base-zip dist/cinis-four-directions-v0.3.2.zip
```

Ausgabe: `dist/v0.3.3/cinis-four-directions/`, `dist/cinis-four-directions-v0.3.3.zip`, Prüfsumme und `dist/build-v0.3.3.json`. Das Paket enthält 18 Kartenkomponenten, ModOps, Metadaten und vier Anleitungen, keine Entwicklungsdateien. Genau drei `.a7tinfo` und die Easy-`.a7t` erhalten einen anderen `PlayableArea`-Wert; die übrigen 14 Kartenkomponenten bleiben bytegleich. Alle anderen FileDB-Felder der vier geänderten Dateien werden nach erneutem Einlesen vollständig verglichen.

Die historische vollständige Kartenpipeline ist unter `scripts/cinis_v2/` dokumentiert. Sie braucht zusätzliche lokale Eingabedaten und Werkzeuge. Der aktuelle Paket-Build ist davon unabhängig; `build_obsidian_fix.py` ist nur noch für die historischen Versionen 0.3.1/0.3.2 vorgesehen.

## Validierung

Für einen erneuten Abgleich mit der eigenen Installation benötigt `audit_cinis.py` zusätzlich NumPy. Es liest die RDA-Verzeichnisse sämtlicher installierter Archive, berücksichtigt Patch-Overrides und vergleicht Inseldefinition, Positionen, Drehungen, Terrain und Land-/Küstenmasken aller 24 Instanzen. Bei abweichendem Steam-Build oder EXE-Hash stoppt es, damit ein neues Spielupdate zuerst untersucht werden muss.

```powershell
python -m pip install numpy
python scripts/audit_cinis.py --game "C:/Program Files (x86)/Steam/steamapps/common/Anno 117 - Pax Romana" --mod dist/v0.3.3/cinis-four-directions
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Validate-Cinis.ps1
python scripts/test_obsidian_balance.py
```

Der PowerShell-Test benötigt `tools/package/external/xmltest2.exe` aus den Anno Modding Tools und die zuvor vom Audit extrahierte aktuelle `assets.xml`. Er prüft mit dem echten ModOp-Werkzeug genau drei geänderte Karten-Assets und sechs Obsidianfelder in zwei Vulkan-Assets; alle übrigen Vulkanfelder müssen gleich bleiben. Die Python-Regressionstests prüfen die so gepatchten Werte anhand des lesend untersuchten nativen Rechenmodells. Berichte bleiben unter `research/` und `dist/` lokal.

Der Actions-Workflow baut und prüft das Paket ohne private Spieldaten. Tags müssen exakt zu `config/modinfo.json` passen; Release-Notizen liegen unter `docs/RELEASE-<Version>.md`. Nach erfolgreichen Prüfungen werden ZIP und Prüfsumme hochgeladen und vor Veröffentlichung anhand der GitHub-Asset-Digests geprüft. `config/release.json` steuert den Vorabversionsstatus. Ein manueller Workflow-Start auf `main` baut nur ein Actions-Artefakt.

Die automatischen Prüfungen ersetzen keinen Spieltest. Offen bleiben insbesondere Mehrspieler über längere Zeit, Vulkanquests und die nachträgliche Anlage eines fehlenden Obsidian-Eintrags in alten Spielständen. Die Baugrenze in Medium/Hard muss zusätzlich im Spiel geprüft werden, da dort die flache Weltdatei eigene, unveränderte SessionSettings enthält.

## Referenzen

- [Patch 1.6.1](https://www.anno-union.com/updates/anno-117-pax-romana-patch-1-6-1/) · [Patch 3.0.1](https://www.anno-union.com/updates/anno-117-pax-romana-patch-3-0-1/)
- [Anno Modding Tools](https://github.com/anno-mods/vscode-anno)
- [AnnoMapEditorRenew](https://github.com/flamme-demon/AnnoMapEditorRenew)
- [Anno Modloader: ModOps](https://jakobharder.github.io/anno-mod-loader/modops/basics/)
- [Anno Modloader: Modinfo](https://jakobharder.github.io/anno-mod-loader/modinfo/)

Unoffizielles Modding-Projekt, nicht mit Ubisoft verbunden. Extrahierte Spieldaten und heruntergeladene Drittanbieter-Werkzeuge gehören nicht in dieses Git-Repository.
