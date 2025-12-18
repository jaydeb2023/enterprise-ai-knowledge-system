import { useState } from "react";
import { askQuestion } from "../api/chat";

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  async function send() {
    if (!input) return;

    const userMsg = { role: "user", text: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");

    const res = await askQuestion(input);

    const botMsg = { role: "bot", text: res.answer };
    setMessages((m) => [...m, botMsg]);
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 w-full mt-6">
      <h2 className="text-xl font-semibold mb-3">💬 Ask Your Knowledge</h2>

      <div className="h-64 overflow-y-auto border p-3 mb-3">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`mb-2 ${
              m.role === "user" ? "text-right" : "text-left"
            }`}
          >
            <span
              className={`inline-block px-3 py-2 rounded ${
                m.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200"
              }`}
            >
              {m.text}
            </span>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 border rounded px-3"
          placeholder="Ask a question..."
        />
        <button
          onClick={send}
          className="bg-green-600 text-white px-4 rounded"
        >
          Send
        </button>
      </div>
    </div>
  );
}
