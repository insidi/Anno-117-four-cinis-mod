Vier Cinis behalten ihre Positionen um Latium und erhalten die Spielgrenze der aktuellen Originalinsel. **Vorabversion**, statisch geprüft gegen Anno 117 **3.0.1 / Steam-Build 26607411**; Spiel- und Mehrspielertests stehen aus.

### Änderungen

- Alle vier Cinis verwenden bereits dieselbe gepatchte Originalinsel, einschließlich der Flächenerweiterung aus Patch 1.6.1. Die zusätzliche Modgrenze schnitt jedoch je Ecke 20 Felder zu viel ab.
- Spielbereich in den drei neuen Kartenvorlagen und der Easy-Weltdatei von `268..3828` auf `248..3848` korrigiert. Je Insel liegen dadurch **2.889 zusätzliche Landrasterfelder** innerhalb der Grenze: 116.963 statt 114.074. Das ist keine Zusage entsprechend vieler freier Bauplätze; Bauhindernisse bleiben bestehen.
- Terrain, Küsten, Positionen, Drehungen, GUIDs und Latium bleiben erhalten. Das alte Layout für 0.2.0-Spielstände bleibt bytegleich. Die sechs Obsidian-Korrekturen aus 0.3.2 ändern sich nicht.
- README, Testanleitung, Patchbericht und Changelog aktualisiert. GitHub Actions erzeugt bei passenden Versionstags das vollständige Mod-ZIP, prüft es und veröffentlicht ZIP und SHA256-Datei.

### Download und Installation

**`cinis-four-directions-v0.3.3.zip` herunterladen**, nicht „Source code“. Der Ordner `cinis-four-directions` gehört nach `Dokumente/Anno 117 - Pax Romana/mods/`; `modinfo.json` liegt direkt darin. Bei Updates den bisherigen Ordner vollständig ersetzen.

Alle Mitspieler benötigen dasselbe ZIP und dieselbe Spielversion. Für die korrigierten Grenzen ein neues freies Standard/Default-Latium-Spiel mit aktiviertem Vulkan-DLC beginnen. Bestehende Spielstände behalten ihre Positionen und können auch die alte Grenze gespeichert haben; deren Aktualisierung ist nicht bestätigt. Save-Dateien werden nicht bearbeitet.

### Prüfungen und Grenzen

- 43 installierte RDA-Verzeichnisse auf relevante Original- und Patchdateien untersucht; alle 24 Cinis-Instanzen der drei Varianten und zwei Layouts geprüft. Die vier gedrehten Instanzen haben jeweils exakt dieselbe aktuelle Land-/Küstenmaske innerhalb der Vorlagengrenze wie das Original.
- Echter ModOp-Test gegen aktuelle Assets ohne Warnungen: genau drei Karten-Assets und sechs Obsidianfelder in zwei Vulkan-Assets; übrige Vulkanfelder unverändert.
- Neun Obsidian-Regressionstests und sieben Paket-/Kartenprüfungen. 14 Kartenkomponenten bytegleich; in vier weiteren ausschließlich ein `PlayableArea`-Feld geändert. ZIP enthält 24 erforderliche Dateien, keine Entwicklungs- oder extrahierten Spieldateien.
- Keine bestätigten Ingame-/Mehrspielertests dieser Version. Offen: Grenzen in bestehenden Saves und Medium/Hard, längere Synchronisation, Vulkanquests sowie Reparatur eines zuvor fehlenden Obsidian-Eintrags beim nächsten Ausbruch. Vier unabhängige Vulkanzyklen werden nicht zugesichert.

Details: [Patch-Kompatibilität](https://github.com/insidi/Anno-117-four-cinis-mod/blob/v0.3.3/docs/PATCH-KOMPATIBILITAET.md) · [Testanleitung](https://github.com/insidi/Anno-117-four-cinis-mod/blob/v0.3.3/docs/TESTANLEITUNG.md).
