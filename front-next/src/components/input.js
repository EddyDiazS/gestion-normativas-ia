"use client";
import { useState } from "react";

export default function Input({ onSend }) {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    
    if (!message.trim()) return;
    
    onSend(message);
    setMessage(""); 
  };

  return (
    <div className="input-container">
      <div className="input-box">
        <input
          type="text"
          className="input-field"
          placeholder="Escribe tu mensaje..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          // Tu versión de una sola línea es mucho más limpia y profesional
          onKeyDown={(e) => e.key === "Enter" && handleSend()} 
        />
        <button 
          className="send-button" 
          onClick={handleSend}
          disabled={!message.trim()} // Deshabilita el botón si no hay texto
        >
          Enviar
        </button>
      </div>
    </div>
  );
}