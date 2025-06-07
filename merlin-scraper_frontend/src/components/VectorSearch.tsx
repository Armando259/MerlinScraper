import React, { useState, FormEvent, useEffect } from "react";

interface Result {
  similarity: number;
  text: string;
  course: string;
  task_id: string;
  userid: string;
}

function VectorSearch() {
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<Result[]>([]);
  const [responseQuery, setResponseQuery] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setResults([]);
    setResponseQuery("");
    setLoading(true);
    try {
      const resp = await fetch("http://localhost:3000/vector_search", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      setLoading(false);
      if (!resp.ok) {
        throw new Error("Došlo je do greške u pretrazi!");
      }
      const data = await resp.json();
      setResults(data.results || []);
      setResponseQuery(data.query || "");
      // Debug:
      console.log("Vector search results:", data.results);
    } catch (err) {
      setLoading(false);
      setError("Greška pri pretrazi!");
    }
  };

  useEffect(() => {
    if (results.length > 0) {
      console.log("Rezultati iz backenda:", results);
    }
  }, [results]);

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "30px auto",
        padding: 24,
        background: "#f7fafc",
        borderRadius: 18,
        boxShadow: "0 2px 18px #e0e6ed",
      }}
    >
      <h2 style={{ color: "#1657b7", marginBottom: 18 }}>
        🔍 Vektorsko pretraživanje taskova
      </h2>
      <form
        onSubmit={handleSearch}
        style={{ display: "flex", gap: 8, marginBottom: 20 }}
      >
        <input
          style={{
            flex: 1,
            padding: "10px 12px",
            borderRadius: 12,
            border: "1px solid #b0c4de",
            fontSize: 16,
          }}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Unesi tekst za pretragu..."
        />
        <button
          style={{
            padding: "10px 20px",
            borderRadius: 12,
            border: "none",
            background: "#1657b7",
            color: "#fff",
            fontWeight: 600,
            fontSize: 16,
            cursor: "pointer",
          }}
          type="submit"
          disabled={loading}
        >
          {loading ? "Pretražujem..." : "Pretraži"}
        </button>
      </form>
      {error && (
        <div style={{ color: "#b00020", marginBottom: 18 }}>{error}</div>
      )}
      {!loading && results.length === 0 && responseQuery && (
        <div style={{ color: "#888", fontStyle: "italic", marginTop: 10 }}>
          Nema rezultata za "{responseQuery}".
        </div>
      )}
      {!loading && responseQuery && results.length > 0 && (
        <div
          style={{
            margin: "30px 0 15px 0",
            fontWeight: 500,
            color: "#224",
            fontSize: 17,
            borderBottom: "1px solid #e0e0e0",
            paddingBottom: 7,
          }}
        >
          Odgovor na upit:{" "}
          <span style={{ color: "#1657b7" }}>{responseQuery}</span>
        </div>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
        {results.map((res, idx) => (
          <div
            key={res.task_id + idx}
            style={{
              borderRadius: 16,
              boxShadow: "0 1px 8px #e0e6ed",
              background: "#fff",
              padding: 16,
              border: "1px solid #ebf1fa",
              transition: "box-shadow 0.2s",
              position: "relative",
            }}
          >
            <span
              style={{
                position: "absolute",
                top: 12,
                right: 18,
                fontSize: 12,
                color: "#757575",
                background: "#e8f0fe",
                padding: "2px 10px",
                borderRadius: 8,
                fontWeight: 600,
              }}
            >
              {(res.similarity * 100).toFixed(1)}%
            </span>
            <div style={{ fontWeight: 600, marginBottom: 6, color: "#234b93" }}>
              {res.course && res.course.trim() !== ""
                ? res.course
                : <span style={{ color: "#888" }}>N/A kolegij</span>}
            </div>
            <div style={{ marginBottom: 6, color: "#334" }}>{res.text}</div>
            <div style={{ fontSize: 12, color: "#bbb" }}>
              <span>task ID: {res.task_id}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default VectorSearch;
