param(
    [string]$AssetsPath,
    [string]$ModPath,
    [string]$XmlTestPath
)

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
if (-not $ModPath) { $ModPath = Join-Path $root 'dist/cinis-four-directions' }
if (-not $XmlTestPath) { $XmlTestPath = Join-Path $root 'tools/package/external/xmltest2.exe' }
if (-not $AssetsPath) {
    $AssetsPath = Join-Path $root 'research/current/config.rda/data/base/config/export/assets.xml'
    if (-not (Test-Path -LiteralPath $AssetsPath)) {
        $AssetsPath = Join-Path $root 'research/config/data/base/config/export/assets.xml'
    }
}
$mod = $ModPath
$metadata = Get-Content ($mod + '/modinfo.json') -Raw | ConvertFrom-Json
if ($metadata.GameSetup.Multiplayer -ne $true) { throw 'Multiplayer must be enabled' }
$sourcePath = $AssetsPath
$patchedPath = Join-Path $root 'research/patched-assets.xml'
New-Item -ItemType Directory -Path (Join-Path $root 'research') -Force | Out-Null
& $XmlTestPath -v -m $mod -o $patchedPath $sourcePath ($mod + '/data/base/config/export/assets.xml') > research/xml-patch-test.log
if ($LASTEXITCODE -ne 0) { throw 'xmltest2 failed' }
if (Select-String -Path research/xml-patch-test.log -Pattern '\[(error|warning)\]' -Quiet) { throw 'Patch warnings/errors' }
$source = New-Object System.Xml.XmlDocument
$source.Load($sourcePath)
$patched = New-Object System.Xml.XmlDocument
$patched.Load($patchedPath)
# xmltest pretty-prints leading/trailing whitespace inside scalar values.
foreach ($document in @($source,$patched)) {
    foreach ($leaf in $document.SelectNodes('//*[not(*)]')) { $leaf.InnerText = $leaf.InnerText.Trim() }
}
$before = @{}
foreach ($asset in $source.SelectNodes('//Asset[Values/Standard/GUID]')) { $before[$asset.Values.Standard.GUID] = $asset.OuterXml }
$changed = @()
$patchedAssets = $patched.SelectNodes('//Asset[Values/Standard/GUID]')
if ($patchedAssets.Count -ne $before.Count) { throw 'Asset count changed' }
foreach ($asset in $patchedAssets) {
    $id = $asset.Values.Standard.GUID
    if (-not $before.ContainsKey($id)) { throw ('Unexpected new asset: ' + $id) }
    if ($asset.OuterXml -ne $before[$id]) { $changed += $id }
}
if (($changed | Sort-Object) -join ',' -ne '144830,144837,3377,44421,44422') { throw ('Unexpected changed assets: ' + ($changed -join ',')) }
foreach ($id in @('3377','44421','44422')) {
    $map = $patched.SelectSingleNode('//Asset[Values/Standard/GUID="' + $id + '"]/Values/MapTemplate')
    if ($map.Attraction.ShrinkWorld -ne '0' -or $map.Attraction.WiggleIterationCount -ne '0') { throw 'Generator layout settings not applied' }
    # 0.3.0: 15 scaled vanilla horizon islands plus the two volcano meshes repeated for four corners.
    $horizon = $map.SelectNodes('EnlargedHorizonIslands/Item')
    $volcanoMeshes = @($horizon | Where-Object { $_.HorizonIslandFile -like '*volcano_mesh*' })
    if ($horizon.Count -ne 23 -or $volcanoMeshes.Count -ne 8) { throw ('Unexpected horizon islands: ' + $horizon.Count + ' items, ' + $volcanoMeshes.Count + ' volcano meshes') }
    $name = $map.EnlargedTemplateFilename -replace '^data/phil/cinis_four_v2/([a-z]+)/.*$','$1'
    if ($map.EnlargedTemplateFilename -ne ('data/phil/cinis_four_v2/' + $name + '/cinis_four_v2_' + $name + '.a7t')) { throw ('Unexpected template path: ' + $map.EnlargedTemplateFilename) }
    # The old path stays in the package: 0.2.0 savegames store it and reload the world from it.
    foreach ($a7t in @((Join-Path $mod $map.EnlargedTemplateFilename), (Join-Path $mod ('data/phil/cinis_four/' + $name + '/cinis_four_' + $name + '.a7t')))) {
        foreach ($extension in @('.a7t','.a7te','.a7tinfo')) {
            if (-not (Test-Path ([IO.Path]::ChangeExtension($a7t,$extension)))) { throw ('Missing template component: ' + [IO.Path]::ChangeExtension($a7t,$extension)) }
        }
        $editor = New-Object System.Xml.XmlDocument
        $editor.Load([IO.Path]::ChangeExtension($a7t,'.a7te'))
        if ($editor.AnnoEditorLevel.Dimensions.X -ne '4096' -or $editor.SelectNodes('//Chunk').Count -ne 4096) { throw 'Editor chunk dimensions mismatch' }
    }
}
# Undo all intended scalars in copies of the two volcano assets. Equality with
# the originals proves that base amounts, capacities and phase logic survived.
$resourceOps = New-Object System.Xml.XmlDocument
$resourceOps.Load((Join-Path $root 'config/obsidian-modops.xml'))
$resourceChanges = @()
$restoredAssets = @{}
foreach ($op in $resourceOps.SelectNodes('/ModOps/ModOp')) {
    $assetPath = '//Asset[Values/Standard/GUID="' + $op.GUID + '"]'
    $originalAsset = $source.SelectSingleNode($assetPath)
    $changedAsset = $patched.SelectSingleNode($assetPath)
    $valuePath = 'Values/' + $op.Replace
    $originalValues = $originalAsset.SelectNodes($valuePath)
    $changedValues = $changedAsset.SelectNodes($valuePath)
    if ($originalValues.Count -ne 1 -or $changedValues.Count -ne 1) { throw ('Ambiguous resource target: ' + $valuePath) }
    $expected = $op.SelectSingleNode('*').InnerText.Trim()
    if ($changedValues[0].InnerText -ne $expected) { throw ('Resource value not applied: ' + $op.GUID + '/' + $op.Replace) }
    if (-not $restoredAssets.ContainsKey($op.GUID)) { $restoredAssets[$op.GUID] = $changedAsset.CloneNode($true) }
    $restoredAssets[$op.GUID].SelectSingleNode($valuePath).InnerText = $originalValues[0].InnerText
    $resourceChanges += [ordered]@{ GUID=$op.GUID; Path=$op.Replace; Before=$originalValues[0].InnerText; After=$expected }
}
if ($resourceChanges.Count -ne 6) { throw 'Expected six obsidian corrections' }
foreach ($id in $restoredAssets.Keys) {
    if ($restoredAssets[$id].OuterXml -ne $before[$id]) { throw ('Unexpected extra volcano changes: ' + $id) }
}
$initial = $patched.SelectSingleNode('//Asset[Values/Standard/GUID="144830"]/Values/VolcanoEruptionBalancing/ConfigPerRegion/Item[Region="Roman"]/InitialLimitedLodeFertilities/Item[LimitedLodeFertility="145337"]')
$eruption = $patched.SelectSingleNode('//Asset[Values/Standard/GUID="144837"]/Values/VolcanoPhase/SpawnLimitedLodeFertilities/Item[LimitedLodeFertility="145337"]')
if ($initial.ScaleAmountMaximumDistance -ne '0' -or $eruption.ScaleAmountMaximumDistance -ne '0') { throw 'Distance scaling must be disabled for both initial stock and replenishment' }
if ($eruption.AdditionalOverdriveAmountMin -ne '300' -or $eruption.AdditionalOverdriveAmountMax -ne '300' -or $eruption.TechIncreaseAmountMin -ne '400' -or $eruption.TechIncreaseAmountMax -ne '400') { throw 'Refill bonuses must use fixed original midpoints' }
$report = [ordered]@{
    Date=(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
    Result='PASS'
    Version=$metadata.Version
    MultiplayerEnabled=$metadata.GameSetup.Multiplayer
    ChangedAssetGUIDs=$changed
    ObsidianChanges=$resourceChanges
    OtherVolcanoFieldsUnchanged=$true
    PatchWarnings=0
    CheckedVariants=3
    MapData='0.3.2 reuses 0.3.0 map data; see obsidian-package-check.json for SHA256 comparison'
    RuntimeTest='NOT RUN - host/client synchronization, world generation, settlement, eruptions, quests, save/reload require in-game testing'
}
$report | ConvertTo-Json -Depth 4 | Set-Content research/validation.json -Encoding UTF8
Write-Output 'PASS: real ModOp engine changed exactly three map assets and six obsidian fields; distance scaling disabled, bonuses fixed; all other volcano fields unchanged; both layouts and editor grids present.'
