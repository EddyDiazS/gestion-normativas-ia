"use client";

import { useState, useEffect, useRef } from "react";
import { sendQuestion } from "../services/api";
import { useRouter } from "next/navigation";
import Message from "../services/message";
import Input from "./input";

function Chat() {
  const router = useRouter();

  const [chats, setChats] = useState([
    { id: 1, title: "Nuevo chat", messages: [] }
  ]);

  const [activeChatId, setActiveChatId] = useState(1);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);
  const activeChat = chats.find(chat => chat.id === activeChatId);

  //  Verificar autenticación
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) router.push("/login");
  }, [router]);

  //  Scroll automático
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat?.messages]);

  // Enviar pregunta
  const handleSend = async (text) => {
    if (!text.trim()) return;

    const updatedChats = chats.map(chat => {
      if (chat.id !== activeChatId) return chat;
      const isFirstMessage = chat.messages.length === 0;
      return {
        ...chat,
        title: isFirstMessage ? text.slice(0, 30) + (text.length > 30 ? "…" : "") : chat.title,
        messages: [...chat.messages, { type: "user", text }]
      };
    });

    setChats(updatedChats);
    setLoading(true);

    try {
      const data = await sendQuestion(text);

      setChats(updatedChats.map(chat => {
        if (chat.id !== activeChatId) return chat;
        return { ...chat, messages: [...chat.messages, { type: "bot", text: data.answer }] };
      }));
    } catch (error) {
      console.error(error);

      if (error.message === "Unauthorized") {
        localStorage.removeItem("token");
        router.push("/login");
        return;
      }

      setChats(updatedChats.map(chat => {
        if (chat.id !== activeChatId) return chat;
        return { ...chat, messages: [...chat.messages, { type: "bot", text: "Error consultando la API." }] };
      }));
    }

    setLoading(false);
  };

  //  Nuevo chat
  const createNewChat = () => {
    const newChat = { id: Date.now(), title: "Nuevo chat", messages: [] };
    setChats([newChat, ...chats]);
    setActiveChatId(newChat.id);
  };

  //  Logout
  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  return (
    <div className="app-container">

      {/* Sidebar */}
      <div className="sidebar">

        <div className="sidebar-header">
          <div className="sidebar-logo">📚</div>
          <span className="sidebar-title">Chats</span>
        </div>

        <button className="new-chat-btn" onClick={createNewChat}>
          Nuevo chat
        </button>

        <div className="chat-list">
          <div className="chat-list-label">Conversaciones</div>
          {chats.map(chat => (
            <div
              key={chat.id}
              className={`chat-item ${chat.id === activeChatId ? "active" : ""}`}
              onClick={() => setActiveChatId(chat.id)}
            >
              {chat.title}
            </div>
          ))}
        </div>

        <button className="logout-btn" onClick={handleLogout}>
          Cerrar sesión
        </button>

      </div>

      {/* Chat principal */}
      <div className="chat-main">

        <div className="chat-header">
          Chat IA Normativas
        </div>

        <div className="messages">

          {activeChat?.messages.length === 0 && !loading && (
            <div className="empty-state">
              <div className="empty-state-icon">📋</div>
              <h3>Consulta las normativas</h3>
              <p>Haz una pregunta sobre las normativas y el sistema buscará la información más relevante.</p>
            </div>
          )}

          {activeChat?.messages.map((msg, index) => (
            <Message key={index} type={msg.type} text={msg.text} />
          ))}

          {loading && (
            <div className="message-bot loading" style={{ maxWidth: 760, margin: "0 auto" }}>
              <div className="typing-indicator">
                <span /><span /><span />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <Input onSend={handleSend} />

      </div>
    </div>
  );
}

export default Chat;