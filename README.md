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

**Version 0.2.0 – Mehrspieler-Prototyp.** Die Datei- und XML-Patchprüfungen sind bestanden. Ein erfolgreicher Test im laufenden Spiel ist noch nicht dokumentiert. Weltgenerierung, Besiedlung, Vulkanausbrüche, Quests, Speichern/Laden und Mehrspieler-Synchronisation müssen noch geprüft werden.

- Standard/Default-Latium in allen drei Inselgrößenvarianten.
- Karte von 2688 × 2688 auf 4096 × 4096 Felder erweitert.
- Vier feste Cinis-Referenzen; bestehende Inselplätze werden gemeinsam zur Mitte verschoben.
- Mehrspieler in den Mod-Metadaten aktiviert. Alle Teilnehmer müssen dasselbe Modpaket und dieselbe Spielversion verwenden.
- Vulkan- und Queststeuerung bleiben unverändert. Vier unabhängige Ausbruchszyklen sind **nicht nachgewiesen**.
- Neues freies Spiel mit aktiviertem Vulkan-DLC erforderlich. Keine Kampagnenunterstützung; bestehende Spielstände werden nicht umgebaut.

[Layoutvorschau](docs/layout.html) · [Installation und Testablauf](docs/TESTANLEITUNG.md) · [Technischer Stand](research/STATUS.md)

Die HTML-Vorschau lokal herunterladen und im Browser öffnen; GitHub zeigt die Datei als Quelltext an.

## Installation

Das Git-Repository enthält den Quellcode und die Dokumentation. Das fertige Modpaket wird lokal unter `dist/cinis-four-directions-v0.2.0.zip` erzeugt und nicht in Git eingecheckt.

1. Anno 117 schließen und das fertige ZIP entpacken.
2. Den Ordner `cinis-four-directions` in den eigenen Dokumente-Ordner unter `Anno 117 - Pax Romana/mods/` kopieren.
3. Prüfen, dass `modinfo.json` direkt im Modordner liegt, und die Mod im Spiel aktivieren.
4. Ein neues freies Spiel mit **Standard/Default-Latium** und aktiviertem Vulkan-DLC starten.

Für Mehrspieler installiert jeder Teilnehmer dasselbe ZIP. Der Host erstellt eine neue Partie. Den ersten Versuch mit einem separaten Testspielstand durchführen; die vollständigen Prüfschritte stehen in der [Testanleitung](docs/TESTANLEITUNG.md).

## Repository-Struktur

| Pfad | Inhalt |
| --- | --- |
| `config/modinfo.json` | Version, Mod-ID und Mehrspielerfreigabe |
| `scripts/MapBuild/` | C#-Werkzeug zum Bearbeiten, Verpacken und Prüfen der Kartendaten |
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

Aus der eigenen Spielinstallation werden folgende Eingaben benötigt:

- `research/config/data/base/config/export/assets.xml`.
- Die drei DLC01-Standard-Kartenvorlagen (`easy`, `medium`, `hard`) als `.a7tinfo` unter ihrer ursprünglichen Verzeichnisstruktur in `research/dlc01/`.
- Die aus den zugehörigen `.a7t`-Archiven entpackte `gamedata.data` unter `research/map-default-easy/` und `research/map-default-medium/`.

Der aktuelle Build verwendet für Medium und Hard dieselbe Meeresvorlage: Ihre Originalarchive waren in der untersuchten Spielversion identisch. Nach Spielupdates müssen Patch-Overrides und diese Annahme erneut geprüft werden. Weitere Formatdetails stehen im [Untersuchungsstand](research/STATUS.md).

Im Repository-Verzeichnis ausführen:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Compile-MapBuild.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Build-Cinis.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Validate-Cinis.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Make-Preview.ps1
```

`ExecutionPolicy Bypass` gilt hier nur für den jeweiligen PowerShell-Prozess. Die Skripte installieren die Mod nicht im Spielverzeichnis.

Sind die Karten bereits gebaut und wurden nur Metadaten oder die Testanleitung geändert, genügt zur neuen Paketierung:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Package-Cinis.ps1
```

Das ZIP und seine SHA256-Prüfsumme liegen anschließend in `dist/`. Die Version stammt aus `config/modinfo.json`.

## Validierung

Der Build prüft die FileDB-Daten durch erneutes Einlesen und vergleicht die Nutzdaten gepackter RDA-Archive nach dem Entpacken per SHA256. Außerdem werden Inselanzahl, Kartengrenzen und Überschneidungen zwischen Cinis und den konservativen Begrenzungsrechtecken der übrigen Inselplätze geprüft.

`Validate-Cinis.ps1` wendet die XML-Patches mit `xmltest2` an und prüft, dass genau die drei vorgesehenen Karten-Assets geändert werden. Der lokale Bericht liegt unter `research/validation.json`.

Diese Prüfungen ersetzen keinen gemeinsamen Spieltest auf Host und Clients.

## Referenzen

- [Anno Modding Tools](https://github.com/anno-mods/vscode-anno)
- [AnnoMapEditorRenew](https://github.com/flamme-demon/AnnoMapEditorRenew)
- [Anno Modloader: ModOps](https://jakobharder.github.io/anno-mod-loader/modops/basics/)
- [Anno Modloader: Modinfo](https://jakobharder.github.io/anno-mod-loader/modinfo/)

Unoffizielles Modding-Projekt, nicht mit Ubisoft verbunden. Extrahierte Spieldaten und heruntergeladene Drittanbieter-Werkzeuge gehören nicht in dieses Git-Repository.
