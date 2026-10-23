#!/usr/bin/env python3
"""Crea el esqueleto del mapa procesal de la LJCA: ljca/datos/procedimientos.json.

Uso:  python3 scripts/esqueleto_ljca.py

Igual que scripts/esqueleto_lrjs.py (con las funciones de scripts/esqueleto_lecrim.py): cada fase
es un título, capítulo o sección del texto consolidado (ljca/datos/ljca.json), con su nombre y su
rango de artículos tal como salen del índice del BOE. Los bloques siguen el canon propuesto por
Claude en el Chat 5 (fuentes/canon_contenido.md › LJCA). Si un bloque ya está desarrollado (sin
"esqueleto": true), se conserva. El bloque «guia» (fichas transversales) no sale del índice: se
escribe a mano y solo se conserva.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esqueleto_lecrim import buscar, claves, claves_rango, fase, num, vacio  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "ljca", "datos")

G0, G1, G2, G3, G4 = ("Guía práctica", "Parte general", "Procedimientos", "Recursos", "Ejecución")

# (id, nombre del bloque, grupo, [(ruta de rótulos, expandir)]); None = bloque escrito a mano
BLOQUES = [
    ("guia", "Antes de interponer: plazos y escrito", G0, None),
    ("generales", "Jurisdicción, competencia y partes", G1,
     [(("TÍTULO I",), True), (("TÍTULO II",), True)]),
    ("objeto", "Objeto del recurso: qué se impugna y qué se pide", G1,
     [(("TÍTULO III",), True)]),
    ("ordinario", "Procedimiento ordinario (primera o única instancia)", G2,
     [(("TÍTULO IV", "CAPÍTULO I"), True)]),
    ("abreviado", "Procedimiento abreviado", G2,
     [(("TÍTULO IV", "CAPÍTULO II"), False)]),
    ("especiales", "Procedimientos especiales", G2,
     [(("TÍTULO V",), True)]),
    ("recursos", "Recursos contra resoluciones procesales", G3,
     [(("TÍTULO IV", "CAPÍTULO III"), True)]),
    ("ejecucion", "Ejecución de sentencias", G4,
     [(("TÍTULO IV", "CAPÍTULO IV"), False)]),
    ("comunes", "Plazos, medidas cautelares, incidentes y costas", G1,
     [(("TÍTULO VI",), True)]),
]

VISTA_PROCEDIMIENTOS = [
    {"grupo": "Antes de interponer", "items": ["guia"]},
    {"grupo": "Procedimientos", "items": ["ordinario", "abreviado", "especiales"]},
    {"grupo": "Medidas cautelares y costas", "items": ["comunes"]},
    {"grupo": "Ejecución", "items": ["ejecucion"]},
]
VISTA_RECURSOS = [
    {"grupo": "Medios de impugnación", "items": ["recursos"]},
]


def main():
    with open(os.path.join(DATOS, "ljca.json"), encoding="utf-8") as f:
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
        if partes is None:  # bloque a mano todavía sin hacer
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
            "id": pid, "nombre": nombre, "bloque": "ljca", "grupo": grupo, "esqueleto": True,
            "resumen": "Esqueleto del bloque: las fases son los títulos, capítulos y secciones del BOE. "
                       "Plazos, alternativas y preguntas, en preparación.",
            "ambito": {"corto": f"Arts. {nums[0]} a {nums[-1]}" if len(nums) > 1 else f"Art. {nums[0]}",
                       "texto": " · ".join(rutas), "articulos": [todos[0]], "literal": []},
            "revisado": False, "fases": fases})
    with open(destino, "w", encoding="utf-8") as f:
        json.dump({"procedimientos": procs, "externos": [], "vista_procedimientos": VISTA_PROCEDIMIENTOS,
                   "vista_recursos": VISTA_RECURSOS}, f, ensure_ascii=False, indent=1)
    print(f"Esqueleto LJCA: {len(procs)} bloques, {sum(len(p['fases']) for p in procs)} fases.")


if __name__ == "__main__":
    main()
