Vier Cinis erhalten jetzt bei gleichen Voraussetzungen dieselbe Obsidianmenge. Der untersuchte 0.3.0-Spielstand hatte auf Süd kein Vorkommen; Ost und West erhielten durch die Entfernungsskalierung nur winzige Auffüllungen.

### Änderungen

- Entfernungsskalierung für Anfangsvorräte und Ausbruchsauffüllung vollständig deaktiviert. Der Wert `0` wurde anhand der aktuellen lokalen Spielroutine geprüft.
- Zufällige Übersteuerungsboni auf fest 300 und Forschungsboni auf fest 400 gesetzt, jeweils vor den weiteren Multiplikatoren.
- Gleiche Zuteilung bei gleichem Forschungs-/Übersteuerungsstand und Phasenfaktor. Freie Kapazität und Verbrauch können weiterhin unterschiedliche Endbestände verursachen.
- Grundmengen, Vorratsgrenzen, Ausbruchszeiten und Queststeuerung bleiben erhalten. Die geänderten Obsidianregeln betreffen auch die übrigen Latium-Inseln.
- Alle 24 Kartendateien bleiben bytegleich zu 0.3.0. Bestehende Spielstände behalten ihre Positionen und ihr Terrain.

### Installation

Anno auf allen beteiligten Rechnern beenden. Den bisherigen Ordner `Dokumente/Anno 117 - Pax Romana/mods/cinis-four-directions` durch den gleichnamigen Ordner aus dem ZIP ersetzen. Alle Mitspieler müssen dasselbe Paket verwenden.

Im bestehenden Spielstand erfolgt keine sofortige Bestandsänderung beim Laden. Die neue Auffüllung beim nächsten tatsächlichen Ausbruch auf Nord, Ost, Süd und West prüfen. Für den Vergleich den Abbau pausieren und Fortschritt sowie freie Kapazität berücksichtigen. Ein neues Spiel sollte rechnerisch auf jeder Cinis mit 120 Obsidian beginnen.

### Prüfung und offene Spieltests

- Echter ModOp-Test gegen aktuelle lokale Spiel-Assets bestanden: drei Karten-Assets und genau sechs Obsidianfelder geändert; übrige Vulkanfelder unverändert.
- Neun Regressionstests bestanden, einschließlich Entfernung, Boni, Kapazitätsgrenzen und Update von 0.3.0/0.3.1 ohne doppelte ModOps. Das Rechenmodell ist aus der Spielroutine abgeleitet; es führt das Spiel nicht aus.
- SHA256-Vergleich der Kartendateien und aller ZIP-Inhalte bestanden.

**Der Spieltest der Auffüllung aller vier Inseln, insbesondere der bislang leeren Süd-Insel im bestehenden Spielstand, sowie die Mehrspieler-Synchronisation stehen noch aus.** Die beiliegenden `README.md` und `OBSIDIAN-FIX.md` beschreiben den Testablauf.

Downloads: vollständiges Mod-ZIP und zugehörige SHA256-Prüfsumme. Vulkan-DLC erforderlich; Standard/Default-Latium, keine Kampagnenunterstützung.
