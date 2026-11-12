# Build-Stufe 2 (ab Version 0.3.0)

`Build-Cinis.ps1` ruft nach MapBuild `build_v2.py` auf. Das Skript arbeitet direkt auf den FileDB- und RDA-Formaten und braucht keine zusätzlichen .NET-Bibliotheken.

Voraussetzung: **Python 3 mit numpy** im `PATH` (geprüft mit Python 3.12 und numpy 2.4). Ein anderer Interpreter lässt sich über die Umgebungsvariable `CINIS_PYTHON` angeben.

| Datei | Inhalt |
| --- | --- |
| `build_v2.py` | `maps`: Kartendaten für beide Pfade; `assets`: `assets.xml` |
| `filedb.py` | Lesen und Schreiben von FileDB Version 3 (`.a7tinfo`, `gamedata.data`) |
| `rda.py`, `rdawrite.py` | Lesen und Schreiben von RDA-2.2-Archiven (`.a7t`) |

## Was `maps` erzeugt

- `data/phil/cinis_four/easy/cinis_four_easy.a7t`: wird neu geschrieben. Das eingebackene Kontinent- und Vulkanterrain der Cinis steht an den vier Positionen, die 0.2.0-Spielstände gespeichert haben (3200/3200, 3200/128, 128/128, 128/3200, jeweils ohne Drehung). Die verschobene Original-Cinis und die mitkopierte Kartenrandlinie bei 3712 werden entfernt. Alle anderen Dateien unter `cinis_four` bleiben die MapBuild-Ausgabe.
- `data/phil/cinis_four_v2/<Variante>/`: Vorlage für neue Spiele. Cinis bündig in den vier Ecken (3328/3328 `Rotation90` 0, 3328/0 3, 0/0 2, 0/3328 1), Spielbereich 268..3828. Bei Easy werden Höhenkarte und Area-IDs mitgedreht; Medium und Hard übernehmen die Welt unverändert, weil deren Original-Welten keine eingebackene Höhe enthalten (das Skript prüft das).
- Die übrigen Inselplätze bleiben wie in 0.2.0. Das Skript prüft, dass sie im neuen Spielbereich liegen und keine Cinis überdecken.

`Rotation90 = k` dreht lokale Inselkoordinaten in Vierteldrehungen: `k = 1` bildet (u, v) auf (768 − v, u) ab. Das wurde an einem Spielstand nachgemessen und im Spiel an allen vier Ecken geprüft.

## Was `assets` erzeugt

Je Kartenvorlage (3377, 44421, 44422) zwei ModOps: `EnlargedTemplateFilename` auf `cinis_four_v2`, `WiggleIterationCount` 0 und `ShrinkWorld` 0 wie bisher, dazu `EnlargedHorizonIslands` mit den Original-Horizontinseln (Positionen mit 4096/2688 skaliert) und den beiden Vulkan-Meshes für jede der vier Ecken.

Die ModOps aus `config/obsidian-modops.xml` werden gemeinsam eingebunden. In 0.3.2 sind es sechs: `ScaleAmountMaximumDistance=0` für Anfangszuteilung (144830) und Eruptionsauffüllung (144837), außerdem feste Min-/Max-Werte für Übersteuerungs- und Forschungsboni in 144837. Alle Ziele betreffen Fertility 145337. Die Kartengenerierung bleibt unverändert.

Für das reine Update eines vorhandenen 0.3.x-Pakets ist kein Kartenneubau und kein numpy nötig: `python scripts/build_obsidian_fix.py --source <0.3.x-Modordner>` nutzt dieselbe XML-Quelle, prüft Bytegleichheit aller Kartendateien und erzeugt ZIP und Prüfsumme. Siehe [Obsidian-Korrektur](../../docs/OBSIDIAN-FIX.md).

## Format-Hinweise

- `.a7t`-Archive müssen mit zlib-Stufe 1 komprimiert sein (Stream-Header `78 01`). Mit höheren Stufen meldete das Spiel „Failed opening file … gamedata.data“.
- Die Welt-Datei (`.a7t`) liefert Kollision und Kamerahöhe der Cinis. Die sichtbare Insel kommt aus der Inseldatei.
- Ein Spielstand speichert Pfad, Positionen und Drehungen der Vorlage, lädt das Terrain aber bei jedem Laden neu aus der `.a7t`.

Die Kartenausgabe ist deterministisch (Zeitstempel 0). Mit den Eingaben von 0.2.0 entstehen dieselben Kartendateien wie im im Spiel getesteten Paket 0.3.0; `assets.xml` enthält ab 0.3.1 zusätzlich die Obsidian-Korrektur.
