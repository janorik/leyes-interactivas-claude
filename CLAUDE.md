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
- **Memoria del proyecto en este archivo.** Cada chat empieza sin recordar los anteriores. Cuando en un chat se acuerde algo nuevo (una decisión del usuario, una forma de trabajar, un bloque hecho, dónde está algo), anótalo aquí en el mismo commit, de forma breve y en su sección. Las dudas jurídicas van a `PENDIENTES.md`, no aquí.
- **Forma de trabajar con GitHub (decisión del usuario, 21-10-2026).** Un solo chat cada vez para este proyecto. Claude hace el código, lo prueba, anota lo acordado aquí y sube copia a la rama del chat sin preguntar (no se publica). **Antes de unir a la rama principal (lo que se publica en la web), Claude pregunta siempre al usuario**; con su «sí», crea la PR y la une él mismo con las herramientas de GitHub, sin que el usuario entre en GitHub. Antes de unir, trae la rama principal (`git fetch origin main`) y, si ha cambiado, la integra y regenera lo necesario. Si hay una PR abierta de otro chat, Claude la integra o avisa al usuario; no la deja olvidada. Al entregar, da el enlace de la PR y la dirección para verlo con `?v=N`. **Número de versión (pedido por el usuario, 22-10-2026):** `scripts/version.json` guarda la versión publicada; se muestra **solo en la portada**, al final del aviso («Versión N», sin fecha ni en las leyes, por decisión del usuario). Antes de cada publicación, Claude sube el número en 1, regenera la portada y usa ese mismo N en `?v=N`.

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
- **Dónde está cada cosa (además del árbol):** `PENDIENTES.md` (dudas de todas las leyes); `lecrim/` y `lrjs/` (app y datos de cada ley, igual que `lec/`); `scripts/extraer_lec.py` (LEC, desde el XML) y `scripts/extraer_ley.py <ley>` (LECrim y LRJS, desde el PDF; lo propio de cada ley está en su diccionario `LEYES`) (texto literal → `<ley>/datos/<ley>.json` e `informe_control.md`); `scripts/esqueleto_lecrim.py` (esqueleto del mapa de la LECrim); `scripts/insertar_datos.py <ley>` (valida y mete los datos en `<ley>/index.html`); `scripts/generar_portada.py` + `scripts/leyes.json` (portada; `leyes.json` también da el nombre corto y el título del mapa de cada ley). `*/datos/lineas_pdf.json` es caché y no se sube.

## Fuente única
- Solo el texto consolidado del BOE subido en `fuentes/` (Ley 1/2000, de 7 de enero, BOE-A-2000-323), versión vigente.
- Si existe `LEC_BOE-A-2000-323.xml` (descargado por el usuario de la API del BOE, en la raíz o en `fuentes/`), muévelo a `fuentes/` y úsalo como fuente principal. Contiene todas las versiones de cada bloque: usa solo la última. Contrasta con el PDF.
- Si no existe el XML, antes de extraer del PDF intenta descargar el texto estructurado de la API de datos abiertos del BOE: `https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/BOE-A-2000-323/texto`. Consulta antes su documentación técnica (`https://boe.es/datosabiertos/documentos/APIconsolidada.pdf`) para las cabeceras necesarias: una prueba sin cabeceras devolvió error 400. Ese endpoint devuelve todas las versiones de cada bloque; usa solo la última. Si funciona, guárdalo en `fuentes/` y úsalo como base, contrastando con el PDF. Si no hay acceso de red, usa solo el PDF y díselo al usuario.
- Prohibido completar o reconstruir texto legal de memoria. Si algo no está en el PDF, dilo.
- Extrae del PDF la fecha de la versión consolidada. Si no la encuentras, pregunta al usuario.
- La app muestra esa fecha y el aviso: "Texto consolidado del BOE de carácter informativo, sin valor jurídico".
- Solo versión vigente. No se comparan reformas.
- **LEC, fuente usada:** `fuentes/LEC_BOE-A-2000-323.xml` es una exportación a XML del PDF consolidado hecha por el usuario (el XML original del BOE que subió primero era el texto de 2000 y se descartó); se contrasta palabra por palabra con el PDF. Versión consolidada: 07 de octubre de 2026.
- **Red desde la nube:** este entorno no llega a boe.es, google.com ni janorik.github.io (bloqueados por el proxy). Las comprobaciones en el BOE (por ejemplo, los enlaces a otras leyes) las hace el usuario; se anotan en `PENDIENTES.md`.
- **Otras leyes citadas.** Cuando la LEC (u otra ley de la app) remita a una ley distinta, o el contenido elaborado necesite mencionarla, no se escribe «otra ley»: se pone «se regula en la [nombre de la ley]» con un enlace a su texto consolidado en el BOE (`https://www.boe.es/buscar/act.php?id=BOE-A-…`). Formato en los JSON: `[[Nombre de la ley|URL del BOE]]` dentro de `descripcion` o `aviso`; `scripts/insertar_datos.py` rechaza enlaces mal formados. No se copia el texto de esa otra ley. Si el nombre, la fecha o la referencia BOE no salen del texto consolidado de la app, se anota en `PENDIENTES.md` para que el usuario los compruebe.
- **Remisiones desfasadas (criterio del usuario, 21-10-2026).** No se corrigen por analogía: se coteja el texto exacto de cada inciso remitente con el artículo de destino y se le da uno de tres estados en `PENDIENTES.md` (resuelta / resuelta con criterio interpretativo / pendiente de revisión individual).
- **Fuentes que aclaran la ley (decisión del usuario, 21-10-2026).** Además de la ley, se mencionan en las fichas (campo `aviso`) las fuentes que ayudan a entenderla, como se hizo con el Tribunal del Jurado: por ejemplo, la Circular 2/2025 de la Fiscalía General del Estado sobre las remisiones desfasadas tras la LO 1/2025. Se cita por su nombre; con enlace `[[Nombre|URL del BOE]]` solo si se conoce su referencia en el BOE (si no, se anota en `PENDIENTES.md`). No se copia su texto. Las aporta el usuario o salen del texto consolidado; Claude no las cita de memoria.
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
- Publicación con GitHub Pages desde la rama principal, carpeta raíz, con dominio propio (archivo `CNAME`): `https://leyes-interactivas.norlexia.es/` (portada) y `…/lec/index.html`, `…/lecrim/index.html`. La dirección antigua `https://janorik.github.io/leyes-interactivas-claude/` redirige a la nueva. Al darle una dirección al usuario, añadir `?v=N` (número nuevo) para que el navegador no muestre una versión guardada.
- **Antes de publicar, probar en navegador** (Playwright con el Chromium instalado, ancho 390 px de móvil): todas las fases abren, sin errores de JavaScript y sin desplazamiento lateral. También la LEC cuando se toca la plantilla. Las etiquetas de plazo largas se parten en dos líneas (`.chip.plazo` con `white-space:normal`) para no desbordar.
- **Dominio propio (Chat 3, 22-10/23-10-2026; registro CNAME creado por el usuario en Cloudflare el 23-10-2026; el usuario no tenía notas que copiar):** el usuario elige `leyes-interactivas.norlexia.es` (subdominio de `norlexia.es`, comprado en DonDominio; la web principal está en Railway y no se toca). Pasos: 1) registro CNAME `leyes-interactivas` → `janorik.github.io` en **Cloudflare** (los DNS de `norlexia.es` están allí: abby/drake.ns.cloudflare.com, comprobado por el usuario el 23-10-2026), con el proxy desactivado (nube gris, «Solo DNS»); 2) solo después, archivo `CNAME` en la raíz del repositorio con el subdominio y «Enforce HTTPS» en Settings › Pages (lo marca el usuario); 3) recomendado: verificar el dominio en la cuenta de GitHub. Antes del cambio, el usuario descarga la copia de sus notas de cada ley (el almacenamiento local va por dirección) y la importa en la nueva. Para deshacer: borrar el registro y el archivo `CNAME`.
- **Volver a una versión anterior:** botón «Revert» de la PR ya unida en GitHub, o pedírselo a Claude (cada versión queda en el historial). No se pueden crear etiquetas de versión desde aquí (GitHub devuelve 403).

## Vistas de la app LEC
Enfoque acordado con el usuario: app para **aprender**, no solo para leer la ley. El centro es el **mapa procesal**.
1. **Mapa** (pantalla de inicio; antes «Procesos»): cada procedimiento como ruta de fases en vista de conjunto. Cada fase abre una ficha con: qué ocurre, plazos (con la frase literal del artículo), alternativas desplegables («¿y si no contesta?»), pregunta «Ponte a prueba», conexiones y enlaces a otros procesos. En móvil la ficha se abre como hoja inferior; en ordenador, como panel lateral.
1 bis. **Procedimientos**: los mismos bloques del mapa agrupados por tipo de juicio (declarativos, especiales, ejecución, cautelares…), definidos en `vista_procedimientos` de `procedimientos.json`. Pedido por el usuario para estudiar por tipo de juicio.
1 ter. **Recursos**: pestaña propia. En la LEC abre el selector, las fichas y el test; en una ley sin `recursos.json` muestra los bloques de `vista_recursos`.
2. **Ley**: árbol navegable (Libros > Títulos > Capítulos > Secciones > Artículos) con el texto literal. El nombre de la ley en el título es un enlace a su texto consolidado en el BOE (`act.php?id=` + `ley.boe`; pedido por el usuario, Chat 4).
3. **Buscar**: por número de artículo, por texto de la ley y por fases y plazos del mapa.
4. **Repaso**: tarjetas generadas de preguntas, alternativas y plazos, con progreso guardado en local.
5. **Recursos**: selector por resolución (qué recurso cabe, plazo y órgano, con frase literal), fichas de cada recurso y test de opción múltiple.
6. **Notas**: marcadores y notas personales en artículos, fases y recursos, guardados en el almacenamiento local del navegador. No se sincronizan entre el móvil y el PC; para pasarlos hay copia de seguridad (descargar / importar archivo JSON).

Datos del mapa: `lec/datos/procedimientos.json` (contenido elaborado, `revisado: false`). Cada plazo, alternativa y respuesta lleva una frase `literal`; `scripts/insertar_datos.py` comprueba que esa frase está en el artículo citado y, si no, no publica. Una fase puede llevar `recursos_rel` (ids de `recursos.json`): la ficha muestra botones a esos recursos y a «¿Qué recurso cabe?»; el script rechaza ids inexistentes.

Todo artículo citado en cualquier vista es un enlace que abre su texto literal.

**Criterio de contenido para todas las leyes (aprobado por el usuario, 22-10-2026).** La app sirve para orientarse de forma sencilla en procedimientos, opciones y recursos; no para cargar toda la ley (para el detalle están el texto literal y el BOE). Antes de desarrollar o mantener una ficha, la pregunta es: «¿ayuda a orientarse en el procedimiento, las opciones y los recursos?», no «¿está en el canon?». El canon marca el máximo. **Pendiente:** revisar con este criterio lo ya hecho en la LEC, empezando por las disposiciones generales (propuesta de Claude en el Chat 3: mantener competencia objetiva y territorial, declinatoria, formas de terminar el proceso, procurador y abogado, plazos, presentación de escritos, caducidad y costas; dudosas o a índice, las demás). No se cambia nada hasta que el usuario lo confirme.

**Finalidad y núcleo obligatorio de cada ley (decisión del usuario, Chat 4, 23-10-2026).** La app sirve para la práctica profesional y para aprender, memorizar y repasar la ley. «Terminar una ley» es terminar su funcionalidad en la app, no el texto literal, que va siempre completo. En todas las leyes deben estar completos los **procedimientos, las resoluciones y los recursos** de cada ámbito procesal; eso es lo que importa. El canon lo decide el usuario, pero Claude, al leerlo, le recomienda y aconseja con criterio jurídico qué añadir o quitar (como propuesta argumentada con artículos, No verificable hasta que él la confirme). El canon se va modificando sobre la marcha. Orden de trabajo pedido: LECrim al nivel de la LEC → LRJS → ley administrativa. El usuario subió a `fuentes/` los PDF de la LRJS y de las Leyes 39/2015 y 40/2015 (23-10-2026); la ley administrativa se decide después: el usuario tiene que ver cuál es la ley procesal (la 29/1998 no está subida). El usuario hará la revisión de lo hecho (puntos amarillos) más adelante, en una tarde libre.

## Reglas anti-error (obligatorias)
- Todo plazo, fase, recurso o tarjeta lleva el artículo o artículos en que se basa.
- Todo contenido elaborado (no literal) se crea con `revisado: false`.
- La app marca el estado con un **punto de color** junto al nombre (decisión del usuario, 22-10-2026): amarillo = pendiente de revisión, verde = revisado (`revisado: true`), gris = solo índice (esqueleto). En las listas va solo el punto; en la ficha abierta, el punto con su texto. Leyenda bajo el aviso del BOE. Cada punto lleva texto oculto (`aria-label` y `title`) para que no dependa solo del color.
- Si el texto legal admite varias lecturas, o un plazo depende de supuestos, no elijas: anótalo y pregunta.
- Nunca presentes un plazo como seguro si no sale literalmente del artículo citado.
- **Comprueba quién dicta cada resolución** antes de clasificarla (corrección del usuario: el LAJ solo dicta diligencias de ordenación y decretos, nunca autos). `insertar_datos.py` rechaza un auto o una sentencia en el grupo «LAJ» del selector de recursos.
- La calculadora de plazos con calendario (días hábiles, agosto, festivos) NO se hace ahora. Es una segunda parte.

## Diseño
- Paleta NOrlexia: verde `#0d4a45`, oro `#c9a04a`, crema `#f5f0e8`.
- Logo de `assets/`, en la cabecera. Junto al logo: «NORLEXIA» pequeño, la abreviatura de la ley en dorado y su nombre debajo (hasta 3 líneas), en todas las pestañas, para saber siempre en qué ley se está (opción elegida por el usuario, Chat 4).
- Botón de modo claro/oscuro, recordado en local.
- Diseño adaptado a móvil (prioridad) y a ordenador. Texto legible y zoom cómodo.
- Botón flotante «‹ Atrás» propio de la app (pedido por el usuario): vuelve a la pantalla anterior o, si se entró por enlace, sube un nivel. Oculto en la pantalla de inicio y con una ficha abierta.
- Barra de pestañas desplazable en el móvil (Mapa, Procedimientos, Recursos, Ley, Buscar, Repaso, Notas). Las pestañas sin contenido se ocultan.
- Almacenamiento local con prefijo de la ley (`lec:`, `lecrim:`): `tema`, `tam`, `q`, `progreso`, `mis`. Si se añade otra clave, ponerla en `cookies.html`.

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
- **F7** — Portada (`/index.html`) que enlaza a cada ley, preparada para añadir LECrim, LRJS y ET. Hecha: se genera con `python3 scripts/generar_portada.py` a partir de `scripts/leyes.json`. Para añadir una ley: crear su carpeta con su `index.html` y poner su estado a «disponible» en `leyes.json`. Los enlaces apuntan a `carpeta/index.html?v=N` (N = versión publicada, Chat 4) para que funcionen también en local y para que, al entrar por la portada, el móvil no muestre una ley guardada de una versión anterior.
- **Segunda parte** — Calculadora de plazos con calendario.

## Pie legal y páginas legales (todas las leyes)
- Pie igual que el de norlexia.es en la portada y en cada ley: «© 2026 J A Noriega (Norik)» abre la ventana «Propiedad intelectual y condiciones de uso»; enlaces a Aviso legal, Privacidad y Cookies. Está en la plantilla `lec/index.html` y en `scripts/generar_portada.py`.
- Páginas `aviso-legal.html`, `politica-privacidad.html` y `cookies.html` en la raíz, con estilo en `assets/legal.css`. Adaptadas de las de la web (repositorio privado `janorik/WEB-NORLEXIA`, carpeta `bocetos/`) a esta app: sin formulario, sin fuentes externas, solo almacenamiento local.
- Decisiones del usuario: el pie en la portada y en cada ley; páginas propias adaptadas, no copia ni enlace a la web; la ventana © lleva los cuatro primeros párrafos de la web (sin el de las demostraciones); **el NIF y el domicilio no se copian aquí** porque este repositorio es público: el aviso legal remite al de norlexia.es. El correo janorlex@gmail.com sí figura.
- Si la app guarda algo nuevo en el navegador (otra clave de localStorage), hay que añadirlo a `cookies.html`.
- Dudas en `PENDIENTES.md › Páginas legales`.

## LECrim
- Fuente: `fuentes/LECrim_BOE-A-1882-6036.pdf` (Real Decreto de 14 de septiembre de 1882, BOE-A-1882-6036), texto consolidado con última modificación de 09 de abril de 2026. Sin XML: se extrae solo del PDF con `python3 scripts/extraer_ley.py lecrim` (antes `extraer_lecrim.py`; el extractor común da exactamente el mismo resultado, comprobado el 23-10-2026), que lo contrasta con pdftotext y escribe `lecrim/datos/informe_control.md`.
- App: `lecrim/index.html`, generada con `python3 scripts/insertar_datos.py lecrim`. La app es la misma para todas las leyes: `lec/index.html` es la plantilla y el script la copia con los datos de cada ley. Una mejora de la app se hace en `lec/index.html` y se regeneran todas.
- Mientras una ley no tenga mapa procesal, la app abre en «Ley» y oculta «Mapa»; «Repaso» se oculta si no hay tarjetas.
- **F1 LECrim (hecha):** texto literal completo (1059 artículos y 10 disposiciones), árbol, buscador, notas y portada. Pendiente de revisión del usuario.
- **Esqueleto del mapa (hecho):** `python3 scripts/esqueleto_lecrim.py` genera `lecrim/datos/procedimientos.json` con 14 bloques y 86 fases sacados del índice del BOE (nombre literal y rango de artículos, `"esqueleto": true`, sin plazos ni alternativas). Al desarrollar un bloque se quita su `"esqueleto": true` y el script deja de regenerarlo.
- **Canon del usuario (22-10-2026):** `fuentes/canon_contenido.md` recoge sus marcas SI / PARCIAL / NO por bloques de la LEC y la LECrim (extracto de su documento de la plataforma jurídica, en desarrollo). **Original:** repositorio privado `janorik/plataforma-juridica`, archivo `docs/canon-contenido.md` (se añade a la sesión con `add_repo`, solo lectura). Incluye también el canon de la **LRJS** (índice revisado 1-37). Comparado el 23-10-2026: LEC y LECrim iguales, salvo la redacción de la nota del bloque 66 de la LEC (sin referencias internas a la plataforma, a propósito) y los bloques 13-15 de la LECrim (aquí SI desde el Chat 4; allí siguen NO hasta que el usuario lo cambie). Decide **qué se desarrolla en el mapa**: lo marcado NO queda como índice (punto gris); en lo PARCIAL se desarrollan solo las fases de los artículos listados. No afecta al texto literal, que sigue completo. Las fases ya hechas fuera del canon (8 en la LECrim) se mantienen. **El canon marca el máximo, no el mínimo (decisión del usuario, 22-10-2026):** en cada bloque se valora con criterio jurídico si el contenido sirve a la finalidad de la app (orientar en procedimientos, opciones y recursos, de forma sencilla, sin cargar toda la ley; para el detalle está el texto literal y el BOE). Lo que no sirve queda como índice aunque el canon lo marque PARCIAL. El canon no está cerrado: el usuario puede añadir o quitar sobre la marcha. Si el usuario actualiza su canon, se vuelve a copiar. El 22-10-2026 el usuario añadió el art. 988 bis al bloque 35 (ejecución) y se corrigió la nota de la audiencia preliminar (art. 785); ambos cambios están también en su plataforma.
- **Método acordado con el usuario:** primero el esqueleto completo del mapa; después se desarrolla un bloque cada vez (plazos con frase literal, alternativas, preguntas), con su visto bueno.
- **Sumario ordinario (solo en «Procedimientos»):** une en una ruta las fases de instrucción, conclusión y juicio oral (`UNIDOS` en `esqueleto_lecrim.py`, marca `solo_procedimientos`). El Mapa sigue la ley por libros y no se toca: decisión del usuario («son dos cosas diferentes»). El bloque unido se regenera siempre desde los tres del Mapa; el contenido se desarrolla en esos tres. Temas comunes enlazados aparte: detención y prisión, medidas de investigación, fianzas.
- **Procedimiento abreviado (hecho):** primer bloque desarrollado del mapa (arts. 757-794, 10 fases, 32 plazos), elegido por el usuario. Se genera editando `lecrim/datos/procedimientos.json`; ya no lleva `"esqueleto": true`. Dudas en `PENDIENTES.md › LECrim › Procedimiento abreviado`. Pendiente de revisión del usuario.
- **Instrucción del sumario (hecho):** segundo bloque desarrollado (arts. 299-485, 12 fases, 18 plazos), elegido por el usuario. Sus fases pasan solas a «Procedimientos › Sumario ordinario» al regenerar con `esqueleto_lecrim.py`; el ámbito corto debe seguir siendo «Arts. 299 a 485» porque ese script lo usa. Dudas en `PENDIENTES.md › LECrim › Instrucción del sumario`. Pendiente de revisión del usuario.
- **Conclusión del sumario (hecho):** tercer bloque desarrollado (arts. 622-648, 5 fases, 10 plazos). Con la instrucción, forma parte de la ruta «Procedimientos › Sumario ordinario». Ámbito corto «Arts. 622 a 648» (lo usa el script). Dudas en `PENDIENTES.md`. Pendiente de revisión del usuario.
- **Juicio oral del sumario (hecho):** cuarto bloque desarrollado (arts. 649-749, 9 fases, 11 plazos). Con él, «Procedimientos › Sumario ordinario» queda completo: 26 fases sin esqueleto. Ámbito corto «Arts. 649 a 749» (lo usa el script). Dudas en `PENDIENTES.md`. Pendiente de revisión del usuario.
- **Juicio rápido (hecho):** quinto bloque desarrollado (arts. 795-803, 8 fases, 12 plazos), elegido por el usuario. Los arts. 803 bis (aceptación de decreto) y 803 ter (decomiso) quedan para «Otros procedimientos especiales». Dudas en `PENDIENTES.md`. Pendiente de revisión del usuario.
- **Detención, prisión y libertad provisional (hecho):** sexto bloque desarrollado (arts. 486-544 quinquies, 8 fases, 21 plazos), elegido por el usuario. Es el tema común de medidas cautelares personales que enlazan el sumario, el abreviado y el juicio rápido. Dudas en `PENDIENTES.md`. Pendiente de revisión del usuario.
- **Juicio sobre delitos leves (hecho):** séptimo bloque desarrollado (arts. 962-977, 6 fases, 4 plazos; 978-982 derogados), elegido por el usuario. Dudas en `PENDIENTES.md`. Pendiente de revisión del usuario.
- **Ejecución de las sentencias (hecho):** octavo bloque desarrollado (arts. 983-999, 6 fases, 8 plazos), elegido por el usuario. Dudas en `PENDIENTES.md`. Pendiente de revisión del usuario.
- **Medidas de investigación (hecho):** noveno bloque desarrollado (arts. 545-588 octies, 9 fases y 18 plazos), elegido por el usuario en el Chat 3 (22-10-2026). Es el primero hecho con el canon: la fase «Registro de libros y papeles» (573-578) queda como índice porque el canon no marca ninguno de sus artículos. Se mantienen los id de fase del esqueleto (`investigacion-545`…) para no perder notas. Dudas en `PENDIENTES.md › LECrim › Medidas de investigación`. Pendiente de revisión del usuario.
- **Apelación, casación y revisión (hecho):** décimo bloque desarrollado (arts. 846 bis a-961, 7 fases y 15 plazos), elegido por el usuario en el Chat 3 (22-10-2026). La queja por denegación del testimonio (862-872) queda como índice (fuera del canon). Complementa la pestaña Recursos sin cambiarla. Dudas en `PENDIENTES.md › LECrim › Apelación, casación y revisión`. Pendiente de revisión del usuario.
- **Aceptación de decreto e injuria y calumnia (hecho):** undécimo desarrollo, dentro del bloque `especiales` (ya sin `"esqueleto": true`), elegido por el usuario en el Chat 3 (22-10-2026): 4 fases nuevas (`especiales-803_bis_a`, `especiales-803_bis_e`, `especiales-804`, `especiales-808`) y 5 plazos. Las demás fases del bloque siguen como índice (fuera del canon). Dudas en `PENDIENTES.md › LECrim`. Pendiente de revisión del usuario.
- **Disposiciones generales (hecho, parcial):** del Libro I solo se desarrollan «Competencia» (`generales-8`) y «Acciones penal y civil» (`generales-100`), por decisión del usuario en el Chat 3 (22-10-2026); el resto queda como índice. Con esto queda cubierto todo lo que el usuario quiere desarrollar de la LECrim según su canon. Pendiente de revisión del usuario.
- **Resoluciones, recursos contra resoluciones e inicio del proceso (Chat 4, 23-10-2026, hecho):** por la regla del núcleo obligatorio, fichas `generales-141` (resoluciones) y `generales-216` (recursos contra resoluciones, puerta a la pestaña Recursos), y bloque `inicio` desarrollado (denuncia, querella, Policía judicial: 3 fases, 5 plazos; el usuario lo pasó de NO a SI en el canon a propuesta de Claude). En la LEC, ficha `act-resoluciones` en «Actuaciones procesales». Dudas en `PENDIENTES.md`. Pendiente de revisión del usuario.
- **Recursos de la LECrim (hecho):** `lecrim/datos/recursos.json` con el mismo formato que la LEC: 14 recursos, 27 casos del selector agrupados en `grupos_selector` (LAJ, Juez de Instrucción, Tribunales, Juez o Tribunal, Sentencias) y test. El usuario quiere que cada ley tenga las tres secciones de la LEC: «Por resolución», «Recursos» y «Ponte a prueba». Pendiente de revisión del usuario; dudas en `PENDIENTES.md › LECrim`.
- **Leyes relacionadas:** el Tribunal del Jurado se muestra como tarjeta «otra ley» con enlace al BOE (campo `externos` de `procedimientos.json`), no se desarrolla.
- **Fuera del esqueleto:** fases que solo tienen artículos derogados o sin contenido (caps. II-IV del título II del libro V). El Real Decreto de aprobación (arts. 1.º-5.º) va como «Real Decreto de aprobación», separado de la ley. Los rangos del BOE («Artículos 48 a 50») son una sola entrada; buscar «49» lleva a ella.

## LRJS
- Fuente: `fuentes/LRJS_BOE-A-2011-15936.pdf` (Ley 36/2011, de 10 de octubre, reguladora de la jurisdicción social, BOE-A-2011-15936), texto consolidado con última modificación de 30 de abril de 2025. Subido por el usuario el 23-10-2026 (como «LRJS consolidado.pdf»; renombrado). Sin XML: `python3 scripts/extraer_ley.py lrjs`. La LRJS tiene **subsecciones** (arts. 127-136): el extractor las reconoce (tipo `subseccion`).
- **F1 LRJS (Chat 4, 23-10-2026, hecha):** texto literal completo (preámbulo, 310 artículos y 16 disposiciones; 92 rótulos de estructura, todos los del índice), árbol, buscador, notas y portada. Sin mapa todavía: la app abre en «Ley». Pendiente de revisión del usuario; dudas en `PENDIENTES.md › LRJS`.
- **Canon:** copiado de la plataforma a `fuentes/canon_contenido.md › LRJS` (39 bloques, sin las notas internas de carga de la plataforma).
- **Siguiente paso (con el visto bueno del usuario):** esqueleto del mapa y propuesta jurídica sobre el canon según la regla del núcleo obligatorio (procedimientos, resoluciones y recursos completos).
- PDF también subidos (23-10-2026), sin usar todavía: `fuentes/LPACAP 39_2015 consolidado.pdf` y `fuentes/LRBSP 40_2015 consolidado.pdf`.

