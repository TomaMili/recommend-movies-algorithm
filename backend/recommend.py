import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, pairwise_distances
from scipy.sparse import csr_matrix

from tmdb_loader import build_movies_dataframe

# ============================================================
# 1. Load dataset from TMDB instead of movies.json
# ============================================================
# Increase pages if you want more movies (more data, but slower startup).
df: pd.DataFrame = build_movies_dataframe(pages=250)
df = df.copy()
print("!!! DEBUG: DataFrame rows =", len(df))

# ------------------------------------------------------------
# Basic cleaning / helper columns
# ------------------------------------------------------------
def _safe_str(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    return str(x)


def _extract_year(date_str):
    if not isinstance(date_str, str) or not date_str:
        return np.nan
    try:
        return int(date_str[:4])
    except Exception:
        return np.nan


df["overview"] = df["overview"].map(_safe_str)
df["tagline"] = df["tagline"].map(_safe_str)
df["director"] = df["director"].map(_safe_str)
df["original_language"] = df["original_language"].map(_safe_str)
df["release_year"] = df["release_date"].map(_extract_year)

# ============================================================
# 2. GENRES
# ============================================================
GENRE_MAP = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}


def _extract_genre_names(row) -> list[str]:
    names: list[str] = []

    genres = row.get("genres")
    if isinstance(genres, list):
        for g in genres:
            name = None
            if isinstance(g, dict):
                name = g.get("name")
            elif isinstance(g, str):
                name = g
            if name:
                names.append(name)

    if not names:
        genre_ids = row.get("genre_ids")
        if isinstance(genre_ids, list):
            for gid in genre_ids:
                if gid in GENRE_MAP:
                    names.append(GENRE_MAP[gid])

    return sorted(set(names))


df["genre_names"] = df.apply(_extract_genre_names, axis=1)

mlb_genres = MultiLabelBinarizer()
genre_features = mlb_genres.fit_transform(df["genre_names"])
genre_features = csr_matrix(genre_features)

# ============================================================
# 3. ACTORS (MultiLabelBinarizer)
# ============================================================
def _ensure_list(x):
    return x if isinstance(x, list) else []


df["actors_list"] = df["actors"].map(_ensure_list)

mlb_actors = MultiLabelBinarizer()
actor_features = mlb_actors.fit_transform(df["actors_list"])
actor_features = csr_matrix(actor_features)

# ============================================================
# 4. DIRECTOR (one-hot)
# ============================================================
df["director_clean"] = df["director"].fillna("").astype(str)

mlb_director = MultiLabelBinarizer()
director_features = mlb_director.fit_transform(
    df["director_clean"].map(lambda d: [d] if d else [])
)
director_features = csr_matrix(director_features)

# ============================================================
# 5. LANGUAGE (one-hot on original_language)
# ============================================================
df["lang_clean"] = df["original_language"].fillna("").astype(str)

mlb_lang = MultiLabelBinarizer()
lang_features = mlb_lang.fit_transform(
    df["lang_clean"].map(lambda l: [l] if l else [])
)
lang_features = csr_matrix(lang_features)

# ============================================================
# 6. OVERVIEW + TAGLINE (TF-IDF)
# ============================================================
tfidf_overview = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    stop_words="english",
)
overview_features = tfidf_overview.fit_transform(df["overview"])

tfidf_tagline = TfidfVectorizer(
    max_features=3000,
    ngram_range=(1, 2),
    stop_words="english",
)
tagline_features = tfidf_tagline.fit_transform(df["tagline"])

# ============================================================
# 7. NUMERIC FEATURES (for seminar: popularity, vote_average, release_year)
# ============================================================
numeric_cols = ["popularity", "vote_average", "release_year"]

for col in numeric_cols:
    if col not in df.columns:
        df[col] = np.nan

for col in numeric_cols:
    median_val = df[col].median()
    df[col] = df[col].fillna(median_val)

scaler_numeric = StandardScaler()
numeric_scaled = scaler_numeric.fit_transform(df[numeric_cols])

# ============================================================
# 8. WEIGHTS (you can tune for seminar)
# ============================================================
WEIGHTS = {
    "overview": 0.55,
    "tagline": 0.50,
    "genres": 0.20,
    "actors": 0.20,
    "director": 0.10,
    "language": 0.05,
    "numeric": 0.15,
}


def _cosine_sim_row(matrix, idx: int) -> np.ndarray:
    return cosine_similarity(matrix[idx], matrix).flatten()


def _numeric_similarity_by_column(idx: int) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """
    Compute similarity per numeric column and combined numeric similarity.
    Returns:
      numeric_sims: dict[col_name] -> similarity array
      numeric_all:  combined similarity (mean over columns)
    """
    numeric_sims: dict[str, np.ndarray] = {}
    for col_idx, col_name in enumerate(numeric_cols):
        column = numeric_scaled[:, col_idx].reshape(-1, 1)
        q = column[idx].reshape(1, -1)

        dists = pairwise_distances(q, column, metric="euclidean").flatten()
        sim = 1 / (1 + dists)
        sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)
        numeric_sims[col_name] = sim

    numeric_all = np.zeros(len(df))
    for col_name in numeric_cols:
        numeric_all += numeric_sims[col_name]
    numeric_all /= len(numeric_cols)

    return numeric_sims, numeric_all


def _find_movie_index_by_title(title: str) -> int | None:
    """
    1) exact match (case-insensitive)
    2) fallback: substring match (e.g. 'godfather' -> 'The Godfather Part II')
    """
    if "title" not in df.columns:
        return None

    query = title.strip().lower()
    titles = df["title"].fillna("").str.lower()

    exact_mask = titles == query
    exact_idxs = titles[exact_mask].index.to_list()
    if exact_idxs:
        return exact_idxs[0]

    contains_mask = titles.str.contains(query, na=False)
    contains_idxs = titles[contains_mask].index.to_list()
    if contains_idxs:
        return contains_idxs[0]

    return None


def recommend_weighted(title: str, top_n: int = 8) -> pd.DataFrame:
    """
    Main API function:
      - Finds the movie by title
      - Computes per-feature similarities
      - Combines them with WEIGHTS
      - Returns top_n most similar movies (DataFrame)
    """
    idx = _find_movie_index_by_title(title)
    if idx is None:
        print(f"Movie '{title}' not found in dataset.")
        return pd.DataFrame()

    # ---- Per-feature similarities ----
    overview_sim = _cosine_sim_row(overview_features, idx)
    tagline_sim = _cosine_sim_row(tagline_features, idx)
    genres_sim = _cosine_sim_row(genre_features, idx)
    actors_sim = _cosine_sim_row(actor_features, idx)
    director_sim = _cosine_sim_row(director_features, idx)
    lang_sim = _cosine_sim_row(lang_features, idx)
    numeric_sims, numeric_all = _numeric_similarity_by_column(idx)

    popularity_sim = numeric_sims.get("popularity")
    vote_average_sim = numeric_sims.get("vote_average")
    release_year_sim = numeric_sims.get("release_year")

    # ---- Weighted combination ----
    combined = (
        WEIGHTS["overview"] * overview_sim
        + WEIGHTS["tagline"] * tagline_sim
        + WEIGHTS["genres"] * genres_sim
        + WEIGHTS["actors"] * actors_sim
        + WEIGHTS["director"] * director_sim
        + WEIGHTS["language"] * lang_sim
        + WEIGHTS["numeric"] * numeric_all
    )

    df_scores = df.copy()
    df_scores["similarity_score"] = combined

    # Individual components (for display / explanation in React + seminars)
    df_scores["overview_score"] = overview_sim
    df_scores["tagline_score"] = tagline_sim
    df_scores["genres_score"] = genres_sim
    df_scores["actors_score"] = actors_sim
    df_scores["director_score"] = director_sim
    df_scores["language_score"] = lang_sim
    df_scores["numeric_score"] = numeric_all

    if popularity_sim is not None:
        df_scores["popularity_score"] = popularity_sim
    else:
        df_scores["popularity_score"] = 0.0

    if vote_average_sim is not None:
        df_scores["vote_average_score"] = vote_average_sim
    else:
        df_scores["vote_average_score"] = 0.0

    if release_year_sim is not None:
        df_scores["release_year_score"] = release_year_sim
    else:
        df_scores["release_year_score"] = 0.0

    # Remove query movie from results & sort
    df_scores = df_scores[df_scores.index != idx]
    df_scores = df_scores.sort_values("similarity_score", ascending=False)

    return df_scores.head(top_n)


if __name__ == "__main__":
    test_title = "Godfather"
    print(f"Testing recommendations for: {test_title}")
    recs = recommend_weighted(test_title, top_n=10)
    if recs.empty:
        print("No recommendations (movie not found or dataset empty).")
    else:
        print(
            recs[
                [
                    "title",
                    "similarity_score",
                    "genres_score",
                    "actors_score",
                    "director_score",
                    "tagline_score",
                    "language_score",
                    "popularity_score",
                    "vote_average_score",
                    "release_year_score",
                ]
            ].to_string(index=False)
        )
