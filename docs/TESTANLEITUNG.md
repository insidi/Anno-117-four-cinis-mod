# Vier Cinis - Mehrspieler-Testversion 0.3.3

Experimenteller Kartenprototyp fuer Anno 117: Standard-Latium (alle drei Inselgroessen) mit 4096 x 4096 Feldern und vier Cinis. Version 0.3.3 gleicht die Baugrenze an die aktuelle Originalinsel an; die Obsidianregeln aus 0.3.2 bleiben erhalten. Statisch geprueft gegen Patch 3.0.1, Steam-Build 26607411. Vorabversion ohne bestaetigten Spiel-/Mehrspielertest. Der Modordner heisst weiterhin `cinis-four-directions`, die ModID bleibt `cinis-four-directions-phil`.

Mehrspieler ist in `modinfo.json` aktiviert. Alle Spieler muessen exakt dasselbe Paket und dieselbe Spielversion verwenden.

## Was 0.3.3 aendert

Alle vier Instanzen nutzen die aktuell gepatchte Original-Cinis, einschliesslich der Flaechenaenderung aus Patch 1.6.1. Die Modgrenze schnitt allerdings bisher je Ecke 20 Felder mehr ab als das Original. Der neue Spielbereich `248..3848` entspricht dessen Randabstand: je Insel 116.963 statt 114.074 Landrasterfelder innerhalb der Grenze, also 2.889 mehr. Bauhindernisse bleiben erhalten; diese Zahl ist keine Zusage entsprechend vieler freier Bauplaetze. Kueste, Hoehenkarte, Positionen, Drehungen, GUIDs und Latium bleiben unveraendert. Details: [Patch-Kompatibilitaet](https://github.com/insidi/Anno-117-four-cinis-mod/blob/main/docs/PATCH-KOMPATIBILITAET.md), auch im ZIP enthalten.

Fuer die neue Grenze ein **neues Spiel** erzeugen. Bestehende Spielstaende behalten ihr Layout und koennen die alte Grenze gespeichert haben; deren Aktualisierung ist nicht bestaetigt. Keine Save-Dateien werden bearbeitet. Das alte Layout fuer 0.2.0-Spielstaende bleibt unveraendert enthalten.

## Was 0.3.2 aendert

Im untersuchten 0.3.0-Spielstand hatte Sued kein Obsidian, Ost und West erhielten nur sehr kleine Vorraete. 0.3.2 setzt beide Entfernungswerte auf 0. Die lokale Spielroutine ueberspringt damit die Entfernungsskalierung vollstaendig. Zusaetzlich sind Uebersteuerungsboni fest 300 statt zufaellig 250..350 und Forschungsboni fest 400 statt 350..450, jeweils vor den weiteren Multiplikatoren. Auch andere Latium-Inseln profitieren davon. Grundmengen, Vorratsobergrenzen, Fortschritt und Ausbruchszeiten bleiben erhalten.

Gleichmaessig bedeutet: gleiche Zuteilung bei gleichem Forschungs-/Uebersteuerungsstand und Phasenfaktor. Unterschiedlicher Abbau oder eine schon fast volle Insel kann trotzdem zu anderen Endbestaenden fuehren. Es wird nicht bei jedem Ausbruch zwangsweise bis zur Obergrenze aufgefuellt.

Die XML-Anwendung und Paketdaten sind statisch pruefbar; die Wirkung auf alle vier Inseln und die Mehrspieler-Synchronisation muessen noch im Spiel bestaetigt werden. Details: [Obsidian-Fix](https://github.com/insidi/Anno-117-four-cinis-mod/blob/main/docs/OBSIDIAN-FIX.md), auch im ZIP enthalten.

Ein vorhandener Spielstand bekommt beim Laden nicht sofort neue Vorraete. Die neue Auffuellung wird erst beim naechsten Ausbruch erwartet. Ob die Engine dabei auch einen bisher ganz fehlenden Obsidian-Eintrag auf Sued ergaenzt, ist noch zu pruefen.

## Was 0.3.0 gegenueber 0.2.0 aendert

Die Kontinent- und Vulkanlandmasse der Cinis ist in der Weltdatei (`.a7t`, Hoehenkarte) eingebacken. Schiffskollision und Kamerahoehe kommen daraus, die sichtbare Insel aus der Inseldatei. In 0.2.0 lag dieses Terrain der Nord-Cinis 256 Felder neben der Insel, die drei Kopien hatten keines: Schiffe fuhren durch die Kopien, die Kamera stieg ueber ihren Vulkanen nicht an. Ausserdem lief die mitkopierte alte Kartenrandlinie (Hoehe 0) bei x = 3712 und y = 3712 durch die Karte, und die Horizontinseln fehlten.

- **Bestehende 0.2.0-Spielstaende** laden weiter `data/phil/cinis_four/...`, weil der Spielstand diesen Pfad und die Inselpositionen speichert. Die Easy-Weltdatei dort ist neu gebaut: Terrain an allen vier gespeicherten Positionen, Phantomstreifen und Grat entfernt. Medium und Hard sind unveraendert.
- **Neue Spiele** verwenden `data/phil/cinis_four_v2/...`: Cinis buendig in den vier Ecken wie im Original, die Kopien mit `Rotation90` so gedreht, dass die offene Kueste zur Kartenmitte zeigt. Das Easy-Terrain ist passend mitgedreht. Der urspruengliche Spielbereich 268..3828 wird in 0.3.3 auf 248..3848 korrigiert. Uebrige Inselplaetze und Startposition wie in 0.2.0.
- Horizontinseln wiederhergestellt (auf 4096 skaliert, Vulkan-Meshes hinter allen vier Ecken). `WiggleIterationCount` 0 und `ShrinkWorld` 0 wie bisher.

## Installation

1. Spiel auf allen Rechnern schliessen und den Spielstand sichern.
2. Alle Spieler bekommen exakt dasselbe ZIP der Version 0.3.3. Neben dem ZIP liegt dessen SHA256-Pruefsumme; mit `Get-FileHash -Algorithm SHA256 <ZIP-Pfad>` vergleichen.
3. Den Ordner `Dokumente/Anno 117 - Pax Romana/mods/cinis-four-directions` komplett durch den Ordner aus dem ZIP ersetzen. Keine zweite Kopie behalten. `modinfo.json` muss direkt im Modordner liegen.
4. Spiel starten und `Dokumente/Anno 117 - Pax Romana/mods/mod-loader.log` pruefen: Version 0.3.3 geladen, keine Warnungen.
5. Fuer ein neues Spiel: freies Spiel, Latium, Kartentyp **Standard/Default**, Vulkan-DLC aktiv. Andere Kartentypen werden nicht veraendert. Keine Kampagnenunterstuetzung.

## Testablauf

Obsidian in einem bestehenden Spielstand:

1. Separaten Testspielstand anlegen; Obsidianabbau fuer den Vergleich pausieren.
2. **Nord, Ost, Sued und West** einzeln pruefen und den Obsidianvorrat der Insel vor dem Ausbruch notieren. Gemeint ist das Vorkommen, nicht das Warenlager.
3. Forschungs-/Uebersteuerungsstand und freie Kapazitaet je Insel festhalten. Nach der naechsten tatsaechlichen Eruptionsphase alle vier Werte erneut notieren und die Zuwachsmengen vergleichen. Bei gleichen Voraussetzungen muessen sie gleich sein. Sued muss ein positives Vorkommen erhalten. Eine volle Insel nimmt nichts mehr auf; bei wenig freiem Platz wird die Zuteilung begrenzt.
4. Gemeinsam speichern, neu laden und die Werte zwischen Host und Clients vergleichen.
5. Fehlt Sued weiterhin, den Spielstand nach dem Ausbruch aufbewahren. Die nachtraegliche Anlage eines fehlenden Eintrags ist noch nicht im Spiel nachgewiesen.

Neues Spiel mit 0.3.3: Zusaetzlich sofort nach der Weltgenerierung auf **allen vier Cinis** den Anfangsvorrat pruefen. Nach der geprueften Berechnung sind jeweils 120 zu erwarten (100 Grundmenge x 1,2 Inselgroessenfaktor). Danach denselben Ausbruchstest durchfuehren. Ohne Zusatzboni und bei genuegend Platz ergeben sich 420 bei Faktor 0,5 bzw. 840 bei Faktor 1. Diese Rechenwerte sind noch im Spiel zu bestaetigen.

Bestehender 0.2.0-Spielstand:

1. Laden und alle vier Cinis anfahren. Schiffe muessen an den Kuesten stoppen, die Kamera muss ueber den Vulkanen ansteigen.
2. Rueckseiten der Cinis meiden (siehe Bekannte Grenzen).

Neues Spiel:

1. Alle vier Ecken anfahren. Pro Ecke pruefen: Kueste zeigt zur Kartenmitte, Schiffe stoppen an Land, Kamera folgt dem Vulkan, Horizont hinter der Cinis passt.
2. Moeglichst alle drei Inselgroessen einmal starten (Gross, Mittel, Klein).
3. Unterschiedliche Spieler besiedeln unterschiedliche Cinis. Baugebiete, Hafen, Ressourcen und Lieferwege zwischen Host und Mitspielern vergleichen. An jeder Cinis dieselben lokalen Positionen entlang der bisher abgeschnittenen Grenze mit Strassen/Bauplanung testen; die Drehung der Insel beruecksichtigen. Auch Medium und Hard gezielt pruefen: Deren Weltdateien behalten die bisherigen SessionSettings, die Vorlagen enthalten die neue Grenze.
4. Mindestens einen Vulkanzyklus gemeinsam beobachten: Ausbruchszeitpunkt, Asche, Schaden, Obsidian und Meldungen je Himmelsrichtung vergleichen. Auf Desyncs achten.
5. Speichern, beenden und gemeinsam neu laden. Inselbesitz, Questfortschritt und Vulkanzustand vergleichen.

Ergebnis bitte mit Spielversion, Modversion, Spielerzahl, Seed, Inselgroesse und Beobachtungen pro Himmelsrichtung festhalten. Bei einem Desync die Logs beider Rechner und eventuell erzeugte Dateien im `desync`-Ordner aufbewahren.

## Bekannte Grenzen

- In 0.2.0-Spielstaenden behalten die Kopien ihre alte Position mit 128 Feldern Abstand zum Kartenrand und ihre alte Ausrichtung; beides ist im Spielstand gespeichert. Die Rueckseiten liegen dadurch im befahrbaren Bereich. Das Original-Terrain hat dort keine saubere Kollision, Schiffe koennen an den Rueckseiten weiterhin in die Insel fahren. Das korrekte Layout mit gedrehten Kopien gibt es nur in neuen Spielen.
- Vulkansteuerung, Vulkanhaendler und Quests sind weiterhin auf eine Cinis ausgelegt. Mehrere unabhaengige Ausbruchszyklen sind nicht nachgewiesen.
- Die groessere Karte braucht voraussichtlich mehr Speicher.
- Gleiches Modpaket ist Voraussetzung, aber keine Garantie gegen Desyncs.
- Die neue Grenze in bereits gespeicherten Spielen und das Zusammenspiel der beiden Grenzdefinitionen in Medium/Hard sind noch nicht im Spiel bestaetigt.
- Einen mit dieser Karte gespeicherten Spielstand nicht ohne die Mod weiterverwenden.

Die Mod referenziert die installierte Original-Cinis; die Inseldatei wird nicht mitgeliefert.
