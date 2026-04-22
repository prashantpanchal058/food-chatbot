import { useState, useRef, useEffect } from "react";

const API_URL = "http://127.0.0.1:8000/chat";

export default function App() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "👋 Welcome! Type 'menu' to see food options 🍔" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userMsg.text })
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.response }
      ]);

    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "⚠️ Server error. Try again." }
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md h-[600px] bg-gray-800 rounded-xl flex flex-col shadow-lg">

        {/* HEADER */}
        <div className="p-4 text-white font-bold text-center border-b border-gray-700">
          🍔 Food Ordering Bot
        </div>

        {/* CHAT AREA */}
        <div className="flex-1 overflow-y-auto p-3 space-y-3">

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`px-4 py-2 rounded-lg max-w-[75%] text-sm whitespace-pre-line ${
                  msg.role === "user"
                    ? "bg-green-500 text-white"
                    : "bg-gray-700 text-gray-200"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {loading && (
            <div className="text-gray-400 text-sm">Bot is typing...</div>
          )}

          <div ref={bottomRef}></div>
        </div>

        {/* INPUT */}
        <div className="p-3 border-t border-gray-700 flex gap-2">

          <input
            className="flex-1 p-2 rounded-lg bg-gray-700 text-white outline-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type 'menu', 'order', 'checkout'..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />

          <button
            onClick={sendMessage}
            disabled={loading}
            className="bg-green-500 hover:bg-green-600 text-white px-4 rounded-lg disabled:opacity-50"
          >
            Send
          </button>

        </div>

      </div>
    </div>
  );
}