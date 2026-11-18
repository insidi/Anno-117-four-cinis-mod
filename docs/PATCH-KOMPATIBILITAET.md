# Patch-Kompatibilität – Mod 0.3.3

Geprüft am 18.11.2026 gegen die lokal installierte Steam-Version **Anno 117: Pax Romana 3.0.1**, Build **26607411**. Die Prüfung liest Spieldateien; sie startet oder verändert keine Spielstände.

## Verifizierte Änderungen an Cinis

[Patch 1.6.1](https://www.anno-union.com/updates/anno-117-pax-romana-patch-1-6-1/) erweiterte laut Ubisoft die bebaubare Fläche von Cinis, ohne neue Minen-/Flussslots oder zusätzliche Küstenfläche. Die Erweiterung wurde als mit bestehenden Spielständen kompatibel angekündigt. Ein unveränderter Stand vor 1.6.1 liegt in dieser Installation nicht mehr vor; der damalige Gesamtzuwachs lässt sich deshalb lokal nicht vollständig nachmessen.

Die vorhandenen Inseldateien ergeben:

| Inseldatei aus Archiv | Landrasterfelder | Küstenrasterfelder |
| --- | ---: | ---: |
| Patch 1.6.1 | 117.064 | 963 |
| Patch 2.0 | 117.242 | 963 |
| Patch 3.0, weiterhin aktuell unter 3.0.1 | 117.242 | 964 |

Das sind Kategorien des Inselrasters, keine Garantie für frei platzierbare Gebäude auf jedem Feld. Zwischen 1.6.1 und 2.0 ändern sich außerdem Höhen- und weitere Rasterdaten. Zwischen 2.0 und 3.0 bleibt die Höhenkarte gleich; ein Rasterfeld wird zur Küstenfläche. Die zusätzlichen Küstenänderungen in [Patch 3.0.1](https://www.anno-union.com/updates/anno-117-pax-romana-patch-3-0-1/) betreffen laut Patchnotes Aegyptus. Im installierten Patch-3.0.1-Archiv liegt kein neuer Cinis-Override.

Alle vier Cinis der Mod referenzieren dieselbe Originaldatei mit Insel-GUID `145426`. Damit übernehmen sie bereits gemeinsam die aktuelle Inselgeometrie, Bauflächen, Küsten und Slots. Eine separate Inseldatei wird nicht mitgeliefert.

## Korrektur der Spielgrenze

Die Original-Cinis beginnt bei `(1920, 1920)` in einer 2688 × 2688 großen Welt. Die Spielgrenze endet bei 2440: 520 lokale Felder der Insel liegen innerhalb dieser Grenze. Die vier Ecken der Mod ließen durch den bisherigen Bereich `268..3828` nur 500 lokale Felder zu.

0.3.3 korrigiert den neuen Kartenpfad `cinis_four_v2` auf **`248..3848`**. Nach Rückdrehen jeder Insel sind die Land- und Küstenmasken innerhalb der Spielgrenze identisch mit dem aktuellen Original:

| Vergleich | Landrasterfelder innerhalb der Spielgrenze | Küstenrasterfelder |
| --- | ---: | ---: |
| Aktuelles Original | 116.963 | 964 |
| Mod bis 0.3.2, je Cinis | 114.074 | 964 |
| Mod 0.3.3, je Cinis | 116.963 | 964 |

Damit werden rechnerisch **2.889 Landrasterfelder je Cinis** wieder zugänglich. Geändert wird ausschließlich `PlayableArea` in den drei neuen Kartenvorlagen und in der zugehörigen Easy-Weltdatei. Höhen, Gebietsmarker, Inselpositionen, Drehungen und übrige Inselplätze bleiben erhalten. Die alte Vorlage `cinis_four` für 0.2.0-Spielstände bleibt bytegleich.

## Vulkan und Mehrspieler

Die XML-Operationen und Obsidianwerte aus 0.3.2 bleiben gleich. Es werden keine neuen GUIDs, Inseltypen, Timer oder lokalen Spielskripte angelegt. Die vier Instanzen behalten eindeutige Labels. Die Abschaltung der Obsidian-Entfernungsskalierung mit `0` wurde auch in der aktuellen 3.0.1-Spielroutine erneut lesend geprüft.

Alle Teilnehmer benötigen dasselbe Modpaket, dieselbe Spielversion und den Vulkan-DLC. Der laufende Mehrspielerbetrieb, Ausbrüche und Quests wurden für 0.3.3 nicht im Spiel getestet. Die Veröffentlichung ist deshalb als Vorabversion gekennzeichnet.

## Bestehende Spielstände und offene Tests

Es werden keine gespeicherten Positionen, Vorräte oder Dateien eines Spielstands bearbeitet. Bestehende Spielstände können ihre bereits gespeicherte Spielgrenze behalten. Eine automatische Vergrößerung im geladenen Spiel ist nicht bestätigt; für die korrigierte Grenze eine neue freie Partie verwenden. Das unveränderte alte Layout behält seine bekannten Einschränkungen an den Inselrückseiten.

Im Spiel sind noch zu prüfen: Bauen auf den zusätzlich freigegebenen Randflächen in allen vier Himmelsrichtungen; Kollision/Kamerahöhe; Medium und Hard; gemeinsames Speichern/Laden; Obsidianauffüllung und Vulkanereignisse. Eine statische Prüfung ersetzt diese Spieltests nicht.
