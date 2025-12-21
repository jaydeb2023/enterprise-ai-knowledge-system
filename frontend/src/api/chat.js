// API base URL - uses VITE_API_URL environment variable in production (set in Vercel)
// Falls back to localhost for development
const API_BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

/**
 * Send a question to the AI backend and get the RAG response
 * @param {string} question - The user's question
 * @returns {Promise<Object>} - { answer: string }
 */
export async function askAI(question) {
  if (!question || question.trim() === "") {
    throw new Error("Please enter a question");
  }

  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query: question.trim() }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Failed to get AI response. Please try again.");
  }

  const data = await response.json();
  return data; // { answer: "..." }
}