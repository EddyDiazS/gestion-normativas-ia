const API_URL = "http://127.0.0.1:8000";

export const sendQuestion = async (question, session_id) => {

  const token = localStorage.getItem("token");

  const response = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      question: question,
      top_k: 5,
      session_id: session_id
    }),
  });

  if (!response.ok) {
    throw new Error(response.status === 401 ? "Unauthorized" : "Error en la API");
  }

  return response.json();
};

export const getChatHistory = async (session_id) => {

  const token = localStorage.getItem("token");
  const response = await fetch(`${API_URL}/chat/history?session_id=${session_id}`, {
    headers: {Authorization: `Bearer ${token}`}
  });

  if (!response.ok) return [];
  return response.json();
    
  }

export const getChatSessions = async () => {
  const token = localStorage.getItem("token");
  const response = await fetch(`${API_URL}/chat/sessions`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  if (!response.ok) return [];
  return response.json();
};