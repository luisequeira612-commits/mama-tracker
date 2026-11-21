# MAMA 2026 stage chart

Tracker personal de reproducciones en YouTube para MAMA 2026 — Chapter 1 + Chapter 2 (ambos días en un ranking combinado).

## Qué hace

- Agrupa vídeos por acto principal ignorando mayúsculas/minúsculas y espacios extra.
- Suma las vistas actuales de todos los vídeos configurados y muestra el porcentaje de cada acto sobre el total; el redondeo de un decimal se distribuye para que los porcentajes visibles sumen exactamente 100.0%.
- Cuenta canciones únicas atribuidas, vídeos y colaboraciones.
- Cada vídeo se cuenta una sola vez en el total general; los cortes de canciones ya contabilizadas usan `songs=0` para evitar duplicar el contador de canciones.
- Las colaboraciones se atribuyen a un acto principal para evitar filas duplicadas; se marcan con `collab`.
- Muestra aparte las vistas y el porcentaje de los vídeos colaborativos, también atribuidos una sola vez al acto principal. Sus porcentajes visibles también suman exactamente 100.0%, y esta sección no vuelve a sumarse al ranking general.
- Ordena los actos por vistas y destaca el #1.
- Suma en un único ranking los vídeos oficiales de Chapter 1 y Chapter 2, agrupados por acto principal.
- Actualiza `docs/stats.json` cada 15 minutos mediante Cloudflare Worker + GitHub Actions.
- La página refresca los datos cada 5 minutos.
- Usa GitHub Pages + GitHub Actions + YouTube Data API v3, sin servidor ni base de datos.

## Configuración inicial

### 1. YouTube Data API

En Google Cloud Console:

1. Crea o selecciona un proyecto.
2. Activa **YouTube Data API v3**.
3. Ve a **Credentials → API key**.
4. Restringe la clave a YouTube Data API v3.

### 2. Guardar la clave en GitHub

En este repositorio:

**Settings → Secrets and variables → Actions → New repository secret**

Nombre exacto:

`YT_API_KEY`

Nunca pongas la clave directamente en este repositorio.

### 3. GitHub Pages

En:

**Settings → Pages → Build and deployment**

Selecciona:

- Source: **Deploy from a branch**
- Branch: **main**
- Folder: **/docs**

La página será:

https://luisequeira612-commits.github.io/mama-tracker/

### 4. Videos

Edita `videos.txt`.

Inventario combinado de Chapter 1 y Chapter 2: **69 vídeos oficiales únicos y 26 actos**, reconciliados con los uploads de Mnet incluidos en el tracker de referencia. Se incluyen las publicaciones de escenario completo y los cortes individuales oficiales; no se incluyen Shorts. Las versiones alternativas 4K cuentan como vídeos independientes cuando la referencia las incluye, pero usan `songs=0` para no duplicar canciones. Las colaboraciones se atribuyen al acto principal que Mnet acredita primero. Taeyang se agrupa bajo BIGBANG en el vídeo compartido, y el corte de I.O.I se mantiene como acto independiente. BABYMONSTER figura con **2 canciones, 2 vídeos y 1 colaboración**; `DOCKING COMPLETE` de Street World Fighter sigue separado de la colaboración con BABYMONSTER.

Formato:

`Acto principal | URL o ID | canciones únicas atribuidas | collab`

Ejemplo:

`ARTISTA | https://www.youtube.com/watch?v=XXXXXXXXXXX | 1 | collab`

Las líneas que empiezan por `#` son comentarios y no se procesan.

Solo deben añadirse IDs de videos reales y confirmados. No se deben inventar IDs.

### 5. Hora de inicio

Edita `config.json`:

`day1_start_kst`

Está en hora de Corea (KST, UTC+9). La página usa este dato para mostrar cuánto tiempo ha pasado desde el comienzo de Day 1.

### 6. Actualización manual

Ve a:

**Actions → Update MAMA stats → Run workflow**

El workflow se ejecuta automáticamente cada 15 minutos mediante Cloudflare y también cuando cambian `videos.txt` o `config.json`.

## Cuota

La API usa `videos.list` para obtener estadísticas.

- Cada lote de hasta 50 IDs cuesta 1 unidad de cuota.
- Hasta 50 IDs caben en una sola llamada.
- La cuota estándar gratuita de YouTube Data API es de 10.000 unidades/día.
- Con 69 vídeos, cada actualización programada usa 2 unidades (un lote de 50 y otro de 19).

## Seguridad y datos

- La API key vive únicamente en el secret `YT_API_KEY`.
- `docs/stats.json` contiene datos públicos de estadísticas.
- Si una actualización falla, el script no reemplaza unos datos buenos por un archivo vacío o parcial.

## Datos de ejemplo

La interfaz incluye datos de ejemplo para que la página no aparezca vacía antes de configurar la API. El aviso **Datos de ejemplo** desaparece cuando `stats.json` contiene datos reales.

## Estructura

```
videos.txt
config.json
scripts/update.py
tests/test_update.py
docs/index.html
docs/stats.json
.github/workflows/update.yml
README.md
```
