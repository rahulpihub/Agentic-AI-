import { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/ping/")
      .then((res) => setMessage(res.data.message))
      .catch((err) => setMessage("❌ Failed to connect to backend"));
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center px-4">
      <h1 className="text-3xl font-bold text-blue-600 mb-4">
        🎯 Vite + Django + Tailwind Connected!
      </h1>
      <p className="text-lg text-gray-800">{message}</p>
    </div>
  );
}

export default App;
