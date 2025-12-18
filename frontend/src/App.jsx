import UploadBox from "./components/UploadBox";

import { askAI } from "./api/chat";
import { useState } from "react";

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleAsk() {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");

    try {
      const res = await askAI(question);
      setAnswer(res.answer || "No response received.");
    } catch (err) {
      setAnswer("❌ Failed to fetch AI response.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-slate-900 to-black px-6 py-10 text-white">
      <div className="max-w-7xl mx-auto bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-10 shadow-2xl">

        {/* HEADER */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-extrabold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
            Enterprise AI Knowledge System
          </h1>
          <p className="text-slate-400 mt-4 text-lg">
            Private RAG • Qdrant • Groq LLM • FastAPI • React
          </p>
        </header>

        {/* MAIN GRID */}
        <div className="grid lg:grid-cols-3 gap-10">

          {/* LEFT: DOCUMENT UPLOAD */}
          <div className="lg:col-span-1">
            <UploadBox />
          </div>

          {/* MIDDLE: CHAT */}
          <div className="lg:col-span-1 space-y-4">
            <h2 className="text-xl font-semibold text-cyan-300">
              Ask your documents
            </h2>

            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask anything from your enterprise knowledge..."
              className="w-full h-40 rounded-xl bg-black/40 border border-white/10 p-4 text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />

            <button
              onClick={handleAsk}
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 font-semibold hover:opacity-90 transition disabled:opacity-50"
            >
              {loading ? "Thinking..." : "Ask AI"}
            </button>
          </div>

          {/* RIGHT: RESPONSE */}
          <div className="lg:col-span-1 bg-black/40 border border-white/10 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-purple-300 mb-4">
              AI Response
            </h2>

            <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
              {answer || "Your AI-generated answer will appear here."}
            </div>
          </div>
        </div>

        {/* FOOTER */}
        <footer className="text-center text-slate-500 text-sm mt-14">
          © 2025 Enterprise AI • Built with ❤️ using Python & React
        </footer>
      </div>
    </div>
  );
}
