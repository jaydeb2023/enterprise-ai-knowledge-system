const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "https://enterprise-ai-knowledge-system-production.up.railway.app/api/v1";

export async function uploadDocument(file) {
  if (!file) {
    throw new Error("No file provided");
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Upload failed");
    }

    return await response.json();
  } catch (err) {
    throw new Error("Cannot connect to backend. Please try again.");
  }
}
