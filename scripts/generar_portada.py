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
/* pie legal y ventana © (igual que norlexia.es) */
:root{--pie-oro:#8a6a1f}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--pie-oro:#c9a04a}}
:root[data-theme="dark"]{--pie-oro:#c9a04a}
.pie-legal{border-top:1px solid var(--borde);margin-top:18px;padding-top:16px}
.pie-marca{font:500 .72rem/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--suave);margin:0 0 10px}
.pie-links{display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline;margin:0;font-size:.88rem}
.pie-links a{color:var(--pie-oro)}
.pie-copy{background:none;border:0;padding:0;cursor:pointer;color:var(--pie-oro);text-decoration:underline;font:500 .78rem/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.08em;text-transform:uppercase}
.ip{max-width:600px;width:calc(100% - 32px);border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:22px 24px 10px;background:#062e2b;color:#e3ded2;box-shadow:0 20px 50px rgba(0,0,0,.45);font-size:16px}
.ip::backdrop{background:rgba(5,20,18,.55)}
.ip-cab{display:flex;justify-content:space-between;align-items:flex-start;gap:14px}
.ip h2{font-family:Georgia,serif;font-size:1.25rem;font-weight:500;line-height:1.3;margin:0 0 14px;color:#f5f0e8}
.ip-cerrar{flex:none;background:transparent;border:1px solid rgba(255,255,255,.25);color:#e3ded2;border-radius:6px;padding:7px 12px;cursor:pointer;font:500 .72rem ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.12em;text-transform:uppercase}
.ip p{margin:0 0 12px;font-size:.95rem;line-height:1.6}
.ip strong{color:#f5f0e8}
</style>
</head>
<body>
<header><div class="in">
  <div class="cab">__LOGO__<div><b>NORLEXIA</b><span>Leyes interactivas</span></div>
    <button id="tema" aria-label="Cambiar modo claro u oscuro" title="Modo claro/oscuro">◐</button></div>
  <div class="hero"><h1>Consulta las leyes como un mapa</h1>
    <p>Fases de cada procedimiento, plazos con la frase literal del BOE, recursos, test de repaso y tus notas. Funciona en el móvil y sin conexión.</p></div>
</div></header>
<main class="in">
  <div class="t">Leyes</div>
  <div class="grid">__LEYES__</div>
  <p class="aviso">Textos consolidados del BOE de carácter informativo, sin valor jurídico. Los esquemas, plazos y preguntas son material de estudio elaborado: cada app indica qué está pendiente de revisión. Tus notas y tu progreso se guardan solo en este navegador. Versión __VERSION__.</p>
</main>
<footer class="in" style="padding-bottom:30px"><div class="pie-legal">
  <p class="pie-marca">NORLEXIA · Leyes interactivas</p>
  <nav class="pie-links" aria-label="Información legal">
    <button type="button" class="pie-copy" id="ipAbrir" aria-haspopup="dialog">© 2026 J A Noriega (Norik)</button>
    <a href="aviso-legal.html">Aviso legal</a>
    <a href="politica-privacidad.html">Privacidad</a>
    <a href="cookies.html">Cookies</a>
  </nav>
</div></footer>
<dialog class="ip" id="ip" aria-labelledby="ipTit">
  <div class="ip-cab"><h2 id="ipTit">Propiedad intelectual y condiciones de uso</h2>
    <button type="button" class="ip-cerrar" id="ipCerrar">Cerrar</button></div>
  <p><strong>© 2026 J A Noriega (Norik). Desarrollador de NORLEXia.</strong></p>
  <p>Se autoriza consultar esta web y compartir su dirección libremente.</p>
  <p>No se autoriza copiar ni modificar el código, la estructura, el diseño ni el desarrollo original, ni
    explotarlos comercialmente, sin autorización previa y expresa de su desarrollador.</p>
  <p>Las normas, los datos públicos y los enlaces a fuentes oficiales conservan su propio régimen jurídico y no se
    reivindican como contenido exclusivo.</p>
</dialog>
<script>
(function(){
  var d=document.getElementById("ip");
  document.getElementById("ipAbrir").onclick=function(){ if(d.showModal) d.showModal(); else d.setAttribute("open",""); };
  var cerrar=function(){ if(d.close) d.close(); else d.removeAttribute("open"); };
  document.getElementById("ipCerrar").onclick=cerrar;
  d.addEventListener("click",function(e){ if(e.target===d) cerrar(); });  // pulsar fuera de la ventana
})();
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


def tarjeta(l, version):
    e = html.escape
    if l["estado"] == "disponible":
        return (f'<a class="ley" href="{e(l["carpeta"])}index.html?v={version}"><div class="ab">{e(l["abreviatura"])}</div>'
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
    with open(os.path.join(RAIZ, "scripts", "version.json"), encoding="utf-8") as f:
        v = json.load(f)
    out = PLANTILLA.replace("__VERSION__", str(v["version"])).replace("__LOGO__", img).replace("__LEYES__", "".join(tarjeta(l, v["version"]) for l in leyes))
    with open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    print(f"index.html generado: {sum(l['estado']=='disponible' for l in leyes)} ley(es) disponible(s), "
          f"{sum(l['estado']!='disponible' for l in leyes)} en preparación.")


if __name__ == "__main__":
    main()
