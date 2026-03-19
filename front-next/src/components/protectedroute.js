"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "../context/authcontext"

export default function ProtectedRoute({ children }) {

  const { token } = useAuth()
  const router    = useRouter()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const storedToken = localStorage.getItem("token")
    if (!storedToken) {
      router.push("/login")
    } else {
      setReady(true)
    }
  }, [token, router])

  if (!ready) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
        <span style={{ fontSize: 13, color: "var(--text-3)" }}>Verificando sesión…</span>
      </div>
    )
  }

  return children
}