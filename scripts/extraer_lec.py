#!/usr/bin/env python3
"""Extrae la LEC completa a JSON y genera el informe de control.

Uso:  python3 scripts/extraer_lec.py

Fuentes (carpeta fuentes/):
  - LEC_BOE-A-2000-323.xml  Exportación XML (Acrobat "SaveAsXML") del PDF
                            consolidado del BOE. FUENTE PRINCIPAL: cada artículo
                            es un <Div> y cada párrafo un <P>.
  - LEC_BOE-A-2000-323.pdf  PDF consolidado del BOE. CONTRASTE: se vuelve a leer
                            línea a línea y se compara, palabra por palabra, con
                            el texto sacado del XML. También aporta lo que el XML
                            no conserva: los incisos destacados en negrita.

Salidas (carpeta lec/datos/):
  - lec.json                datos de la app (esquema común de CLAUDE.md)
  - informe_control.md      informe de control para el usuario
  - informe_control.json    lo mismo, en formato máquina
  - lineas_pdf.json         caché de líneas del PDF (no se sube a git)

Regla: el texto legal no se escribe ni se corrige a mano. Solo se quitan los
saltos de línea internos del XML y los espacios repetidos.
"""
import json
import os
import re
import sys
from collections import Counter, OrderedDict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XML = os.path.join(RAIZ, "fuentes", "LEC_BOE-A-2000-323.xml")
PDF = os.path.join(RAIZ, "fuentes", "LEC_BOE-A-2000-323.pdf")
DATOS = os.path.join(RAIZ, "lec", "datos")
CACHE = os.path.join(DATOS, "lineas_pdf.json")

SUFIJOS = ("bis|ter|quater|quáter|quinquies|sexies|septies|octies|nonies|decies|"
           "undecies|duodecies|terdecies|quaterdecies|quindecies")
RE_ART = re.compile(rf"^Artículo (\d+)((?: (?:{SUFIJOS}))?(?: [a-z]\))?)\.\s*(.*)$")
RE_DISP = re.compile(r"^Disposición (adicional|transitoria|derogatoria|final) "
                     r"([a-záéíóúñ ]+?)\.\s*(.*)$")
RE_ESTR = re.compile(r"^(LIBRO|TÍTULO|CAPÍTULO) ([IVXLC]+(?: (?:BIS|TER))?|PRELIMINAR)$")
RE_SECC = re.compile(rf"^Sección (\d+\.ª(?: (?:{SUFIJOS})\.)?)\s+(.*)$")
RE_VACIO = re.compile(r"^\((Sin contenido|Derogad[oa]|Anulad[oa]|Suprimid[oa])\)\.?$")

ORDINALES = {
    "primera": 1, "segunda": 2, "tercera": 3, "cuarta": 4, "quinta": 5,
    "sexta": 6, "séptima": 7, "octava": 8, "novena": 9, "décima": 10,
    "undécima": 11, "duodécima": 12, "decimotercera": 13, "decimocuarta": 14,
    "decimoquinta": 15, "decimosexta": 16, "decimoséptima": 17,
    "decimoctava": 18, "decimonovena": 19, "vigésima": 20,
}
DECENAS = {"vigésima": 20, "vigésimo": 20, "trigésima": 30, "trigésimo": 30}
GRUPOS = {
    "adicional": ("da", "Disposiciones adicionales"),
    "transitoria": ("dt", "Disposiciones transitorias"),
    "derogatoria": ("dd", "Disposiciones derogatorias"),
    "final": ("df", "Disposiciones finales"),
}
NIVEL = {"libro": 1, "titulo": 2, "capitulo": 3, "seccion": 4}


def ordinal_a_numero(txt):
    txt = txt.strip().lower()
    if txt == "única":
        return 1
    if txt in ORDINALES:
        return ORDINALES[txt]
    p = txt.split()
    if len(p) == 2 and p[0] in DECENAS and p[1] in ORDINALES:
        return DECENAS[p[0]] + ORDINALES[p[1]]
    return None


def limpiar(t):
    """Quita saltos de línea del XML y espacios repetidos. No toca nada más."""
    t = t.replace("\r", "").replace("\n", "")
    return re.sub(r"[ \t ]+", " ", t).strip()


def sin_espacios(t):
    return re.sub(r"\s+", "", t)


# =================================================================== XML
def texto_elem(e):
    return limpiar("".join(e.itertext()))


def leer_xml():
    from lxml import etree
    parser = etree.XMLParser(recover=True, huge_tree=True)
    raiz = etree.parse(XML, parser).getroot()
    sect = raiz.find(".//Sect")
    if sect is None:
        sys.exit("ERROR: el XML no tiene la estructura esperada (falta <Sect>).")
    marcadores = [b.get("title") for b in raiz.find("bookmark-tree").iter("bookmark")]
    return [e for e in sect if e.tag == "Div"], marcadores


def construir(divs):
    """Recorre los <Div> del XML en orden y construye árbol y artículos."""
    avisos = []
    fecha = None
    nota_general = ""
    estructura, pila = [], []
    articulos = OrderedDict()
    secuencia = []         # para el contraste: [(clave | None, div)]
    actual = None
    empezado = False
    grupos = {}

    def ruta():
        # "LIBRO I. De…" (como en el índice del BOE); "Sección 1.ª De…" (sin punto).
        sep = lambda n: " " if n["tipo"] == "seccion" else ". "
        return [(n["rotulo"] + sep(n) + n["titulo"]) if n["rotulo"] else n["titulo"]
                for _, n in pila]

    def colgar(nodo, nivel):
        while pila and pila[-1][0] >= nivel:
            pila.pop()
        (pila[-1][1]["hijos"] if pila else estructura).append(nodo)
        pila.append((nivel, nodo))

    def nueva_unidad(clave, rotulo, titulo):
        nonlocal actual
        if clave in articulos:
            avisos.append(f"Clave duplicada: {clave}")
            clave += "-duplicado"
        actual = {"rotulo": rotulo, "titulo": titulo, "parrafos": [],
                  "notas_boe": [], "ruta": ruta()}
        articulos[clave] = actual
        (pila[-1][1]["hijos"] if pila else estructura).append({"tipo": "articulo", "clave": clave})
        return clave

    def volcar_cuerpo(div, desde=0):
        """Añade a la unidad actual los párrafos y notas de un <Div>."""
        for hijo in list(div)[desde:]:
            if hijo.tag == "P":
                t = texto_elem(hijo)
                if t:
                    actual["parrafos"].append(t)
            elif hijo.tag == "Div":
                nota = texto_elem(hijo)
                nota = re.sub(r"\s+([.,;])", r"\1", nota)
                if nota.startswith("Téngase en cuenta"):
                    actual["notas_boe"].append(nota)
                else:
                    avisos.append(f"Bloque anidado no reconocido en {actual['rotulo']}: {nota[:80]}")
                    volcar_cuerpo(hijo)
            else:
                avisos.append(f"Elemento <{hijo.tag}> no tratado en {actual['rotulo']}")

    for div in divs:
        hijos = [h for h in div if h.tag in ("P", "Div", "Table")]
        if not hijos:
            continue
        primero = texto_elem(hijos[0])

        if not empezado:
            if primero.startswith("TEXTO CONSOLIDADO"):
                for h in hijos:
                    m = re.match(r"^Última modificación: (.+)$", texto_elem(h))
                    if m:
                        fecha = m.group(1).strip()
            elif primero.startswith("Téngase en cuenta"):
                nota_general = re.sub(r"\s+([.,;])", r"\1", texto_elem(div))
            elif primero.startswith("JUAN CARLOS I"):
                empezado = True
                clave = nueva_unidad("preambulo", "Preámbulo", "")
                volcar_cuerpo(div)
                secuencia.append((clave, div))
            continue

        m_estr = RE_ESTR.match(primero)
        m_secc = RE_SECC.match(primero)
        m_art = RE_ART.match(primero)
        m_disp = RE_DISP.match(primero)

        if m_estr:
            tipo = {"LIBRO": "libro", "TÍTULO": "titulo", "CAPÍTULO": "capitulo"}[m_estr.group(1)]
            resto = [texto_elem(h) for h in hijos[1:]]
            nodo = {"tipo": tipo, "rotulo": primero, "titulo": resto[0] if resto else "",
                    "hijos": []}
            if len(resto) > 1:
                nodo["estado"] = " ".join(resto[1:])
            colgar(nodo, NIVEL[tipo])
            secuencia.append((None, div))
        elif m_secc:
            nodo = {"tipo": "seccion", "rotulo": "Sección " + m_secc.group(1),
                    "titulo": m_secc.group(2), "hijos": []}
            if len(hijos) > 1:
                nodo["estado"] = " ".join(texto_elem(h) for h in hijos[1:])
            colgar(nodo, NIVEL["seccion"])
            secuencia.append((None, div))
        elif m_art:
            num = m_art.group(1) + m_art.group(2)
            clave = nueva_unidad(num, f"Artículo {num}", m_art.group(3))
            volcar_cuerpo(div, 1)
            secuencia.append((clave, div))
        elif m_disp:
            tipo, ordtxt = m_disp.group(1), m_disp.group(2).strip()
            pref, nombre = GRUPOS[tipo]
            numero = ordinal_a_numero(ordtxt)
            if numero is None:
                avisos.append(f"Ordinal no reconocido: {ordtxt}")
                numero = ordtxt.replace(" ", "_")
            if tipo not in grupos:
                pila.clear()
                g = {"tipo": "grupo", "rotulo": "", "titulo": nombre, "hijos": []}
                estructura.append(g)
                grupos[tipo] = g
                pila.append((0, g))
            clave = nueva_unidad(f"{pref}{numero}", f"Disposición {tipo} {ordtxt}", m_disp.group(3))
            volcar_cuerpo(div, 1)
            secuencia.append((clave, div))
        elif primero.startswith('"') and actual is not None:
            # Texto citado entre comillas dentro de una disposición final.
            volcar_cuerpo(div)
            secuencia.append((None, div))
        elif primero == "Por tanto,":
            pila.clear()
            clave = nueva_unidad("formula_final", "Fórmula final y firmas", "")
            volcar_cuerpo(div)
            secuencia.append((clave, div))
        elif primero.startswith("Este documento es de carácter informativo"):
            pass
        else:
            avisos.append(f"Bloque no reconocido (se añade a {actual['rotulo']}): {primero[:80]}")
            volcar_cuerpo(div)
            secuencia.append((None, div))

    return fecha, nota_general, estructura, articulos, secuencia, avisos


# =================================================================== PDF
def leer_lineas_pdf():
    if os.path.exists(CACHE) and os.path.getmtime(CACHE) > os.path.getmtime(PDF):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    import pdfplumber
    lineas = []
    with pdfplumber.open(PDF) as pdf:
        for i, pag in enumerate(pdf.pages):
            for ln in pag.extract_text_lines(return_chars=True):
                tramos = []
                for c in ln["chars"]:
                    f = c["fontname"].split("+")[-1]
                    est = ("b" if "Bold" in f else "") + ("i" if "Italic" in f else "")
                    if tramos and tramos[-1][0] == est:
                        tramos[-1][1] += c["text"]
                    else:
                        tramos.append([est, c["text"]])
                tam = Counter(round(c["size"], 1) for c in ln["chars"]).most_common(1)[0][0]
                lineas.append({"p": i + 1, "x": round(ln["x0"], 1), "top": round(ln["top"], 1),
                               "s": tam, "t": ln["text"], "tramos": tramos})
    os.makedirs(DATOS, exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(lineas, f, ensure_ascii=False)
    return lineas


def es_cabecera_pie(ln):
    if ln["top"] < 60 and ln["t"] in ("BOLETÍN OFICIAL DEL ESTADO", "LEGISLACIÓN CONSOLIDADA"):
        return True
    return ln["top"] > 790 and re.match(r"^Página \d+$", ln["t"]) is not None


def es_encabezado_unidad(ln):
    return (abs(ln["x"] - 90.7) < 1.5 and ln["tramos"] and ln["tramos"][0][0] == "b"
            and (RE_ART.match(ln["t"]) or RE_DISP.match(ln["t"])))


def segmentar_pdf(lineas):
    """Divide el cuerpo del PDF por encabezados de artículo/disposición."""
    cuerpo, dentro = [], False
    for ln in lineas:
        if ln["p"] < 8 or es_cabecera_pie(ln):
            continue
        if ln["t"] == "JUAN CARLOS I":
            dentro = True
        if dentro:
            cuerpo.append(ln)
    segmentos = [["preambulo", []]]
    for ln in cuerpo:
        if es_encabezado_unidad(ln):
            segmentos.append([ln["t"], []])
        elif ln["t"] == "Por tanto,":
            segmentos.append(["formula_final", []])
        segmentos[-1][1].append(ln)
    # Quita el aviso final del PDF.
    segmentos[-1][1] = [l for l in segmentos[-1][1]
                        if not l["t"].startswith("Este documento es de carácter informativo")]
    return segmentos


def tokens(texto):
    return texto.split()


def tokens_pdf(lineas):
    """Palabras del PDF; una línea que acaba en guion se une a la siguiente."""
    out, pend = [], ""
    for ln in lineas:
        t = ln["t"].strip()
        if pend:
            t = pend + t
            pend = ""
        if t.endswith("-") and not t.endswith(" -"):
            pend = t
            continue
        out.extend(t.split())
    if pend:
        out.extend(pend.split())
    return out


def primera_diferencia(a, b):
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    return n if len(a) != len(b) else None


def localizar(texto, buscado_sin_esp):
    """Busca un fragmento (sin espacios) dentro de un texto y lo devuelve con sus espacios."""
    idx = [i for i, c in enumerate(texto) if not c.isspace()]
    plano = "".join(texto[i] for i in idx)
    pos = plano.find(buscado_sin_esp)
    if pos < 0:
        return None
    return texto[idx[pos]: idx[pos + len(buscado_sin_esp) - 1] + 1]


def destacados_pdf(segmento):
    """Fragmentos en negrita dentro del cuerpo (no encabezados), unidos entre líneas."""
    frags, cur = [], ""
    for k, ln in enumerate(segmento):
        if k == 0 and es_encabezado_unidad(ln):
            continue
        tr = ln["tramos"]
        for j, (est, txt) in enumerate(tr):
            if "b" in est and "i" not in est:
                cur += txt
                if j < len(tr) - 1:
                    frags.append(cur)
                    cur = ""
            else:
                if cur:
                    frags.append(cur)
                    cur = ""
    if cur:
        frags.append(cur)
    return [sin_espacios(f) for f in frags if sin_espacios(f)]


# =================================================================== control
def contrastar(articulos, secuencia, lineas, avisos, estructura):
    titulos_estr = set()

    def recoger(lista):
        for n in lista:
            if n["tipo"] != "articulo":
                titulos_estr.add(sin_espacios(n["titulo"] + n.get("estado", "")))
                titulos_estr.add(sin_espacios(n["titulo"]))
                recoger(n["hijos"])
    recoger(estructura)
    seg_pdf = segmentar_pdf(lineas)

    # Texto XML esperado por unidad = la unidad + bloques sin clave que la siguen
    # (encabezados de libro, título, etc.). Las notas del BOE se comparan aparte.
    def texto_sin_notas(div):
        partes = []
        for h in div:
            if h.tag == "Div" and texto_elem(h).startswith("Téngase en cuenta"):
                continue
            partes.append(texto_sin_notas(h) if h.tag == "Div" else texto_elem(h))
        return " ".join(partes)

    esperado = []
    for clave, div in secuencia:
        texto = texto_sin_notas(div)
        if clave is None and esperado:
            esperado[-1][1].append(texto)
        else:
            esperado.append([clave, [texto]])

    resultado = {"unidades_xml": len(esperado), "unidades_pdf": len(seg_pdf),
                 "coinciden": 0, "difieren": [], "destacados": []}
    if len(esperado) != len(seg_pdf):
        avisos.append(f"El XML tiene {len(esperado)} unidades y el PDF {len(seg_pdf)}.")

    for (clave, textos), (cab_pdf, lineas_seg) in zip(esperado, seg_pdf):
        a = articulos[clave]
        if clave not in ("preambulo", "formula_final") and \
                not sin_espacios(cab_pdf).startswith(sin_espacios(a["rotulo"]) + "."):
            resultado["difieren"].append({"clave": clave, "rotulo": a["rotulo"],
                                          "motivo": f"desfase de cabecera (PDF: {cab_pdf[:60]})"})
            continue
        tx_sin_notas = tokens(" ".join(textos))
        notas_lineas = [l for l in lineas_seg if l["s"] == 9.0]
        tp = tokens_pdf([l for l in lineas_seg if l["s"] != 9.0])
        if sin_espacios(" ".join(l["t"] for l in notas_lineas)) != sin_espacios(" ".join(a["notas_boe"])):
            resultado["difieren"].append({"clave": clave, "rotulo": a["rotulo"],
                                          "motivo": "la nota del BOE no coincide"})
        d = primera_diferencia(tx_sin_notas, tp)
        if d is None:
            resultado["coinciden"] += 1
        else:
            motivo = "espacios distintos" if sin_espacios(" ".join(tx_sin_notas)) == sin_espacios(" ".join(tp)) else "texto distinto"
            resultado["difieren"].append({
                "clave": clave, "rotulo": a["rotulo"], "motivo": motivo,
                "xml": " ".join(tx_sin_notas[max(0, d - 6): d + 8]),
                "pdf": " ".join(tp[max(0, d - 6): d + 8]),
            })
        # Incisos destacados (negrita) que solo conserva el PDF.
        cuerpo = "\n".join(a["parrafos"])
        for frag in destacados_pdf(lineas_seg):
            if RE_VACIO.match(frag) or re.match(r"^[a-z0-9]+[.)]\(", frag):
                continue
            if frag.startswith('"') or frag in titulos_estr:
                continue
            original = localizar(cuerpo, frag)
            if original and not RE_VACIO.match(original):
                a.setdefault("destacado", []).append(original)
                resultado["destacados"].append({"clave": clave, "texto": original})
            elif not original:
                avisos.append(f"Negrita del PDF no localizada en {a['rotulo']}: {frag[:60]}")
    return resultado


def controles(articulos, marcadores, estructura):
    num = []
    for clave in articulos:
        m = re.match(r"^(\d+)", clave)
        if m and not clave.startswith(("d",)):
            num.append(int(m.group(1)))
    basicos = sorted(set(num))
    faltan = [n for n in range(1, max(basicos) + 1) if n not in basicos]

    vacios, cortos, sin_titulo, raros = [], [], [], []
    for clave, a in articulos.items():
        texto = "\n".join(a["parrafos"])
        if not texto:
            vacios.append(clave)
        elif RE_VACIO.match(texto.strip()):
            pass
        elif len(texto) < 40:
            cortos.append(f"{a['rotulo']}: «{texto}»")
        if clave not in ("preambulo", "formula_final") and not a["titulo"] and not clave.startswith("d"):
            sin_titulo.append(a["rotulo"])
        for p in a["parrafos"]:
            if re.search(r"(BOLETÍN OFICIAL DEL ESTADO|LEGISLACIÓN CONSOLIDADA|Página \d+$)", p):
                raros.append(f"{a['rotulo']}: posible cabecera/pie de página: «{p[:70]}»")
            if re.match(r"^(LIBRO|TÍTULO|CAPÍTULO) [IVXLC]+$", p):
                raros.append(f"{a['rotulo']}: posible encabezado dentro del texto: «{p}»")
            if "  " in p or "�" in p:
                raros.append(f"{a['rotulo']}: carácter o espacio extraño: «{p[:70]}»")
    estado_vacio = Counter()
    for clave, a in articulos.items():
        t = "\n".join(a["parrafos"]).strip()
        if RE_VACIO.match(t):
            estado_vacio[t] += 1

    # Marcadores (índice) del PDF frente a lo extraído.
    rotulos_unidades = set()
    for a in articulos.values():
        rotulos_unidades.add(sin_espacios(a["rotulo"] + "." + a["titulo"]).rstrip("."))
    nodos = []

    def recorrer(lista):
        for n in lista:
            if n["tipo"] != "articulo":
                nodos.append(n)
                recorrer(n["hijos"])
    recorrer(estructura)
    rotulos_nodos = set()
    for n in nodos:
        if n["tipo"] == "grupo":
            rotulos_nodos.add(sin_espacios("[" + n["titulo"] + "]"))
        else:
            rotulos_nodos.add(sin_espacios(n["rotulo"] + "." + n["titulo"]).rstrip("."))
            rotulos_nodos.add(sin_espacios(n["rotulo"] + n["titulo"]).rstrip("."))
            rotulos_nodos.add(sin_espacios(n["rotulo"].rstrip(".") + "." + n["titulo"]).rstrip("."))
    sin_pareja = []
    for t in marcadores[1:]:
        k = sin_espacios(t).rstrip(".")
        if t in ("[Preámbulo]", "[Firma]"):
            continue
        if k not in rotulos_unidades and k not in rotulos_nodos:
            sin_pareja.append(t)
    return {
        "articulos_numerados": len(num),
        "articulo_max": max(basicos),
        "numeros_que_faltan": faltan,
        "sin_texto": vacios,
        "muy_cortos": cortos,
        "articulos_sin_titulo": sin_titulo,
        "sospechas": raros,
        "estados": dict(estado_vacio),
        "marcadores_pdf": len(marcadores) - 1,
        "marcadores_sin_pareja": sin_pareja,
        "nodos_estructura": Counter(n["tipo"] for n in nodos),
    }


def escribir_informe(datos, ctrl, contraste, avisos):
    arts = datos["articulos"]
    tipos = Counter()
    for k in arts:
        if k in ("preambulo", "formula_final"):
            tipos["otros"] += 1
        elif k.startswith("da"):
            tipos["Disposiciones adicionales"] += 1
        elif k.startswith("dt"):
            tipos["Disposiciones transitorias"] += 1
        elif k.startswith("dd"):
            tipos["Disposiciones derogatorias"] += 1
        elif k.startswith("df"):
            tipos["Disposiciones finales"] += 1
        else:
            tipos["Artículos"] += 1
    L = []
    L.append("# Informe de control — Extracción LEC (F1)\n")
    L.append(f"- Fuente principal: `fuentes/LEC_BOE-A-2000-323.xml` (exportación XML del PDF consolidado)")
    L.append(f"- Contraste: `fuentes/LEC_BOE-A-2000-323.pdf`")
    L.append(f"- Versión consolidada: **{datos['ley']['fecha_version']}** (\"Última modificación\" en la pág. 8 del PDF)\n")
    L.append("## Recuento\n")
    L.append("| Tipo | Número |\n|---|---|")
    for k in ("Artículos", "Disposiciones adicionales", "Disposiciones transitorias",
              "Disposiciones derogatorias", "Disposiciones finales"):
        L.append(f"| {k} | {tipos[k]} |")
    L.append(f"| Preámbulo y fórmula final | {tipos['otros']} |")
    L.append(f"| **Total de unidades** | **{len(arts)}** |\n")
    L.append(f"- Artículos con número propio: del 1 al {ctrl['articulo_max']}. "
             f"Números que faltan en la secuencia: {ctrl['numeros_que_faltan'] or 'ninguno'}.")
    bis = [k for k in arts if re.match(r"^\d+ ", k)]
    L.append(f"- Artículos bis/ter/etc.: {len(bis)}.")
    ne = ctrl["nodos_estructura"]
    L.append(f"- Estructura: {ne.get('libro', 0)} libros, {ne.get('titulo', 0)} títulos, "
             f"{ne.get('capitulo', 0)} capítulos, {ne.get('seccion', 0)} secciones, "
             f"{ne.get('grupo', 0)} grupos de disposiciones.")
    L.append("- Artículos/disposiciones sin contenido vigente (el BOE solo pone la marca): " +
             ", ".join(f"{k} ×{v}" for k, v in ctrl["estados"].items()) + ".\n")
    L.append("## Contraste XML ↔ PDF (palabra por palabra)\n")
    L.append(f"- Unidades comparadas: {contraste['unidades_xml']} (XML) / {contraste['unidades_pdf']} (PDF).")
    L.append(f"- Idénticas: **{contraste['coinciden']}**.")
    L.append(f"- Con diferencias: **{len(contraste['difieren'])}**.\n")
    if contraste["difieren"]:
        L.append("| Unidad | Motivo | XML | PDF |\n|---|---|---|---|")
        for d in contraste["difieren"]:
            L.append(f"| {d['rotulo']} | {d['motivo']} | {d.get('xml', '')} | {d.get('pdf', '')} |")
        L.append("")
    L.append("## Índice del PDF (marcadores) frente a lo extraído\n")
    L.append(f"- Marcadores del PDF: {ctrl['marcadores_pdf']}. Sin pareja en la extracción: "
             f"{len(ctrl['marcadores_sin_pareja'])}.")
    for t in ctrl["marcadores_sin_pareja"]:
        L.append(f"  - {t}")
    L.append("")
    L.append("## Posibles problemas de extracción\n")
    hay = False
    for titulo, lista in (("Unidades sin texto", ctrl["sin_texto"]),
                          ("Unidades con texto muy corto (revisar)", ctrl["muy_cortos"]),
                          ("Artículos sin epígrafe", ctrl["articulos_sin_titulo"]),
                          ("Sospechas en el texto", ctrl["sospechas"]),
                          ("Avisos del script", avisos)):
        if lista:
            hay = True
            L.append(f"**{titulo}** ({len(lista)}):")
            for x in lista:
                L.append(f"- {x}")
            L.append("")
    if not hay:
        L.append("Ninguno detectado por los controles automáticos.\n")
    L.append("## Notas del BOE e incisos destacados\n")
    notas = [(a["rotulo"], n) for a in arts.values() for n in a.get("notas_boe", [])]
    L.append(f"- Nota general (pág. 8): {datos['ley']['nota_general_boe']}")
    for r, n in notas:
        L.append(f"- {r}: {n}")
    for d in contraste["destacados"]:
        L.append(f"- Inciso en negrita en el PDF ({arts[d['clave']]['rotulo']}): «{d['texto']}»")
    L.append("\n## Lo que los controles NO garantizan\n")
    L.append("- XML y PDF salen del mismo documento del BOE: si el propio BOE tuviera una errata, "
             "ambos la tendrían. El contraste detecta errores de extracción, no erratas del original.")
    L.append("- La negrita (inciso destacado) solo se conserva en el PDF; se ha recuperado de ahí.")
    return "\n".join(L) + "\n"


def main():
    divs, marcadores = leer_xml()
    fecha, nota_general, estructura, articulos, secuencia, avisos = construir(divs)
    if not fecha:
        sys.exit("ERROR: no se encuentra la fecha de la versión consolidada. Pregunta al usuario.")
    lineas = leer_lineas_pdf()
    contraste = contrastar(articulos, secuencia, lineas, avisos, estructura)
    ctrl = controles(articulos, marcadores, estructura)

    salida = OrderedDict()
    for clave, a in articulos.items():
        u = {"rotulo": a["rotulo"], "titulo": a["titulo"],
             "texto_literal": "\n".join(a["parrafos"]), "ruta": a["ruta"]}
        if a["notas_boe"]:
            u["notas_boe"] = a["notas_boe"]
        if a.get("destacado"):
            u["destacado"] = a["destacado"]
        salida[clave] = u

    datos = OrderedDict([
        ("ley", OrderedDict([
            ("id", "lec"),
            ("nombre", "Ley 1/2000, de 7 de enero, de Enjuiciamiento Civil"),
            ("abreviatura", "LEC"),
            ("boe", "BOE-A-2000-323"),
            ("fecha_version", fecha),
            ("nota_general_boe", nota_general),
            ("aviso", "Texto consolidado del BOE de carácter informativo, sin valor jurídico"),
        ])),
        ("estructura", estructura),
        ("articulos", salida),
        ("plazos", []),
        ("procedimientos", []),
        ("recursos", []),
        ("repaso", []),
    ])
    os.makedirs(DATOS, exist_ok=True)
    with open(os.path.join(DATOS, "lec.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    informe = escribir_informe(datos, ctrl, contraste, avisos)
    with open(os.path.join(DATOS, "informe_control.md"), "w", encoding="utf-8") as f:
        f.write(informe)
    with open(os.path.join(DATOS, "informe_control.json"), "w", encoding="utf-8") as f:
        json.dump({"controles": ctrl, "contraste": contraste, "avisos": avisos},
                  f, ensure_ascii=False, indent=1, default=dict)
    print(informe)


if __name__ == "__main__":
    main()
