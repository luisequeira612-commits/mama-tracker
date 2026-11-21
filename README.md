# MAMA 2026 stage chart

Tracker personal de reproducciones en YouTube para MAMA 2026 — Day 1.

## Qué hace

- Agrupa vídeos por acto principal ignorando mayúsculas/minúsculas y espacios extra.
- Suma las vistas actuales de todos los vídeos configurados y muestra el porcentaje de cada acto sobre el total; el redondeo de un decimal se distribuye para que los porcentajes visibles sumen exactamente 100.0%.
- Cuenta canciones únicas atribuidas, vídeos y colaboraciones.
- Cada vídeo se cuenta una sola vez en el total general; los cortes de canciones ya contabilizadas usan `songs=0` para evitar duplicar el contador de canciones.
- Las colaboraciones se atribuyen a un acto principal para evitar filas duplicadas; se marcan con `collab`.
- Muestra aparte las vistas y el porcentaje de los vídeos colaborativos, también atribuidos una sola vez al acto principal. Sus porcentajes visibles también suman exactamente 100.0%, y esta sección no vuelve a sumarse al ranking general.
- Ordena los actos por vistas y destaca el #1.
- Actualiza `docs/stats.json` cada 30 minutos iniciando GitHub Actions desde un Cloudflare Worker Cron Trigger.
- La página refresca los datos cada 5 minutos.
- Usa GitHub Pages + GitHub Actions + YouTube Data API v3 + Cloudflare Worker como disparador, sin servidor propio ni base de datos.

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

Inventario verificado de Chapter 1: **36 vídeos únicos y 14 actos principales**. BABYMONSTER figura con **2 canciones, 2 vídeos y 1 colaboración**. El vídeo independiente `DOCKING COMPLETE` de Street World Fighter está separado de la colaboración con BABYMONSTER.

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

El Worker de Cloudflare inicia este mismo workflow cada 30 minutos. Los cambios en `videos.txt` o `config.json` también lo ejecutan automáticamente.

La configuración del Worker y los pasos para desplegarlo están en [docs/CLOUDFLARE-SCHEDULER.md](docs/CLOUDFLARE-SCHEDULER.md).

## Cuota

La API usa `videos.list` para obtener estadísticas.

- Cada lote de hasta 50 IDs cuesta 1 unidad de cuota.
- Hasta 50 IDs caben en una sola llamada.
- La cuota estándar gratuita de YouTube Data API es de 10.000 unidades/día.
- Con los 36 vídeos actuales de Chapter 1, cada actualización programada usa 1 unidad.

## Seguridad y datos

- La API key vive únicamente en el secret `YT_API_KEY` de GitHub.
- El token de GitHub para el Worker se guarda como secreto `GITHUB_TOKEN` en Cloudflare y solo tiene permiso Actions: write en este repositorio.
- El Worker solo inicia el workflow; no recibe la API key de YouTube ni procesa estadísticas.
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
cloudflare/worker.js
wrangler.toml
docs/CLOUDFLARE-SCHEDULER.md
docs/index.html
docs/stats.json
.github/workflows/update.yml
README.md
```
