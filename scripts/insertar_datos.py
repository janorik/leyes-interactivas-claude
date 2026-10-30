#!/usr/bin/env python3
"""Inserta los datos de una ley y el logo dentro de su index.html.

Uso:  python3 scripts/insertar_datos.py           (LEC)
      python3 scripts/insertar_datos.py lecrim    (LECrim; vale para cualquier ley con carpeta propia)
Se puede ejecutar cuantas veces se quiera: sustituye los datos anteriores.
La app es la misma para todas las leyes: lec/index.html hace de plantilla y se copia a la
carpeta de cada ley con sus datos (así una mejora de la app llega a todas).
El logo (assets/logo.*) se recorta al emblema, se reduce y se incrusta en base64,
para que lec/index.html funcione sin conexión y sin archivos externos.
"""
import base64
import glob
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEY = sys.argv[1] if len(sys.argv) > 1 else "lec"
PLANTILLA = os.path.join(RAIZ, "lec", "index.html")
HTML = os.path.join(RAIZ, LEY, "index.html")
JSON_LEY = os.path.join(RAIZ, LEY, "datos", LEY + ".json")
JSON_PROC = os.path.join(RAIZ, LEY, "datos", "procedimientos.json")
JSON_REC = os.path.join(RAIZ, LEY, "datos", "recursos.json")

# Recorte del emblema "N" en el logo cuadrado de 2048 px (proporciones relativas).
RECORTE = (680 / 2048, 930 / 2048, 1420 / 2048, 1500 / 2048)


def logo_base64():
    candidatos = sorted(glob.glob(os.path.join(RAIZ, "assets", "logo.*")))
    if not candidatos:
        print("Aviso: no hay logo en assets/; la cabecera irá sin imagen.")
        return ""
    try:
        from PIL import Image
    except ImportError:
        print("Aviso: falta Pillow; la cabecera irá sin imagen.")
        return ""
    im = Image.open(candidatos[0]).convert("RGB")
    w, h = im.size
    if w == h:  # logo cuadrado del usuario: se usa el emblema
        im = im.crop((int(RECORTE[0] * w), int(RECORTE[1] * h), int(RECORTE[2] * w), int(RECORTE[3] * h)))
    im.thumbnail((160, 120))
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _norm(t):
    return re.sub(r"\s+", " ", t).strip()


# «LAJ» en lugar de «secretario judicial» y «Letrado de la Administración de Justicia»
# (decisión del usuario, 23-10-2026), también en el texto de los artículos. Se hace aquí,
# al insertar, para que los datos extraídos (<ley>/datos/<ley>.json) sigan siendo literales.
RE_LAJ_GENERO = re.compile(r"\b([Ee]l|[Dd]el|[Aa]l)\s+(?:[Ll]etrado\s+o\s+la|o\s+la)\s+(?=[Ll]etrada\s+de\s+la\s+[Aa]dministración)")
RE_LAJ = re.compile(r"[Ll]etrad[oa]s?(?:\s+o\s+[Ll]etrad[oa]s?|\s+[Ll]etrad[oa]s?)?\s+de\s+la\s+[Aa]dministración\s+de\s+[Jj]usticia"
                    r"|[Ss]ecretari[oa]s?\s+[Jj]udicial(?:es)?")


def laj(o):
    if isinstance(o, str):
        return RE_LAJ.sub("LAJ", RE_LAJ_GENERO.sub(lambda m: m.group(1) + " ", o))
    if isinstance(o, list):
        return [laj(v) for v in o]
    if isinstance(o, dict):
        return {k: (v if k == "nota_general_boe" else laj(v)) for k, v in o.items()}
    return o


# Enlace a una ley distinta de la LEC: [[Nombre de la ley|https://www.boe.es/...]]
RE_LEY_EXT = re.compile(r"\[\[[^|\]]+\|https://www\.boe\.es/[^\]\s]+\]\]")


def validar_y_anadir_procedimientos(datos):
    """Comprueba el contenido elaborado contra el texto literal y lo añade a los datos.

    - Todo artículo citado debe existir en la LEC extraída.
    - Toda frase 'literal' debe aparecer tal cual en el artículo citado.
    - Todo procedimiento debe llevar revisado (false hasta que lo valide el usuario).
    Si algo falla, el script se detiene: no se publica nada sin comprobar.
    """
    if not os.path.exists(JSON_PROC):
        return
    with open(JSON_PROC, encoding="utf-8") as f:
        bruto = laj(json.load(f))
    proc = bruto["procedimientos"]
    externos = bruto.get("externos", [])
    arts = datos["articulos"]
    errores = []

    def art(k, donde):
        if k not in arts:
            errores.append(f"{donde}: el artículo {k} no existe")

    def lit(articulo, texto, donde):
        art(articulo, donde)
        if articulo in arts and _norm(texto) not in _norm(arts[articulo]["texto_literal"]):
            errores.append(f"{donde}: la frase no está en el art. {articulo}: «{texto[:70]}»")

    plazos = []
    for p in proc:
        if "revisado" not in p:
            errores.append(f"{p['id']}: falta 'revisado'")
        for k in p["ambito"]["articulos"]:
            art(k, p["id"])
        for l in p["ambito"].get("literal", []):
            lit(l["articulo"], l["texto"], p["id"] + "/ámbito")
        for f in p["fases"]:
            d = f["id"]
            for campo in ("descripcion", "aviso"):
                txt = f.get(campo, "")
                if txt.count("[[") != len(RE_LEY_EXT.findall(txt)):
                    errores.append(f"{d}/{campo}: enlace a otra ley mal formado (use [[Nombre|https://www.boe.es/...]])")
            for k in f["articulos"] + f.get("conexiones", []):
                art(k, d)
            for pl in f["plazos"]:
                lit(pl["articulo"], pl["literal"], d + "/plazo")
                plazos.append({"id": f"{d}-{len(plazos) + 1}", "acto": pl["acto"], "plazo": pl["plazo"],
                               "computo": "", "articulos": [pl["articulo"]], "bloque": p["bloque"],
                               "procedimiento": p["id"], "fase": f["fase"], "literal": pl["literal"],
                               "revisado": p["revisado"]})
            for r in f["ramas"]:
                for k in r["articulos"]:
                    art(k, d)
                lit(r["literal"]["articulo"], r["literal"]["texto"], d + "/rama")
            q = f.get("pregunta")
            if q:
                lit(q["literal"]["articulo"], q["literal"]["texto"], d + "/pregunta")
    # Leyes distintas enlazadas desde el mapa (p. ej. el Tribunal del Jurado en la LECrim).
    for e in externos:
        if len(RE_LEY_EXT.findall(e["texto"])) != 1 or e["texto"].count("[[") != 1:
            errores.append(f"externo {e['id']}: el texto debe llevar un enlace [[Nombre|https://www.boe.es/...]]")
        for k in e.get("articulos", []):
            art(k, "externo " + e["id"])
    # Pestañas «Procedimientos» y «Recursos»: cada elemento debe existir.
    ids_proc = {p["id"]: p for p in proc}
    ids_ext = {e["id"] for e in externos}
    vistas = {k: bruto.get(k, []) for k in ("vista_procedimientos", "vista_recursos")}
    for nombre, grupos in vistas.items():
        for g in grupos:
            for it in g["items"]:
                if isinstance(it, str):
                    ok = it in ids_proc
                elif "externo" in it:
                    ok = it["externo"] in ids_ext
                else:
                    ok = it["proc"] in ids_proc and any(f["id"] == it["fase"] for f in ids_proc[it["proc"]]["fases"])
                if not ok:
                    errores.append(f"{nombre} «{g['grupo']}»: no existe {it}")
    if errores:
        sys.exit("ERROR en procedimientos.json:\n- " + "\n- ".join(errores))
    datos["procedimientos"] = proc
    datos["externos"] = externos
    datos.update(vistas)
    datos["plazos"] = plazos
    print(f"Procedimientos comprobados: {len(proc)} ({sum(len(p['fases']) for p in proc)} fases, "
          f"{len(plazos)} plazos). Todas las frases literales están en su artículo.")


def validar_y_anadir_recursos(datos):
    """Igual que con los procedimientos: artículos existentes y frases literales comprobadas."""
    if not os.path.exists(JSON_REC):
        return
    with open(JSON_REC, encoding="utf-8") as f:
        rec = laj(json.load(f))
    arts = datos["articulos"]
    errores = []
    ids = {r["id"] for r in rec["recursos"]}

    def lit(l, donde):
        a, t = l["articulo"], l["texto"]
        if a not in arts:
            errores.append(f"{donde}: el artículo {a} no existe")
        elif _norm(t) not in _norm(arts[a]["texto_literal"]):
            errores.append(f"{donde}: la frase no está en el art. {a}: «{t[:70]}»")

    for r in rec["recursos"]:
        for k in r["articulos"]:
            if k not in arts:
                errores.append(f"{r['id']}: el artículo {k} no existe")
        for l in r["literales"]:
            lit(l, r["id"])
    for s in rec["selector"]:
        # El LAJ solo dicta diligencias y decretos: un auto o una sentencia en su grupo es un error.
        if s["quien"] == "LAJ" and not s["res"].startswith(("Diligencia", "Decreto")):
            errores.append(f"selector «{s['res']}»: el LAJ solo dicta diligencias y decretos")
        if s["recurso"] is not None and s["recurso"] not in ids:
            errores.append(f"selector «{s['res']}»: recurso {s['recurso']} no definido")
        lit(s["literal"], "selector «" + s["res"] + "»")
    # Fichas del mapa que enlazan a recursos concretos (campo recursos_rel de la fase).
    for p in datos.get("procedimientos", []):
        for f in p["fases"]:
            for k in f.get("recursos_rel", []):
                if k not in ids:
                    errores.append(f"{f['id']}/recursos_rel: recurso {k} no definido")
    if errores:
        sys.exit("ERROR en recursos.json:\n- " + "\n- ".join(errores))
    datos["recursos"] = rec["recursos"]
    datos["selector_recursos"] = rec["selector"]
    datos["recursos_revisado"] = rec["revisado"]
    # Grupos del selector «Por resolución» (si no hay, la app usa LAJ / Tribunal, como en la LEC).
    datos["grupos_selector"] = rec.get("grupos_selector", [])
    datos["recursos_ubicacion"] = rec.get("ubicacion", "")
    sin_grupo = {s["quien"] for s in rec["selector"]} - {g["quien"] for g in datos["grupos_selector"]}
    if datos["grupos_selector"] and sin_grupo:
        sys.exit(f"ERROR en recursos.json: casos del selector sin grupo: {sorted(sin_grupo)}")
    print(f"Recursos comprobados: {len(rec['recursos'])} recursos, {len(rec['selector'])} casos del selector.")


def anadir_enlaces_otras_leyes(datos):
    """Botones entre fichas de dos leyes (scripts/enlaces_leyes.json): campo otra_ley de cada fase."""
    ruta = os.path.join(RAIZ, "scripts", "enlaces_leyes.json")
    if not os.path.exists(ruta) or not datos.get("procedimientos"):
        return
    with open(ruta, encoding="utf-8") as f:
        pares = json.load(f)["pares"]
    with open(os.path.join(RAIZ, "scripts", "leyes.json"), encoding="utf-8") as f:
        abrev = {l["id"]: l["abreviatura"] for l in json.load(f)["leyes"]}
    cache, errores, n = {}, [], 0

    def fase(ref):
        ley, fid = ref.split(":", 1)
        if ley not in cache:
            with open(os.path.join(RAIZ, ley, "datos", "procedimientos.json"), encoding="utf-8") as f:
                cache[ley] = {fa["id"]: (p, fa) for p in json.load(f)["procedimientos"]
                              if not p.get("solo_procedimientos") for fa in p["fases"]}
        pf = cache[ley].get(fid)
        if not pf:
            errores.append(f"{ref}: ficha no encontrada")
        elif pf[1].get("esqueleto"):
            errores.append(f"{ref}: es una ficha de índice")
        return ley, fid, pf

    propias = {fa["id"]: fa for p in datos["procedimientos"] for fa in p["fases"]}
    for a, b in pares:
        for de, a_ in ((a, b), (b, a)):
            ley, fid, _ = fase(de)
            ley2, fid2, pf2 = fase(a_)
            if ley != LEY or not pf2 or fid not in propias:
                continue
            propias[fid].setdefault("otra_ley", []).append(
                {"ley": ley2, "abr": abrev[ley2], "proc": pf2[0]["id"], "fase": fid2, "nombre": laj(pf2[1]["fase"])})
            n += 1
    if errores:
        sys.exit("ERROR en enlaces_leyes.json:\n- " + "\n- ".join(sorted(set(errores))))
    if n:
        print(f"Enlaces a otras leyes: {n}.")


def main():
    with open(JSON_LEY, encoding="utf-8") as f:
        datos = laj(json.load(f))
    # Nombre corto de la ley (cabecera del árbol), el mismo que en la portada.
    with open(os.path.join(RAIZ, "scripts", "leyes.json"), encoding="utf-8") as f:
        ficha = next((l for l in json.load(f)["leyes"] if l["id"] == LEY), None)
    if ficha:
        datos["ley"]["nombre_corto"] = ficha["nombre"]
        datos["ley"]["titulo_mapa"] = ficha.get("mapa", "Mapa procesal")
        if ficha.get("rotulos"):  # rótulos propios del mapa (el ET no es ley procesal: «Ficha», no «Fase»)
            datos["ley"]["rotulos"] = ficha["rotulos"]
    validar_y_anadir_procedimientos(datos)
    validar_y_anadir_recursos(datos)
    anadir_enlaces_otras_leyes(datos)
    js = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    js = js.replace("</", "<\\/")  # no puede cerrar la etiqueta <script>
    with open(PLANTILLA, encoding="utf-8") as f:
        html = f.read()
    patron = re.compile(r'(<script id="datos-ley" type="application/json">)(.*?)(</script>)', re.S)
    if not patron.search(html):
        sys.exit("ERROR: no encuentro el bloque de datos en la plantilla lec/index.html")
    html = patron.sub(lambda m: m.group(1) + js + m.group(3), html, count=1)
    patron_logo = re.compile(r'const LOGO_SRC = "[^"]*";')
    if not patron_logo.search(html):
        sys.exit("ERROR: no encuentro LOGO_SRC en la plantilla lec/index.html")
    logo = logo_base64()
    html = patron_logo.sub(lambda m: f'const LOGO_SRC = "{logo}";', html, count=1)
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{LEY}/index.html actualizado: {len(datos['articulos'])} unidades, "
          f"{os.path.getsize(HTML) / 1e6:.2f} MB.")


if __name__ == "__main__":
    main()
