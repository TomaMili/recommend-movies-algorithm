# Movie Recommendation System (TMDB + FastAPI + React)

A high-performance, content-based movie recommender powered by TMDB, FastAPI, and React.
<img width="1147" height="913" alt="image" src="https://github.com/user-attachments/assets/e88f1e10-be4c-4e7b-bb92-724f0cafa0f3" />

## Overview

This project is a full-stack movie recommendation system that analyzes thousands of movies from TMDB and computes similarity using:

- TF-IDF vectorization
- cosine similarity
- weighted feature scoring
- numeric normalization
- cast/crew/genre metadata

The system automatically groups together movie franchises (Star Wars, Marvel, LOTR, Harry Potter) while also detecting independent thematic similarity.

## Features

• Advanced movie similarity engine  
• TMDB dataset builder (5,000–15,000 movies)  
• FastAPI backend  
• React frontend with smooth similarity color gradients  
• Netflix-style match bar  
• Per-feature similarity breakdown  
• Instant responses using cached TMDB dataset

## Similarity Features

The recommender uses:

- Overview similarity (TF-IDF cosine)
- Tagline similarity
- Genre overlap
- Actor vector similarity
- Director match
- Language match bonus
- Numeric similarity (release year, popularity, rating)

Weights used in similarity calculation:

    overview: 0.6      – thematic meaning
    tagline: 0.2       – light influence
    genres: 1.2        – strong franchise grouping
    actors: 1.3        – cast continuity
    director: 0.9      – stylistic consistency
    language: 0.1      – minor influence
    numeric: 0.5       – era + prominence

## Architecture

1. TMDB Loader downloads full movie metadata + credits.
2. Features are vectorized (TF-IDF, one-hot, normalized numbers).
3. Cosine similarity is computed per feature.
4. Weighted scores are normalized to a final similarity value (0–1).
5. FastAPI exposes /recommend endpoint.
6. React UI displays results with colors and match bars.

## Installation

Backend:
cd backend
python -m venv venv
venv/Scripts/activate (Windows)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

Place your TMDB API key in .env:
TMDB_API_KEY=your_api_key_here

Frontend:
cd frontend
npm install
npm run dev

## API Endpoints

GET /recommend?title=Inception&top_n=10
GET /health
GET /titles?limit=50

## Example JSON Output

{
"query": "Star Wars",
"count": 10,
"results": [
{
"title": "Star Wars: Episode V",
"similarity_score": 0.912,
"genres_score": 1.00,
"actors_score": 0.87,
"director_score": 1.00,
"tagline_score": 0.45,
"language_score": 1.00,
"numeric_score": 0.77
}
]
}

## Future Improvements

- Hybrid collaborative filtering
- User profiles and personalization
- BERT/SBERT sentence embeddings
- Image-based poster similarity
- Full-text search
- Visualizations (t-SNE clustering, PCA maps)

## License

MIT License
