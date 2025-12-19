// ✅ PRODUCTION BACKEND (Railway)
// This works on laptop, mobile, anywhere
const API_BASE = "https://enterprise-ai-knowledge-system-production.up.railway.app/api/v1";

/**
 * Upload a document to the backend
 * @param {File} file
 */
export async function uploadDocument(file) {
  if (!file) {
    throw new Error("No file provided");
  }

  const formData = new FormData();
  // Must be "file" to match FastAPI UploadFile
  formData.append("file", file);

  try {
    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData,
      // ❌ DO NOT set Content-Type manually
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
  } catch (error) {
    // Network / CORS / backend unreachable
    if (error.name === "TypeError") {
      throw new Error(
        "Cannot connect to backend. Please check backend URL or network."
      );
    }
    throw error;
  }
}
