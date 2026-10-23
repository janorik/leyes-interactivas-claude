#!/usr/bin/env python3
"""Extrae una ley completa del PDF consolidado del BOE a <ley>/datos/<ley>.json.

Uso:  python3 scripts/extraer_ley.py lecrim
      python3 scripts/extraer_ley.py lrjs
      python3 scripts/extraer_ley.py ljca

Vale para las leyes sin XML, con la maquetación de los PDF consolidados del BOE
(la LEC usa scripts/extraer_lec.py porque parte del XML). Lo propio de cada ley
(PDF, página donde empieza el texto, preámbulo, nombre) está en LEYES, más abajo.
El texto se toma tal cual del PDF; no se completa nada a mano.

Cómo lee el PDF (maquetación del BOE):
- Encabezado de artículo: línea en negrita en el margen izquierdo («Artículo 14.»,
  «Artículo 588 bis a. Principios rectores.», «Artículos 48 a 50.»).
- Libro / Título / Capítulo: rótulo centrado sin negrita y, debajo, el nombre en negrita
  (puede ocupar varias líneas). Sección: negrita cursiva.
- Párrafo nuevo: línea con sangría. Notas del BOE («Téngase en cuenta…»): letra menor.
- El Real Decreto de aprobación (con sus propios «Artículo 1º…5º») va como preámbulo,
  para no confundirlo con los artículos de la ley.

Genera además lecrim/datos/informe_control.md y .json con el número de artículos y los
posibles problemas de extracción.
"""
import json
import os
import re
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lo propio de cada ley. pag_cuerpo: primera página tras el índice del PDF.
# El preámbulo va de la línea que empieza por inicio_pre hasta la línea fin_pre;
# si saltar_fin, esa línea es un rótulo que no se guarda (la LECrim repite su nombre).
LEYES = {
    "lecrim": {"pdf": "LECrim_BOE-A-1882-6036.pdf", "pag_cuerpo": 7,
               "inicio_pre": "Teniendo presente", "fin_pre": "LEY DE ENJUICIAMIENTO CRIMINAL", "saltar_fin": True,
               "rotulo_pre": "Real Decreto de aprobación",
               "ley": {"id": "lecrim", "nombre": "Real Decreto de 14 de septiembre de 1882 por el que se aprueba la "
                                                "Ley de Enjuiciamiento Criminal",
                       "abreviatura": "LECrim", "boe": "BOE-A-1882-6036"}},
    "lrjs": {"pdf": "LRJS_BOE-A-2011-15936.pdf", "pag_cuerpo": 5,
             "inicio_pre": "JUAN CARLOS I", "fin_pre": "LIBRO PRIMERO", "saltar_fin": False,
             "rotulo_pre": "Preámbulo",
             "ley": {"id": "lrjs", "nombre": "Ley 36/2011, de 10 de octubre, reguladora de la jurisdicción social",
                     "abreviatura": "LRJS", "boe": "BOE-A-2011-15936"}},
    "ljca": {"pdf": "LJCA_BOE-A-1998-16718.pdf", "pag_cuerpo": 3,
             "inicio_pre": "JUAN CARLOS I", "fin_pre": "TÍTULO I", "saltar_fin": False,
             "rotulo_pre": "Preámbulo",
             "ley": {"id": "ljca", "nombre": "Ley 29/1998, de 13 de julio, reguladora de la Jurisdicción "
                                             "Contencioso-administrativa",
                     "abreviatura": "LJCA", "boe": "BOE-A-1998-16718"}},
}
LEY = sys.argv[1] if len(sys.argv) > 1 else "lecrim"
CFG = LEYES[LEY]
PDF = os.path.join(RAIZ, "fuentes", CFG["pdf"])
DATOS = os.path.join(RAIZ, LEY, "datos")
CACHE = os.path.join(DATOS, "lineas_pdf.json")

SUFIJOS = ("bis|ter|quater|quáter|quinquies|sexies|septies|octies|nonies|decies|"
           "undecies|duodecies|terdecies|quaterdecies")
NUM = rf"\d+(?: (?:{SUFIJOS}))?(?: \d+| [a-z]\)?)?"
RE_ART = re.compile(rf"^Artículo ({NUM})\.(?:\s+(.*))?$")
RE_ARTS = re.compile(r"^Artículos (\d+) a (\d+)\.(?:\s+(.*))?$")
RE_DISP = re.compile(r"^Disposición (adicional|transitoria|derogatoria|final)(?: (\S+))?\.(?:\s+(.*))?$")
RE_ESTR = re.compile(r"^(LIBRO|TÍTULO|CAPÍTULO) ([IVXLC]+(?: (?:BIS|TER|bis|ter))?|PRELIMINAR|"
                     r"PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|SÉPTIMO)$")
RE_SECC = re.compile(r"^Sección (\d+\.ª)\s*(.*)$")
RE_SUBSECC = re.compile(r"^Subsección (\d+\.ª)\s*(.*)$")  # LRJS: letra normal, centrada
RE_VACIO = re.compile(r"^\((Sin contenido|Derogad[oa]s?|Anulad[oa]s?|Suprimid[oa]s?)\)\.?$")

ORDINALES = {"primera": 1, "segunda": 2, "tercera": 3, "cuarta": 4, "quinta": 5, "sexta": 6,
             "séptima": 7, "octava": 8, "novena": 9, "décima": 10, "undécima": 11,
             "duodécima": 12, "decimoprimera": 11, "decimotercera": 13, "decimocuarta": 14, "decimoquinta": 15}
PREF = {"adicional": "da", "transitoria": "dt", "derogatoria": "dd", "final": "df"}
GRUPOS = {"da": "Disposiciones adicionales", "dt": "Disposiciones transitorias",
          "dd": "Disposiciones derogatorias", "df": "Disposiciones finales"}
NIVEL = {"libro": 1, "titulo": 2, "capitulo": 3, "seccion": 4, "subseccion": 5}
X_IZQ, X_SANGRIA = 90.7, 107.7


# ================================================================ lectura del PDF
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


def negrita(ln, cursiva=None):
    """Toda la línea en negrita (cursiva=True exige cursiva; False la excluye)."""
    tr = [t for t in ln["tramos"] if t[1].strip()]
    if not tr or not all("b" in e for e, _ in tr):
        return False
    if cursiva is None:
        return True
    return all(("i" in e) == cursiva for e, _ in tr)


def empieza_negrita(ln):
    tr = [t for t in ln["tramos"] if t[1].strip()]
    return bool(tr) and "b" in tr[0][0] and "i" not in tr[0][0]


def solo_estilo(ln, estilos):
    tr = [t for t in ln["tramos"] if t[1].strip()]
    return bool(tr) and all(e in estilos for e, _ in tr)


def unir_notas(lineas):
    """Las notas del BOE no llevan sangría: una nota nueva empieza tras punto final o «Ref. BOE-…»."""
    out = []
    for ln in lineas:
        t = ln["t"].strip()
        if not t:
            continue
        if not out or re.search(r"(\.|BOE-A-\d+-\d+)$", out[-1]):
            out.append(t)
        else:
            out[-1] += ("" if out[-1].endswith("-") else " ") + t
    return out


def es_nota(ln):
    return ln["s"] < 9.6


def clave_disp(tipo, ordinal):
    pref = PREF[tipo]
    if not ordinal:
        return pref
    o = ordinal.lower()
    return pref + str(ORDINALES[o]) if o in ORDINALES else pref + "_" + o


def encabezado(ln):
    """Si la línea abre un artículo o disposición, devuelve (clave, rótulo, epígrafe)."""
    if abs(ln["x"] - X_IZQ) > 1.5 or not empieza_negrita(ln):
        return None
    t = ln["t"].strip()
    m = RE_ART.match(t)
    if m:
        return m.group(1).replace(")", ""), "Artículo " + m.group(1), m.group(2) or ""
    m = RE_ARTS.match(t)
    if m:
        return f"{m.group(1)} a {m.group(2)}", f"Artículos {m.group(1)} a {m.group(2)}", m.group(3) or ""
    m = RE_DISP.match(t)
    if m:
        rot = "Disposición " + m.group(1) + (" " + m.group(2) if m.group(2) else "")
        return clave_disp(m.group(1), m.group(2)), rot, m.group(3) or ""
    return None


# ================================================================ construcción
def localizar(texto, buscado_sin_esp):
    """Busca un fragmento (sin espacios) dentro del texto y lo devuelve con sus espacios."""
    idx = [i for i, c in enumerate(texto) if not c.isspace()]
    plano = "".join(texto[i] for i in idx)
    pos = plano.find(buscado_sin_esp)
    if pos < 0 or not buscado_sin_esp:
        return None
    return texto[idx[pos]: idx[pos + len(buscado_sin_esp) - 1] + 1]


def unir(lineas):
    """Une líneas en párrafos: la sangría abre párrafo; el guion final une sin espacio."""
    parrafos = []
    for ln in lineas:
        t = ln["t"].strip()
        if not t:
            continue
        nuevo = not parrafos or ln["x"] > X_IZQ + 5
        if nuevo:
            parrafos.append(t)
        elif parrafos[-1].endswith("-") and not parrafos[-1].endswith(" -"):
            parrafos[-1] += t
        else:
            parrafos[-1] += " " + t
    return parrafos


def destacados(lineas):
    """Fragmentos en negrita (no cursiva) dentro del texto: incisos que el BOE resalta."""
    frags, cur = [], ""
    for ln in lineas:
        for est, txt in ln["tramos"]:
            if "b" in est and "i" not in est:
                cur += txt
            elif txt.strip():
                if cur.strip():
                    frags.append(re.sub(r"\s+", " ", cur).strip())
                cur = ""
        cur += " "
    if cur.strip():
        frags.append(re.sub(r"\s+", " ", cur).strip())
    return [f for f in frags if not RE_VACIO.match(f)]


def construir(lineas):
    avisos = []
    cuerpo = [ln for ln in lineas if ln["p"] >= CFG["pag_cuerpo"] and not es_cabecera_pie(ln)]
    # Fecha y notas generales (antes del preámbulo).
    fecha, notas_gen, i = None, [], 0
    while i < len(cuerpo) and not cuerpo[i]["t"].strip().startswith(CFG["inicio_pre"]):
        t = cuerpo[i]["t"]
        m = re.match(r"^Última modificación: (.+)$", t)
        if m:
            fecha = m.group(1).strip()
        elif t == "TEXTO CONSOLIDADO":
            notas_gen = []  # lo anterior es el final del índice (LJCA: acaba en la página del cuerpo)
        else:
            notas_gen.append(cuerpo[i])
        i += 1
    notas_generales = unir_notas(notas_gen)
    # Preámbulo (en la LECrim, el Real Decreto de aprobación), hasta el rótulo de la ley o el Libro primero.
    pre = []
    while i < len(cuerpo) and cuerpo[i]["t"].strip() != CFG["fin_pre"]:
        pre.append(cuerpo[i])
        i += 1
    if CFG["saltar_fin"]:
        i += 1
    articulos = {"preambulo": {"rotulo": CFG["rotulo_pre"], "titulo": "",
                               "texto_literal": "\n".join(unir_preambulo(pre)), "ruta": []}}
    estructura = [{"tipo": "articulo", "clave": "preambulo"}]
    pila = []  # nodos abiertos (libro > título > capítulo > sección)
    actual = None  # [clave, lineas_texto, lineas_nota]
    orden = []

    def contenedor():
        return pila[-1]["hijos"] if pila else estructura

    def cerrar():
        if actual is None:
            return
        k, txt, notas = actual
        a = articulos[k]
        a["texto_literal"] = "\n".join(unir(txt))
        if notas:
            a["notas_boe"] = unir_notas(notas)
        # Los tramos del PDF no traen los espacios: cada fragmento se busca en el texto ya unido.
        d = [localizar(a["texto_literal"], re.sub(r"\s+", "", f)) for f in destacados(txt)]
        d = [f for f in d if f and not RE_VACIO.match(f)]
        if d:
            a["destacado"] = d
        if not a["texto_literal"]:
            avisos.append(f"{a['rotulo']}: sin texto")

    def ruta():
        return [n["rotulo"] + (". " + n["titulo"] if n["titulo"] else "") for n in pila]

    while i < len(cuerpo):
        ln = cuerpo[i]
        t = ln["t"].strip()
        if t.startswith("Este documento es de carácter informativo"):
            i += 1
            continue
        m = RE_ESTR.match(t)
        if m and ln["x"] > 150:  # el rótulo va centrado (a veces en negrita)
            cerrar(); actual = None
            tipo = {"LIBRO": "libro", "TÍTULO": "titulo", "CAPÍTULO": "capitulo"}[m.group(1)]
            i += 1
            nombre = []
            while i < len(cuerpo) and negrita(cuerpo[i], cursiva=False) and not encabezado(cuerpo[i]) \
                    and not RE_VACIO.match(cuerpo[i]["t"].strip()):
                nombre.append(cuerpo[i]["t"].strip())
                i += 1
            nodo = {"tipo": tipo, "rotulo": t, "titulo": " ".join(nombre), "hijos": []}
            while pila and NIVEL[pila[-1]["tipo"]] >= NIVEL[tipo]:
                pila.pop()
            contenedor().append(nodo)
            pila.append(nodo)
            continue
        m = RE_SECC.match(t)
        if m and negrita(ln, cursiva=True):
            cerrar(); actual = None
            nombre = [m.group(2)]
            i += 1
            while i < len(cuerpo) and negrita(cuerpo[i], cursiva=True) and not RE_SECC.match(cuerpo[i]["t"]):
                nombre.append(cuerpo[i]["t"].strip())
                i += 1
            nodo = {"tipo": "seccion", "rotulo": "Sección " + m.group(1), "titulo": " ".join(nombre).strip(),
                    "hijos": []}
            while pila and NIVEL[pila[-1]["tipo"]] >= NIVEL["seccion"]:
                pila.pop()
            contenedor().append(nodo)
            pila.append(nodo)
            continue
        m = RE_SUBSECC.match(t)
        if m and ln["x"] > X_IZQ + 5 and solo_estilo(ln, ("",)):
            cerrar(); actual = None
            nombre = [m.group(2)]
            i += 1
            while i < len(cuerpo) and not encabezado(cuerpo[i]) and solo_estilo(cuerpo[i], ("",)) \
                    and cuerpo[i]["x"] > X_IZQ + 5:
                nombre.append(cuerpo[i]["t"].strip())
                i += 1
            nodo = {"tipo": "subseccion", "rotulo": "Subsección " + m.group(1), "titulo": " ".join(nombre).strip(),
                    "hijos": []}
            while pila and NIVEL[pila[-1]["tipo"]] >= NIVEL["subseccion"]:
                pila.pop()
            contenedor().append(nodo)
            pila.append(nodo)
            continue
        e = encabezado(ln)
        if e:
            cerrar()
            k, rot, epi = e
            i += 1
            # El epígrafe puede seguir en negrita en las líneas siguientes.
            while epi and i < len(cuerpo) and abs(cuerpo[i]["x"] - X_IZQ) < 1.5 and \
                    not encabezado(cuerpo[i]) and solo_estilo(cuerpo[i], ("b", "i", "bi")):
                epi += ("" if epi.endswith("-") and not epi.endswith(" -") else " ") + cuerpo[i]["t"].strip()
                i += 1
            if k in articulos:
                avisos.append(f"{rot}: aparece dos veces (pág. {ln['p']})")
                k = k + f" (pág. {ln['p']})"
            if k[:2] in GRUPOS and (not pila or pila[0].get("tipo") != "grupo" or pila[0]["clave"] != k[:2]):
                pila = [{"tipo": "grupo", "rotulo": "", "titulo": GRUPOS[k[:2]], "hijos": [], "clave": k[:2]}]
                estructura.append(pila[0])
            articulos[k] = {"rotulo": rot, "titulo": epi.strip(), "texto_literal": "",
                            "ruta": [GRUPOS[k[:2]]] if k[:2] in GRUPOS and pila and pila[0]["tipo"] == "grupo"
                            else ruta()}
            contenedor().append({"tipo": "articulo", "clave": k})
            orden.append(k)
            actual = [k, [], []]
            continue
        if actual is None:
            if t:
                avisos.append(f"Línea fuera de artículo (pág. {ln['p']}): «{t[:70]}»")
        elif es_nota(ln):
            actual[2].append(ln)
        else:
            actual[1].append(ln)
        i += 1
    cerrar()
    for n in estructura:
        n.pop("clave", None) if n.get("tipo") == "grupo" else None
    return fecha, notas_generales, articulos, estructura, orden, avisos


def unir_preambulo(lineas):
    out = []
    for ln in lineas:
        t = ln["t"].strip()
        if re.match(r"^Artículo \dº\.$", t) or t in ("ALFONSO", "Vengo en decretar lo siguiente:") or \
                t.startswith("El Ministro de") or t.isupper():
            out.append(t)
        elif not out or ln["x"] > X_IZQ + 5:
            out.append(t)
        elif out[-1].endswith("-") and not out[-1].endswith(" -"):
            out[-1] += t
        else:
            out[-1] += " " + t
    return out


# ================================================================ control
def base_num(k):
    m = re.match(r"^(\d+)", k)
    return int(m.group(1)) if m else None


def controles(articulos, orden, estructura, lineas):
    ctrl = {}
    arts = [k for k in orden if base_num(k) is not None]
    cubiertos = set()
    for k in arts:
        m = re.match(r"^(\d+) a (\d+)$", k)
        if m:
            cubiertos.update(range(int(m.group(1)), int(m.group(2)) + 1))
        else:
            cubiertos.add(base_num(k))
    maximo = max(cubiertos)
    ctrl["huecos_numeracion"] = [n for n in range(1, maximo + 1) if n not in cubiertos]
    nums = [base_num(k) for k in arts]
    ctrl["fuera_de_orden"] = [arts[j] for j in range(1, len(nums)) if nums[j] < nums[j - 1]]
    ctrl["vacios"] = [k for k in orden if RE_VACIO.match(articulos[k]["texto_literal"].strip() or "x")]
    ctrl["sin_texto"] = [k for k in orden if not articulos[k]["texto_literal"].strip()]
    ctrl["muy_cortos"] = [k for k in orden if 0 < len(articulos[k]["texto_literal"]) < 25
                          and k not in ctrl["vacios"]]
    # Rótulos del índice del PDF (págs. 1-6) frente a los encontrados en el cuerpo.
    indice = []
    for ln in lineas:
        if ln["p"] < CFG["pag_cuerpo"] and not es_cabecera_pie(ln):
            t = re.sub(r"\s*(\. ?)+\s*\d+$", "", ln["t"]).strip()
            if re.match(r"^(LIBRO|TÍTULO|Capítulo|CAPÍTULO|Sección|Subsección) ", t):
                indice.append(t)
    encontrados = []

    def rec(nodos):
        for n in nodos:
            if n["tipo"] in NIVEL:
                encontrados.append(n)
                rec(n["hijos"])
    rec(estructura)
    ctrl["rotulos_indice"] = len(indice)
    ctrl["rotulos_cuerpo"] = len(encontrados)
    norm = lambda s: re.sub(r"[^a-z0-9ñ]", "", s.lower())
    cuerpo_norm = {norm(n["rotulo"] + n["titulo"]) for n in encontrados}
    # Las líneas del índice pueden venir cortadas: basta con que el rótulo del cuerpo empiece igual.
    ctrl["indice_no_encontrado"] = [t for t in indice
                                    if not any(c.startswith(norm(t)) for c in cuerpo_norm)]
    ctrl["n_articulos"] = len(arts)
    ctrl["n_disposiciones"] = len([k for k in orden if base_num(k) is None])
    ctrl["con_notas_boe"] = len([k for k in orden if articulos[k].get("notas_boe")])
    ctrl["con_destacado"] = [k for k in orden if articulos[k].get("destacado")]
    return ctrl


def contrastar(datos):
    """Segunda lectura independiente del PDF (pdftotext) y comparación palabra por palabra."""
    import difflib
    import shutil
    import subprocess
    if not shutil.which("pdftotext"):
        return None
    raw = subprocess.run(["pdftotext", "-f", str(CFG["pag_cuerpo"]), PDF, "-"], capture_output=True, text=True).stdout
    quitar = ("BOLETÍN OFICIAL DEL ESTADO", "LEGISLACIÓN CONSOLIDADA", "TEXTO CONSOLIDADO")
    lin = [l for l in raw.split("\n") if l.strip() not in quitar and not re.match(r"^Página \d+$", l.strip())
           and not l.startswith("Última modificación")
           and not l.startswith("Este documento es de carácter informativo")]
    w1 = re.findall(r"[\wºª]+", " ".join(lin))
    A = datos["articulos"]
    seq = [datos["ley"]["nota_general_boe"], A["preambulo"]["texto_literal"]] + ([CFG["fin_pre"]] if CFG["saltar_fin"] else [])

    def rec(nodos):
        for n in nodos:
            if n["tipo"] == "articulo":
                a = A[n["clave"]]
                seq.extend([a["rotulo"], a["titulo"], a["texto_literal"]] + a.get("notas_boe", []))
            else:
                if n["tipo"] != "grupo":
                    seq.extend([n["rotulo"], n["titulo"]])
                rec(n["hijos"])
    rec(datos["estructura"][1:])
    w2 = re.findall(r"[\wºª]+", " ".join(seq))
    difs = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, w1, w2, autojunk=False).get_opcodes():
        if op != "equal":
            difs.append({"pdftotext": " ".join(w1[max(0, i1 - 4):i2 + 4]),
                         "extraido": " ".join(w2[max(0, j1 - 4):j2 + 4])})
    return {"palabras_pdftotext": len(w1), "palabras_extraidas": len(w2), "diferencias": difs}


def escribir_informe(ley, ctrl, avisos, contraste):
    with open(os.path.join(DATOS, "informe_control.json"), "w", encoding="utf-8") as f:
        json.dump({"control": ctrl, "avisos": avisos, "contraste": contraste}, f, ensure_ascii=False, indent=1)
    L = [f"# Informe de control — {ley['abreviatura']} ({ley['boe']})", "",
         f"Fuente: `fuentes/{CFG['pdf']}` (texto consolidado; última modificación: {ley['fecha_version']}).",
         "Sin XML ni acceso a la API del BOE: extracción solo desde el PDF.", "",
         "## Recuento", "",
         f"- Encabezados de artículo extraídos: **{ctrl['n_articulos']}** (los rangos como «Artículos 48 a 50» cuentan como uno).",
         f"- Disposiciones: **{ctrl['n_disposiciones']}**.",
         f"- Sin contenido / derogados / anulados / suprimidos: {len(ctrl['vacios'])}.",
         f"- Con notas del BOE: {ctrl['con_notas_boe']}.",
         f"- Rótulos de estructura: {ctrl['rotulos_cuerpo']} en el cuerpo, {ctrl['rotulos_indice']} en el índice del PDF.", "",
         "## Posibles problemas", ""]

    def lista(tit, xs):
        L.append(f"- **{tit}:** " + (", ".join(map(str, xs)) if xs else "ninguno"))
    lista("Números que faltan en la secuencia 1…último", ctrl["huecos_numeracion"])
    lista("Artículos fuera de orden", ctrl["fuera_de_orden"])
    lista("Artículos sin texto", ctrl["sin_texto"])
    lista("Textos muy cortos (revisar)", ctrl["muy_cortos"])
    lista("Rótulos del índice no encontrados en el cuerpo", ctrl["indice_no_encontrado"])
    lista("Artículos con incisos resaltados en negrita por el BOE", ctrl["con_destacado"])
    L += ["", "## Contraste con una segunda lectura del PDF (pdftotext)", ""]
    if contraste is None:
        L.append("- No se ha podido hacer: falta `pdftotext`.")
    else:
        L.append(f"- Palabras: {contraste['palabras_extraidas']} extraídas frente a "
                 f"{contraste['palabras_pdftotext']} de pdftotext; tramos distintos: **{len(contraste['diferencias'])}**.")
        L.append("- Las diferencias suelen ser de maquetación (palabras con guion a final de línea, "
                 "orden de lectura de un epígrafe partido). Revisar cada una:")
        L.append("")
        L += [f"  - pdftotext: «{d['pdftotext']}» · extraído: «{d['extraido']}»" for d in contraste["diferencias"]]
    L += ["", "## Avisos de la extracción", ""] + ([f"- {a}" for a in avisos] or ["- Ninguno."])
    with open(os.path.join(DATOS, "informe_control.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    lineas = leer_lineas_pdf()
    fecha, notas_gen, articulos, estructura, orden, avisos = construir(lineas)
    if not fecha:
        raise SystemExit("No se encuentra la fecha de la versión consolidada en el PDF.")
    ley = dict(CFG["ley"], fecha_version=fecha, nota_general_boe="\n".join(notas_gen),
               aviso="Texto consolidado del BOE de carácter informativo, sin valor jurídico")
    ctrl = controles(articulos, orden, estructura, lineas)
    datos = {"ley": ley, "estructura": estructura, "articulos": articulos,
             "plazos": [], "procedimientos": [], "recursos": [], "repaso": []}
    with open(os.path.join(DATOS, LEY + ".json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    contraste = contrastar(datos)
    escribir_informe(ley, ctrl, avisos, contraste)
    print(f"Versión consolidada: {fecha}")
    print(f"Artículos: {ctrl['n_articulos']} · disposiciones: {ctrl['n_disposiciones']} · "
          f"vacíos: {len(ctrl['vacios'])} · avisos: {len(avisos)}")
    print(f"Huecos: {ctrl['huecos_numeracion'][:30]} · fuera de orden: {ctrl['fuera_de_orden']}")
    print(f"Índice no encontrado: {ctrl['indice_no_encontrado']}")
    if contraste:
        print(f"Contraste con pdftotext: {len(contraste['diferencias'])} tramos distintos")


if __name__ == "__main__":
    main()
