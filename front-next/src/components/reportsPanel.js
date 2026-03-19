"use client"

import { useEffect, useState, useMemo } from "react"

export default function ReportsPanel() {

  const [queries, setQueries] = useState([])
  const [users,   setUsers]   = useState([])
  const [loading, setLoading] = useState(true)

  // ── Filtros ──
  const [filterFaculty, setFilterFaculty] = useState("")
  const [filterProgram, setFilterProgram] = useState("")
  const [filterDateFrom, setFilterDateFrom] = useState("")
  const [filterDateTo,   setFilterDateTo]   = useState("")

  useEffect(() => {
    const token = localStorage.getItem("token")
    const fetchAll = async () => {
      try {
        const [resQ, resU] = await Promise.all([
          fetch("http://127.0.0.1:8000/reports/faculty_queries", {
            headers: { Authorization: `Bearer ${token}` }
          }),
          fetch("http://127.0.0.1:8000/users", {
            headers: { Authorization: `Bearer ${token}` }
          })
        ])
        const dataQ = await resQ.json()
        const dataU = await resU.json()
        setQueries(Array.isArray(dataQ) ? dataQ : [])
        setUsers(Array.isArray(dataU)   ? dataU : [])
      } catch {
        setQueries([])
        setUsers([])
      }
      setLoading(false)
    }
    fetchAll()
  }, [])

  const userMap = useMemo(() => {
    const map = {}
    users.forEach(u => { map[u.id] = u })
    return map
  }, [users])

  // Opciones únicas para selects
  const facultyOptions = useMemo(() =>
    [...new Set(users.map(u => u.faculty).filter(Boolean))], [users])
  const programOptions = useMemo(() =>
    [...new Set(users.map(u => u.program).filter(Boolean))], [users])

  // ── Filtrado ──
  const filteredQueries = useMemo(() => {
    return queries.filter(q => {
      const user = userMap[q.user_id]

      if (filterFaculty && (user?.faculty || "") !== filterFaculty) return false
      if (filterProgram && (user?.program || "") !== filterProgram) return false

      if (filterDateFrom && q.created_at) {
        const qDate = new Date(q.created_at)
        const from  = new Date(filterDateFrom)
        from.setHours(0, 0, 0, 0)
        if (qDate < from) return false
      }

      if (filterDateTo && q.created_at) {
        const qDate = new Date(q.created_at)
        const to    = new Date(filterDateTo)
        to.setHours(23, 59, 59, 999)
        if (qDate > to) return false
      }

      return true
    })
  }, [queries, userMap, filterFaculty, filterProgram, filterDateFrom, filterDateTo])

  const hasActiveFilters = filterFaculty || filterProgram || filterDateFrom || filterDateTo

  const clearFilters = () => {
    setFilterFaculty("")
    setFilterProgram("")
    setFilterDateFrom("")
    setFilterDateTo("")
  }

  return (
    <div className="reports-container">

      {/* Header */}
      <div className="reports-header">
        <h1 className="reports-title">Reportes</h1>
        <p className="reports-subtitle">
          {loading ? "Cargando…" : (
            <>
              {filteredQueries.length} de {queries.length} consulta{queries.length !== 1 ? "s" : ""}
              {hasActiveFilters && <span style={{ color: "var(--accent)", marginLeft: 6 }}>· filtrado</span>}
            </>
          )}
        </p>
      </div>

      {/* Stats */}
      {!loading && filteredQueries.length > 0 && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📋</div>
            <div className="stat-value">{filteredQueries.length}</div>
            <div className="stat-label">Consultas</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">👤</div>
            <div className="stat-value">{new Set(filteredQueries.map(q => q.user_id)).size}</div>
            <div className="stat-label">Usuarios únicos</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🏛️</div>
            <div className="stat-value">
              {new Set(filteredQueries.map(q => userMap[q.user_id]?.faculty).filter(Boolean)).size}
            </div>
            <div className="stat-label">Facultades</div>
          </div>
        </div>
      )}

      {/* ── Barra de filtros ── */}
      {!loading && (
        <div style={{
          background: "var(--bg-2)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-lg)",
          padding: "16px 20px",
          display: "flex",
          gap: 12,
          flexWrap: "wrap",
          alignItems: "flex-end"
        }}>

          {/* Facultad */}
          <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 160 }}>
            <label className="form-label">Facultad</label>
            {facultyOptions.length > 0 ? (
              <select
                value={filterFaculty}
                onChange={e => setFilterFaculty(e.target.value)}
                className="form-input"
                style={{ padding: "8px 12px", fontSize: 13 }}
              >
                <option value="">Todas</option>
                {facultyOptions.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            ) : (
              <input
                type="text"
                value={filterFaculty}
                onChange={e => setFilterFaculty(e.target.value)}
                placeholder="Buscar facultad…"
                className="form-input"
                style={{ padding: "8px 12px", fontSize: 13 }}
              />
            )}
          </div>

          {/* Programa */}
          <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 160 }}>
            <label className="form-label">Programa</label>
            {programOptions.length > 0 ? (
              <select
                value={filterProgram}
                onChange={e => setFilterProgram(e.target.value)}
                className="form-input"
                style={{ padding: "8px 12px", fontSize: 13 }}
              >
                <option value="">Todos</option>
                {programOptions.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            ) : (
              <input
                type="text"
                value={filterProgram}
                onChange={e => setFilterProgram(e.target.value)}
                placeholder="Buscar programa…"
                className="form-input"
                style={{ padding: "8px 12px", fontSize: 13 }}
              />
            )}
          </div>

          {/* Fecha desde */}
          <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 150 }}>
            <label className="form-label">Desde</label>
            <input
              type="date"
              value={filterDateFrom}
              onChange={e => setFilterDateFrom(e.target.value)}
              className="form-input"
              style={{ padding: "8px 12px", fontSize: 13, colorScheme: "dark" }}
            />
          </div>

          {/* Fecha hasta */}
          <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 150 }}>
            <label className="form-label">Hasta</label>
            <input
              type="date"
              value={filterDateTo}
              onChange={e => setFilterDateTo(e.target.value)}
              className="form-input"
              style={{ padding: "8px 12px", fontSize: 13, colorScheme: "dark" }}
            />
          </div>

          {/* Limpiar */}
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              style={{
                padding: "8px 16px",
                background: "var(--red-glow)",
                color: "var(--red)",
                border: "1px solid rgba(255,79,106,0.2)",
                borderRadius: "var(--radius-md)",
                fontSize: 13,
                fontWeight: 600,
                cursor: "pointer",
                transition: "var(--transition)",
                whiteSpace: "nowrap",
                alignSelf: "flex-end"
              }}
            >
              ✕ Limpiar
            </button>
          )}
        </div>
      )}

      {/* Contenido */}
      {loading ? (
        <div className="report-empty-state">
          <div className="loading-spinner" />
          <p style={{ color: "var(--text-3)", fontSize: 14 }}>Cargando reportes…</p>
        </div>
      ) : filteredQueries.length > 0 ? (
        <div className="reports-grid">
          {filteredQueries.map((q) => {
            const user = userMap[q.user_id]
            return (
              <div key={q.id} className="report-card">

                {/* Pregunta */}
                <div>
                  <p className="report-question-label">Pregunta</p>
                  <p className="report-question-text">"{q.question}"</p>
                </div>

                {/* Info usuario en grilla */}
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 10,
                  paddingTop: 12,
                  borderTop: "1px solid var(--border)"
                }}>
                  <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    <span className="report-user-label">ID</span>
                    <span className="report-user-value" style={{ fontFamily: "monospace" }}>#{q.user_id}</span>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    <span className="report-user-label">Usuario</span>
                    <span className="report-user-value">
                      {user?.username || <span style={{ color: "var(--text-3)" }}>—</span>}
                    </span>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    <span className="report-user-label">Facultad</span>
                    <span className="report-user-value" style={{ fontSize: 12 }}>
                      {user?.faculty || <span style={{ color: "var(--text-3)" }}>—</span>}
                    </span>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    <span className="report-user-label">Programa</span>
                    <span className="report-user-value" style={{ fontSize: 12 }}>
                      {user?.program || <span style={{ color: "var(--text-3)" }}>—</span>}
                    </span>
                  </div>
                </div>

                {/* Fecha */}
                {q.created_at && (
                  <div style={{ display: "flex", justifyContent: "flex-end", paddingTop: 8 }}>
                    <span style={{ fontSize: 11, color: "var(--text-3)" }}>
                      🕐 {new Date(q.created_at).toLocaleDateString("es-CO", {
                        day: "2-digit", month: "short", year: "numeric"
                      })}
                    </span>
                  </div>
                )}

              </div>
            )
          })}
        </div>
      ) : (
        <div className="report-empty-state">
          <span style={{ fontSize: 48, opacity: 0.4 }}>
            {hasActiveFilters ? "🔍" : "📭"}
          </span>
          <p style={{ fontSize: 15, color: "var(--text-3)", fontWeight: 500 }}>
            {hasActiveFilters
              ? "No hay consultas que coincidan con los filtros."
              : "No hay consultas disponibles aún."}
          </p>
        </div>
      )}

    </div>
  )
}