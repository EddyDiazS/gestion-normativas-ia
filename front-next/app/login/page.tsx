/*#D4006A*/
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useEffect } from "react";


export default function Login() {


  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);


  const redesSociales = [
    {
      nombre: "Facebook",
      logoPath: "/facebook6.png",
      link: "https://www.facebook.com/U.KONRADLORENZ/?locale=es_LA"
    },
    {
      nombre: "Youtube",
      logoPath: "/youtube.webp",
      link: "https://www.youtube.com/channel/UCUB2pNEFswCAXYBfQsDYZ9w"
    },
    {
      nombre: "Instagram",
      logoPath: "/instagram2.png",
      link: "https://www.instagram.com/ukonradlorenz"
    },
    {
      nombre: "Pagina Web",
      logoPath: "/web2.png",
      link: "https://www.konradlorenz.edu.co/"
    }
  ];
  const toggleTheme = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);

    if (newMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }

    localStorage.setItem("theme", newMode ? "dark" : "light");
  };

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {
      document.documentElement.classList.add("dark");
      setDarkMode(true);
    }
  }, []);


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
        localStorage.setItem("user", JSON.stringify({ username: data.username, role: data.role }));
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
    <main style={{
      minHeight: "100vh",
      background: "var(--bg)",
      display: "flex",
      position: "relative",
      overflow: "hidden",
    }}>

      {/* ── Franja superior 4 colores ── */}
      <div style={{
        position: "fixed", top: 0, left: 0, right: 0, height: 4, zIndex: 100,
        background: "linear-gradient(90deg, #D4006A 0% 25%, #F5A623 25% 50%, #4CAF50 50% 75%, #2196F3 75% 100%)"
      }} />

      {/* ── Panel izquierdo institucional ── */}
      <div style={{
        width: "45%",
        background: "#D4006A",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "60px 48px",
        position: "relative",
        overflow: "hidden",
      }}>
        {/* Círculos decorativos */}
        <div style={{
          position: "absolute", width: 400, height: 400, borderRadius: "50%",
          border: "1px solid rgba(255,255,255,0.1)",
          top: -100, right: -100,
        }} />
        <div style={{
          position: "absolute", width: 300, height: 300, borderRadius: "50%",
          border: "1px solid rgba(255,255,255,0.08)",
          bottom: -80, left: -80,
        }} />
        <div style={{
          position: "absolute", width: 200, height: 200, borderRadius: "50%",
          background: "rgba(0,0,0,0.1)",
          top: "40%", right: -60,
        }} />

        {/* Logo */}
        <div style={{ position: "relative", zIndex: 1, textAlign: "center" }}>
          <div style={{
            background: "rgba(255,255,255,1)",
            borderRadius: 20,
            padding: "21px 29px",
            marginBottom: 40,
            display: "inline-block",
            boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
          }}>
            <Image
              src="/Logo Konrad2.png"
              alt="Konrad Lorenz"
              width={230}
              height={80}
              style={{ objectFit: "contain" }}
              priority
            />
          </div>

          <h1 style={{
            fontFamily: "'Open Sans', sans-serif",
            fontSize: 38,
            fontWeight: 800,
            color: "#fff",
            lineHeight: 1.2,
            letterSpacing: "-0.5px",
            marginBottom: 16,
          }}>
            Konrad Lorenz:<br />
            <span style={{ opacity: 0.9 }}>1000 Días con IA</span>
          </h1>

          <p style={{
            color: "rgba(255,255,255,0.75)",
            fontSize: 15,
            lineHeight: 1.7,
            maxWidth: 340,
            margin: "0 auto",
          }}>
            |
            <br />
            Plataforma institucional de inteligencia artificial para consulta de normativas y analítica académica.
            <br />
            |
          </p>

          <div style={{ display: "flex", gap: "20px", justifyContent: "center" }}>
            {redesSociales.map((red) => (
              <a
                key={red.nombre}
                href={red.link}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "inline-block",
                  transition: "transform 0.2s ease-in-out",
                  cursor: "pointer"
                }}
              >

                <Image
                  src={red.logoPath}
                  alt={`Logo de ${red.nombre}`}
                  width={30}
                  height={30}
                  style={{ objectFit: "contain" }}
                />
              </a>
            ))}
          </div>

          {/* Stats decorativos */}
          <div style={{
            display: "flex", gap: 32, marginTop: 48,
            justifyContent: "center",
          }}>

          </div>
        </div>
      </div>

      {/* ── Panel derecho — formulario ── */}
      <div style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 48px",
        background: "var(--bg)",
      }}>

        <button
          onClick={toggleTheme}
          style={{
            position: "absolute",
            top: 20,
            right: 20,
            padding: "10px 14px",
            borderRadius: 20,
            border: "none",
            cursor: "pointer",
            background: "var(--border)",
            color: "var(--text-1)",
            fontSize: 14,
          }}
        >
          {darkMode ? "☀️ Claro" : "🌙 Oscuro"}
        </button>

        <div style={{ width: "100%", maxWidth: 400 }}>

          {/* Encabezado */}
          <div style={{ marginBottom: 40 }}>
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 8,
              padding: "4px 12px",
              background: "rgba(200,16,46,0.1)",
              border: "1px solid rgba(200,16,46,0.2)",
              borderRadius: 99,
              marginBottom: 20,
            }}>
              <div style={{ width: 0, height: 0, borderRadius: "", background: "" }} />
            </div>

            <h2 style={{
              fontFamily: "'Open Sans', sans-serif",
              fontSize: 30, fontWeight: 800,
              color: "var(--text-1)",
              letterSpacing: "-0.5px",
              marginBottom: 6,
            }}>
              Bienvenido
            </h2>
            <p style={{ fontSize: 14, color: "var(--text-3)" }}>
              Ingresa con tu usuario o cédula y contraseña.
            </p>
          </div>

          {/* Formulario */}
          <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: 18 }}>

            <div>
              <label className="form-label">Usuario o Cédula</label>
              <input
                type="text"
                placeholder="Ej: jperez o 1032938114"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="form-input"
                required
                autoComplete="username"
                autoFocus
                style={{ fontSize: 15 }}
              />
            </div>

            <div>
              <label className="form-label">Contraseña</label>
              <div style={{ position: "relative" }}>
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="form-input"
                  style={{ paddingRight: 48, fontSize: 15 }}
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: "absolute", right: 14, top: "50%",
                    transform: "translateY(-50%)",
                    background: "none", border: "none",
                    cursor: "pointer", color: "var(--text-3)",
                    fontSize: 16, padding: 4,
                  }}
                  tabIndex={-1}
                >
                  {showPassword ? "🙈" : "👁️"}
                </button>
              </div>
            </div>

            {error && (
              <div style={{
                padding: "12px 16px",
                background: "rgba(200,16,46,0.08)",
                border: "1px solid rgba(200,16,46,0.2)",
                borderRadius: "var(--radius-md)",
                color: "#D4006A",
                fontSize: 13.5,
                display: "flex", alignItems: "center", gap: 8,
              }}>
                ⚠️ {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !username.trim() || !password.trim()}
              style={{
                width: "100%", padding: "14px",
                background: loading || !username.trim() || !password.trim()
                  ? "rgba(200,16,46,0.4)"
                  : "#D4006A",
                color: "#fff",
                fontFamily: "'Open Sans', sans-serif",
                fontSize: 15, fontWeight: 700,
                border: "none", borderRadius: "var(--radius-md)",
                cursor: loading || !username.trim() || !password.trim() ? "not-allowed" : "pointer",
                transition: "var(--transition)",
                marginTop: 4,
                boxShadow: "0 4px 20px rgba(200,16,46,0.3)",
              }}
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
          <div style={{
            marginTop: 36, paddingTop: 24,
            borderTop: "1px solid var(--border)",
            textAlign: "center",
          }}>
            <p style={{ fontSize: 12, color: "var(--text-3)", lineHeight: 1.6 }}>
              Fundación Universitaria Konrad Lorenz<br />
              <span style={{ color: "var(--text-3)", opacity: 0.6 }}>
                Acreditación Institucional de Alta Calidad
              </span>
            </p>
          </div>

        </div>
      </div>

    </main>
  );
}