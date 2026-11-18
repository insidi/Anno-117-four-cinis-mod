# Änderungen

## 0.3.3 – 18.11.2026

- Kompatibilitätsprüfung gegen Anno 117 3.0.1 (Steam-Build 26607411), einschließlich Cinis-Änderungen aus 1.6.1, 2.0 und 3.0.
- Spielgrenze der vier Cinis-Ecken von `268..3828` auf `248..3848` korrigiert. Damit entspricht die Land-/Küstenmaske innerhalb der Grenze dem aktuellen Original; rechnerisch 2.889 zusätzliche Landrasterfelder je Insel.
- Die vier Instanzen verwenden weiterhin die aktuelle Originalinsel. Terrain, Platzierungen, GUIDs und Obsidianregeln bleiben erhalten; alter Kartenpfad unverändert.
- Vollständiges, reproduzierbares ZIP aus dem per SHA256 festgelegten 0.3.2-Basispaket. Entwicklungsdateien wie Layout-JSON werden nicht mitgeliefert.
- GitHub Actions erstellt bei Versionstags Paket, Prüfsumme und Release. Prüfung gegen die installierten Spieldaten bleibt ein gesonderter lokaler Schritt.
- Vorabversion: Ingame-/Mehrspielertest und Übernahme der erweiterten Grenze in bestehende Spielstände noch nicht bestätigt.

## 0.3.2 – 12.11.2026

- Obsidian-Entfernungsskalierung ausgeschaltet; feste Mittelwerte für Forschungs- und Übersteuerungsboni.
- Gleichmäßige Zuteilung bei gleichen Voraussetzungen; Vorratsgrenzen und Fortschritt bleiben erhalten.

## 0.3.0 – 24.09.2026

- Terrainkorrektur für die Cinis-Kopien und gedrehte Inseln an den vier Ecken neuer Spiele.
- Alter Kartenpfad für bestehende 0.2.0-Spielstände erhalten; Horizontdekorationen ergänzt.
