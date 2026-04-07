"use client"

import { useEffect, useState } from "react"

export default function GastosPanel() {

  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [filter,  setFilter]  = useState("")

  useEffect(() => {
    const token = localStorage.getItem("token")
    fetch("http://127.0.0.1:8000/reports/gastos", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const filtered = data?.detalle?.filter(q =>
    !filter ||
    q.username?.toLowerCase().includes(filter.toLowerCase()) ||
    q.faculty?.toLowerCase().includes(filter.toLowerCase()) ||
    q.question?.toLowerCase().includes(filter.toLowerCase())
  ) || []

  return (
    <div className="reports-container">

      {/* Header */}
      <div className="reports-header">
        <h1 className="reports-title">Gastos de Chat</h1>
        <p className="reports-subtitle">
          {loading ? "Cargando…" : `${filtered.length} consulta${filtered.length !== 1 ? "s" : ""}`}
        </p>
      </div>

      {/* Tarjetas resumen */}
      {!loading && data?.resumen && (
        <div className="stats-grid" style={{ marginBottom: 20 }}>
          <div className="stat-card">
            <div className="stat-icon">📋</div>
            <div className="stat-value">{data.resumen.total_consultas}</div>
            <div className="stat-label">Consultas totales</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🔢</div>
            <div className="stat-value">{data.resumen.total_tokens.toLocaleString()}</div>
            <div className="stat-label">Tokens totales</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📥</div>
            <div className="stat-value">{data.resumen.total_input_tokens.toLocaleString()}</div>
            <div className="stat-label">Tokens de entrada</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📤</div>
            <div className="stat-value">{data.resumen.total_output_tokens.toLocaleString()}</div>
            <div className="stat-label">Tokens de salida</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">💲</div>
            <div className="stat-value">${data.resumen.costo_total_usd.toFixed(4)}</div>
            <div className="stat-label">Costo total USD</div>
          </div>
        </div>
      )}

      {/* Filtro */}
      {!loading && (
        <div style={{
          background: "var(--bg-2)", border: "1px solid var(--border)",
          borderRadius: "var(--radius-lg)", padding: "16px 20px",
          display: "flex", gap: 12, alignItems: "flex-end", marginBottom: 20
        }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 280 }}>
            <label className="form-label">Buscar por usuario, facultad o pregunta</label>
            <input type="text" value={filter}
              onChange={e => setFilter(e.target.value)}
              placeholder="Ej: admin, Psicología, cancelar materia…"
              className="form-input" style={{ padding: "8px 12px", fontSize: 13 }} />
          </div>
          {filter && (
            <button onClick={() => setFilter("")} style={{
              padding: "8px 16px", background: "var(--red-glow)", color: "var(--red)",
              border: "1px solid rgba(255,79,106,0.2)", borderRadius: "var(--radius-md)",
              fontSize: 13, fontWeight: 600, cursor: "pointer", alignSelf: "flex-end"
            }}>✕ Limpiar</button>
          )}
        </div>
      )}

      {/* Tabla */}
      {loading ? (
        <div className="report-empty-state">
          <div className="loading-spinner" />
          <p style={{ color: "var(--text-3)", fontSize: 14 }}>Cargando gastos…</p>
        </div>
      ) : filtered.length > 0 ? (
        <div className="panel-card">
          <div className="table-wrapper">
            <table className="data-table">
              <thead className="data-table-head">
                <tr>
                  <th>Usuario</th>
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
                    <td style={{ fontWeight: 600, color: "var(--text-1)" }}>{q.username}</td>
                    <td style={{ fontSize: 12, color: "var(--text-3)" }}>{q.faculty || "—"}</td>
                    <td style={{ maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", color: "var(--text-2)" }}
                      title={q.question}>
                      {q.question}
                    </td>
                    <td style={{ textAlign: "right", fontFamily: "monospace", fontSize: 13 }}>{q.input_tokens.toLocaleString()}</td>
                    <td style={{ textAlign: "right", fontFamily: "monospace", fontSize: 13 }}>{q.output_tokens.toLocaleString()}</td>
                    <td style={{ textAlign: "right", fontFamily: "monospace", fontSize: 13, fontWeight: 600 }}>{q.total_tokens.toLocaleString()}</td>
                    <td style={{ textAlign: "right", fontFamily: "monospace", fontSize: 13, color: "var(--accent)" }}>
                      ${q.estimated_cost.toFixed(6)}
                    </td>
                    <td style={{ fontSize: 11, color: "var(--text-3)", whiteSpace: "nowrap" }}>
                      {q.created_at ? new Date(q.created_at).toLocaleDateString("es-CO", {
                        day: "2-digit", month: "short", year: "numeric"
                      }) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="report-empty-state">
          <span style={{ fontSize: 48, opacity: 0.4 }}>{filter ? "🔍" : "💰"}</span>
          <p style={{ fontSize: 15, color: "var(--text-3)", fontWeight: 500 }}>
            {filter ? "No hay consultas que coincidan." : "No hay consultas con datos de tokens aún."}
          </p>
        </div>
      )}

    </div>
  )
}