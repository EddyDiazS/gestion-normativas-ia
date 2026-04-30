"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter, usePathname } from "next/navigation"
import Link from "next/link"
import Image from "next/image";

export default function MenuPanel() {

  const [role, setRole] = useState(null)
  const [username, setUsername] = useState("")
  const [openDropdown, setOpenDropdown] = useState(false)
  const router = useRouter()
  const pathname = usePathname()
  const dropRef = useRef(null)
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    setDarkMode(document.documentElement.classList.contains("dark"));
  }, []);

  useEffect(() => {
    const stored = localStorage.getItem("user")
    if (stored) {
      const parsed = JSON.parse(stored)
      setRole(parsed.role)
      setUsername(parsed.username || "")
    }
  }, [])

  // Cerrar dropdown al click fuera
  useEffect(() => {
    const handler = (e) => {
      if (dropRef.current && !dropRef.current.contains(e.target)) {
        setOpenDropdown(false)
      }
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const logout = () => {
    localStorage.clear()
    router.push("/login")
  }

  // Construir links de gestión según rol
  const adminLinks = []
  if (role === "ADMINISTRADOR" || role === "RECTOR") {
    adminLinks.push({ path: "/usuarios", label: "Usuarios", icon: "👥" })
    adminLinks.push({ path: "/gastos", label: "Gastos de ChatBot", icon: "💰" })
  }

  if (["ADMINISTRADOR", "RECTOR", "DECANO", "DIRECTOR"].includes(role)) {
    adminLinks.push({ path: "/reportes", label: "Reportes", icon: "📊" })
  }

  const isAdminChildActive = adminLinks.some(l => pathname === l.path)

  return (
    <nav className="nav-wrapper">
      <div className="nav-inner">

        {/* Brand */}
        <Link href="/chat" className="nav-brand">

          <Image
            src="/favicon.ico"
            alt="Logo Konrad Lorenz"
            width={40}
            height={40}

          />

          <span>Konrad Lorenz: 1000 Días con IA</span>
        </Link>

        {/* Links */}
        <div className="nav-links-container">

          {/* Chat siempre visible */}
          <Link
            href="/chat"
            className={pathname === "/chat" ? "nav-item-active" : "nav-item"}
          >
            <span>💬</span>
            <span>Chat</span>
          </Link>

          {/* Gestión — solo si hay links disponibles */}
          {adminLinks.length > 0 && (
            <div className="dropdown-container" ref={dropRef}>
              <button
                onClick={() => setOpenDropdown(prev => !prev)}
                className={isAdminChildActive || openDropdown ? "nav-item-active" : "nav-item"}
              >
                <span>⚙️</span>
                <span>Gestión</span>
                <span style={{
                  fontSize: 10,
                  transition: "transform 0.25s",
                  transform: openDropdown ? "rotate(180deg)" : "rotate(0deg)",
                  display: "inline-block"
                }}>▼</span>
              </button>

              <div className={`nav-dropdown-menu ${openDropdown ? "nav-dropdown-open" : "nav-dropdown-closed"}`}>
                <div style={{ padding: "4px 0" }}>
                  {adminLinks.map(link => (
                    <Link
                      key={link.path}
                      href={link.path}
                      onClick={() => setOpenDropdown(false)}
                      className={pathname === link.path ? "nav-sublink-active" : "nav-sublink"}
                    >
                      <span>{link.icon}</span>
                      <span>{link.label}</span>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right side: user chip + logout */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {username && (
            <div style={{
              display: "flex", alignItems: "center", gap: 8,
              background: "var(--surface)", border: "1px solid var(--border)",
              borderRadius: 99, padding: "5px 12px 5px 8px"
            }}>
              <div style={{
                width: 22, height: 22, borderRadius: "50%",
                background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 11, color: "#fff", fontWeight: 700
              }}>
                {username[0].toUpperCase()}
              </div>
              <span style={{ fontSize: 13, color: "var(--text-2)", fontWeight: 500 }}>
                {username}
              </span>
              {role && (
                <span style={{
                  fontSize: 10, fontWeight: 700, textTransform: "uppercase",
                  letterSpacing: "0.06em", color: "var(--accent)",
                  background: "rgba(79,124,255,0.12)", padding: "2px 6px", borderRadius: 99
                }}>
                  {role}
                </span>
              )}
            </div>
          )}

          <button onClick={logout} className="nav-logout-btn">
            <span>🚪</span>
            <span className="hidden sm:inline">Salir</span>
          </button>

          <button
            onClick={() => {
              const newMode = !darkMode;
              setDarkMode(newMode);
              document.documentElement.classList.toggle("dark", newMode);
              localStorage.setItem("theme", newMode ? "dark" : "light");
            }}
            className="nav-logout-btn"
            style={{ fontSize: 16 }}
          >
            {darkMode ? "☀️ Claro" : "🌙 Oscuro"}
          </button>
        </div>

      </div>
    </nav>
  )
}