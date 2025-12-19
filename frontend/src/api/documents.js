// ✅ Railway backend (PUBLIC)
const API_BASE = "https://enterprise-ai-knowledge-system-production.up.railway.app/api/v1";

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
      let errorMessage = "Upload failed";
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        errorMessage = `Server error (${response.status})`;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (err) {
    throw new Error(
      "Cannot connect to backend. Backend URL not reachable."
    );
  }
}
