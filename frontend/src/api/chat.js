const API_BASE = "https://enterprise-ai-knowledge-system-production.up.railway.app";

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
    throw new Error(text || "AI request failed");
  }

  return await response.json();
}
