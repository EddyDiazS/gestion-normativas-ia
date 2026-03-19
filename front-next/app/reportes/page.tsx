"use client"

import MenuPanel from "../../src/components/menuPanel"
import ReportsPanel from "../../src/components/reportsPanel"
import ProtectedRoute from "../../src/components/protectedroute"

export default function ReportesPage() {
  return (
    <ProtectedRoute>
      <div className="page-layout">
        <MenuPanel />
        <main className="page-body">
          <ReportsPanel />
        </main>
      </div>
    </ProtectedRoute>
  )
}