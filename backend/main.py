from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from recommend import recommend_weighted, df

app = FastAPI(
    title="Movie Recommender API",
    description="Content-based movie recommender using TMDB data.",
    version="1.0.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "movies_loaded": len(df)}


@app.get("/recommend")
def recommend(title: str, top_n: int = 8):
    if not title:
        raise HTTPException(status_code=400, detail="Title query parameter is required")

    recs = recommend_weighted(title, top_n=top_n)
    if recs.empty:
        raise HTTPException(status_code=404, detail=f"Movie '{title}' not found in dataset")

    return {"query": title, "count": len(recs), "results": recs.to_dict(orient="records")}
