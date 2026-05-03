"use client";

import { useState, useEffect, useRef } from "react";
import { sendQuestion, getChatHistory, getChatSessions } from "../services/api";
import { useRouter } from "next/navigation";
import Message from "../services/message";
import Input from "./input";


function Chat() {
  const router = useRouter();

  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);
  const activeChat = chats.find(chat => chat.id === activeChatId);

  //  Verificar autenticación
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
    getChatSessions().then(sessions => {
      if (sessions.length === 0) {
        const newChat = { id: Date.now(), title: "Nuevo chat", messages: [], session_id: crypto.randomUUID() };
        setChats([newChat]);
        setActiveChatId(newChat.id);
        return;
      }
      const loaded = sessions.map((s, i) => ({
        id: i + 1, title: s.title, messages: [], session_id: s.session_id
      }));
      setChats(loaded);
      setActiveChatId(loaded[0].id);
    });
  }, [router]);

  //  Scroll automático
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat?.messages]);

  useEffect(() => {
    if (!activeChatId || chats.length === 0) return;
    const chat = chats.find(c => c.id === activeChatId);
    if (!chat?.session_id) return;
    if (chat.messages.length > 0) return; // ya cargado, no recargar

    getChatHistory(chat.session_id).then(msgs => {
      if (!Array.isArray(msgs) || msgs.length === 0) return;
      setChats(prev => prev.map(c => c.id !== activeChatId ? c : {
        ...c,
        messages: msgs.map(m => ({ type: m.role === "user" ? "user" : "bot", text: m.content }))
      }));
    });
  }, [activeChatId, chats.length]);

  // Obtiene el session_id del chat activo (UUID único por conversación), o genera uno nuevo si no existe (para nuevos chats)
  const getSessionId = (chatId) => {
    const chat = chats.find(c => c.id === chatId);
    return chat?.session_id || crypto.randomUUID();
  };

  // Enviar pregunta
  const typeMessage = (text, chatId, currentChats) => {
    const words = text.split(" ")
    let current = ""
    words.forEach((word, i) => {
      setTimeout(() => {
        current += (i === 0 ? "" : " ") + word
        setChats(prev => prev.map(chat => {
          if (chat.id !== chatId) return chat
          const msgs = [...chat.messages]
          msgs[msgs.length - 1] = { type: "bot", text: current }
          return { ...chat, messages: msgs }
        }))
      }, i * 30) // 30ms por palabra
    })
  }

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
      const data = await sendQuestion(text, getSessionId(activeChatId));

      const withEmpty = updatedChats.map(chat => {
        if (chat.id !== activeChatId) return chat
        return { ...chat, messages: [...chat.messages, { type: "bot", text: "" }] }
      })
      setChats(withEmpty)
      setLoading(false)

      // Luego escribe palabra por palabra
      typeMessage(data.answer, activeChatId, withEmpty)
      return
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
          setLoading(false);
    }
  };

  //  Crea un nuevo chat vacío con session_id único para que aparezca en el sidebar
  const createNewChat = () => {
    const newChat = { id: Date.now(), title: "Nuevo chat", messages: [], session_id: crypto.randomUUID() };
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
          Chat IA Normativas y Dudas Academicas
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