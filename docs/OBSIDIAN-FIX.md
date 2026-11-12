# Gleichmäßige Obsidian-Auffüllung – 0.3.2

Alle vier Cinis sollen bei gleichen Voraussetzungen dieselbe Obsidianmenge bekommen. Version 0.3.2 schaltet deshalb die Entfernungsskalierung vollständig ab und ersetzt zufällige Zusatzmengen durch feste Mittelwerte.

## Nachgewiesener Fehler

Der am 12.11.2026 untersuchte neue 0.3.0-Spielstand hat vier korrekt platzierte Cinis, aber sehr unterschiedliche Obsidianvorkommen:

| Insel | Früher Spielstand, vor dem ersten Ausbruch | Nach dem ersten Ausbruch |
| --- | ---: | ---: |
| Nord | 108 | 432 |
| Ost | 1 | 8 |
| Süd | kein Obsidian-Eintrag | weiterhin kein Eintrag |
| West | 10 | 49 |

Die Zahlen stammen aus gespeicherten Inselvorkommen, nicht aus Warenlagern. Auf Nord wurde zwischenzeitlich Obsidian abgebaut; die Spalten sind deshalb kein reiner Vorher/Nachher-Vergleich der Ausbruchsmenge. Ost und West wurden tatsächlich aufgefüllt, aber nur sehr wenig.

In den aktuellen Spieldaten steht `ScaleAmountMaximumDistance=3500` sowohl für die anfängliche Zuteilung (Asset 144830) als auch für die Auffüllung bei Ausbrüchen (Asset 144837). Die vier Cinis liegen auf einer 4096 × 4096 großen Karte. Die Gegenüberstellung von Inselpositionen und gespeicherten Vorräten spricht für die Entfernungsskalierung vom ursprünglichen Vulkan als Ursache; eine Auswertung pro nächstgelegenem Vulkan erfolgt offenbar nicht wie für vier unabhängige Instanzen benötigt.

## Was geändert wird

| Einstellung | Original | 0.3.2 |
| --- | ---: | ---: |
| Entfernungsskalierung beim Spielstart | Reichweite 3500 | aus (`0`) |
| Entfernungsskalierung bei Ausbrüchen | Reichweite 3500 | aus (`0`) |
| Zusatzmenge je Übersteuerungsstufe | zufällig 250–350 | fest 300 |
| Zusatzmenge je Forschungsstufe | zufällig 350–450 | fest 400 |

Die zufälligen Bonusspannen werden auf ihre bisherigen Mittelwerte gesetzt. Die Grundmengen bleiben 100 beim Start und 700 je Ausbruch. Danach berücksichtigt die Engine weiterhin Inselgröße, Phasenfaktor und freie Kapazität.

**Gleiche Auffüllung bedeutet gleiche zugeteilte Menge bei gleichem Forschungs-/Übersteuerungsstand und Phasenfaktor.** Unterschiedlicher Verbrauch oder zu wenig freier Platz kann zu verschiedenen Endbeständen führen. Forschungsfortschritt wird nicht angeglichen.

Für jede Cinis ergeben sich rechnerisch 120 Anfangsvorrat (100 × 1,2). Ohne Zusatzboni sind es 420 Auffüllung bei Phasenfaktor 0,5 bzw. 840 bei Faktor 1, jeweils bis zur Vorratsgrenze. Diese Werte sind noch im Spiel zu bestätigen.

- Neue Spiele verwenden die geänderte Berechnung für den Anfangsvorrat.
- Bestehende Spiele verwenden die geänderten Assets für künftige Ausbrüche. **Die Reparatur der fehlenden Süd-Zuteilung muss beim nächsten Ausbruch noch im Spiel bestätigt werden.** Beim Laden wird kein Bestand direkt geändert.
- Die Änderung gilt auch für die übrigen Latium-Inseln: Auch dort entfällt der Entfernungseinfluss.
- Anfangs- und Ausbruchsgrundmenge, Vorratsobergrenzen, Fortschritt und Phasenlängen bleiben unverändert. Forschungs- und Übersteuerungsboni verwenden jetzt feste Mengen.
- Ein Ausbruch bedeutet weiterhin nicht zwangsläufig einen vollen Vorrat: Das Original berücksichtigt unter anderem den ersten Ausbruch und Forschung. Diese Mod entfernt keine Verbrauchsprüfung und erzeugt kein unendliches Obsidian.
- Keine neuen Skripte, Timer oder Zufallsentscheidungen. Karten, Positionen, Drehungen und Terrain bleiben bytegleich zu 0.3.0.

## Warum `0` funktioniert

Die aktuelle lokale Spielroutine wurde ausschließlich lesend untersucht. Sowohl bei der Initialisierung als auch bei der Eruption führt die Engine die Distanzrechnung nur aus, wenn `ScaleAmountMaximumDistance > 0` ist. Bei `0` überspringt sie den Block einschließlich der Division. Die zuvor in 0.3.1 verwendete Reichweite 1.000.000 verringerte den Einfluss lediglich und wird deshalb ersetzt.

Die Zuordnung des XML-Felds und beide Verzweigungen sind für die untersuchte ausführbare Datei im [technischen Stand](https://github.com/insidi/Anno-117-four-cinis-mod/blob/main/research/STATUS.md) dokumentiert. Die Mod benötigt keine Änderung an der ausführbaren Datei.

## Installieren und im vorhandenen Spiel testen

1. Auf **allen beteiligten Rechnern** das Spiel beenden und dasselbe ZIP `cinis-four-directions-v0.3.2.zip` entpacken.
2. Den bisherigen Modordner `cinis-four-directions` durch den gleichnamigen Ordner aus dem ZIP ersetzen. Nicht als zweite Mod daneben installieren.
3. Den vorhandenen Spielstand laden und einen separaten Testspielstand anlegen. Ein Neustart der Partie ist für die geänderten Ausbruchsparameter nicht vorgesehen.
4. Für Nord, Ost, Süd und West Vorkommen, freie Kapazität und Forschungs-/Übersteuerungsstand notieren. Zur Vergleichbarkeit den Obsidianabbau pausieren.
5. Nach dem nächsten tatsächlichen Ausbruch die Zuwächse vergleichen: Bei gleichen Voraussetzungen müssen alle vier dieselbe Menge erhalten. Süd muss erstmals einen positiven Eintrag bekommen. Eine volle Insel erhält nichts mehr; bei wenig freiem Platz wird die Zuteilung begrenzt.
6. Speichern, gemeinsam neu laden und die Vorräte zwischen Host und Mitspielern vergleichen.
7. Zusätzlich in einem neuen Spiel vor jeglichem Abbau die Anfangsvorräte aller vier Cinis vergleichen; rechnerisch jeweils 120.

Falls Süd weiterhin keinen Eintrag erhält, den Spielstand **nach** dem Ausbruch aufbewahren. Dann muss zusätzlich geklärt werden, ob die Engine eine einmal bei der Weltgenerierung fehlende Zuteilung bei späteren Ausbrüchen ergänzt. Dieser Fall wird nicht durch ungeprüfte Änderungen an einem Spielstand umgangen.

## Prüfstand

Der echte ModOp-Test prüft gegen die aktuellen lokalen Spiel-Assets: drei Karten-Assets und genau sechs Obsidianfelder in zwei weiteren Assets; alle übrigen Vulkanfelder unverändert. Regressionstests prüfen die gepatchten Werte anhand des aus der lokalen Spielroutine abgeleiteten Rechenmodells: Entfernungen bis zur Kartendiagonale, erste und spätere Eruption, feste Boni, Kapazitätsgrenzen und Updates ohne doppelte ModOps. Sie führen das Spiel nicht aus.

Der Paket-Build vergleicht alle 24 Kartendateien per SHA256 mit 0.3.0 und prüft jedes ZIP-Mitglied. Die Wirkung auf alle vier Inseln, Süd im bestehenden Spielstand und die Mehrspieler-Synchronisation sind erst nach dem beschriebenen Spieltest bestätigt.
