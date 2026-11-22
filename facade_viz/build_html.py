#!/usr/bin/env python3
"""Assemble the interactive gallery index.html from styles.json (data inlined)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "styles.json"), encoding="utf-8"))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Grand Commercial Façade Library — 96 Schematic Elevations</title>
<style>
  :root{
    --bg:#0f1419; --panel:#161d26; --panel2:#1d2733; --line:#2a3744;
    --text:#e7edf3; --muted:#9aa9b8; --accent:#4aa3df;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
  header{padding:22px 26px 10px;border-bottom:1px solid var(--line);}
  h1{margin:0;font-size:20px;letter-spacing:.2px}
  .sub{color:var(--muted);font-size:13px;margin-top:4px}
  .controls{display:flex;gap:12px;flex-wrap:wrap;padding:16px 26px;border-bottom:1px solid var(--line);
    position:sticky;top:0;background:var(--bg);z-index:5}
  input,select{background:var(--panel2);color:var(--text);border:1px solid var(--line);
    border-radius:8px;padding:9px 12px;font-size:14px;min-width:160px}
  input{flex:1;min-width:240px}
  .count{color:var(--muted);font-size:13px;align-self:center;margin-left:auto}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:18px;padding:22px 26px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;
    cursor:pointer;transition:transform .12s ease,border-color .12s ease}
  .card:hover{transform:translateY(-3px);border-color:var(--accent)}
  .thumb{background:#eef3f7;display:block;width:100%;height:auto}
  .card .meta{padding:10px 12px 12px}
  .card .nm{font-size:14px;font-weight:600;line-height:1.25}
  .badge{display:inline-block;margin-top:7px;font-size:11px;color:var(--muted);
    background:var(--panel2);border:1px solid var(--line);border-radius:20px;padding:3px 9px}
  .overlay{position:fixed;inset:0;background:rgba(6,9,13,.78);display:none;align-items:center;
    justify-content:center;padding:24px;z-index:50}
  .overlay.open{display:flex}
  .modal{background:var(--panel);border:1px solid var(--line);border-radius:14px;max-width:980px;
    width:100%;max-height:92vh;overflow:auto;display:grid;grid-template-columns:minmax(280px,420px) 1fr}
  .modal .left{background:#eef3f7;padding:16px;display:flex;align-items:center;justify-content:center}
  .modal .left img{width:100%;height:auto;border-radius:8px}
  .modal .right{padding:22px 24px}
  .modal h2{margin:0 0 4px;font-size:19px}
  .modal .cat{color:var(--accent);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.5px}
  .modal section{margin-top:18px}
  .modal h3{font-size:12px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);margin:0 0 7px}
  .modal p{margin:0;font-size:14px;line-height:1.5;color:#d7e0e9}
  .tags{display:flex;flex-wrap:wrap;gap:6px}
  .tag{font-size:12px;background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:4px 9px}
  .params{font-size:13px;line-height:1.5;color:#d7e0e9}
  .params li{margin-bottom:4px}
  pre{white-space:pre-wrap;font-size:13px;line-height:1.5;color:#cfd9e3;
    background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:12px;margin:0}
  .close{position:absolute;top:14px;right:18px;font-size:22px;color:#fff;cursor:pointer;
    background:none;border:none}
  @media(max-width:720px){.modal{grid-template-columns:1fr}}
</style>
</head>
<body>
<header>
  <h1>Grand Commercial Façade Library — 96 Schematic Elevations</h1>
  <div class="sub">Version 4.0-Expanded · Archicad 29 via Tapir MCP · procedurally generated 2D elevations</div>
</header>
<div class="controls">
  <input id="q" placeholder="Search name, category, element, intent…" />
  <select id="cat"><option value="">All categories</option></select>
  <select id="sort">
    <option value="id">Sort: library order</option>
    <option value="name">Sort: name A→Z</option>
    <option value="category">Sort: category</option>
  </select>
  <span class="count" id="count"></span>
</div>
<div class="grid" id="grid"></div>

<div class="overlay" id="overlay">
  <button class="close" id="closeBtn">×</button>
  <div class="modal" id="modal"></div>
</div>

<script id="data" type="application/json">/*DATA*/</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const grid = document.getElementById('grid');
const catSel = document.getElementById('cat');
const qEl = document.getElementById('q');
const sortEl = document.getElementById('sort');
const countEl = document.getElementById('count');
const overlay = document.getElementById('overlay');
const modal = document.getElementById('modal');

const cats = [...new Set(DATA.map(d=>d.category))].sort();
cats.forEach(c=>{const o=document.createElement('option');o.value=c;o.textContent=c;catSel.appendChild(o);});

const ACCENT = {
 "Solar Shading & Louver Systems":"#2c6e8f","Structural Exoskeletons & Grids":"#8a5a2b",
 "Massing & Volumetric Transformations":"#556b7a","Modular & Pixelated Skins":"#6b5b95",
 "Perforated, Cultural & Biophilic Screens":"#4a7c59","Double-Skin & Kinetic Envelopes":"#b5651d",
 "Sculptural & Parametric Signatures":"#9b3b6a","Contemporary Material & Cladding Systems":"#5a6470",
 "Parametric & Computational Geometry":"#8454a8","Organic & Biomimetic Façades":"#2e8b6f",
 "Adaptive & Intelligent Façades":"#1f7a8c","Sustainable & Energy-Generating Façades":"#3a9d4e",
 "Traditional & Cultural Architectural Façades":"#a8632d","High-Rise Architectural Expression":"#3d4a5c",
 "Minimalist & Contemporary Façades":"#6f7d8c","Advanced Glazing Systems":"#3f7fae",
 "Experimental & Futuristic Façades":"#c0397b"};

function fmtParams(p){
  if(!p||!Object.keys(p).length) return '<em style="color:var(--muted)">No parameters listed.</em>';
  let h='<ul class="params" style="padding-left:18px;margin:0">';
  for(const k in p){
    let v=p[k];
    if(Array.isArray(v)) v=v.join(' · ');
    else if(typeof v==='object') v=JSON.stringify(v);
    h+=`<li><b>${k}</b>: ${v}</li>`;
  }
  return h+'</ul>';
}

function card(d){
  const el=document.createElement('div');el.className='card';
  el.innerHTML=`<img class="thumb" src="${d.svg}" alt="${d.name}" loading="lazy"/>
    <div class="meta"><div class="nm">${d.name}</div>
    <span class="badge">${d.category}</span></div>`;
  el.onclick=()=>openModal(d);
  return el;
}

function render(){
  const q=qEl.value.trim().toLowerCase();
  const c=catSel.value;const s=sortEl.value;
  let list=DATA.filter(d=>{
    if(c&&d.category!==c) return false;
    if(!q) return true;
    const hay=(d.name+' '+d.category+' '+d.intent+' '+d.elements.join(' ')+' '+d.build_logic).toLowerCase();
    return hay.includes(q);
  });
  if(s==='name') list.sort((a,b)=>a.name.localeCompare(b.name));
  else if(s==='category') list.sort((a,b)=>a.category.localeCompare(b.category)||a.id.localeCompare(b.id));
  grid.innerHTML='';
  list.forEach(d=>grid.appendChild(card(d)));
  countEl.textContent=`${list.length} / ${DATA.length} façades`;
}

function openModal(d){
  const ac=ACCENT[d.category]||'#54616e';
  modal.innerHTML=`
    <div class="left"><img src="${d.svg}" alt="${d.name}"/></div>
    <div class="right">
      <div class="cat">${d.category}</div>
      <h2>${d.name}</h2>
      <div class="tags" style="margin-top:8px">
        ${d.elements.map(e=>`<span class="tag">${e}</span>`).join('')}
      </div>
      <section><h3>Architectural Intent</h3><p>${d.intent}</p></section>
      <section><h3>Parameters</h3>${fmtParams(d.parameters)}</section>
      <section><h3>Tapir Build Logic</h3><pre>${d.build_logic}</pre></section>
      <section><h3>Library ID</h3><p style="font-family:monospace;color:var(--muted)">${d.id}</p></section>
    </div>`;
  overlay.classList.add('open');
}
function closeModal(){overlay.classList.remove('open');}
document.getElementById('closeBtn').onclick=closeModal;
overlay.onclick=e=>{if(e.target===overlay)closeModal();};
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});
qEl.oninput=render;catSel.onchange=render;sortEl.onchange=render;
render();
</script>
</body>
</html>
"""

data_js = json.dumps(data, ensure_ascii=False)
html_out = TEMPLATE.replace("/*DATA*/", data_js)
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_out)
print("Wrote index.html  (%d bytes)" % len(html_out))
