#!/usr/bin/env python3
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS = os.path.join(ROOT, "videos.txt")
CONFIG = os.path.join(ROOT, "config.json")
OUTPUT = os.path.join(ROOT, "docs", "stats.json")
HISTORY = os.path.join(ROOT, "data", "view_history.json")
API = "https://www.googleapis.com/youtube/v3/videos"

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def parse_video_id(value):
    value = value.strip()
    if VIDEO_ID_RE.fullmatch(value):
        return value

    parsed = urllib.parse.urlparse(value if "://" in value else "https://" + value)
    host = parsed.netloc.lower().split(":")[0]
    path = parsed.path.strip("/")

    if host in {"youtu.be", "www.youtu.be"} and VIDEO_ID_RE.fullmatch(path):
        return path

    if host.endswith("youtube.com"):
        if path == "watch":
            candidate = urllib.parse.parse_qs(parsed.query).get("v", [""])[0]
            if VIDEO_ID_RE.fullmatch(candidate):
                return candidate
        if path.startswith("shorts/"):
            candidate = path.split("/", 1)[1]
            if VIDEO_ID_RE.fullmatch(candidate):
                return candidate

    fail(f"ID de YouTube inválido: {value}")


def load_videos():
    entries = []
    seen = set()

    with open(VIDEOS, encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            parts = [part.strip() for part in line.split("|")]
            if len(parts) < 3 or len(parts) > 4:
                fail(f"videos.txt línea {line_no}: se esperaban 3 o 4 campos")

            artist, url_or_id, songs_text = parts[:3]
            if not artist:
                fail(f"videos.txt línea {line_no}: artista vacío")

            try:
                songs = int(songs_text)
            except ValueError:
                fail(f"videos.txt línea {line_no}: canciones debe ser numérico")

            if songs < 0:
                fail(f"videos.txt línea {line_no}: canciones no puede ser negativo")

            collab = len(parts) == 4 and parts[3].strip().lower() == "collab"
            video_id = parse_video_id(url_or_id)

            if video_id in seen:
                fail(f"videos.txt línea {line_no}: ID repetido {video_id}")
            seen.add(video_id)

            entries.append({
                "artist": artist,
                "key": " ".join(artist.split()).casefold(),
                "id": video_id,
                "songs": songs,
                "collab": collab,
            })

    if not entries:
        fail("videos.txt no contiene ningún video configurado")

    return entries


def api_request(ids, api_key):
    query = urllib.parse.urlencode({
        "part": "statistics,snippet",
        "id": ",".join(ids),
        "key": api_key,
    })
    req = urllib.request.Request(
        f"{API}?{query}",
        headers={"User-Agent": "mama-tracker/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except Exception as exc:
        fail(f"falló YouTube Data API: {exc}")


def fetch_all(entries, api_key):
    found = {}

    for start in range(0, len(entries), 50):
        batch = entries[start:start + 50]
        data = api_request([item["id"] for item in batch], api_key)

        api_error = data.get("error")
        if api_error:
            message = api_error.get("message", "error desconocido")
            fail(f"YouTube Data API: {message}")

        for item in data.get("items", []):
            stats = item.get("statistics", {})
            raw_views = stats.get("viewCount")
            if raw_views is None:
                print(f"WARNING: {item['id']} no tiene viewCount; se omite.", file=sys.stderr)
                continue

            found[item["id"]] = {
                "id": item["id"],
                "title": item.get("snippet", {}).get("title", ""),
                "views": int(raw_views),
            }

    missing = [item["id"] for item in entries if item["id"] not in found]
    if missing:
        fail("YouTube no devolvió todos los videos configurados: " + ", ".join(missing))

    return found


def percentage_tenths(values, total):
    if total <= 0:
        return [0 for _ in values]

    raw = [max(0, int(value)) * 1000 / total for value in values]
    allocated = [int(value) for value in raw]
    remaining = 1000 - sum(allocated)
    order = sorted(
        range(len(values)),
        key=lambda index: (-(raw[index] - allocated[index]), index),
    )
    for index in order[:remaining]:
        allocated[index] += 1
    return allocated



def load_history():
    if not os.path.exists(HISTORY):
        return {"snapshots": []}
    try:
        with open(HISTORY, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data.get("snapshots"), list):
            raise ValueError("snapshots debe ser una lista")
        return data
    except Exception as exc:
        fail(f"no se pudo leer el historial de vistas: {exc}")


def update_history(history, found, now):
    snapshots = history.setdefault("snapshots", [])
    snapshot = {
        "captured_at": now.isoformat().replace("+00:00", "Z"),
        "views": {video_id: video["views"] for video_id, video in found.items()},
    }
    if snapshots:
        last_time = datetime.fromisoformat(snapshots[-1]["captured_at"].replace("Z", "+00:00"))
        if (now - last_time).total_seconds() < 300:
            snapshots[-1] = snapshot
        else:
            snapshots.append(snapshot)
    else:
        snapshots.append(snapshot)

    cutoff = now.timestamp() - 24 * 60 * 60
    history["snapshots"] = [
        item for item in snapshots
        if datetime.fromisoformat(item["captured_at"].replace("Z", "+00:00")).timestamp() >= cutoff
    ]
    return history


def calculate_radar(history, entries, found, now):
    candidates = []
    for snapshot in history.get("snapshots", []):
        captured = datetime.fromisoformat(snapshot["captured_at"].replace("Z", "+00:00"))
        age_minutes = (now - captured).total_seconds() / 60
        if 45 <= age_minutes <= 75:
            candidates.append((abs(age_minutes - 60), captured, snapshot))

    if not candidates:
        return {"available": False, "window_minutes": None, "videos": []}

    _, captured, baseline = min(candidates, key=lambda item: item[0])
    elapsed_hours = (now - captured).total_seconds() / 3600
    window_minutes = round(elapsed_hours * 60)
    ranked = []
    for entry in entries:
        video_id = entry["id"]
        previous = baseline["views"].get(video_id)
        current = found[video_id]["views"]
        if previous is None:
            continue
        delta = current - int(previous)
        if delta <= 0:
            continue
        ranked.append({
            "id": video_id,
            "artist": entry["artist"],
            "title": found[video_id]["title"],
            "views": current,
            "views_gained": delta,
            "views_per_hour": round(delta / elapsed_hours),
        })

    ranked.sort(key=lambda item: (-item["views_per_hour"], -item["views_gained"], item["artist"].casefold()))
    return {"available": True, "window_minutes": window_minutes, "videos": ranked[:10]}

def build_stats(entries, found, config):
    groups = {}

    for entry in entries:
        key = entry["key"]
        group = groups.setdefault(key, {
            "artist": entry["artist"],
            "views": 0,
            "songs": 0,
            "videos": 0,
            "collabs": 0,
            "collab_views": 0,
            "video_list": [],
        })

        video = found[entry["id"]]
        group["views"] += video["views"]
        group["songs"] += entry["songs"]
        group["videos"] += 1
        group["collabs"] += int(entry["collab"])
        if entry["collab"]:
            group["collab_views"] += video["views"]
        group["video_list"].append({
            "id": video["id"],
            "title": video["title"],
            "views": video["views"],
            "collab": entry["collab"],
        })

    acts = sorted(groups.values(), key=lambda item: (-item["views"], item["artist"].casefold()))

    for rank, act in enumerate(acts, 1):
        act["rank"] = rank

    total_views = sum(act["views"] for act in acts)
    for act, share_tenths in zip(
        acts, percentage_tenths([act["views"] for act in acts], total_views)
    ):
        act["share_tenths"] = share_tenths

    now = datetime.now(timezone.utc)
    kst = now.astimezone(timezone(timedelta(hours=9)))
    updated_kst_text = kst.strftime("%-d %b at %H:%M KST")


    return {
        "demo": False,
        "event": config["event"],
        "day": config["day"],
        "updated": now.isoformat().replace("+00:00", "Z"),
        "updated_kst_text": updated_kst_text,
        "total_views": total_views,
        "total_collaboration_views": sum(act["collab_views"] for act in acts),
        "total_videos": len(entries),
        "total_acts": len(acts),
        "acts": acts,
    }


def atomic_write(data, path=OUTPUT):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(
        prefix="stats.", suffix=".json", dir=os.path.dirname(path)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        os.replace(temp_path, path)
    except Exception:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def main():
    api_key = os.environ.get("YT_API_KEY", "").strip()
    if not api_key:
        fail("falta el secret YT_API_KEY")

    try:
        with open(CONFIG, encoding="utf-8") as fh:
            config = json.load(fh)
    except Exception as exc:
        fail(f"no se pudo leer config.json: {exc}")

    if not config.get("event") or not config.get("day"):
        fail("config.json debe contener event y day")

    entries = load_videos()
    found = fetch_all(entries, api_key)
    now = datetime.now(timezone.utc)
    history = update_history(load_history(), found, now)
    atomic_write(history, HISTORY)
    stats = build_stats(entries, found, config)
    stats["radar"] = calculate_radar(history, entries, found, now)
    atomic_write(stats)
    print(
        f"OK: {stats['total_videos']} videos, {stats['total_acts']} acts, "
        f"{stats['total_views']:,} views"
    )


if __name__ == "__main__":
    main()
