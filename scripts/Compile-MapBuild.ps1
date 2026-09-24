$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$output = Join-Path $root 'tools/map-build'
New-Item -ItemType Directory -Force $output | Out-Null
$libs = Join-Path $root 'tools/map-editor-source/flamme-demon-AnnoMapEditorRenew-35c302a/AnnoMapEditor/Libs'
$argsFile = Join-Path $output 'compile.rsp'
$lines = @('-target:exe', '-langversion:10', '-nullable:enable', ('-out:"' + $output + '/MapBuild.dll"'))
$refs = Get-ChildItem 'tools/dotnet-sdk6/packs/Microsoft.NETCore.App.Ref/6.0.36/ref/net6.0' -Filter '*.dll'
foreach ($ref in $refs) { $lines += '-r:"' + $ref.FullName + '"' }
foreach ($name in @('FileDBReader', 'FileDBSerializer', 'RDAExplorer')) {
    $lines += '-r:"' + $libs + '/' + $name + '.dll"'
    Copy-Item ($libs + '/' + $name + '.dll') $output -Force
}
$lines += '"' + $root + '/scripts/MapBuild/Program.cs"'
$lines | Set-Content $argsFile -Encoding UTF8
& tools/dotnet6/dotnet.exe tools/dotnet-sdk6/sdk/6.0.428/Roslyn/bincore/csc.dll ('@' + $argsFile)
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed' }
Copy-Item tools/sharpziplib-1.4.2/lib/net6.0/ICSharpCode.SharpZipLib.dll $output -Force
'{"runtimeOptions":{"tfm":"net6.0","framework":{"name":"Microsoft.NETCore.App","version":"6.0.0"}}}' | Set-Content ($output + '/MapBuild.runtimeconfig.json') -Encoding UTF8
