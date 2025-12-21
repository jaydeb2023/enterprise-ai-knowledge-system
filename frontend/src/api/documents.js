// API base URL - uses VITE_API_URL environment variable in production (set in Vercel)
// Falls back to localhost for development
const API_BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

/**
 * Upload a document (PDF, DOCX, XLSX, PPTX, CSV, TXT, MD, images, etc.)
 * @param {File} file - The file object from input
 * @returns {Promise<Object>} - Success message from backend
 */
export async function uploadDocument(file) {
  if (!file) {
    throw new Error("No file selected");
  }

  const formData = new FormData();
  formData.append("file", file);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout

  try {
    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Document upload failed. Please try again.");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === "AbortError") {
      throw new Error("Upload timed out. Try a smaller file or better network.");
    }
    throw error;
  }
}