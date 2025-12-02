const BASE_URL = "http://localhost:8000";

export async function getRecommendations(title, topN = 8) {
  const url = new URL(`${BASE_URL}/recommend`);
  url.searchParams.set("title", title);
  url.searchParams.set("top_n", String(topN));

  const res = await fetch(url.toString());
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(`Backend error (${res.status}): ${msg}`);
  }

  const data = await res.json();
  return data.results;
}
