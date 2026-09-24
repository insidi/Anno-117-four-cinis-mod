$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$dotnet = Join-Path $root 'tools/dotnet6/dotnet.exe'
$builder = Join-Path $root 'tools/map-build/MapBuild.dll'
$rda = Join-Path $root 'tools/package/external/build/RdaConsole.exe'
$mod = Join-Path $root 'dist/cinis-four-directions'
New-Item -ItemType Directory -Force $mod | Out-Null

function Run-Builder([string[]]$Arguments) {
    & $dotnet $builder @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('MapBuild failed: ' + ($Arguments -join ' ')) }
}

# Each source is the installed DLC version; patch scans found no overrides for Default templates.
$variants = @(
    @{ Name='easy'; Guid='3377'; Sea='research/map-default-easy/gamedata.data' },
    @{ Name='medium'; Guid='44421'; Sea='research/map-default-medium/gamedata.data' },
    @{ Name='hard'; Guid='44422'; Sea='research/map-default-medium/gamedata.data' }
)
# Medium and Hard .a7t containers have identical SHA256 in this game installation.
$seaOutputs = @{}
foreach ($variant in $variants) {
    $name = $variant.Name
    $relative = 'data/phil/cinis_four/' + $name + '/cinis_four_' + $name
    $target = Join-Path $mod $relative
    New-Item -ItemType Directory -Force (Split-Path $target -Parent) | Out-Null
    $source = @(Get-ChildItem research/dlc01 -Recurse -Filter ('*default_01_' + $name + '*.a7tinfo'))
    if ($source.Count -ne 1) { throw ('Ambiguous source: ' + $name) }
    Run-Builder @('template', $source[0].FullName, ($target + '.a7tinfo'))
    if (-not $seaOutputs.ContainsKey($variant.Sea)) {
        $build = Join-Path $root ('research/export-' + $name)
        New-Item -ItemType Directory -Force $build | Out-Null
        Run-Builder @('resize', (Join-Path $root $variant.Sea), ($build + '/gamedata.data'), '4096')
        Run-Builder @('pack', ($build + '/gamedata.data'), ($build + '/ocean.a7t'))
        # Independently unpack using RdaConsole and compare the full payload hash.
        & $rda extract -f ($build + '/ocean.a7t') -y -o ($build + '/verify') -n
        if ($LASTEXITCODE -ne 0) { throw 'RDA re-extraction failed' }
        if ((Get-FileHash ($build + '/gamedata.data')).Hash -ne (Get-FileHash ($build + '/verify/gamedata.data')).Hash) { throw 'RDA payload hash mismatch' }
        $seaOutputs[$variant.Sea] = $build + '/ocean.a7t'
    }
    Copy-Item $seaOutputs[$variant.Sea] ($target + '.a7t') -Force

    $editor = New-Object System.Text.StringBuilder
    [void]$editor.AppendLine('<AnnoEditorLevel><FileVersion>4</FileVersion><ScenarioGuid>0</ScenarioGuid><Dimensions><X>4096</X><Z>4096</Z></Dimensions><ChunkSize><X>64</X><Z>64</Z></ChunkSize><Chunks>')
    $seq = 0
    for ($column=0; $column -lt 64; $column++) {
        [void]$editor.AppendLine('<Column>')
        for ($chunk=0; $chunk -lt 64; $chunk++) {
            [void]$editor.AppendLine(('<Chunk>0x{0:x}</Chunk>' -f $seq)); $seq++
        }
        [void]$editor.AppendLine('</Column>')
    }
    [void]$editor.AppendLine('</Chunks></AnnoEditorLevel>')
    [IO.File]::WriteAllText($target + '.a7te', $editor.ToString(), (New-Object Text.UTF8Encoding $false))
}

$assetsDir = Join-Path $mod 'data/base/config/export'
New-Item -ItemType Directory -Force $assetsDir | Out-Null
$assets = New-Object System.Text.StringBuilder
[void]$assets.AppendLine('<ModOps>')
foreach ($variant in $variants) {
    $path = 'data/phil/cinis_four/' + $variant.Name + '/cinis_four_' + $variant.Name + '.a7t'
    [void]$assets.AppendLine(('  <ModOp GUID="{0}" Merge="MapTemplate"><MapTemplate><EnlargedTemplateFilename>{1}</EnlargedTemplateFilename><Attraction><WiggleIterationCount>0</WiggleIterationCount><ShrinkWorld>0</ShrinkWorld></Attraction></MapTemplate></ModOp>' -f $variant.Guid,$path))
    # Vanilla horizon decorations use the old outer boundary; omit them on the expanded test map.
    [void]$assets.AppendLine(('  <ModOp GUID="{0}" Replace="MapTemplate/EnlargedHorizonIslands"><EnlargedHorizonIslands /></ModOp>' -f $variant.Guid))
}
[void]$assets.AppendLine('</ModOps>')
[IO.File]::WriteAllText((Join-Path $assetsDir 'assets.xml'),$assets.ToString(),(New-Object Text.UTF8Encoding $false))

# Check every targeted GUID/path against actual source assets, not just XML syntax.
$sourceAssets = New-Object System.Xml.XmlDocument
$sourceAssets.Load((Join-Path $root 'research/config/data/base/config/export/assets.xml'))
$patch = New-Object System.Xml.XmlDocument
$patch.Load((Join-Path $assetsDir 'assets.xml'))
foreach ($operation in $patch.ModOps.ModOp) {
    $matches = $sourceAssets.SelectNodes('//Asset[Values/Standard/GUID="' + $operation.GUID + '"]/Values/' + $(if ($operation.Merge) {$operation.Merge} else {$operation.Replace}))
    if ($matches.Count -ne 1) { throw ('Patch target not unique: ' + $operation.GUID) }
}
& (Join-Path $PSScriptRoot 'Package-Cinis.ps1')
Write-Output 'PASS: three variants built, RDA payload hashes verified, six patch targets verified, ZIP created.'
