import { useState } from "react";

const API_BASE = "https://backend.icyocean-23544f11.swedencentral.azurecontainerapps.io";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          session_id: sessionId,
        }),
      });

      const data = await response.json();

      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply, sources: data.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: could not reach backend." },
      ]);
    } finally {
      setInput("");
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Enterprise AI Knowledge Assistant</h2>

      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: 8,
          padding: 16,
          height: 400,
          overflowY: "auto",
          marginBottom: 16,
        }}
      >
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 12 }}>
            <strong>{m.role === "user" ? "You" : "Assistant"}:</strong> {m.content}
            {m.sources && m.sources.length > 0 && (
              <div style={{ fontSize: 12, color: "#666" }}>
                Source: {m.sources.join(", ")}
              </div>
            )}
          </div>
        ))}
        {loading && <div style={{ color: "#888" }}>Thinking...</div>}
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          style={{ flex: 1, padding: 8 }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question..."
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>

      {sessionId && (
        <div style={{ fontSize: 12, color: "#999", marginTop: 8 }}>
          Session: {sessionId}
        </div>
      )}
    </div>
  );
}

export default App;
