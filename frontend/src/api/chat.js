// src/api/chat.js

const API_BASE = "http://127.0.0.1:8001/api/v1";

export async function askAI(question) {
  if (!question || typeof question !== "string" || question.trim() === "") {
    throw new Error("Please enter a question");
  }

  try {
    const response = await fetch(`${API_BASE}/chat`, {  // ← FIXED: /chat not /chat/ask
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: question.trim(),  // Backend expects "query"
      }),
    });

    if (!response.ok) {
      let errorMessage = "Unknown error";
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || JSON.stringify(errorData);
      } catch {
        errorMessage = await response.text();
      }
      throw new Error(`AI Response Failed: ${response.status} - ${errorMessage}`);
    }

    const data = await response.json();

    // RAGService.answer_question likely returns dict with 'answer' key
    const answer = data.answer || data.response || data.message || JSON.stringify(data);

    return { answer };
  } catch (error) {
    if (error.name === "TypeError" && error.message.toLowerCase().includes("fetch")) {
      throw new Error("Cannot connect to backend. Is the server running on port 8001?");
    }
    throw error;
  }
}