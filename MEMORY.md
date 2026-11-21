# Project memory

## MAMA Tracker — 2026-11-21

- Keep the main artist ranking ordered by cumulative views.
- Show each artist's estimated views gained in the last hour directly below the artist name, in small text. Aggregate the change across that artist's tracked videos.
- Do not create a separate growth ranking or label the feature “K-pop Radar”.
- Calculate the hourly estimate from the closest historical snapshot between 45 and 75 minutes old, normalized to 60 minutes. Until a valid baseline exists, show a concise collection status and no fabricated numbers.
- Preserve the 15-minute statistics update cadence and the existing cumulative ranking.
