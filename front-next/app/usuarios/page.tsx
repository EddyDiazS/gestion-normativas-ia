"use client"

import MenuPanel from "../../src/components/menuPanel"
import AdminPanel from "../../src/components/adminPanel"
import ProtectedRoute from "../../src/components/protectedroute"

export default function UsuariosPage() {
  return (
    <ProtectedRoute>
      <div className="page-layout">
        <MenuPanel />
        <main className="page-body">
          <AdminPanel />
        </main>
      </div>
    </ProtectedRoute>
  )
}
