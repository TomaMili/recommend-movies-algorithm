// src/App.jsx
import { useState } from "react";
import "./index.css";
import { getRecommendations } from "./api/backend";

function App() {
  const [query, setQuery] = useState("");
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    setError("");
    setRecs([]);

    if (!query.trim()) return;

    try {
      setLoading(true);
      const results = await getRecommendations(query.trim(), 10);
      setRecs(results);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold mb-4 text-center">
        Movie Recommender (Backend + TMDB)
      </h1>

      <form onSubmit={handleSearch} className="flex gap-2 w-full max-w-xl mb-6">
        <input
          type="text"
          placeholder="Enter a movie title..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 px-3 py-2 rounded-md bg-slate-800 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          className="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 font-semibold"
          disabled={loading}
        >
          {loading ? "Loading..." : "Recommend"}
        </button>
      </form>

      {error && <p className="text-red-400 mb-4 text-sm">{error}</p>}

      {recs.length > 0 && (
        <div className="w-full max-w-5xl">
          <h2 className="text-xl font-semibold mb-3">
            Recommendations for:{" "}
            <span className="text-indigo-400">{query}</span>
          </h2>
          <ul className="space-y-2">
            {recs.map((movie, i) => (
              <li
                key={movie.id ?? movie.title + i}
                className="bg-slate-900 rounded-lg p-4 flex flex-col gap-2"
              >
                {/* Header: rank, title, main similarity score */}
                <div className="flex justify-between items-baseline gap-2">
                  <div>
                    <span className="text-sm text-slate-400 mr-2">
                      #{i + 1}
                    </span>
                    <span className="font-semibold">{movie.title}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-slate-400 mr-1">Similarity:</span>
                    <span className="font-semibold text-indigo-400">
                      {movie.similarity_score?.toFixed(3)}
                    </span>
                  </div>
                </div>

                {/* Optional: year & rating from TMDB data itself */}
                <div className="text-xs text-slate-400">
                  Year: {movie.release_year ?? "N/A"} · Vote avg:{" "}
                  {movie.vote_average ?? "N/A"} · Popularity:{" "}
                  {movie.popularity?.toFixed?.(1) ?? "N/A"}
                </div>

                {/* Feature scores grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-x-4 gap-y-1 text-xs text-slate-300 mt-1">
                  <div>
                    <span className="text-slate-400">Genres:</span>{" "}
                    {movie.genres_score?.toFixed?.(3) ?? "—"}
                  </div>
                  <div>
                    <span className="text-slate-400">Actors:</span>{" "}
                    {movie.actors_score?.toFixed?.(3) ?? "—"}
                  </div>
                  <div>
                    <span className="text-slate-400">Director:</span>{" "}
                    {movie.director_score?.toFixed?.(3) ?? "—"}
                  </div>
                  <div>
                    <span className="text-slate-400">Tagline:</span>{" "}
                    {movie.tagline_score?.toFixed?.(3) ?? "—"}
                  </div>
                  <div>
                    <span className="text-slate-400">Language:</span>{" "}
                    {movie.language_score?.toFixed?.(3) ?? "—"}
                  </div>
                  <div>
                    <span className="text-slate-400">Release year:</span>{" "}
                    {movie.release_year_score?.toFixed?.(3) ?? "—"}
                  </div>
                  <div>
                    <span className="text-slate-400">Popularity:</span>{" "}
                    {movie.popularity_score?.toFixed?.(3) ?? "—"}
                  </div>
                  <div>
                    <span className="text-slate-400">Vote avg:</span>{" "}
                    {movie.vote_average_score?.toFixed?.(3) ?? "—"}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
