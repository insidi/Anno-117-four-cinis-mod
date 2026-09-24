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

**Version 0.3.0 – Mehrspieler-Prototyp.** Im Spiel getestet am 24.09.2026: In einem laufenden 0.2.0-Mehrspielerspielstand (Easy) sind die drei Kopien jetzt fest (Schiffe stoppen an der Küste, die Kamera folgt den Vulkanen); in einem neuen Spiel stehen alle vier Cinis gedreht in den Ecken. Vulkanausbrüche, Quests und Mehrspieler-Synchronisation über längere Zeit sind noch nicht geprüft.

- Standard/Default-Latium in allen drei Inselgrößenvarianten.
- Karte von 2688 × 2688 auf 4096 × 4096 Felder erweitert.
- Neue Spiele: vier Cinis bündig in den Ecken, die Kopien per `Rotation90` zur Kartenmitte gedreht; bestehende Inselplätze gemeinsam zur Mitte verschoben.
- Das eingebackene Kontinent- und Vulkanterrain der Weltdatei (Kollision, Kamerahöhe) liegt an allen vier Cinis. In 0.2.0 fehlte es bei den Kopien.
- Bestehende 0.2.0-Spielstände laden weiter und bekommen die Terrainkorrektur, behalten aber ihr altes Layout (siehe [Testanleitung](docs/TESTANLEITUNG.md)).
- Mehrspieler in den Mod-Metadaten aktiviert. Alle Teilnehmer müssen dasselbe Modpaket und dieselbe Spielversion verwenden.
- Vulkan- und Queststeuerung bleiben unverändert. Vier unabhängige Ausbruchszyklen sind **nicht nachgewiesen**.
- Vulkan-DLC erforderlich. Keine Kampagnenunterstützung.

[Layoutvorschau](docs/layout.html) · [Installation und Testablauf](docs/TESTANLEITUNG.md) · [Technischer Stand](research/STATUS.md)

Die HTML-Vorschau lokal herunterladen und im Browser öffnen; GitHub zeigt die Datei als Quelltext an.

## Download

Das fertige Modpaket liegt als ZIP bei den [Releases](https://github.com/insidi/Anno-117-four-cinis-mod/releases). Aktuelle Version: [v0.3.0](https://github.com/insidi/Anno-117-four-cinis-mod/releases/tag/v0.3.0). Neben dem ZIP liegt eine `.sha256`-Datei zum Prüfen des Downloads. Das Git-Repository selbst enthält nur Quellcode und Dokumentation; die Kartendateien werden nicht eingecheckt.

## Installation

1. Anno 117 schließen und das ZIP aus dem Release entpacken.
2. Den Ordner `cinis-four-directions` in den eigenen Dokumente-Ordner unter `Anno 117 - Pax Romana/mods/` kopieren.
3. Prüfen, dass `modinfo.json` direkt im Modordner liegt, und die Mod im Spiel aktivieren.
4. Ein neues freies Spiel mit **Standard/Default-Latium** und aktiviertem Vulkan-DLC starten.

Beim Update von 0.2.0 den alten Modordner vorher löschen; ein vorhandener 0.2.0-Spielstand lädt danach weiter.

Für Mehrspieler installiert jeder Teilnehmer dasselbe ZIP. Der Host erstellt eine neue Partie. Den ersten Versuch mit einem separaten Testspielstand durchführen; die vollständigen Prüfschritte stehen in der [Testanleitung](docs/TESTANLEITUNG.md).

## Repository-Struktur

| Pfad | Inhalt |
| --- | --- |
| `config/modinfo.json` | Version, Mod-ID und Mehrspielerfreigabe |
| `scripts/MapBuild/` | C#-Werkzeug zum Bearbeiten, Verpacken und Prüfen der Kartendaten |
| `scripts/cinis_v2/` | Python-Build-Stufe 2: Weltdateien für beide Layouts und `assets.xml` ([Beschreibung](scripts/cinis_v2/README.md)) |
| `scripts/*.ps1` | Kompilierung, Mod-Build, Paketierung, Validierung und Vorschau |
| `docs/` | Testanleitung und Layoutvorschau |
| `research/STATUS.md` | Erkenntnisse zum Dateiformat und offene Aufgaben |
| `research/` (sonstige Dateien) | Lokale Spieldaten, Zwischenergebnisse und Prüfberichte; von Git ausgeschlossen |
| `tools/` | Lokale Werkzeuge und Bibliotheken; von Git ausgeschlossen |
| `dist/` | Erzeugter Modordner und ZIP-Pakete; von Git ausgeschlossen |

## Lokal bauen

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

Sind die Karten bereits gebaut und wurden nur Metadaten oder die Testanleitung geändert, genügt zur neuen Paketierung:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Package-Cinis.ps1
```

Das ZIP und seine SHA256-Prüfsumme liegen anschließend in `dist/`. Die Version stammt aus `config/modinfo.json`. Für eine neue Version werden beide Dateien als Anhang an ein Release mit dem Tag `v<Version>` gehängt.

## Validierung

Der Build prüft die FileDB-Daten durch erneutes Einlesen und vergleicht die Nutzdaten gepackter RDA-Archive nach dem Entpacken per SHA256. Außerdem werden Inselanzahl, Kartengrenzen und Überschneidungen zwischen Cinis und den konservativen Begrenzungsrechtecken der übrigen Inselplätze geprüft.

`build_v2.py` prüft, dass Medium und Hard keine eingebackene Höhe haben und dass alle Inselplätze im neuen Spielbereich liegen, ohne eine Cinis zu überdecken.

`Validate-Cinis.ps1` wendet die XML-Patches mit `xmltest2` an und prüft, dass genau die drei vorgesehenen Karten-Assets geändert werden, die Horizontinseln vollständig sind und beide Vorlagenpfade im Paket liegen. Der lokale Bericht liegt unter `research/validation.json`.

Diese Prüfungen ersetzen keinen gemeinsamen Spieltest auf Host und Clients.

## Referenzen

- [Anno Modding Tools](https://github.com/anno-mods/vscode-anno)
- [AnnoMapEditorRenew](https://github.com/flamme-demon/AnnoMapEditorRenew)
- [Anno Modloader: ModOps](https://jakobharder.github.io/anno-mod-loader/modops/basics/)
- [Anno Modloader: Modinfo](https://jakobharder.github.io/anno-mod-loader/modinfo/)

Unoffizielles Modding-Projekt, nicht mit Ubisoft verbunden. Extrahierte Spieldaten und heruntergeladene Drittanbieter-Werkzeuge gehören nicht in dieses Git-Repository.
