import { useState } from "react";
import "./index.css";
import { getRecommendations } from "./api/backend";

// Clamp score to [0, 1]
const clamp01 = (value) => {
  if (value == null || Number.isNaN(value)) return 0;
  return Math.max(0, Math.min(1, value));
};

// Map similarity score (0–1) to hue: 0 = red, 0.5 = yellow, 1 = green
const getSimilarityHue = (score) => {
  const s = clamp01(score);
  return s * 120; // 0 (red) -> 120 (green)
};

// Text color style (smooth HSL)
const getSimilarityTextStyle = (score) => {
  const hue = getSimilarityHue(score);
  return {
    color: `hsl(${hue} 85% 55%)`,
  };
};

// Progress bar style: width + gradient (red -> yellow -> green)
const getSimilarityBarStyle = (score) => {
  const s = clamp01(score);
  return {
    width: `${s * 100}%`,
    background:
      "linear-gradient(to right, hsl(0 90% 55%), hsl(60 90% 55%), hsl(120 90% 55%))",
  };
};

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
      const results = await getRecommendations(query.trim(), 20);
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
      <h1 className="text-3xl font-bold mb-4 text-center">Movie Recommender</h1>

      <form onSubmit={handleSearch} className="flex gap-2 w-full max-w-xl mb-6">
        <input
          type="text"
          placeholder="Enter a movie title..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 px-3 py-2 rounded-md bg-slate-800 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-300"
        />
        <button
          type="submit"
          className="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 font-semibold transition-all duration-300 cursor-pointer"
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
                    <span
                      className={`text-sm ${
                        i > 2
                          ? "text-slate-400"
                          : i === 0
                          ? "text-yellow-400"
                          : i === 1
                          ? "text-slate-200"
                          : "text-yellow-700"
                      } mr-2 font-bold text-xl`}
                    >
                      #{i + 1}
                    </span>
                    <span className="font-semibold">{movie.title}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-slate-400 mr-1">Similarity:</span>
                    <span
                      className="font-semibold"
                      style={getSimilarityTextStyle(movie.similarity_score)}
                    >
                      {(movie.similarity_score?.toFixed(3) > 1
                        ? movie.similarity_score
                        : movie.similarity_score
                      ).toFixed(3)}
                    </span>
                  </div>
                </div>
                {/* Similarity progress bar (Netflix style) */}
                <div className="mt-1 w-full max-w-xs">
                  <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-300"
                      style={getSimilarityBarStyle(movie.similarity_score)}
                    />
                  </div>
                  <div className="mt-1 text-[10px] text-slate-400">
                    {(clamp01(movie.similarity_score) * 100).toFixed(0)}% match
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
