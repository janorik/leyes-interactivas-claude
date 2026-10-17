# LEYES INTERACTIVAS — NOrlexia LEGALTECH

## Quién es el usuario y cómo trabajar con él
- Letrado colegiado no ejerciente (no usar el término "abogado" para referirse a él). Usa la app para repaso personal y práctica profesional.
- No es programador. Trabaja desde el móvil (Android): app Claude (pestaña Code) y GitHub desde el navegador.
- Explica cada paso que tenga que hacer él de forma breve, concreta y comprobable.
- Responde siempre en español.
- Etiqueta cada dato jurídico o técnico como **Verificable** o **No verificable**.
- Si una petición admite varias interpretaciones, pregunta; no elijas por él.
- Si el usuario se equivoca, dile "estás equivocado" y explica por qué. Si te corrige con razón, di "tienes razón" y corrige.
- No suenes seguro de algo que no lo estás. Cierra cada respuesta con tu nivel de certeza.

## Objetivo
Una app interactiva por cada ley para estudiarla, repasarla y consultarla a diario. La primera es la Ley de Enjuiciamiento Civil (LEC). Después vendrán LECrim, LRJS, Estatuto de los Trabajadores y otras.

## Estructura del repositorio
```
leyes-interactivas-claude/
├── CLAUDE.md            ← este archivo
├── index.html           ← portada que enlaza todas las leyes (fase F7)
├── assets/
│   └── logo.*           ← logo NOrlexia subido por el usuario
├── fuentes/
│   └── LEC_BOE-A-2000-323.pdf   ← texto consolidado del BOE
├── scripts/
│   └── (scripts de extracción PDF → JSON)
└── lec/
    ├── index.html       ← app de la LEC, autocontenida
    └── datos/           ← JSON intermedios generados por los scripts
```
- Cada ley vive en su propia carpeta con su propio `index.html` autocontenido e independiente.
- La portada (`/index.html`) solo enlaza a cada ley. No contiene datos de ninguna.
- Rutas siempre relativas, para que funcione en GitHub Pages y abriendo el archivo en local.
- Si el PDF o el XML del BOE o el logo están en la raíz del repositorio, muévelos a `fuentes/` y `assets/` antes de empezar (renombra el PDF a `LEC_BOE-A-2000-323.pdf` y el XML a `LEC_BOE-A-2000-323.xml`).

## Fuente única
- Solo el texto consolidado del BOE subido en `fuentes/` (Ley 1/2000, de 7 de enero, BOE-A-2000-323), versión vigente.
- Si existe `LEC_BOE-A-2000-323.xml` (descargado por el usuario de la API del BOE, en la raíz o en `fuentes/`), muévelo a `fuentes/` y úsalo como fuente principal. Contiene todas las versiones de cada bloque: usa solo la última. Contrasta con el PDF.
- Si no existe el XML, antes de extraer del PDF intenta descargar el texto estructurado de la API de datos abiertos del BOE: `https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/BOE-A-2000-323/texto`. Consulta antes su documentación técnica (`https://boe.es/datosabiertos/documentos/APIconsolidada.pdf`) para las cabeceras necesarias: una prueba sin cabeceras devolvió error 400. Ese endpoint devuelve todas las versiones de cada bloque; usa solo la última. Si funciona, guárdalo en `fuentes/` y úsalo como base, contrastando con el PDF. Si no hay acceso de red, usa solo el PDF y díselo al usuario.
- Prohibido completar o reconstruir texto legal de memoria. Si algo no está en el PDF, dilo.
- Extrae del PDF la fecha de la versión consolidada. Si no la encuentras, pregunta al usuario.
- La app muestra esa fecha y el aviso: "Texto consolidado del BOE de carácter informativo, sin valor jurídico".
- Solo versión vigente. No se comparan reformas.
- **Otras leyes citadas.** Cuando la LEC (u otra ley de la app) remita a una ley distinta, o el contenido elaborado necesite mencionarla, no se escribe «otra ley»: se pone «se regula en la [nombre de la ley]» con un enlace a su texto consolidado en el BOE (`https://www.boe.es/buscar/act.php?id=BOE-A-…`). Formato en los JSON: `[[Nombre de la ley|URL del BOE]]` dentro de `descripcion` o `aviso`; `scripts/insertar_datos.py` rechaza enlaces mal formados. No se copia el texto de esa otra ley. Si el nombre, la fecha o la referencia BOE no salen del texto consolidado de la app, se anota en `PENDIENTES.md` para que el usuario los compruebe.
- **Si una regla impide algo útil, avisa y pregunta.** Cuando una regla de este archivo te lleve a dejar fuera algo que al usuario le serviría (por ejemplo, nombrar o enlazar otra ley), no lo omitas en silencio: díselo, explica qué regla lo impide y pregúntale qué prefiere.

## Alcance de la LEC
**Texto literal:** la LEC completa en el árbol y el buscador. Se extrae por script, así no quedan huecos cuando un artículo remite a otro.

**Contenido elaborado** (esquemas, plazos, recursos, repaso), solo para estos bloques:
- Núcleo:
  - disposiciones generales (competencia, partes, postulación, actuaciones procesales, plazos, notificaciones, costas)
  - juicio ordinario
  - juicio verbal
  - prueba
  - recursos
  - monitorio
  - ejecución y embargo
  - medidas cautelares
- Procesos especiales:
  - familia y capacidad
  - división de herencia
  - juicio cambiario
  - ejecución hipotecaria

Los rangos de artículos de cada bloque se obtienen del propio PDF, no de memoria.

## Arquitectura técnica
- `lec/index.html`: un único archivo HTML+CSS+JS autocontenido, sin servidor y sin dependencias externas obligatorias. Funciona sin conexión.
- Los datos van embebidos en el HTML como JSON, con un esquema común reutilizable para todas las leyes:
```
ley:            {id, nombre, boe, fecha_version}
estructura:     [libro > título > capítulo > sección > artículos]
articulos:      {num: {titulo, texto_literal, ruta}}
plazos:         [{id, acto, plazo, computo, articulos, bloque, revisado}]
procedimientos: [{id, nombre, bloque, fases: [{fase, descripcion, articulos}], revisado}]
recursos:       [{id, recurso, contra_que, plazo, organo, articulos, revisado}]
repaso:         [{id, pregunta, respuesta, articulos, origen, revisado}]
```
- El texto de los artículos se extrae siempre con un script (en `scripts/`), nunca copiándolo a mano.
- Un script inserta el JSON final dentro de `lec/index.html`.
- Publicación con GitHub Pages desde la rama principal, carpeta raíz.

## Vistas de la app LEC
Enfoque acordado con el usuario: app para **aprender**, no solo para leer la ley. El centro es el **mapa procesal**.
1. **Procesos** (pantalla de inicio): cada procedimiento como ruta de fases en vista de conjunto. Cada fase abre una ficha con: qué ocurre, plazos (con la frase literal del artículo), alternativas desplegables («¿y si no contesta?»), pregunta «Ponte a prueba», conexiones y enlaces a otros procesos. En móvil la ficha se abre como hoja inferior; en ordenador, como panel lateral.
2. **Ley**: árbol navegable (Libros > Títulos > Capítulos > Secciones > Artículos) con el texto literal.
3. **Buscar**: por número de artículo, por texto de la ley y por fases y plazos del mapa.
4. **Repaso**: tarjetas generadas de preguntas, alternativas y plazos, con progreso guardado en local.
5. **Recursos**: selector por resolución (qué recurso cabe, plazo y órgano, con frase literal), fichas de cada recurso y test de opción múltiple.
6. **Notas**: marcadores y notas personales en artículos, fases y recursos, guardados en el almacenamiento local del navegador. No se sincronizan entre el móvil y el PC; para pasarlos hay copia de seguridad (descargar / importar archivo JSON).

Datos del mapa: `lec/datos/procedimientos.json` (contenido elaborado, `revisado: false`). Cada plazo, alternativa y respuesta lleva una frase `literal`; `scripts/insertar_datos.py` comprueba que esa frase está en el artículo citado y, si no, no publica.

Todo artículo citado en cualquier vista es un enlace que abre su texto literal.

## Reglas anti-error (obligatorias)
- Todo plazo, fase, recurso o tarjeta lleva el artículo o artículos en que se basa.
- Todo contenido elaborado (no literal) se crea con `revisado: false`.
- La app lo muestra con la etiqueta "Pendiente de revisión" hasta que el usuario lo valide.
- Si el texto legal admite varias lecturas, o un plazo depende de supuestos, no elijas: anótalo y pregunta.
- Nunca presentes un plazo como seguro si no sale literalmente del artículo citado.
- La calculadora de plazos con calendario (días hábiles, agosto, festivos) NO se hace ahora. Es una segunda parte.

## Diseño
- Paleta NOrlexia: verde `#0d4a45`, oro `#c9a04a`, crema `#f5f0e8`.
- Logo de `assets/`, en la cabecera.
- Botón de modo claro/oscuro, recordado en local.
- Diseño adaptado a móvil (prioridad) y a ordenador. Texto legible y zoom cómodo.

## Pendientes
Las dudas de interpretación y los puntos a revisar se anotan en `PENDIENTES.md` (el usuario los repasará al final). No se elige una interpretación: se anota y se sigue. Un único `PENDIENTES.md` para todas las leyes, con una sección por ley (`## LEC`, `## LECrim`…). Cada duda de interpretación lleva una **propuesta** argumentada con artículos (No verificable hasta que el usuario la confirme) y un hueco «Tu respuesta».

## Fases de trabajo
Una fase cada vez. Al cerrar cada fase:
- haz commit con un mensaje claro;
- entrega un resumen corto;
- da la lista de lo que el usuario debe revisar.

No empieces la siguiente fase sin su visto bueno.

- **F1** — Extracción de la LEC completa del PDF a JSON. App base con:
  - diseño (paleta, logo, modo claro/oscuro);
  - árbol navegable;
  - buscador;
  - fecha de versión y aviso del BOE.
  - Incluye un informe de control: número de artículos extraídos y artículos con posibles problemas de extracción.
- **F2** — Mapa procesal (prototipo hecho): juicio ordinario, juicio verbal y monitorio, con plazos, alternativas y repaso. Pendiente de revisión del usuario.
- **F3** — Mapa procesal: ejecución y embargo (arts. 517-680, sin la hipotecaria) y medidas cautelares (arts. 721-747). Hecha; pendiente de revisión del usuario.
- **F4** — Mapa de recursos (`lec/datos/recursos.json`): selector «¿qué recurso cabe?» por resolución, fichas de cada recurso y test interactivo. Hecha; pendiente de revisión del usuario.
- **F5** — Marcadores y notas (☆ y ✎ en artículos, fases y recursos; pestaña «Notas»; búsqueda en notas; copia de seguridad descargable e importable para pasar del móvil al PC). Hecha.
- **F6** — Procesos especiales: nulidad, separación y divorcio (arts. 748-777), medidas judiciales de apoyo (756-763), división de herencia (782-789), cambiario (819-827) y ejecución hipotecaria (681-698). Hecha; pendiente de revisión del usuario.
- **Ampliación (hecha)** — Procesos añadidos a petición del usuario: desahucio por falta de pago (arts. 22.4, 437-441, 447, 449, 549), filiación (764-768), protección de menores y adopción (778 bis-ter, 779-781), sustracción internacional de menores (778 quáter-sexies), liquidación del régimen económico matrimonial (806-811) e intervención y administración del caudal hereditario (790-805). Pendientes de revisión del usuario.
- **Ampliación 2 (hecha)** — Bloques del núcleo que faltaban: disposiciones generales (competencia, arts. 36-67; partes y postulación, 6-35; actuaciones, plazos, comunicaciones y nulidad, 129-247; costas, 241-246 y 394-398) y prueba (arts. 217 y 281-386). Pendientes de revisión del usuario.
- **F7** — Portada (`/index.html`) que enlaza a cada ley, preparada para añadir LECrim, LRJS y ET. Hecha: se genera con `python3 scripts/generar_portada.py` a partir de `scripts/leyes.json`. Para añadir una ley: crear su carpeta con su `index.html` y poner su estado a «disponible» en `leyes.json`. Los enlaces apuntan a `carpeta/index.html` para que funcionen también en local.
- **Segunda parte** — Calculadora de plazos con calendario.

## LECrim
- Fuente: `fuentes/LECrim_BOE-A-1882-6036.pdf` (Real Decreto de 14 de septiembre de 1882, BOE-A-1882-6036), texto consolidado con última modificación de 09 de abril de 2026. Sin XML: se extrae solo del PDF con `python3 scripts/extraer_lecrim.py`, que lo contrasta con pdftotext y escribe `lecrim/datos/informe_control.md`.
- App: `lecrim/index.html`, generada con `python3 scripts/insertar_datos.py lecrim`. La app es la misma para todas las leyes: `lec/index.html` es la plantilla y el script la copia con los datos de cada ley. Una mejora de la app se hace en `lec/index.html` y se regeneran todas.
- Mientras una ley no tenga mapa procesal, la app abre en «Ley» y oculta «Procesos» y «Repaso».
- **F1 LECrim (hecha):** texto literal completo (1059 artículos y 10 disposiciones), árbol, buscador, notas y portada. Pendiente de revisión del usuario.
- **Contenido elaborado de la LECrim:** bloques por decidir con el usuario a partir del índice real del PDF. No empezar sin su visto bueno.
