import { useState } from "react";
import { searchMessages } from "../services/api";

export default function SearchBar({ conversationId, onClose }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await searchMessages(query, conversationId);
      setResults(data);
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Render highlighted context with **match** markers
  const renderHighlighted = (text) => {
    const parts = text.split(/\*\*(.*?)\*\*/g);
    return parts.map((part, i) =>
      i % 2 === 1 ? (
        <mark key={i} className="bg-yellow-200 text-yellow-900 px-0.5 rounded font-medium">
          {part}
        </mark>
      ) : (
        <span key={i}>{part}</span>
      )
    );
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl max-h-[80vh] flex flex-col">
        {/* Search header */}
        <div className="px-5 py-4 border-b border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-bold text-slate-800">🔍 Search Conversations</h2>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-500"
            >
              ✕
            </button>
          </div>
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search keywords or phrases..."
              autoFocus
              className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-5 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? "..." : "Search"}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto px-5 py-3">
          {results === null && (
            <div className="text-center py-12 text-slate-400 text-sm">
              Search across all conversation messages
            </div>
          )}

          {results && results.total_results === 0 && (
            <div className="text-center py-12">
              <div className="text-4xl mb-3">🔍</div>
              <p className="text-slate-500 text-sm">No results found for "{query}"</p>
            </div>
          )}

          {results && results.total_results > 0 && (
            <div>
              <p className="text-xs text-slate-400 mb-3">
                {results.total_results} result{results.total_results > 1 ? "s" : ""} found
              </p>
              {results.results.map((result, i) => (
                <div key={i} className="mb-3 p-3 rounded-xl bg-slate-50 border border-slate-100 hover:border-slate-200 transition-colors">
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                      result.role === "doctor"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-emerald-100 text-emerald-700"
                    }`}>
                      {result.role === "doctor" ? "🩺 Doctor" : "🧑 Patient"}
                    </span>
                    <span className="text-xs text-slate-400">
                      {new Date(result.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {renderHighlighted(result.match_context)}
                  </p>
                  {result.translated_text && (
                    <p className="text-xs text-slate-400 mt-1 italic truncate">
                      🌐 {result.translated_text}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
