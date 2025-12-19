const API_BASE = import.meta.env.VITE_API_URL;

export async function uploadDocument(file) {
  if (!file) {
    throw new Error("No file provided");
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Upload failed. Backend unreachable.");
  }

  return await response.json();
}
