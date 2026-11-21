# Project memory

## MAMA Tracker — 2026-11-21

- Keep the main artist ranking ordered by cumulative views.
- Show each artist's estimated views gained in the last hour directly below the artist name, in small text. Aggregate the change across that artist's tracked videos.
- Do not create a separate growth ranking or label the feature “K-pop Radar”.
- Calculate the hourly estimate from the closest historical snapshot between 45 and 75 minutes old, normalized to 60 minutes. Until a valid baseline exists, show a concise collection status and no fabricated numbers.
- Preserve the 15-minute statistics update cadence and the existing cumulative ranking.

- Visual treatment approved on 2026-11-21: show positive hourly gains in small green text with an ascending arrow (↗) and wording such as “+3,240 vistas en la última hora”, directly below each artist name. Keep cumulative views, songs, videos, collaborations, and percentage layout unchanged. Use a descending arrow and restrained red for negative changes; a neutral arrow/muted color for zero.

- Decisión aprobada el 2026-11-21: mantener estadísticas acumuladas (reproducciones, canciones, vídeos, colaboraciones y porcentajes) con refresco cada 15 minutos; actualizar el indicador verde de vistas ganadas por artista una vez por hora, en el límite de cada hora KST. Mantener intactos el orden del ranking y la disposición de los demás datos. Si no hay una captura histórica válida, conservar el último valor válido (o mostrar que aún se recopilan capturas si nunca hubo uno), sin inventar cifras.
