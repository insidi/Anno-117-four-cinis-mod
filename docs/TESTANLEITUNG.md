# Vier Cinis - Mehrspieler-Testversion 0.2.0

Diese Mod ist ein **experimenteller, noch nicht im Spiel getesteter Kartenprototyp** fuer Anno 117. Sie erzeugt vier feste Cinis-Inselreferenzen. Ob das Spiel alle vier korrekt erzeugt und deren Vulkane betreibt, muss im Spiel geprueft werden.

Mehrspieler ist in `modinfo.json` aktiviert. Ziel ist ein gemeinsames freies Spiel, bei dem alle Spieler dasselbe Paket verwenden. Diese Freigabe allein beweist noch keine fehlerfreie Synchronisation.

## Inhalt

- Standard-Latium-Karte, alle drei Inselgroessenvarianten.
- Intern 4096 x 4096 statt 2688 x 2688 Felder.
- Je eine Cinis im Norden, Osten, Sueden und Westen der um 45 Grad gedrehten Spielansicht.
- Bestehende normale Inselplaetze, Startposition und zusaetzliche DLC-Inselplaetze bleiben relativ zueinander erhalten und werden um 1024/1024 verschoben.
- Originale Vulkan- und Queststeuerung. Keine unabhaengigen Ausbruchstimer implementiert.
- Nord-Cinis behaelt das originale Insel-Label; die drei Kopien bekommen eigene Labels. Alle verwenden die originale Inseldatei und Rotation.

## Voraussetzungen und Installation

1. Gleiche Spielversion auf allen Rechnern verwenden. Vulkan-DLC muss fuer die gemeinsame Sitzung verfuegbar und aktiviert sein; die normalen DLC-Zugangsregeln des Spiels gelten weiterhin.
2. **Alle Spieler** bekommen exakt dasselbe ZIP der Version 0.2.0. Keine Mischung mit 0.1.0 oder selbst veraenderten Dateien verwenden. Neben dem ZIP liegt dessen SHA256-Pruefsumme.
3. Auf jedem Rechner das Spiel schliessen und den Ordner `cinis-four-directions` aus dem ZIP nach `Dokumente/Anno 117 - Pax Romana/mods/` kopieren. Bei einem Update die alte Kopie ersetzen und keine zweite Kopie behalten. `modinfo.json` muss direkt im Modordner liegen.
4. Mod auf jedem Rechner aktivieren, falls sie nicht automatisch aktiv ist. Fuer den ersten Test bei allen Spielern nur diese Mod aktivieren.
5. Der Host erstellt ein **neues freies Mehrspielerspiel**, die anderen treten vor dem Start bei. Fuer Latium den Kartentyp **Standard/Default** auswaehlen. Bei Zufall ist dieser Prototyp nicht gezielt pruefbar. Andere Kartentypen werden nicht veraendert.

Die Mod ist nicht fuer die Kampagne vorbereitet. Einzelspieler bleibt moeglich. Bestehende Spielstaende werden nicht auf vier Cinis umgebaut. Falls das DLC erst im Spielverlauf aktiviert wird, gilt das neue Layout erst nach dessen Kartenerweiterung.

## Testablauf

1. Mit mindestens zwei Rechnern starten: Erreichen Host und Mitspieler dieselbe Welt ohne Modkonflikt oder Desync? Sind alle Spieler mit Startposition, Schiffen bzw. Startinsel und NPCs vorhanden?
2. Nach der DLC-Kartenerweiterung alle vier Cinis suchen. Positionen und Inseln zwischen Host und Mitspielern vergleichen; Schiffswege pruefen.
3. Unterschiedliche Spieler besiedeln unterschiedliche Cinis. Insgesamt alle vier pruefen: Baugebiete, Hafen, Ressourcen, Lieferwege und sichtbare Besitzwechsel muessen uebereinstimmen.
4. Mindestens einen natuerlichen Vulkanzyklus gemeinsam beobachten. Fuer jede Himmelsrichtung Ausbruchszeitpunkt, Asche, Schaden, Obsidian und Meldungen vergleichen. Dabei auf Desyncs achten.
5. DLC-Questfortschritt und Vulkanhaendler pruefen. Es ist nur der originale einzelne Haendler vorgesehen. Die normale Questzuteilung an einen Teilnehmer wird nicht veraendert.
6. Einen separaten Testspielstand speichern, beide Spiele beenden und die Partie gemeinsam neu laden. Inselbesitz, Questfortschritt und Vulkanzustand vergleichen.
7. Einen weiteren Speichertest nach einem Ausbruch durchfuehren; anschliessend mit der gewuenschten Spielerzahl wiederholen.

Ergebnis bitte mit Spielversion, Modversion, Spielerzahl, Seed, Inselgroesse und Beobachtungen pro Himmelsrichtung festhalten. Das Modloader-Log liegt unter `Dokumente/Anno 117 - Pax Romana/mods/mod-loader.log`. Bei einem Desync die Logs beider Rechner und eventuell erzeugte Dateien im `desync`-Ordner desselben Anno-Dokumentenverzeichnisses aufbewahren.

## Bekannte Grenzen

- Die Vulkansteuerung ist in den Assets pro Region definiert; die Session besitzt einen `VolcanoEruptionManager`. Mehrere unabhaengige Vulkane sind nicht nachgewiesen.
- Quests, Vulkanhaendler, Ausbrueche und Mehrfachinstanzen der Insel wurden noch nicht zur Laufzeit getestet.
- Gleiches Modpaket ist Voraussetzung fuer den Test, aber keine Garantie gegen Desyncs. Ein echter Host/Client-Test steht noch aus.
- Die Mod fuegt keine Lua-Skripte, clientseitigen Timer oder vom Rechner abhaengigen Zufallsentscheidungen hinzu. Bestehende Spieler- und Multiplayer-Assets werden nicht gepatcht.
- Die groessere Karte braucht voraussichtlich mehr Speicher. Ein erfolgreicher Dateitest belegt noch keine funktionierende Weltgenerierung.
- Die Inseln behalten zunaechst alle die originale Drehung.
- Fuer diese Standard-Karten wurden Generatorverschiebung und automatisches Schrumpfen deaktiviert. Die erweiterten Horizontdekorationen werden entfernt, da sie auf die alte Kartengrenze abgestimmt sind.
- Ausschliesslich mit entbehrlichen Testspielstaenden verwenden. Einen mit dieser Karte gespeicherten Spielstand nicht ohne die Mod weiterverwenden.

## Durchgefuehrte Dateipruefungen

- Alle installierten `zz_patchfiles_*.rda` auf Overrides der ausgewaehlten Karten geprueft.
- Vier feste Cinis-Referenzen je Vorlage, eindeutige Labels und konsistente Elementzahlen.
- Konservative Begrenzungsrechtecke anhand der ausgelesenen Inselgroessen: keine Ueberschneidung zwischen Cinis und vorhandenen Inselplaetzen.
- FileDB-Version 3: erneutes Einlesen und Vergleich aller geschriebenen Knoten und Nutzdaten.
- RDA-Archive erneut entpackt; SHA256 der enthaltenen `gamedata.data` mit der Eingabedatei verglichen.
- Alle sechs XML-Patchziele existieren eindeutig in der installierten `assets.xml`.
- Zusaetzlich mit `xmltest2` tatsaechlich angewendet: genau die drei Karten-Assets geaendert, keine Vulkan-Assets; keine Patchwarnungen.

Die Mod referenziert die installierte Original-Cinis; die Inseldatei wird nicht mitgeliefert.
