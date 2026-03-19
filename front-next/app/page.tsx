"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

const API_URL = "http://127.0.0.1:8000"

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    const validate = async () => {
      const token = localStorage.getItem("token")

      if (!token) {
        router.replace("/login")
        return
      }

      try {
        const res = await fetch(`${API_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        })

        if (res.ok) {
          router.replace("/chat")
        } else {
          // Token inválido o expirado — limpiar y mandar al login
          localStorage.removeItem("token")
          localStorage.removeItem("user")
          localStorage.removeItem("role")
          router.replace("/login")
        }
      } catch {
        // Backend caído o error de red — limpiar igual
        localStorage.removeItem("token")
        localStorage.removeItem("user")
        localStorage.removeItem("role")
        router.replace("/login")
      }
    }

    validate()
  }, [])

  // Pantalla de carga mientras valida
  return (
    <div className="loading-screen">
      <div className="loading-spinner" />
      <span style={{ fontSize: 13, color: "var(--text-3)" }}>Cargando…</span>
    </div>
  )
}
