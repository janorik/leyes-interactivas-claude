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
1. Árbol navegable (Libros > Títulos > Capítulos > Secciones > Artículos) con el texto literal.
2. Buscador por número de artículo y por texto.
3. Esquemas de procedimientos por fases, con el artículo de cada fase enlazado.
4. Tabla de plazos filtrable por bloque y por acto procesal.
5. Mapa de recursos: qué recurso cabe, contra qué resolución, plazo y órgano.
6. Marcadores y notas personales, guardados en el almacenamiento local del navegador. No se sincronizan entre el móvil y el PC; el usuario lo sabe.
7. Modo repaso con tarjetas generadas a partir de plazos, procedimientos y recursos, con su progreso guardado en local.

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
- **F2** — Tabla de plazos de los bloques núcleo.
- **F3** — Esquemas de procedimientos: ordinario, verbal, monitorio, ejecución y cautelares.
- **F4** — Mapa de recursos.
- **F5** — Marcadores, notas y modo repaso.
- **F6** — Procesos especiales: familia y capacidad, división de herencia, cambiario y ejecución hipotecaria (plazos, esquemas y repaso).
- **F7** — Portada (`/index.html`) que enlaza a cada ley, preparada para añadir LECrim, LRJS y ET.
- **Segunda parte** — Calculadora de plazos con calendario.
