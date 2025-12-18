import UploadBox from "../components/UploadBox";
import ChatBox from "../components/ChatBox";

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold mb-6">
        🧠 Enterprise AI Knowledge System
      </h1>

      <UploadBox />
      <ChatBox />
    </div>
  );
}
