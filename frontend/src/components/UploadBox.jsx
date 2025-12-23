import { useState } from "react";
import { uploadDocument } from "../api/documents";

export default function UploadBox() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    setFile(selectedFile);
    if (selectedFile) {
      setStatus(
        `Selected: ${selectedFile.name} (${(
          selectedFile.size /
          1024 /
          1024
        ).toFixed(2)} MB)`
      );
    } else {
      setStatus("");
    }
  };

  async function handleUpload() {
    if (!file) {
      setStatus("❌ Please select a file first");
      return;
    }

    setIsUploading(true);
    setStatus("⏳ Uploading and processing document...");

    try {
      // 🔥 CAPTURE RESPONSE
      const res = await uploadDocument(file);

      // 🔥 STORE document_id (CRITICAL)
      if (res?.document_id) {
        localStorage.setItem("latest_document_id", res.document_id);
      }

      setStatus("✅ Document uploaded and indexed successfully!");
      setFile(null);
      document.querySelector('input[type="file"]').value = "";
    } catch (err) {
      console.error("Upload error:", err);
      setStatus(`❌ Upload failed: ${err.message || "Unknown error"}`);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div className="bg-black/40 border border-white/10 rounded-xl p-6 space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-cyan-300 mb-2">
          Upload Documents
        </h3>
        <p className="text-sm text-slate-400">
          Supported: PDF, DOCX, XLSX, PPTX, CSV, TXT, MD, Images (JPG, PNG)
        </p>
      </div>

      <input
        type="file"
        accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.csv,.txt,.md,.jpg,.jpeg,.png,.tiff"
        onChange={handleFileChange}
        disabled={isUploading}
        className="block w-full text-sm text-slate-300 file:mr-4 file:py-3 file:px-6 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-cyan-600 file:to-purple-600 file:text-white hover:file:opacity-90 cursor-pointer"
      />

      <button
        onClick={handleUpload}
        disabled={!file || isUploading}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 font-semibold text-white hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isUploading ? "⏳ Processing..." : "Upload & Index"}
      </button>

      {status && (
        <p
          className={`mt-4 text-sm font-medium break-words ${
            status.startsWith("✅")
              ? "text-green-400"
              : status.startsWith("❌")
              ? "text-red-400"
              : "text-slate-300"
          }`}
        >
          {status}
        </p>
      )}
    </div>
  );
}
