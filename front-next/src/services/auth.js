const API_URL = "http://127.0.0.1:8000";

export const login = async (username, password) => {

  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
      username: username,
      password: password
    })
  });

  if (!response.ok) {
    throw new Error("Credenciales incorrectas");
  }

  const data = await response.json();

  console.log("LOGIN RESPONSE:", data)

  localStorage.setItem("token", data.access_token);
  localStorage.setItem("role", data.role || "");

  return data;
};