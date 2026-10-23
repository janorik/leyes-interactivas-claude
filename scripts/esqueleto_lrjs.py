#!/usr/bin/env python3
"""Crea el esqueleto del mapa procesal de la LRJS: lrjs/datos/procedimientos.json.

Uso:  python3 scripts/esqueleto_lrjs.py

Igual que scripts/esqueleto_lecrim.py (y con sus mismas funciones): cada fase es un título,
capítulo o sección del propio texto consolidado (lrjs/datos/lrjs.json), con su nombre y su
rango de artículos tal como salen del índice del BOE. Sin plazos, alternativas ni preguntas:
se añaden bloque a bloque. Si un bloque ya está desarrollado (sin "esqueleto": true), se conserva.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esqueleto_lecrim import buscar, claves, claves_rango, fase, num, vacio  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "lrjs", "datos")

L1, L2, L3, L4 = "LIBRO PRIMERO", "LIBRO SEGUNDO", "LIBRO TERCERO", "LIBRO CUARTO"
G1, G2, G3, G4 = ("Libro I · Parte general", "Libro II · Proceso ordinario y modalidades",
                  "Libro III · Medios de impugnación", "Libro IV · Ejecución")

# (id, nombre del bloque, grupo, [(ruta de rótulos, expandir)])
BLOQUES = [
    ("generales", "Jurisdicción, competencia y partes", G1,
     [((L1, "TÍTULO I"), True), ((L1, "TÍTULO II"), True)]),
    ("acumulacion", "Acumulación de acciones, procesos, recursos y ejecuciones", G1,
     [((L1, "TÍTULO III", "CAPÍTULO I"), True), ((L1, "TÍTULO III", "CAPÍTULO II"), False)]),
    ("actos", "Actos procesales, resoluciones y comunicaciones", G1,
     [((L1, "TÍTULO IV"), True), ((L1, "TÍTULO VI"), False)]),
    ("evitacion", "Conciliación o mediación previa y vía administrativa", G1,
     [((L1, "TÍTULO V"), True)]),
    ("ordinario", "Proceso ordinario y monitorio", G2,
     [((L2, "TÍTULO I", "CAPÍTULO I"), True), ((L2, "TÍTULO I", "CAPÍTULO II"), True),
      ((L2, "TÍTULO II", "CAPÍTULO I"), False)]),
    ("despido", "Despido, sanciones y extinción del contrato", G2,
     [((L2, "TÍTULO II", "CAPÍTULO II"), True), ((L2, "TÍTULO II", "CAPÍTULO IV"), True),
      ((L2, "TÍTULO II", "CAPÍTULO III"), False)]),
    ("condiciones", "Condiciones de trabajo y materia electoral", G2,
     [((L2, "TÍTULO II", "CAPÍTULO V"), True)]),
    ("seguridad-social", "Seguridad Social, procedimiento de oficio y actos administrativos", G2,
     [((L2, "TÍTULO II", "CAPÍTULO VI"), False), ((L2, "TÍTULO II", "CAPÍTULO VII"), True)]),
    ("colectivos", "Conflictos colectivos, convenios y estatutos sindicales", G2,
     [((L2, "TÍTULO II", "CAPÍTULO VIII"), False), ((L2, "TÍTULO II", "CAPÍTULO IX"), False),
      ((L2, "TÍTULO II", "CAPÍTULO X"), False)]),
    ("tutela", "Tutela de los derechos fundamentales", G2,
     [((L2, "TÍTULO II", "CAPÍTULO XI"), False)]),
    ("rebelde", "Audiencia al demandado rebelde", G2,
     [((L2, "TÍTULO III"), False)]),
    # La audiencia al rebelde (Libro II) figura en su sitio («rebelde») y también aquí, por ser un medio de
    # impugnación (decisión del usuario, Chat 4).
    ("recursos", "Recursos, audiencia al rebelde y revisión", G3,
     [((L3, "TÍTULO I"), False), ((L3, "TÍTULO II"), False), ((L3, "TÍTULO III"), False),
      ((L3, "TÍTULO IV"), False), ((L3, "TÍTULO V"), False), ((L2, "TÍTULO III"), False),
      ((L3, "TÍTULO VI"), False)]),
    ("ejecucion", "Ejecución de sentencias", G4,
     [((L4, "TÍTULO I", "CAPÍTULO I"), True), ((L4, "TÍTULO I", "CAPÍTULO II"), True),
      ((L4, "TÍTULO I", "CAPÍTULO III"), False), ((L4, "TÍTULO I", "CAPÍTULO IV"), False)]),
    ("provisional", "Ejecución provisional", G4,
     [((L4, "TÍTULO II"), True)]),
]

VISTA_PROCEDIMIENTOS = [
    {"grupo": "Antes del juicio", "items": ["evitacion"]},
    {"grupo": "Proceso ordinario", "items": ["ordinario"]},
    {"grupo": "Despido y extinción", "items": ["despido"]},
    {"grupo": "Modalidades procesales", "items": ["condiciones", "seguridad-social", "colectivos", "tutela"]},
    {"grupo": "Ejecución", "items": ["ejecucion", "provisional"]},
]
VISTA_RECURSOS = [
    {"grupo": "Medios de impugnación", "items": ["recursos"]},
]


def main():
    with open(os.path.join(DATOS, "lrjs.json"), encoding="utf-8") as f:
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
                if sueltos:
                    fases.append(fase(pid, {"tipo": "x", "rotulo": n["rotulo"], "titulo": n["titulo"],
                                            "hijos": sueltos}))
                fases += [fase(pid, h, n) for h in subs]
            else:
                fases.append(fase(pid, n))
        fases = [f for f in fases if not all(vacio(k, ley) for k in claves_rango(est, f["rango"]))]
        nums = sorted({int(num(k)) for k in todos if num(k).isdigit()})
        procs.append({
            "id": pid, "nombre": nombre, "bloque": "lrjs", "grupo": grupo, "esqueleto": True,
            "resumen": "Esqueleto del bloque: las fases son los títulos, capítulos y secciones del BOE. "
                       "Plazos, alternativas y preguntas, en preparación.",
            "ambito": {"corto": f"Arts. {nums[0]} a {nums[-1]}" if len(nums) > 1 else f"Art. {nums[0]}",
                       "texto": " · ".join(rutas), "articulos": [todos[0]], "literal": []},
            "revisado": False, "fases": fases})
    with open(destino, "w", encoding="utf-8") as f:
        json.dump({"procedimientos": procs, "externos": [], "vista_procedimientos": VISTA_PROCEDIMIENTOS,
                   "vista_recursos": VISTA_RECURSOS}, f, ensure_ascii=False, indent=1)
    print(f"Esqueleto LRJS: {len(procs)} bloques, {sum(len(p['fases']) for p in procs)} fases.")


if __name__ == "__main__":
    main()
