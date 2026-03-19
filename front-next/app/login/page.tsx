"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Login() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password })
      });

      const data = await response.json();

      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify({
          username: username,
          role: data.role
        }));
        router.push("/chat");
      } else {
        setError("Usuario o contraseña incorrectos.");
      }
    } catch {
      setError("No se pudo conectar con el servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">

      {/* Glow de fondo */}
      <div className="login-glow" />

      {/* Decoración extra de fondo */}
      <div style={{
        position: "absolute",
        width: 300,
        height: 300,
        borderRadius: "50%",
        background: "radial-gradient(circle, rgba(124,92,252,0.06) 0%, transparent 70%)",
        top: "20%",
        right: "15%",
        pointerEvents: "none"
      }} />

      <div className="login-card">

        {/* Logo */}
        <div className="login-logo">📚</div>

        {/* Títulos */}
        <h1 className="login-title">Gestión y Consulta de Normativas con IA</h1>
        <p className="login-subtitle">
          Inicia sesión con tus credenciales de acceso
        </p>

        {/* Formulario */}
        <form onSubmit={handleLogin} className="login-form">

          {/* Username */}
          <div>
            <label className="form-label">Usuario</label>
            <div style={{ position: "relative" }}>
              <span style={{
                position: "absolute", left: 14, top: "50%",
                transform: "translateY(-50%)",
                fontSize: 16, pointerEvents: "none", opacity: 0.5
              }}></span>
              <input
                type="text"
                placeholder="Nombre de usuario"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="form-input"
                style={{ paddingLeft: 42 }}
                required
                autoComplete="username"
                autoFocus
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="form-label">Contraseña</label>
            <div style={{ position: "relative" }}>
              <span style={{
                position: "absolute", left: 14, top: "50%",
                transform: "translateY(-50%)",
                fontSize: 16, pointerEvents: "none", opacity: 0.5
              }}></span>
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-input"
                style={{ paddingLeft: 42, paddingRight: 48 }}
                required
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: "absolute", right: 12, top: "50%",
                  transform: "translateY(-50%)",
                  background: "none", border: "none",
                  cursor: "pointer", color: "var(--text-3)",
                  fontSize: 16, padding: 4,
                  transition: "color 0.2s"
                }}
                tabIndex={-1}
              >
                {showPassword ? "🙈" : "👁️"}
              </button>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="login-error">
              ⚠️ {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading || !username.trim() || !password.trim()}
            className="login-btn"
            style={{ marginTop: 4 }}
          >
            {loading ? (
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
                <span style={{
                  width: 16, height: 16,
                  border: "2px solid rgba(255,255,255,0.3)",
                  borderTopColor: "#fff",
                  borderRadius: "50%",
                  display: "inline-block",
                  animation: "spin 0.75s linear infinite"
                }} />
                Verificando…
              </span>
            ) : "Iniciar Sesión"}
          </button>

        </form>

        {/* Footer */}
        <p style={{
          textAlign: "center",
          fontSize: 12,
          color: "var(--text-3)",
          marginTop: 24,
          paddingTop: 20,
          borderTop: "1px solid var(--border)"
        }}>
          Sistema de consulta de normativas institucionales
        </p>

      </div>
    </main>
  );
}
