// Correct base URL with /api/v1 prefix
const API_BASE = "http://localhost:8001/api/v1";
// Or use 127.0.0.1 if you prefer
// const API_BASE = "http://127.0.0.1:8001/api/v1";

export async function uploadDocument(file) {
  if (!file) {
    throw new Error("No file provided");
  }

  const formData = new FormData();
  formData.append("file", file); // Key must be "file" to match FastAPI UploadFile

  try {
    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData,
      // DO NOT set Content-Type! Browser sets it correctly with boundary
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
    // Network errors, CORS, etc.
    if (err.name === "TypeError" && err.message.includes("Failed to fetch")) {
      throw new Error("Cannot connect to backend. Is the server running on port 8001?");
    }
    throw err; // Re-throw with original message
  }
}