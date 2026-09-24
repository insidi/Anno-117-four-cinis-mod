$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$variants = @{}
foreach ($name in @('easy','medium','hard')) {
    $variants[$name] = Get-Content ('dist/cinis-four-directions/data/phil/cinis_four/' + $name + '/cinis_four_' + $name + '.a7tinfo.layout.json') -Raw | ConvertFrom-Json
}
$json = $variants | ConvertTo-Json -Depth 8 -Compress
$html = @'
<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vier Cinis – Layoutvorschau</title>
<style>body{font:16px system-ui;background:#102330;color:#edf4f5;max-width:1050px;margin:24px auto;padding:0 20px}h1{margin-bottom:6px}p{color:#b5ced6;line-height:1.5}select{font:inherit;padding:8px;background:#243f4c;color:white;border:1px solid #63808b;border-radius:6px}svg{width:100%;max-height:78vh}text{font:16px system-ui;fill:#edf4f5;text-anchor:middle}.legend{display:flex;gap:24px;flex-wrap:wrap}.dot{display:inline-block;width:12px;height:12px;margin-right:7px}.warning{color:#ffd197}</style>
<h1>Vier Cinis um Latium</h1><p>Entwurf aus den exportierten Kartendaten · 4096 × 4096 · Spielansicht um 45° gedreht</p>
<label>Inselgrößenvariante: <select id="variant"><option value="easy">Groß</option><option value="medium">Mittel</option><option value="hard">Klein</option></select></label>
<svg id="map" viewBox="0 0 1040 1030" role="img" aria-label="Vier Cinis im Norden, Osten, Süden und Westen mit Latium in der Mitte"></svg>
<div class="legend"><span><i class="dot" style="background:#ec9d58"></i>Cinis, 768 × 768</span><span><i class="dot" style="background:#59ad9a"></i>Zufallsinselplätze</span><span><i class="dot" style="background:#ffe09a"></i>Startposition</span></div>
<p>Rechtecke zeigen maximale Inselabmessungen, keine Küstenkonturen. Ein Mouseover zeigt Position und Größe. Normale Inseln werden weiterhin vom Spiel ausgewählt.</p>
<p class="warning">Ungetesteter Prototyp: Die Vorschau belegt keine funktionierende Weltgenerierung oder Vulkanmechanik.</p>
<script>
const layouts=__DATA__;
const svg=document.querySelector('#map'),ns='http://www.w3.org/2000/svg';
function project(x,y){return [520+(x-y)*.105,505-(x+y-4096)*.105]}
function add(tag,attrs,text){const e=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.appendChild(e);return e}
function box(x,y,size,fill,stroke){return add('polygon',{points:[[x,y],[x+size,y],[x+size,y+size],[x,y+size]].map(p=>project(...p).join(',')).join(' '),fill,stroke,'stroke-width':1.5})}
function draw(){svg.replaceChildren();box(20,20,4056,'#173543','#527989');box(1044,1044,2000,'#1a4149','#448477');for(const slot of layouts[document.querySelector('#variant').value]){let e;if(slot.kind==='Start'){const[x,y]=project(slot.x,slot.y);e=add('circle',{cx:x,cy:y,r:6,fill:'#ffe09a'})}else{e=box(slot.x,slot.y,slot.size,slot.kind==='Cinis'?'#ec9d58':'#59ad9a','#102330');e.setAttribute('fill-opacity',slot.kind==='Cinis'?'.9':'.65')}const title=document.createElementNS(ns,'title');title.textContent=`${slot.kind} ${slot.label}: (${slot.x}, ${slot.y}), ${slot.size} × ${slot.size}`;e.appendChild(title)}add('text',{x:520,y:45},'NORDEN · CINIS');add('text',{x:940,y:510},'OSTEN');add('text',{x:520,y:985},'SÜDEN · CINIS');add('text',{x:90,y:510},'WESTEN');add('text',{x:520,y:470,'font-weight':'bold'},'LATIUM')}
document.querySelector('#variant').addEventListener('change',draw);draw();
</script></html>
'@
[IO.File]::WriteAllText((Join-Path (Get-Location) 'docs/layout.html'),$html.Replace('__DATA__',$json),(New-Object Text.UTF8Encoding $false))
