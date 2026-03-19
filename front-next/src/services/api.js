const API_URL = "http://127.0.0.1:8000";

export const sendQuestion = async (question) => {

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
      session_id: "react-session"
    }),
  });

  if (!response.ok) {
    throw new Error("Error en la API");
  }

  return response.json();
};