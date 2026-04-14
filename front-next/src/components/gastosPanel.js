"use client"
import { useEffect, useState } from "react"

const FACULTADES = [
  "Facultad de Matemáticas e Ingenierías",
  "Escuela de Negocios",
  "Facultad de Psicología",
  "Escuela de Posgrados",
]
const ROLES = ["ESTUDIANTE", "DOCENTE", "DIRECTOR", "DECANO", "RECTOR", "ADMINISTRADOR"]

export default function GastosPanel() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [vista, setVista] = useState("detalle")
  const [topUsuarios, setTopUsuarios] = useState([])
  const [porFacultad, setPorFacultad] = useState([])
  const [filterText, setFilterText] = useState("")
  // Filtros
  const [filterFaculty, setFilterFaculty] = useState("")
  const [filterRole, setFilterRole] = useState("")
  const [filterDateFrom, setFilterDateFrom] = useState("")
  const [filterDateTo, setFilterDateTo] = useState("")

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : ""

  useEffect(() => {
    const headers = { Authorization: `Bearer ${token}` }
    Promise.all([
      fetch("http://127.0.0.1:8000/reports/gastos", { headers }).then(r => r.json()),
      fetch("http://127.0.0.1:8000/reports/gastos/top_usuarios", { headers }).then(r => r.json()),
      fetch("http://127.0.0.1:8000/reports/gastos/por_facultad", { headers }).then(r => r.json()),
    ])
      .then(([gastos, top, fac]) => {
        setData(gastos)
        setTopUsuarios(Array.isArray(top) ? top : [])
        setPorFacultad(Array.isArray(fac) ? fac : [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const hasFilters = filterFaculty || filterRole || filterDateFrom || filterDateTo || filterText
  const clearFilters = () => {
    setFilterFaculty(""); setFilterRole(""); setFilterDateFrom(""); setFilterDateTo(""); setFilterText("")
  }

  const filtered = (data?.detalle || []).filter(q => {
    if (filterFaculty && q.faculty !== filterFaculty) return false
    if (filterRole && q.role !== filterRole) return false
    if (filterDateFrom && q.created_at && new Date(q.created_at) < new Date(filterDateFrom)) return false
    if (filterDateTo && q.created_at && new Date(q.created_at) > new Date(filterDateTo + "T23:59:59")) return false
    if (filterText && !q.username.toLowerCase().includes(filterText.toLowerCase()) && !q.question.toLowerCase().includes(filterText.toLowerCase()) && !q.faculty.toLowerCase().includes(filterText.toLowerCase()))
      return false
    return true
  })

  const btnVista = (key, label) => (
    <button key={key} onClick={() => setVista(key)} style={{
      padding: "8px 18px", borderRadius: "var(--radius-md)", fontSize: 13,
      cursor: "pointer", fontWeight: vista === key ? 700 : 400,
      border: vista === key ? "1px solid var(--accent)" : "1px solid var(--border)",
      background: vista === key ? "rgba(79,124,255,0.12)" : "var(--bg-2)",
      color: vista === key ? "var(--accent)" : "var(--text-2)",
      transition: "var(--transition)"
    }}>{label}</button>
  )

  return (
    <div className="reports-container">

      {/* Header */}
      <div className="reports-header">
        <h1 className="reports-title">Gastos de Chat</h1>
        <p className="reports-subtitle">{loading ? "Cargando…" : `${filtered.length} consulta${filtered.length !== 1 ? "s" : ""}`}</p>
      </div>

      {/* Tarjetas resumen */}
      {!loading && data?.resumen && (
        <div className="stats-grid" style={{ marginBottom: 20 }}>
          {[
            { icon: "📋", val: data.resumen.total_consultas, label: "Consultas" },
            { icon: "🔢", val: data.resumen.total_tokens.toLocaleString(), label: "Tokens totales" },
            { icon: "📥", val: data.resumen.total_input_tokens.toLocaleString(), label: "Tokens entrada" },
            { icon: "📤", val: data.resumen.total_output_tokens.toLocaleString(), label: "Tokens salida" },
            { icon: "💲", val: `$${Number(data.resumen.costo_total_usd).toFixed(4)}`, label: "Costo total USD" },
          ].map((s, i) => (
            <div key={i} className="stat-card">
              <div className="stat-icon">{s.icon}</div>
              <div className="stat-value">{s.val}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Botones de vista */}
      {!loading && (
        <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
          {btnVista("detalle", "📋 Detalle")}
          {btnVista("top_usuarios", "🏆 Top Usuarios")}
          {btnVista("por_facultad", "🏛️ Por Facultad")}
        </div>
      )}

      {/* DETALLE */}
      {!loading && vista === "detalle" && (
        <>
          {/* Filtros */}
          <div style={{
            background: "var(--bg-2)", border: "1px solid var(--border)",
            borderRadius: "var(--radius-lg)", padding: "16px 20px",
            display: "flex", gap: 12, flexWrap: "wrap", alignItems: "flex-end", marginBottom: 20
          }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 200 }}>
              <label className="form-label">Buscar</label>
              <input type="text" value={filterText} onChange={e => setFilterText(e.target.value)}
                placeholder="Usuario, pregunta…" className="form-input"
                style={{ padding: "8px 12px", fontSize: 13 }} />
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 180 }}>
              <label className="form-label">Facultad</label>
              <select value={filterFaculty} onChange={e => setFilterFaculty(e.target.value)}
                className="form-input" style={{ padding: "8px 12px", fontSize: 13 }}>
                <option value="">Todas</option>
                {FACULTADES.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 150 }}>
              <label className="form-label">Rol</label>
              <select value={filterRole} onChange={e => setFilterRole(e.target.value)}
                className="form-input" style={{ padding: "8px 12px", fontSize: 13 }}>
                <option value="">Todos</option>
                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 150 }}>
              <label className="form-label">Desde</label>
              <input type="date" value={filterDateFrom} onChange={e => setFilterDateFrom(e.target.value)}
                className="form-input" style={{ padding: "8px 12px", fontSize: 13, colorScheme: "dark" }} />
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 150 }}>
              <label className="form-label">Hasta</label>
              <input type="date" value={filterDateTo} onChange={e => setFilterDateTo(e.target.value)}
                className="form-input" style={{ padding: "8px 12px", fontSize: 13, colorScheme: "dark" }} />
            </div>
            {hasFilters && (
              <button onClick={clearFilters} style={{
                padding: "8px 16px", background: "var(--red-glow)", color: "var(--red)",
                border: "1px solid rgba(255,79,106,0.2)", borderRadius: "var(--radius-md)",
                fontSize: 13, fontWeight: 600, cursor: "pointer", alignSelf: "flex-end"
              }}>✕ Limpiar</button>
            )}
          </div>

          {filtered.length > 0 ? (
            <div className="panel-card">
              <div className="table-wrapper">
                <table className="data-table">
                  <thead className="data-table-head">
                    <tr>
                      <th>Usuario</th>
                      <th>Rol</th>
                      <th>Facultad</th>
                      <th>Pregunta</th>
                      <th>Tokens entrada</th>
                      <th>Tokens salida</th>
                      <th>Total tokens</th>
                      <th>Costo USD</th>
                      <th>Fecha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map(q => (
                      <tr key={q.id}>
                        <td style={{ fontWeight: 600 }}>{q.username}</td>
                        <td><span style={{
                          fontSize: 11, fontWeight: 700, textTransform: "uppercase",
                          color: "var(--accent)", background: "rgba(79,124,255,0.12)",
                          padding: "2px 8px", borderRadius: 99
                        }}>{q.role}</span></td>
                        <td style={{ fontSize: 12, color: "var(--text-3)" }}>{q.faculty || "—"}</td>
                        <td style={{ maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={q.question}>{q.question}</td>
                        <td style={{ textAlign: "right", fontFamily: "monospace", fontSize: 13 }}>{q.input_tokens.toLocaleString()}</td>
                        <td style={{ textAlign: "right", fontFamily: "monospace", fontSize: 13 }}>{q.output_tokens.toLocaleString()}</td>
                        <td style={{ textAlign: "right", fontFamily: "monospace", fontSize: 13, fontWeight: 600 }}>{q.total_tokens.toLocaleString()}</td>
                        <td style={{ textAlign: "right", fontFamily: "monospace", fontSize: 13, color: "var(--accent)" }}>${Number(q.estimated_cost).toFixed(6)}</td>
                        <td style={{ fontSize: 11, color: "var(--text-3)", whiteSpace: "nowrap" }}>
                          {q.created_at ? new Date(q.created_at).toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" }) : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="report-empty-state">
              <span style={{ fontSize: 48, opacity: 0.4 }}>{hasFilters ? "🔍" : "💰"}</span>
              <p style={{ fontSize: 15, color: "var(--text-3)", fontWeight: 500 }}>
                {hasFilters ? "No hay consultas que coincidan." : "No hay consultas con datos de tokens aún."}
              </p>
            </div>
          )}
        </>
      )}

      {/* TOP USUARIOS  */}
      {!loading && vista === "top_usuarios" && (
        <div className="panel-card">
          <div className="table-wrapper">
            <table className="data-table">
              <thead className="data-table-head">
              </thead>
              <tbody>
                {topUsuarios.length > 0 ? topUsuarios.map((u, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 700, color: i === 0 ? "#FFD700" : i === 1 ? "#C0C0C0" : i === 2 ? "#CD7F32" : "var(--text-3)", fontSize: 16 }}>
                      {i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : `#${i + 1}`}
                    </td>
                    <td style={{ fontWeight: 600 }}>{u.username}</td>
                    <td style={{ fontSize: 12, color: "var(--text-3)" }}>{u.faculty}</td>
                    <td style={{ textAlign: "right", fontFamily: "monospace" }}>{u.total_consultas}</td>
                    <td style={{ textAlign: "right", fontFamily: "monospace", fontWeight: 600 }}>{u.total_tokens.toLocaleString()}</td>
                    <td style={{ textAlign: "right", fontFamily: "monospace", color: "var(--accent)" }}>${u.total_costo.toFixed(6)}</td>
                  </tr>
                )) : (
                  <tr><td colSpan={7} style={{ textAlign: "center", padding: 40, color: "var(--text-3)" }}>No hay datos disponibles aún.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/*POR FACULTAD*/}
      {!loading && vista === "por_facultad" && (
        <div className="panel-card">
          <div className="table-wrapper">
            <table className="data-table">
              <thead className="data-table-head">
                <tr><th>Facultad</th><th>Consultas</th><th>Total tokens</th><th>Costo USD</th></tr>
              </thead>
              <tbody>
                {porFacultad.length > 0 ? porFacultad.map((f, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600 }}>{f.faculty}</td>
                    <td style={{ textAlign: "right", fontFamily: "monospace" }}>{f.total_consultas}</td>
                    <td style={{ textAlign: "right", fontFamily: "monospace", fontWeight: 600 }}>{f.total_tokens.toLocaleString()}</td>
                    <td style={{ textAlign: "right", fontFamily: "monospace", color: "var(--accent)" }}>${f.total_costo.toFixed(6)}</td>
                  </tr>
                )) : (
                  <tr><td colSpan={4} style={{ textAlign: "center", padding: 40, color: "var(--text-3)" }}>No hay datos disponibles aún.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {loading && (
        <div className="report-empty-state">
          <div className="loading-spinner" />
          <p style={{ color: "var(--text-3)", fontSize: 14 }}>Cargando gastos…</p>
        </div>
      )}
    </div>
  )
}