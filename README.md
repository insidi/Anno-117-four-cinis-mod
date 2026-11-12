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

**Version 0.3.2 – Gleichmäßige Obsidian-Auffüllung.** Süd hatte im untersuchten 0.3.0-Spielstand kein Obsidian; Ost und West erhielten nur winzige Auffüllungen. 0.3.2 schaltet die Entfernungsskalierung vollständig ab und ersetzt zufällige Auffüllboni durch feste Mittelwerte. Alle vier Cinis erhalten bei gleichem Forschungs-/Übersteuerungsstand und Phasenfaktor dieselbe Menge, begrenzt durch ihre freie Kapazität. Das betrifft auch die übrigen Latium-Inseln. Der gemeinsame Spieltest steht noch aus. Siehe [Befunde und Testablauf](docs/OBSIDIAN-FIX.md).

Die Kartendateien entsprechen unverändert 0.3.0. Dessen Terrainkorrektur und gedrehte Ecken wurden am 24.09.2026 im Spiel geprüft. Quests und Mehrspieler-Synchronisation über längere Zeit sind weiterhin offen.

- Standard/Default-Latium in allen drei Inselgrößenvarianten.
- Karte von 2688 × 2688 auf 4096 × 4096 Felder erweitert.
- Neue Spiele: vier Cinis bündig in den Ecken, die Kopien per `Rotation90` zur Kartenmitte gedreht; bestehende Inselplätze gemeinsam zur Mitte verschoben.
- Das eingebackene Kontinent- und Vulkanterrain der Weltdatei (Kollision, Kamerahöhe) liegt an allen vier Cinis. In 0.2.0 fehlte es bei den Kopien.
- Bestehende 0.2.0-Spielstände laden weiter und bekommen die Terrainkorrektur, behalten aber ihr altes Layout (siehe [Testanleitung](docs/TESTANLEITUNG.md)).
- Mehrspieler in den Mod-Metadaten aktiviert. Alle Teilnehmer müssen dasselbe Modpaket und dieselbe Spielversion verwenden.
- Ausbruchszeiten, Grundmengen, Vorratsobergrenzen und Queststeuerung bleiben unverändert. Geändert werden zwei Entfernungswerte und vier Grenzen der zufälligen Obsidianboni. Vier unabhängige Ausbruchszyklen sind **nicht nachgewiesen**.
- Vulkan-DLC erforderlich. Keine Kampagnenunterstützung.

[Layoutvorschau](docs/layout.html) · [Installation und Testablauf](docs/TESTANLEITUNG.md) · [Technischer Stand](research/STATUS.md)

Die HTML-Vorschau lokal herunterladen und im Browser öffnen; GitHub zeigt die Datei als Quelltext an.

## Download

Das vollständige Modpaket liegt bei den [Releases](https://github.com/insidi/Anno-117-four-cinis-mod/releases): **[v0.3.2](https://github.com/insidi/Anno-117-four-cinis-mod/releases/tag/v0.3.2)** mit ZIP und `.sha256`-Prüfsumme. Das Git-Repository selbst enthält nur Quellcode und Dokumentation; die Kartendateien werden nicht eingecheckt.

## Installation

1. Anno 117 schließen und das ZIP der gewünschten Version entpacken.
2. Den Ordner `cinis-four-directions` in den eigenen Dokumente-Ordner unter `Anno 117 - Pax Romana/mods/` kopieren.
3. Prüfen, dass `modinfo.json` direkt im Modordner liegt, und die Mod im Spiel aktivieren.
4. Ein vorhandenes Spiel laden oder ein neues freies Spiel mit **Standard/Default-Latium** und aktiviertem Vulkan-DLC starten.

Beim Update den bisherigen Modordner komplett ersetzen. Bestehende Spielstände behalten ihr Layout. 0.3.2 setzt den Obsidianvorrat beim Laden nicht zurück: Die geänderte Auffüllung muss beim nächsten Ausbruch geprüft werden.

Für Mehrspieler installiert jeder Teilnehmer dasselbe ZIP und startet das Spiel neu. Den ersten Versuch mit einem separaten Testspielstand durchführen; die vollständigen Prüfschritte stehen in der [Testanleitung](docs/TESTANLEITUNG.md).

## Repository-Struktur

| Pfad | Inhalt |
| --- | --- |
| `config/modinfo.json` | Version, Mod-ID und Mehrspielerfreigabe |
| `config/obsidian-modops.xml` | Gemeinsame Quelle der sechs Obsidian-Korrekturen |
| `scripts/build_obsidian_fix.py` | Vollständiges Update aus einem vorhandenen 0.3.x-Paket, ohne Kartenneubau |
| `scripts/test_obsidian_balance.py` | Regressionstests für Gleichverteilung, Boni, Kapazitätsgrenzen und Paket-Update |
| `scripts/MapBuild/` | C#-Werkzeug zum Bearbeiten, Verpacken und Prüfen der Kartendaten |
| `scripts/cinis_v2/` | Python-Build-Stufe 2: Weltdateien für beide Layouts und `assets.xml` ([Beschreibung](scripts/cinis_v2/README.md)) |
| `scripts/*.ps1` | Kompilierung, Mod-Build, Paketierung, Validierung und Vorschau |
| `docs/` | Testanleitung und Layoutvorschau |
| `research/STATUS.md` | Erkenntnisse zum Dateiformat und offene Aufgaben |
| `research/` (sonstige Dateien) | Lokale Spieldaten, Zwischenergebnisse und Prüfberichte; von Git ausgeschlossen |
| `tools/` | Lokale Werkzeuge und Bibliotheken; von Git ausgeschlossen |
| `dist/` | Erzeugter Modordner und ZIP-Pakete; von Git ausgeschlossen |

## Lokal bauen

Für das **Update 0.3.2** genügt Python 3.11 oder neuer ohne Zusatzpakete sowie ein installiertes oder entpacktes vollständiges 0.3.x-Modpaket:

```powershell
python scripts/build_obsidian_fix.py --source "$env:USERPROFILE/Documents/Anno 117 - Pax Romana/mods/cinis-four-directions"
```

Das Skript schreibt den Modordner, das vollständige ZIP und die SHA256-Prüfsumme nach `dist/`. Es ändert weder die Eingabemod noch Spielstände. Es prüft alle übernommenen Kartendateien auf Bytegleichheit und jedes ZIP-Mitglied gegen den erzeugten Ordner. Nur die Mod-Assets, Metadaten und Anleitung werden aktualisiert. Für die anschließende Prüfung gegen die eigenen aktuellen Spieldaten:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Validate-Cinis.ps1 -AssetsPath "<extrahierte aktuelle assets.xml>"
python scripts/test_obsidian_balance.py
```

Die Validierung benötigt `tools/package/external/xmltest2.exe` aus den Anno Modding Tools. Ihr Bericht liegt unter `research/validation.json`, der Paketvergleich unter `research/obsidian-package-check.json`.

### Vollständige Kartenpipeline aus 0.3.0

Die folgende Pipeline wird für den Obsidian-Fix nicht benötigt. Sie setzt zusätzlich die MapBuild-Quellen und alle unten aufgeführten Werkzeuge und Eingabedaten voraus.

Der Build setzt **Windows, PowerShell und vorbereitete lokale Eingabedaten** voraus. Ein frischer Git-Clone ist noch nicht sofort baubar: Die Skripte laden keine Abhängigkeiten herunter und extrahieren die Spieldaten nicht automatisch.

Die derzeit fest eingestellten Werkzeugpfade sind:

- `tools/dotnet6/`: portable .NET Runtime 6.0.36.
- `tools/dotnet-sdk6/`: .NET SDK 6.0.428, einschließlich der .NET-6.0.36-Referenzassemblies.
- `tools/package/external/`: Werkzeuge aus Anno Modding Tools 2.3.0, insbesondere `RdaConsole.exe` und `xmltest2.exe`.
- `tools/map-editor-source/flamme-demon-AnnoMapEditorRenew-35c302a/AnnoMapEditor/Libs/`: `FileDBReader.dll`, `FileDBSerializer.dll` und `RDAExplorer.dll`.
- `tools/sharpziplib-1.4.2/lib/net6.0/`: SharpZipLib 1.4.2.

Für die zweite Build-Stufe wird außerdem **Python 3 mit numpy** benötigt (im `PATH` oder über die Umgebungsvariable `CINIS_PYTHON`).

Aus der eigenen Spielinstallation werden folgende Eingaben benötigt:

- `research/config/data/base/config/export/assets.xml`.
- Die drei DLC01-Standard-Kartenvorlagen (`easy`, `medium`, `hard`) als `.a7tinfo` unter ihrer ursprünglichen Verzeichnisstruktur in `research/dlc01/`.
- Die aus den zugehörigen `.a7t`-Archiven entpackte `gamedata.data` unter `research/map-default-easy/` und `research/map-default-medium/`. Die Easy-Datei liefert außerdem den Terrainblock der Cinis für Build-Stufe 2.

Der aktuelle Build verwendet für Medium und Hard dieselbe Meeresvorlage: Ihre Originalarchive waren in der untersuchten Spielversion identisch. Beide enthalten keine eingebackene Höhe; nur die Easy-Vorlage trägt das Cinis-Terrain. Nach Spielupdates müssen Patch-Overrides und diese Annahme erneut geprüft werden. Weitere Formatdetails stehen im [Untersuchungsstand](research/STATUS.md).

Im Repository-Verzeichnis ausführen:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Compile-MapBuild.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Build-Cinis.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Validate-Cinis.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Make-Preview.ps1
```

`Build-Cinis.ps1` führt nach MapBuild die Python-Stufe `scripts/cinis_v2/build_v2.py` aus. Sie baut die Weltdateien für den alten Pfad `data/phil/cinis_four` (bestehende Spielstände) und den neuen Pfad `data/phil/cinis_four_v2` (neue Spiele) sowie die `assets.xml`.

`ExecutionPolicy Bypass` gilt hier nur für den jeweiligen PowerShell-Prozess. Die Skripte installieren die Mod nicht im Spielverzeichnis.

Für die Paketierung des Obsidian-Updates den oben beschriebenen Python-Build verwenden. Die Version stammt aus `config/modinfo.json`. Für eine Veröffentlichung werden ZIP und Prüfsumme als Anhang an ein Release mit dem Tag `v<Version>` gehängt.

## Validierung

Der Build prüft die FileDB-Daten durch erneutes Einlesen und vergleicht die Nutzdaten gepackter RDA-Archive nach dem Entpacken per SHA256. Außerdem werden Inselanzahl, Kartengrenzen und Überschneidungen zwischen Cinis und den konservativen Begrenzungsrechtecken der übrigen Inselplätze geprüft.

`build_v2.py` prüft, dass Medium und Hard keine eingebackene Höhe haben und dass alle Inselplätze im neuen Spielbereich liegen, ohne eine Cinis zu überdecken.

`Validate-Cinis.ps1` wendet die XML-Patches mit `xmltest2` an und prüft, dass genau die drei vorgesehenen Karten-Assets und sechs Obsidianwerte geändert werden. Alle übrigen Vulkanfelder müssen unverändert bleiben, die Horizontinseln vollständig sein und beide Vorlagenpfade im Paket liegen. `test_obsidian_balance.py` prüft die gepatchten Assets anhand des aus der lokalen Spielroutine abgeleiteten Rechenmodells. Der lokale Bericht liegt unter `research/validation.json`.

Diese Prüfungen ersetzen keinen gemeinsamen Spieltest auf Host und Clients.

## Referenzen

- [Anno Modding Tools](https://github.com/anno-mods/vscode-anno)
- [AnnoMapEditorRenew](https://github.com/flamme-demon/AnnoMapEditorRenew)
- [Anno Modloader: ModOps](https://jakobharder.github.io/anno-mod-loader/modops/basics/)
- [Anno Modloader: Modinfo](https://jakobharder.github.io/anno-mod-loader/modinfo/)

Unoffizielles Modding-Projekt, nicht mit Ubisoft verbunden. Extrahierte Spieldaten und heruntergeladene Drittanbieter-Werkzeuge gehören nicht in dieses Git-Repository.
