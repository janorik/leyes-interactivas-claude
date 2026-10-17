#!/usr/bin/env python3
"""Crea el esqueleto del mapa procesal de la LECrim: lecrim/datos/procedimientos.json.

Uso:  python3 scripts/esqueleto_lecrim.py

Cada bloque es una ruta de fases y cada fase es un título, capítulo o sección del propio
texto consolidado (lecrim/datos/lecrim.json): el nombre de la fase y su rango de artículos
salen literalmente del índice del BOE, no de memoria. No hay todavía plazos, alternativas
ni preguntas: se irán añadiendo bloque a bloque (y entonces la fase deja de ser «esqueleto»).

Si el archivo ya tiene un bloque desarrollado (sin "esqueleto": true), se conserva tal cual.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "lecrim", "datos")

# (id, nombre del bloque, grupo, [(ruta de rótulos, expandir)])
# expandir=True: cada hijo (capítulo/sección) es una fase; False: el nodo entero es una fase.
BLOQUES = [
    ("generales", "Disposiciones generales", "Libro I · Disposiciones generales",
     [(("LIBRO I",), True)]),
    ("inicio", "Denuncia, querella y Policía judicial", "Libro II · Sumario",
     [(("LIBRO II", "TÍTULO I"), False), (("LIBRO II", "TÍTULO II"), False), (("LIBRO II", "TÍTULO III"), False)]),
    ("instruccion", "Instrucción del sumario", "Libro II · Sumario",
     [(("LIBRO II", "TÍTULO IV"), True), (("LIBRO II", "TÍTULO V"), True)]),
    ("cautelares", "Citación, detención, prisión y libertad provisional", "Libro II · Sumario",
     [(("LIBRO II", "TÍTULO VI"), True), (("LIBRO II", "TÍTULO VII"), False)]),
    ("investigacion", "Medidas de investigación limitativas de derechos (art. 18 CE)", "Libro II · Sumario",
     [(("LIBRO II", "TÍTULO VIII"), True)]),
    ("fianzas", "Fianzas, embargos y responsabilidad civil", "Libro II · Sumario",
     [(("LIBRO II", "TÍTULO IX"), False), (("LIBRO II", "TÍTULO X"), False), (("LIBRO II", "TÍTULO X BIS"), False)]),
    ("conclusion", "Conclusión del sumario y sobreseimiento", "Libro II · Sumario",
     [(("LIBRO II", "TÍTULO XI"), True), (("LIBRO II", "TÍTULO XII"), False)]),
    ("juicio-oral", "Juicio oral", "Libro III · Juicio oral",
     [(("LIBRO III", "TÍTULO I"), False), (("LIBRO III", "TÍTULO II"), False), (("LIBRO III", "TÍTULO III"), True)]),
    ("abreviado", "Procedimiento abreviado", "Libro IV · Procedimientos especiales",
     [(("LIBRO IV", "TÍTULO II"), True)]),
    ("rapido", "Enjuiciamiento rápido de determinados delitos", "Libro IV · Procedimientos especiales",
     [(("LIBRO IV", "TÍTULO III"), True)]),
    ("especiales", "Otros procedimientos especiales", "Libro IV · Procedimientos especiales",
     [(("LIBRO IV", "TÍTULO I"), False), (("LIBRO IV", "TÍTULO III BIS"), False), (("LIBRO IV", "TÍTULO III TER"), True),
      (("LIBRO IV", "TÍTULO IV"), False), (("LIBRO IV", "TÍTULO V"), False), (("LIBRO IV", "TÍTULO VI"), False),
      (("LIBRO IV", "TÍTULO VII"), False)]),
    ("recursos", "Recursos de apelación, casación y revisión", "Libro V · Recursos",
     [(("LIBRO V", "TÍTULO I"), False), (("LIBRO V", "TÍTULO II", "CAPÍTULO I"), True),
      (("LIBRO V", "TÍTULO II", "CAPÍTULO II"), False), (("LIBRO V", "TÍTULO II", "CAPÍTULO III"), False),
      (("LIBRO V", "TÍTULO II", "CAPÍTULO IV"), False), (("LIBRO V", "TÍTULO III"), False)]),
    ("leves", "Juicio sobre delitos leves", "Libros VI y VII",
     [(("LIBRO VI",), False)]),
    ("ejecucion", "Ejecución de las sentencias", "Libros VI y VII",
     [(("LIBRO VII",), False)]),
]

# Leyes distintas de la LECrim que el usuario quiere ver en el mapa (solo nombre y enlace).
# El nombre sale del art. 846 bis a de la LECrim; número, fecha y referencia BOE: de memoria,
# anotados en PENDIENTES.md para que el usuario los compruebe.
EXTERNOS = [
    {"id": "jurado", "nombre": "Tribunal del Jurado", "grupo": "Libro IV · Procedimientos especiales",
     "texto": "El procedimiento ante el Tribunal del Jurado se regula en la "
              "[[Ley Orgánica 5/1995, de 22 de mayo, del Tribunal del Jurado|"
              "https://www.boe.es/buscar/act.php?id=BOE-A-1995-12095]]. "
              "La LECrim la nombra «Ley Orgánica del Tribunal del Jurado».",
     "articulos": ["846 bis a", "309 bis"]},
]


CORTO = {"especiales": "Libro IV, varios títulos"}


def claves_rango(est, rango):
    orden = [k for n in est for k in claves(n)]
    return orden[orden.index(rango[0]): orden.index(rango[1]) + 1]


# Pestañas «Procedimientos» y «Recursos»: qué bloques (o fases sueltas) se muestran y en qué grupo.
# Un elemento es el id de un bloque, {"proc", "fase"} para una fase concreta o {"externo"} para otra ley.
VISTA_PROCEDIMIENTOS = [
    {"grupo": "Sumario ordinario",
     "nota": "La ley lo reparte entre el Libro II (sumario) y el Libro III (juicio oral): se recorre en estos tres bloques, por orden.",
     "items": ["instruccion", "conclusion", "juicio-oral"]},
    {"grupo": "Procedimiento abreviado", "items": ["abreviado"]},
    {"grupo": "Enjuiciamiento rápido", "items": ["rapido"]},
    {"grupo": "Delitos leves", "items": ["leves"]},
    {"grupo": "Otros procedimientos", "items": [{"proc": "especiales", "fase": "especiales-803_bis_a"},
                                                {"externo": "jurado"}, "especiales"]},
]
VISTA_RECURSOS = [
    {"grupo": "Recursos contra sentencias", "items": ["recursos"]},
    {"grupo": "Recursos contra las resoluciones procesales (Libro I)",
     "items": [{"proc": "generales", "fase": "generales-216"}]},
]


def hijo(nodos, rotulo):
    for n in nodos:
        if n.get("rotulo") == rotulo:
            return n
    raise SystemExit(f"No encuentro «{rotulo}» en la estructura de la LECrim")


def buscar(estructura, ruta):
    nodos, n = estructura, None
    for r in ruta:
        n = hijo(nodos, r)
        nodos = n["hijos"]
    return n


def claves(n):
    if n["tipo"] == "articulo":
        return [n["clave"]]
    return [k for h in n["hijos"] for k in claves(h)]


def nombre_nodo(n):
    return n["titulo"] or n["rotulo"]


def num(k, ultimo=False):
    """«128 a 140» (rango del BOE) → 128 o 140, para escribir «arts. 118 a 140»."""
    partes = k.split(" a ") if " a " in k and k.split(" a ")[-1].isdigit() else [k]
    return partes[-1] if ultimo else partes[0]


def vacio(k, ley):
    return ley["articulos"][k]["texto_literal"].strip().startswith(("(Sin contenido", "(Derogad", "(Suprimid", "(Anulad"))


def fase(pid, n, padre=None):
    ks = claves(n)
    rot = (padre["rotulo"] + " · " if padre else "") + n["rotulo"]
    return {"id": f"{pid}-{len(ks) and ks[0]}".replace(" ", "_"),
            "fase": nombre_nodo(n),
            "subtitulo": f"{rot} · arts. {num(ks[0])} a {num(ks[-1], True)}" if num(ks[0]) != num(ks[-1], True)
            else f"{rot} · art. {num(ks[0])}",
            "descripcion": "", "articulos": [ks[0], ks[-1]] if len(ks) > 1 else ks,
            "rango": [ks[0], ks[-1]], "plazos": [], "ramas": [], "esqueleto": True}


def main():
    with open(os.path.join(DATOS, "lecrim.json"), encoding="utf-8") as f:
        ley = json.load(f)
    est = ley["estructura"]
    destino = os.path.join(DATOS, "procedimientos.json")
    previos = {}
    if os.path.exists(destino):
        with open(destino, encoding="utf-8") as f:
            previos = {p["id"]: p for p in json.load(f)["procedimientos"] if not p.get("esqueleto")}
    procs = []
    for pid, nombre, grupo, partes in BLOQUES:
        if pid in previos:  # bloque ya desarrollado: no se toca
            procs.append(previos[pid])
            continue
        fases, todos, rutas = [], [], []
        for ruta, expandir in partes:
            n = buscar(est, ruta)
            rutas.append(n["rotulo"] + (". " + n["titulo"] if n["titulo"] else ""))
            todos += claves(n)
            subs = [h for h in n["hijos"] if h["tipo"] != "articulo"] if expandir else []
            if subs:
                sueltos = [h for h in n["hijos"] if h["tipo"] == "articulo"]
                if sueltos:  # artículos colgados directamente del título, antes de sus capítulos
                    fases.append(fase(pid, {"tipo": "x", "rotulo": n["rotulo"], "titulo": n["titulo"],
                                            "hijos": sueltos}))
                fases += [fase(pid, h, n) for h in subs]
            else:
                fases.append(fase(pid, n))
        # Fuera las fases que solo contienen artículos derogados o sin contenido.
        fases = [f for f in fases if not all(vacio(k, ley) for k in claves_rango(est, f["rango"]))]
        procs.append({
            "id": pid, "nombre": nombre, "bloque": "lecrim", "grupo": grupo, "esqueleto": True,
            "resumen": "Esqueleto del bloque: las fases son los títulos, capítulos y secciones del BOE. "
                       "Plazos, alternativas y preguntas, en preparación.",
            "ambito": {"corto": CORTO.get(pid, f"Arts. {num(todos[0])} a {num(todos[-1], True)}"), "texto": " · ".join(rutas),
                       "articulos": [todos[0]], "literal": []},
            "revisado": False, "fases": fases})
    with open(destino, "w", encoding="utf-8") as f:
        json.dump({"procedimientos": procs, "externos": EXTERNOS, "vista_procedimientos": VISTA_PROCEDIMIENTOS,
                   "vista_recursos": VISTA_RECURSOS}, f, ensure_ascii=False, indent=1)
    print(f"Esqueleto: {len(procs)} bloques, {sum(len(p['fases']) for p in procs)} fases; "
          f"{len(EXTERNOS)} ley(es) externa(s) enlazada(s).")


if __name__ == "__main__":
    main()
