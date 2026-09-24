$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$mod = Join-Path $root 'dist/cinis-four-directions'
$metadata = Get-Content ($mod + '/modinfo.json') -Raw | ConvertFrom-Json
if ($metadata.GameSetup.Multiplayer -ne $true) { throw 'Multiplayer must be enabled' }
$sourcePath = Join-Path $root 'research/config/data/base/config/export/assets.xml'
$patchedPath = Join-Path $root 'research/patched-assets.xml'
& tools/package/external/xmltest2.exe -v -m $mod -o $patchedPath $sourcePath ($mod + '/data/base/config/export/assets.xml') > research/xml-patch-test.log
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
foreach ($asset in $patched.SelectNodes('//Asset[Values/Standard/GUID]')) {
    $id = $asset.Values.Standard.GUID
    if (-not $before.ContainsKey($id)) { throw ('Unexpected new asset: ' + $id) }
    if ($asset.OuterXml -ne $before[$id]) { $changed += $id }
}
if (($changed | Sort-Object) -join ',' -ne '3377,44421,44422') { throw ('Unexpected changed assets: ' + ($changed -join ',')) }
foreach ($id in $changed) {
    $map = $patched.SelectSingleNode('//Asset[Values/Standard/GUID="' + $id + '"]/Values/MapTemplate')
    if ($map.Attraction.ShrinkWorld -ne '0' -or $map.Attraction.WiggleIterationCount -ne '0') { throw 'Generator layout settings not applied' }
    if ($map.EnlargedHorizonIslands.HasChildNodes) { throw 'Old horizon islands remain' }
    $a7t = Join-Path $mod $map.EnlargedTemplateFilename
    foreach ($extension in @('.a7t','.a7te','.a7tinfo')) {
        if (-not (Test-Path ([IO.Path]::ChangeExtension($a7t,$extension)))) { throw ('Missing template component: ' + $extension) }
    }
    $editor = New-Object System.Xml.XmlDocument
    $editor.Load([IO.Path]::ChangeExtension($a7t,'.a7te'))
    if ($editor.AnnoEditorLevel.Dimensions.X -ne '4096' -or $editor.SelectNodes('//Chunk').Count -ne 4096) { throw 'Editor chunk dimensions mismatch' }
}
$report = [ordered]@{
    Date=(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
    Result='PASS'
    Version=$metadata.Version
    MultiplayerEnabled=$metadata.GameSetup.Multiplayer
    ChangedAssetGUIDs=$changed
    VulkanAssetsUnchanged=$true
    PatchWarnings=0
    CheckedVariants=3
    FileDBRoundtrip='All node names, types and payloads checked in MapBuild'
    RdaPayload='SHA256 equality checked after independent extraction during build'
    RuntimeTest='NOT RUN - host/client synchronization, world generation, settlement, eruptions, quests, save/reload require in-game testing'
}
$report | ConvertTo-Json -Depth 4 | Set-Content research/validation.json -Encoding UTF8
Write-Output 'PASS: real ModOp engine changed exactly the three intended map assets; Vulkan assets unchanged; all template components and editor grids present.'
