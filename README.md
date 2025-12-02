⭐ Movie Recommendation System (TMDB + FastAPI + React)

A high-performance, content-based movie recommender powered by TMDB, FastAPI, and React.

<p align="center"> <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python" /> <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" /> <img src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react" /> <img src="https://img.shields.io/badge/TMDB-API-01d277?logo=themoviedatabase" /> <img src="https://img.shields.io/badge/License-MIT-green" /> </p>
<p align="center"> <img width="680" src="assets/preview.png" alt="App Screenshot"/> <br/> <em>Recommendation UI with dynamic similarity colors & match bars (example).</em> </p>
🎬 Overview

This project is a full-stack content-based movie recommendation system that analyzes thousands of movies from TMDB and computes similarity using:

TF–IDF vectorization

cosine similarity

multi-feature weighted scoring

numeric normalization

cast/crew/genre signals

The algorithm is designed so that franchises naturally group together (Star Wars, LOTR, Marvel, Harry Potter), while still capturing semantic similarity based on text and metadata.

The frontend provides a modern interface inspired by Netflix/X-Ray design, including:

✨ smooth HSL gradient similarity colors
✨ percentage match bar
✨ feature-by-feature breakdown
✨ instant results from FastAPI backend

🚀 Features
🔍 Advanced Movie Similarity Engine

Similarity is computed from multiple signals:

Feature Description
Overview TF-IDF + cosine similarity
Tagline Short text comparison
Genres One-hot vector overlap
Actors Top cast similarity
Director Directorial match score
Language Exact language bonus
Numeric Year, vote_average, popularity

Weighted combination ensures franchise clustering:

WEIGHTS = {
"overview": 0.6, # thematic context
"tagline": 0.2, # light influence
"genres": 1.2, # strong franchise grouping
"actors": 1.3, # cast continuity
"director": 0.9, # stylistic consistency
"language": 0.1, # minor factor
"numeric": 0.5, # era + prominence
}

🧠 Architecture

<p align="center"> <img width="720" src="assets/architecture.png" alt="Architecture Diagram"/> </p>

Pipeline:

TMDB Loader
Downloads 5k–15k movies + full credits and caches them locally.

Feature Builder

TF-IDF vectors

One-hot encoder for genres

Top actors vector

Director vector

Numeric normalization

Similarity Engine
Cosine similarity per feature → weighted → normalized 0–1.

FastAPI Backend
/recommend?title=Inception&top_n=10

React Frontend
Smooth HSL similarity colors and Netflix-like match bars.

🎨 UI Highlights

Smooth similarity color gradient (0→1):

Green → Yellow → Orange → Red

Netflix-style similarity bar:

<p align="center"> <img width="500" src="assets/image.png"/> </p>

Example result:

Title: Star Wars: Episode V
Similarity: 0.912
Genres: 1.00
Actors: 0.86
Director: 1.00
Numeric: 0.77

🛠 Installation
1️⃣ Backend (FastAPI)
cd backend
python -m venv venv
./venv/Scripts/activate # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

Create .env:

TMDB_API_KEY=your_api_key_here

First run downloads the dataset.
Subsequent runs use tmdb_movies_cache.json for instant startup.

2️⃣ Frontend (React + Vite)
cd frontend
npm install
npm run dev

Runs on:
👉 http://localhost:5173/

📡 API
GET /recommend

Returns similar movies:

/recommend?title=Inception&top_n=10

GET /health

Shows dataset size:

{
"status": "ok",
"movies_loaded": 8432
}

GET /titles?limit=50

Lists sample movie titles.

📁 Project Structure
backend/
│ main.py
│ recommend.py
│ tmdb_loader.py
│ tmdb_movies_cache.json
│
frontend/
│ src/
│ App.jsx
│ api/backend.js
│ components/
│
assets/
│ preview.png
│ architecture.png
│ bar_example.png

📊 Example JSON Response
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

📌 Future Improvements

Hybrid collaborative filtering

User profiles + personalization

BERT/SBERT sentence similarity for overviews

Poster-based similarity using CNN embeddings

Real-time search autocomplete

Recommendation visualizations (clusters, t-SNE, PCA)
