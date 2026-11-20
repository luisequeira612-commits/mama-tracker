# MAMA 2026 stage chart

Tracker personal de reproducciones en YouTube para MAMA 2026 — Day 1.

## Qué hace

- Agrupa videos por artista ignorando mayúsculas/minúsculas y espacios extra.
- Suma las vistas actuales de todos los videos configurados.
- Cuenta canciones, videos y colaboraciones.
- Ordena los actos por vistas y destaca el #1.
- Actualiza `docs/stats.json` cada 30 minutos mediante GitHub Actions.
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

Formato:

`Artista | URL o ID | canciones | collab`

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

El workflow también se ejecuta automáticamente cada 30 minutos y cuando cambian `videos.txt` o `config.json`.

## Cuota

La API usa `videos.list` para obtener estadísticas.

- Cada lote de hasta 50 IDs cuesta 1 unidad de cuota.
- 36 videos caben en una sola llamada.
- La cuota estándar gratuita de YouTube Data API es de 10.000 unidades/día.
- Con 36 IDs, cada actualización programada usa 1 unidad.

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
docs/index.html
docs/stats.json
.github/workflows/update.yml
README.md
```
