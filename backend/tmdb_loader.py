# backend/tmdb_loader.py
import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

CACHE_PATH = "tmdb_movies_cache.json"


class TMDBError(Exception):
    pass


def _tmdb_get(path: str, params: dict | None = None) -> dict:
    if not TMDB_API_KEY:
        raise TMDBError("TMDB_API_KEY is not set in .env")

    url = f"{BASE_URL}{path}"
    p = {"api_key": TMDB_API_KEY, "language": "en-US"}
    if params:
        p.update(params)

    r = requests.get(url, params=p, timeout=15)
    if not r.ok:
        raise TMDBError(f"TMDB request failed: {r.status_code} {r.text}")

    return r.json()


def _fetch_movie_ids(pages: int = 250) -> set[int]:
    ids: set[int] = set()
    endpoints = ("popular", "top_rated", "now_playing", "upcoming")

    for endpoint in endpoints:
        for page in range(1, pages + 1):
            data = _tmdb_get(f"/movie/{endpoint}", {"page": page})
            results = data.get("results", [])
            if not results:
                break
            for m in results:
                if m.get("id") is not None:
                    ids.add(m["id"])

    print(f"Collected {len(ids)} unique movie IDs from TMDB.")
    return ids


def _fetch_movie_with_credits(movie_id: int) -> dict:
    return _tmdb_get(f"/movie/{movie_id}", {"append_to_response": "credits"})


def _download_all_movies(pages: int) -> list[dict]:
    movie_ids = _fetch_movie_ids(pages)
    raw = []

    for i, mid in enumerate(movie_ids, start=1):
        try:
            details = _fetch_movie_with_credits(mid)
            raw.append(details)
        except Exception as e:
            print(f"Skipping movie {mid}: {e}")

        if i % 100 == 0:
            print(f"Processed {i}/{len(movie_ids)} movies...")

    # WRITE CACHE SAFELY
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False)

    print(f"[CACHE] Saved {len(raw)} movies → {CACHE_PATH}")
    return raw


def build_movies_dataframe(pages: int = 250) -> pd.DataFrame:
    # Load cache if exists
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)

            if not isinstance(raw, list) or len(raw) == 0:
                print("[CACHE] Cache empty or invalid → rebuilding...")
                raw = _download_all_movies(pages)

        except Exception:
            print("[CACHE] Corrupted JSON → rebuilding...")
            raw = _download_all_movies(pages)

    else:
        print("[CACHE] No cache found → downloading fresh dataset...")
        raw = _download_all_movies(pages)

    # Convert TMDB raw → DataFrame
    rows = []
    for d in raw:
        credits = d.get("credits", {})
        cast = credits.get("cast", [])
        crew = credits.get("crew", [])

        actors = [c.get("name") for c in cast[:5] if c.get("name")]
        director = next(
            (member.get("name") for member in crew if member.get("job") == "Director"),
            ""
        )

        genres = d.get("genres") or []
        genre_ids = [g.get("id") for g in genres if g.get("id") is not None]

        rows.append({
            "id": d.get("id"),
            "title": d.get("title") or d.get("original_title"),
            "overview": d.get("overview"),
            "tagline": d.get("tagline"),
            "genres": genres,
            "genre_ids": genre_ids,
            "actors": actors,
            "director": director,
            "runtime": d.get("runtime"),
            "popularity": d.get("popularity"),
            "vote_average": d.get("vote_average"),
            "release_date": d.get("release_date"),
            "original_language": d.get("original_language"),
        })

    df = pd.DataFrame(rows)

    print(f"[DATAFRAME] Loaded {len(df)} movies.")
    return df
