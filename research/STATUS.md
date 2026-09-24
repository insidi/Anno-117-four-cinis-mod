# Cinis x4: Untersuchung vom 20.09.2026

Ziel: je eine Cinis im Norden, Osten, Sueden und Westen; Latium in der Mitte. Mehrspieler, wenn alle Teilnehmer dasselbe Modpaket verwenden.

Installation: C:\Program Files (x86)\Steam\steamapps\common\Anno 117 - Pax Romana

## Nachgewiesen in config.rda
- assets.xml liegt unter data/base/config/export/assets.xml (abweichend vom alten Chat).
- Inselasset 145426: roman_dlc01_island_continental_01.
- Vulkanobjekt 144835: VisualObject, Vulkan-Grafik unter data/dlc01/graphics/roman/environment/volcano/volcano_main_performance_01.cfg.
- Vulkansteuerung 144830: VolcanoEruptionManagerBalancing. ConfigPerRegion hat einen Roman-Eintrag mit VolcanoAsset 144835 und VolcanoTraderGuid 145051.
- Phasenreferenzen: 145352, 144831, 144837, 145212, 145213.
- MapTemplate verweist mit EnlargeDLC 67902 und EnlargedTemplateFilename auf DLC01-Karten (.a7t).

## Lokal vorbereitet
- tools/package: Anno Modding Tools 2.3.0 aus dem offiziellen GitHub-Release; darin RdaConsole und FileDBReader.
- research/config: assets.xml und templates.xml aus config.rda.
- research/dlc01: .a7t-Dateien aus dlc01_provinces.rda.
- research/patch210: .a7t-Dateien aus zz_patchfiles_210.rda. Kein assets.xml/templates.xml bei dieser Filterextraktion enthalten.
- research/archives: Arbeitskopien der drei Archive. RdaConsole versucht offenbar mit Schreibzugriff zu oeffnen; deshalb nur Kopien verwendet.
- Originalinstallation und Spielstaende wurden nicht veraendert.

## Prototyp 0.2.0 fuer Mehrspieler vorbereitet
- Aktuelles ZIP: `dist/cinis-four-directions-v0.2.0.zip`; Modordner: `dist/cinis-four-directions`. 0.1.0 ist die alte Version ohne Multiplayer-Freigabe.
- `GameSetup.Multiplayer=true`; identisches ZIP und gleiche Spielversion fuer alle Teilnehmer vorgesehen. Mehrspieler-Laufzeittest noch ausstehend.
- Gemeinsame Metadatenquelle: config/modinfo.json. scripts/Package-Cinis.ps1 erstellt Paket und SHA256-Datei ohne Neubau der Karten.
- Interaktive Layoutvorschau: `docs/layout.html`; Testanleitung: `docs/TESTANLEITUNG.md`.
- Standard/Default-Latium, Karten-Assets 3377 / 44421 / 44422. Keine Kampagnen- oder anderen Kartenvarianten.
- Alle installierten Patcharchive 150, 151, 152, 160, 161, 200, 210 untersucht. Keine Overrides der ausgewaehlten Default-Vorlagen und keine assets.xml/templates.xml in diesen Patcharchiven gefunden.
- .a7t ist ein RDA-2.2-Container mit gamedata.data. .a7tinfo und gamedata.data verwenden FileDB Version3.
- Inselgroesse Cinis laut Metadaten 768 x 768. Welt erweitert von 2688 auf 4096.
- Vier Cinis-Urspruenge: N=(3200,3200), O=(3200,128), S=(128,128), W=(128,3200). Himmelsrichtungen beziehen sich auf die um 45 Grad gedrehte Spielansicht.
- Andere Plaetze um 1024/1024 verschoben. InitialPlayableArea=1044,1044,3044,3044; EnlargementOffset=1024,1024; PlayableArea=20,20,4076,4076.
- Bestehende Gitterinhalte versetzt erhalten; Hoehen-, Displacement-, Wasser-, Fluss-, Furt-, Umgebungs- und Gebietsraster vergroessert. Sparse-Blockabschluss erhalten. Andere Sessionmanager unveraendert.
- Nord-Cinis behaelt den Originalnamen; andere Instanzen haben eigene Labels. Originalrotation bleibt erhalten.
- Originale Vulkansteuerung und einzelner Vulkanhaendler bleiben bestehen.
- Generatorverschiebung und ShrinkWorld deaktiviert; alte erweiterte Horizontdekorationen entfernt.
- Build: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Compile-MapBuild.ps1`, danach `scripts/Build-Cinis.ps1`, `scripts/Validate-Cinis.ps1`, `scripts/Make-Preview.ps1` mit denselben PowerShell-Optionen.
- Validierung: FileDB-Knoten/Nutzdaten nach erneutem Einlesen gleich; RDA entpackt und SHA256 gleich; vier Cinis je Variante; konservative Inselrechtecke kollisionsfrei gegen Cinis; xmltest2 veraendert exakt drei Karten-Assets ohne Warnungen. Siehe research/validation.json.
- 0.2.0 wurde anschliessend im Spiel getestet; Befunde siehe Version 0.3.0.

## Version 0.3.0 (24.09.2026, im Spiel getestet)
- Befund aus dem Spieltest von 0.2.0: Schiffe fuhren durch die drei Kopien, die Kamera stieg ueber ihren Vulkanen nicht an.
- Ursache: Die Weltdatei (.a7t, TerrainManager/HeightMap) enthaelt Kontinent- und Vulkanlandmasse der Cinis eingebacken; Kollision und Kamerahoehe kommen daraus, die sichtbare Insel aus der Inseldatei. In der Easy-Originalvorlage liegt dieser Block in der Ecke (1920,1920). MapBuild `resize` verschiebt die ganze Welt um +1024, der Block lag damit bei (2944,2944), die Nord-Cinis der .a7tinfo aber bei (3200,3200). Die drei Kopien hatten gar kein Terrain. Gedrehte Kopien muessen auch in Hoehenkarte und AreaIDs gedreht werden.
- Zusaetzlich lief die alte Kartenrandlinie (Hoehe 0) bei Kachel 3712 als Grat durch die Karte.
- Medium- und Hard-Originalwelten haben eine flache Hoehenkarte (ueberall 0) ohne eingebackenes Terrain.
- Ein Spielstand speichert Vorlagenpfad, Positionen und Rotation90 der Vorlage, laedt das Terrain aber bei jedem Laden neu aus der .a7t. Deshalb bleibt `data/phil/cinis_four` erhalten und nur dessen Easy-.a7t wird neu gebaut (Terrain an 3200/3200, 3200/128, 128/128, 128/3200).
- Neues Layout `data/phil/cinis_four_v2` fuer neue Spiele: (3328,3328) Rotation90 0, (3328,0) 3, (0,0) 2, (0,3328) 1; PlayableArea 268..3828 in .a7tinfo und (Easy) SessionSettings. Rotation90=1 bildet lokal (u,v) auf (768-v,u) ab, am Spielstand nachgemessen.
- RDA: Das Spiel oeffnete die .a7t nur mit zlib-Stufe 1 (Header 78 01).
- assets.xml: EnlargedTemplateFilename auf cinis_four_v2; Horizontinseln wieder aktiv, Positionen mit 4096/2688 skaliert, Vulkan-Meshes fuer alle vier Ecken gedreht.
- Build: zweite Stufe `scripts/cinis_v2/build_v2.py` (Python 3 + numpy), aufgerufen von `Build-Cinis.ps1`. Mit den 0.2.0-Eingaben byte-identisch zum getesteten Paket.
- Spieltest: laufender 0.2.0-Mehrspielerspielstand (Easy) mit 0.3.0 geladen, Kopien fest, Kamera folgt den Vulkanen; Rueckseiten im alten Layout weiterhin durchfahrbar. Neues Spiel: alle vier Ecken korrekt gedreht.

## Noch offen: Laufzeittest
- Neue Spiele mit Medium und Hard gezielt pruefen (keine eingebackene Hoehe; SessionSettings/PlayableArea der Weltdatei ist dort noch 20..4076, in der .a7tinfo 268..3828).
- Ausrichtung der Horizont-Vulkan-Meshes in allen vier Ecken pruefen.
- Neues freies Mehrspielerspiel mit Vulkan-DLC und Standard/Default-Kartentyp auf mindestens zwei Rechnern erzeugen.
- Kartenvergroesserung und vier tatsaechlich vorhandene/besiedelbare Inseln pruefen.
- Verhalten des einzelnen regionalen VolcanoEruptionManager bei vier Vulkanobjekten pruefen.
- Ausbrueche, Questziele, Vulkanhaendler, Ressourcen und gemeinsames Speichern/Laden auf Host und Clients vergleichen; Desyncs pruefen.
- Regionale Konfiguration belegt weder unabhaengige Timer noch zwingend gleichzeitige Ausbrueche.
- Weitere Kartentypen erst nach funktionierendem Prototyp ausbauen.

Werkzeugquelle: https://github.com/anno-mods/vscode-anno/releases/tag/v2.3.0

Format-/Exportreferenz: https://github.com/flamme-demon/AnnoMapEditorRenew/tree/35c302a (MIT).
ModOps: https://jakobharder.github.io/anno-mod-loader/modops/basics/
Modinfo: https://jakobharder.github.io/anno-mod-loader/modinfo/
Portable Microsoft .NET 6 Runtime/SDK und SharpZipLib 1.4.2 lokal unter tools; keine systemweite Installation.
Grosse RDA-Arbeitskopien und unnoetige XML-Zwischendateien nach Abschluss geloescht; extrahierte Quellen und Build-Eingaben bleiben erhalten.
