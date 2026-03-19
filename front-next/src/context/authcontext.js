"use client"
import { createContext, useContext, useState, useEffect } from "react"

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {

  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)

  useEffect(() => {
    const storedToken = localStorage.getItem("token")
    const storedUser = localStorage.getItem("user")

    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
  }, [])

  const login = (userData, jwtToken) => {
    localStorage.setItem("token", jwtToken)
    localStorage.setItem("user", JSON.stringify(userData))

    setUser(userData)
    setToken(jwtToken)
  }

  const logout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")

    setUser(null)
    setToken(null)

    window.location.href = "/login"
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)