#!/usr/bin/env python3
"""Inserta lec/datos/lec.json y el logo dentro de lec/index.html.

Uso:  python3 scripts/insertar_datos.py
Se puede ejecutar cuantas veces se quiera: sustituye los datos anteriores.
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
HTML = os.path.join(RAIZ, "lec", "index.html")
JSON_LEY = os.path.join(RAIZ, "lec", "datos", "lec.json")

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


def main():
    with open(JSON_LEY, encoding="utf-8") as f:
        datos = json.load(f)
    js = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    js = js.replace("</", "<\\/")  # no puede cerrar la etiqueta <script>
    with open(HTML, encoding="utf-8") as f:
        html = f.read()
    patron = re.compile(r'(<script id="datos-ley" type="application/json">)(.*?)(</script>)', re.S)
    if not patron.search(html):
        sys.exit("ERROR: no encuentro el bloque de datos en lec/index.html")
    html = patron.sub(lambda m: m.group(1) + js + m.group(3), html, count=1)
    patron_logo = re.compile(r'const LOGO_SRC = "[^"]*";')
    if not patron_logo.search(html):
        sys.exit("ERROR: no encuentro LOGO_SRC en lec/index.html")
    logo = logo_base64()
    html = patron_logo.sub(lambda m: f'const LOGO_SRC = "{logo}";', html, count=1)
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"lec/index.html actualizado: {len(datos['articulos'])} unidades, "
          f"{os.path.getsize(HTML) / 1e6:.2f} MB.")


if __name__ == "__main__":
    main()
