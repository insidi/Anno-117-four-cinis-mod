$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$mod = Join-Path $root 'dist/cinis-four-directions'
$metadata = Get-Content config/modinfo.json -Raw | ConvertFrom-Json
if (-not (Test-Path ($mod + '/data/base/config/export/assets.xml'))) { throw 'Build the map files first' }
Copy-Item config/modinfo.json ($mod + '/modinfo.json') -Force
Copy-Item docs/TESTANLEITUNG.md ($mod + '/README.md') -Force
# A shared archive gives every peer exactly the same serialized map and patch data.
$records = Get-ChildItem $mod -Recurse -File | Sort-Object FullName | ForEach-Object {
    [ordered]@{Path=$_.FullName.Substring($mod.Length+1); Bytes=$_.Length; SHA256=(Get-FileHash -LiteralPath $_.FullName).Hash}
}
$records | ConvertTo-Json -Depth 4 | Set-Content research/build-manifest.json -Encoding UTF8
$zip = 'dist/cinis-four-directions-v' + $metadata.Version + '.zip'
Compress-Archive -LiteralPath $mod -DestinationPath $zip -Force
$hash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash
($hash + '  ' + [IO.Path]::GetFileName($zip)) | Set-Content ($zip + '.sha256') -Encoding ASCII
[ordered]@{Version=$metadata.Version; ZIP=$zip; SHA256=$hash; Multiplayer=$metadata.GameSetup.Multiplayer; RuntimeTest='NOT RUN'} | ConvertTo-Json | Set-Content research/zip-sha256.json -Encoding UTF8
Write-Output ('Packaged ' + $zip)
