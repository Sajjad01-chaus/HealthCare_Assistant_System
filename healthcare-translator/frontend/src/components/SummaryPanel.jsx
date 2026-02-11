import { useState } from "react";
import { generateSummary } from "../services/api";

export default function SummaryPanel({ conversationId, onClose }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await generateSummary(conversationId);
      setSummary(result);
    } catch (err) {
      setError("Failed to generate summary. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Simple markdown-like rendering for the summary
  const renderSummary = (text) => {
    return text.split("\n").map((line, i) => {
      if (line.startsWith("## ")) {
        return (
          <h3 key={i} className="text-base font-bold text-slate-800 mt-4 mb-2 flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
            {line.replace("## ", "")}
          </h3>
        );
      }
      if (line.startsWith("- ")) {
        const content = line.replace("- ", "");
        const hasWarning = content.includes("⚠️");
        return (
          <p key={i} className={`text-sm ml-4 mb-1 ${hasWarning ? "text-amber-700 font-medium" : "text-slate-600"}`}>
            • {content}
          </p>
        );
      }
      if (line.trim() === "") return <div key={i} className="h-2" />;
      return <p key={i} className="text-sm text-slate-600 mb-1">{line}</p>;
    });
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-white text-lg">
              📋
            </div>
            <div>
              <h2 className="font-bold text-slate-800">Medical Summary</h2>
              <p className="text-xs text-slate-400">AI-generated clinical overview</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-500 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {!summary && !loading && !error && (
            <div className="text-center py-12">
              <div className="text-5xl mb-4">🤖</div>
              <h3 className="font-semibold text-slate-700 mb-2">Generate Medical Summary</h3>
              <p className="text-sm text-slate-400 mb-6 max-w-sm mx-auto">
                AI will analyze the conversation and extract key medical information including symptoms, diagnoses, medications, and follow-up actions.
              </p>
              <button
                onClick={handleGenerate}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/25 transition-all"
              >
                Generate Summary
              </button>
            </div>
          )}

          {loading && (
            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-sm text-slate-500">Analyzing conversation...</p>
              <p className="text-xs text-slate-400 mt-1">Extracting medical information with AI</p>
            </div>
          )}

          {error && (
            <div className="text-center py-12">
              <div className="text-4xl mb-3">⚠️</div>
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={handleGenerate}
                className="px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200 transition-colors"
              >
                Retry
              </button>
            </div>
          )}

          {summary && (
            <div>
              <div className="bg-blue-50 rounded-xl p-3 mb-4">
                <p className="text-xs text-blue-600 font-medium">
                  Generated on {new Date(summary.created_at).toLocaleString()}
                </p>
              </div>
              {renderSummary(summary.summary_text)}
            </div>
          )}
        </div>

        {/* Footer */}
        {summary && (
          <div className="px-6 py-3 border-t border-slate-200 flex justify-between">
            <button
              onClick={handleGenerate}
              className="px-4 py-2 bg-slate-100 text-slate-600 rounded-lg text-sm hover:bg-slate-200 transition-colors"
            >
              🔄 Regenerate
            </button>
            <button
              onClick={() => {
                navigator.clipboard.writeText(summary.summary_text);
              }}
              className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm hover:bg-blue-200 transition-colors"
            >
              📋 Copy to Clipboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
