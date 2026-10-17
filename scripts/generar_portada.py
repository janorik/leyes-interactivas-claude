#!/usr/bin/env python3
"""Genera la portada /index.html que enlaza a cada ley.

Uso:  python3 scripts/generar_portada.py
Lee scripts/leyes.json. La portada no contiene datos de ninguna ley: solo
nombres y enlaces. Incrusta el logo reducido para funcionar sin conexión.
"""
import html
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
from insertar_datos import logo_base64  # noqa: E402

PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Leyes interactivas · NOrlexia</title>
<meta name="description" content="Apps interactivas para estudiar y repasar leyes procesales y laborales.">
<style>
:root{--verde:#0d4a45;--verde-osc:#0a3a36;--oro:#c9a04a;--crema:#f5f0e8;
  --fondo:#f5f0e8;--superficie:#fffdf8;--texto:#1c2725;--suave:#5d6966;--borde:#e1d8c6;--acento:#0d4a45;
  --sombra:0 1px 2px rgba(0,0,0,.05),0 2px 8px rgba(0,0,0,.05)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--fondo:#0b1c1a;--superficie:#112926;--texto:#ebe5d8;--suave:#a5b2ae;--borde:#244440;--acento:#c9a04a;--sombra:none}}
:root[data-theme="dark"]{--fondo:#0b1c1a;--superficie:#112926;--texto:#ebe5d8;--suave:#a5b2ae;--borde:#244440;--acento:#c9a04a;--sombra:none}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--texto);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{background:var(--verde-osc);color:var(--crema)}
.in{max-width:960px;margin:0 auto;padding:0 16px}
.cab{display:flex;align-items:center;gap:12px;padding:12px 0}
.cab img{height:44px;border-radius:8px}
.cab b{display:block;letter-spacing:.16em;font-size:.9rem}
.cab span{display:block;color:var(--oro);font-size:.78rem}
.cab button{margin-left:auto;background:transparent;border:1px solid rgba(255,255,255,.2);color:var(--crema);border-radius:9px;height:38px;min-width:38px;cursor:pointer}
.hero{padding:22px 0 26px}
.hero h1{font-family:Georgia,serif;font-size:1.9rem;line-height:1.15;margin:0 0 8px}
.hero p{margin:0;color:rgba(245,240,232,.85);max-width:640px}
main{padding:20px 0 50px}
.t{font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:var(--suave);font-weight:700;margin:6px 0 10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.ley{display:block;background:var(--superficie);border:1px solid var(--borde);border-radius:14px;padding:18px;text-decoration:none;color:var(--texto);box-shadow:var(--sombra)}
a.ley:hover{border-color:var(--acento)}
.ley .ab{font-family:Georgia,serif;font-size:1.6rem;font-weight:700;color:var(--acento)}
.ley h2{font-size:1.05rem;margin:2px 0 4px}
.ley .ref{font-size:.8rem;color:var(--suave)}
.ley p{font-size:.9rem;margin:10px 0 12px;color:var(--suave)}
.ley .ir{display:inline-block;background:var(--acento);color:#fff;border-radius:9px;padding:8px 14px;font-weight:700;font-size:.9rem}
:root[data-theme="dark"] .ley .ir{color:#0b1c1a}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .ley .ir{color:#0b1c1a}}
.ley.prox{opacity:.6}
.ley.prox .ir{background:transparent;color:var(--suave);border:1px dashed var(--borde)}
.aviso{font-size:.8rem;color:var(--suave);margin-top:26px;border-top:1px solid var(--borde);padding-top:12px}
</style>
</head>
<body>
<header><div class="in">
  <div class="cab">__LOGO__<div><b>NORLEXIA</b><span>Leyes interactivas</span></div>
    <button id="tema" aria-label="Cambiar modo claro u oscuro" title="Modo claro/oscuro">◐</button></div>
  <div class="hero"><h1>Estudia las leyes procesales como un mapa</h1>
    <p>Fases de cada procedimiento, plazos con la frase literal del BOE, recursos, test de repaso y tus notas. Funciona en el móvil y sin conexión.</p></div>
</div></header>
<main class="in">
  <div class="t">Leyes</div>
  <div class="grid">__LEYES__</div>
  <p class="aviso">Textos consolidados del BOE de carácter informativo, sin valor jurídico. Los esquemas, plazos y preguntas son material de estudio elaborado: cada app indica qué está pendiente de revisión. Tus notas y tu progreso se guardan solo en este navegador.</p>
</main>
<script>
(function(){
  var g=function(k){try{return localStorage.getItem(k)}catch(e){return null}}, s=function(k,v){try{localStorage.setItem(k,v)}catch(e){}};
  var t=g("lec:tema"); if(t) document.documentElement.setAttribute("data-theme",t);
  document.getElementById("tema").onclick=function(){
    var a=document.documentElement.getAttribute("data-theme")||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light");
    var n=a==="dark"?"light":"dark"; document.documentElement.setAttribute("data-theme",n); s("lec:tema",n);
  };
})();
</script>
</body>
</html>
"""


def tarjeta(l):
    e = html.escape
    if l["estado"] == "disponible":
        return (f'<a class="ley" href="{e(l["carpeta"])}index.html"><div class="ab">{e(l["abreviatura"])}</div>'
                f'<h2>{e(l["nombre"])}</h2><div class="ref">{e(l["referencia"])}</div>'
                f'<p>{e(l["descripcion"])}</p><span class="ir">Abrir ›</span></a>')
    return (f'<div class="ley prox"><div class="ab">{e(l["abreviatura"])}</div><h2>{e(l["nombre"])}</h2>'
            f'<p>En preparación.</p><span class="ir">Próximamente</span></div>')


def main():
    with open(os.path.join(RAIZ, "scripts", "leyes.json"), encoding="utf-8") as f:
        leyes = json.load(f)["leyes"]
    for l in leyes:
        if l["estado"] == "disponible" and not os.path.exists(os.path.join(RAIZ, l["carpeta"], "index.html")):
            sys.exit(f"ERROR: {l['abreviatura']} está como disponible pero no existe {l['carpeta']}index.html")
    logo = logo_base64()
    img = f'<img src="{logo}" alt="NOrlexia">' if logo else ""
    out = PLANTILLA.replace("__LOGO__", img).replace("__LEYES__", "".join(tarjeta(l) for l in leyes))
    with open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    print(f"index.html generado: {sum(l['estado']=='disponible' for l in leyes)} ley(es) disponible(s), "
          f"{sum(l['estado']!='disponible' for l in leyes)} en preparación.")


if __name__ == "__main__":
    main()
