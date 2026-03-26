"use client"

import { useEffect, useState, useMemo } from "react"

const ROLES = ["ESTUDIANTE", "ADMINISTRADOR", "RECTOR", "DECANO", "DIRECTOR"]

function getRoleBadgeClass(role) {
  switch (role) {
    case "ADMINISTRADOR": return "role-badge role-admin"
    case "RECTOR":        return "role-badge role-rector"
    case "DECANO":        return "role-badge role-decano"
    case "DIRECTOR":      return "role-badge role-director"
    default:              return "role-badge role-default"
  }
}

function Field({ label, children }) {
  return (
    <div>
      <label className="form-label">{label}</label>
      {children}
    </div>
  )
}

export default function AdminPanel() {

  const [users, setUsers]                 = useState([])
  const [editingUser, setEditingUser]     = useState(null)
  const [creatingUser, setCreatingUser]   = useState(false)
  const [formData, setFormData]           = useState({})
  const [showPassword, setShowPassword]   = useState(false)
  const [loadingAction, setLoadingAction] = useState(false)

  // ── Filtros ──
  const [filterId,       setFilterId]       = useState("")
  const [filterFaculty,  setFilterFaculty]  = useState("")
  const [filterProgram,  setFilterProgram]  = useState("")
  const [filterRole,     setFilterRole]     = useState("")

  const set = (key, val) => setFormData(prev => ({ ...prev, [key]: val }))

  const fetchUsers = () => {
    const token = localStorage.getItem("token")
    fetch("http://127.0.0.1:8000/users", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setUsers(Array.isArray(data) ? data : []))
  }

  useEffect(() => { fetchUsers() }, [])

  // ── Usuarios filtrados en tiempo real ──
  const filteredUsers = useMemo(() => {
    return users.filter(user => {
      if (filterId && !String(user.id).includes(filterId.trim())) return false
      if (filterFaculty && !(user.faculty || "").toLowerCase().includes(filterFaculty.trim().toLowerCase())) return false
      if (filterProgram && !(user.program || "").toLowerCase().includes(filterProgram.trim().toLowerCase())) return false
      if (filterRole && user.role !== filterRole) return false
      return true
    })
  }, [users, filterId, filterFaculty, filterProgram, filterRole])

  const hasActiveFilters = filterId || filterFaculty || filterProgram || filterRole

  const clearFilters = () => {
    setFilterId("")
    setFilterFaculty("")
    setFilterProgram("")
    setFilterRole("")
  }

  // Opciones únicas para los selects de facultad y programa
  const facultyOptions = useMemo(() => [...new Set(users.map(u => u.faculty).filter(Boolean))], [users])
  const programOptions = useMemo(() => [...new Set(users.map(u => u.program).filter(Boolean))], [users])

  const handleEditClick = (user) => {
    setEditingUser(user.id)
    setShowPassword(false)
    setFormData({
      username: user.username || "",
      email:    user.email    || "",
      password: "",
      faculty:  user.faculty  || "",
      program:  user.program  || "",
      cedula:   user.cedula   || "",
    })
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    setLoadingAction(true)
    const token = localStorage.getItem("token")

    const bodyData = { ...formData }
    if (bodyData.faculty  === "") bodyData.faculty  = null
    if (bodyData.program  === "") bodyData.program  = null
    if (bodyData.cedula   === "") bodyData.cedula   = null
    if (bodyData.password === "") delete bodyData.password

    const res = await fetch(`http://127.0.0.1:8000/users/${editingUser}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(bodyData)
    })

    setLoadingAction(false)
    if (res.ok) { fetchUsers(); setEditingUser(null) }
    else alert("Error actualizando usuario.")
  }

  const handleCreateClick = () => {
    setCreatingUser(true)
    setShowPassword(false)
    setFormData({ username: "", email: "", password: "", role: "ESTUDIANTE", faculty: "", program: "", cedula: "" })
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    setLoadingAction(true)
    const token = localStorage.getItem("token")

    const bodyData = { ...formData }
    if (bodyData.faculty === "") bodyData.faculty = null
    if (bodyData.program === "") bodyData.program = null
    if (bodyData.cedula  === "") bodyData.cedula  = null

    const res = await fetch("http://127.0.0.1:8000/users", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(bodyData)
    })

    setLoadingAction(false)
    if (res.ok) { fetchUsers(); setCreatingUser(false) }
    else alert("Error creando usuario.")
  }

  const handleDelete = async (userId, username) => {
    if (!window.confirm(`¿Eliminar al usuario "${username}"? Esta acción no se puede deshacer.`)) return
    const token = localStorage.getItem("token")
    const res = await fetch(`http://127.0.0.1:8000/users/${userId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    })
    res.ok ? fetchUsers() : alert("Error eliminando usuario.")
  }

  const pwdField = (className) => (
    <div style={{ position: "relative" }}>
      <input
        type={showPassword ? "text" : "password"}
        value={formData.password || ""}
        onChange={e => set("password", e.target.value)}
        className={className}
        placeholder="••••••••"
        style={{ paddingRight: 48 }}
      />
      <button
        type="button"
        onClick={() => setShowPassword(p => !p)}
        style={{
          position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
          background: "none", border: "none", cursor: "pointer",
          color: "var(--text-3)", fontSize: 16
        }}
        tabIndex={-1}
      >
        {showPassword ? "🙈" : "👁️"}
      </button>
    </div>
  )

  return (
    <div className="admin-container">

      {/* Header */}
      <div className="admin-header">
        <div>
          <h1 className="admin-title">Usuarios</h1>
          <p className="admin-subtitle">
            {filteredUsers.length} de {users.length} usuario{users.length !== 1 ? "s" : ""}
            {hasActiveFilters && <span style={{ color: "var(--accent)", marginLeft: 6 }}>· filtrado</span>}
          </p>
        </div>
        <button onClick={handleCreateClick} className="btn-create">
          <span>＋</span>
          <span>Crear Usuario</span>
        </button>
      </div>

      {/* ── Barra de filtros ── */}
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
        {/* Filtro ID */}
        <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 100 }}>
          <label className="form-label">ID</label>
          <input
            type="text"
            value={filterId}
            onChange={e => setFilterId(e.target.value)}
            placeholder="Ej: 3"
            className="form-input"
            style={{ padding: "8px 12px", fontSize: 13 }}
          />
        </div>

        {/* Filtro Facultad */}
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

        {/* Filtro Programa */}
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

        {/* Filtro Rol */}
        <div style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 140 }}>
          <label className="form-label">Rol</label>
          <select
            value={filterRole}
            onChange={e => setFilterRole(e.target.value)}
            className="form-input"
            style={{ padding: "8px 12px", fontSize: 13 }}
          >
            <option value="">Todos</option>
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>

        {/* Limpiar filtros */}
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

      {/* Tabla */}
      <div className="panel-card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead className="data-table-head">
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Cedula</th>
                <th>Email</th>
                <th>Rol</th>
                <th>Facultad</th>
                <th>Programa</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map(user => (
                <tr key={user.id}>
                  <td style={{ color: "var(--text-3)", fontSize: 12 }}>#{user.id}</td>
                  <td style={{ color: "var(--text-1)", fontWeight: 600 }}>{user.username}</td>
                  <td style={{ color: "var(--accent)", fontFamily: "monospace", fontSize: 13 }}>
                    {user.cedula || <span style={{ color: "var(--text-3)", fontSize: 12 }}>—</span>}
                  </td>
                  <td style={{ color: "var(--text-3)" }}>{user.email}</td>
                  <td><span className={getRoleBadgeClass(user.role)}>{user.role}</span></td>
                  <td>{user.faculty || <span style={{ color: "var(--text-3)", fontSize: 12 }}>—</span>}</td>
                  <td>{user.program || <span style={{ color: "var(--text-3)", fontSize: 12 }}>—</span>}</td>
                  <td>
                    <div className="table-action-group">
                      <button className="btn-edit" onClick={() => handleEditClick(user)}>Editar</button>
                      <button className="btn-delete" onClick={() => handleDelete(user.id, user.username)} title="Eliminar">🗑️</button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredUsers.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", padding: "40px", color: "var(--text-3)" }}>
                    {hasActiveFilters ? "No hay usuarios que coincidan con los filtros." : "No hay usuarios registrados."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Modal Editar ── */}
      {editingUser && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setEditingUser(null)}>
          <div className="modal-content">
            <div className="modal-header-blue">
              <h3 className="modal-title">Editar Usuario</h3>
              <p className="modal-subtitle-blue">ID #{editingUser} · el rol no es editable</p>
            </div>
            <form onSubmit={handleUpdate} className="modal-form">
              <div className="form-grid-2">
                <Field label="Username">
                  <input type="text" value={formData.username} onChange={e => set("username", e.target.value)}
                    className="form-input" placeholder="nombre de usuario" required />
                </Field>
                <Field label="Email">
                  <input type="email" value={formData.email} onChange={e => set("email", e.target.value)}
                    className="form-input" placeholder="correo@ejemplo.com" required />
                </Field>
              </div>
              <Field label="Nueva Contraseña (dejar vacío para no cambiar)">
                {pwdField("form-input")}
              </Field>
              <div className="form-grid-2">
                <Field label="Facultad">
                  <input type="text" value={formData.faculty} onChange={e => set("faculty", e.target.value)}
                    className="form-input" placeholder="Opcional" />
                </Field>
                <Field label="Programa">
                  <input type="text" value={formData.program} onChange={e => set("program", e.target.value)}
                    className="form-input" placeholder="Opcional" />
                </Field>
              </div>
              <Field label="Cedula">
                <input type="text" value={formData.cedula} onChange={e => set("cedula", e.target.value)}
                  className="form-input" placeholder="Ej: 100000001" />
              </Field>
              <div className="modal-actions">
                <button type="button" onClick={() => setEditingUser(null)} className="btn-cancel">Cancelar</button>
                <button type="submit" className="btn-save-blue" disabled={loadingAction}>
                  {loadingAction ? "Guardando…" : "Guardar Cambios"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Modal Crear ── */}
      {creatingUser && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setCreatingUser(false)}>
          <div className="modal-content">
            <div className="modal-header-green">
              <h3 className="modal-title">Nuevo Usuario</h3>
              <p className="modal-subtitle-green">Registrar cuenta en el sistema</p>
            </div>
            <form onSubmit={handleCreate} className="modal-form">
              <div className="form-grid-2">
                <Field label="Username">
                  <input type="text" required value={formData.username} onChange={e => set("username", e.target.value)}
                    className="form-input-green" placeholder="nombre de usuario" />
                </Field>
                <Field label="Email">
                  <input type="email" required value={formData.email} onChange={e => set("email", e.target.value)}
                    className="form-input-green" placeholder="correo@ejemplo.com" />
                </Field>
              </div>
              <Field label="Contraseña">
                {pwdField("form-input-green")}
              </Field>
              <div className="form-grid-2">
                <Field label="Rol">
                  <select value={formData.role} onChange={e => set("role", e.target.value)} className="form-input-green">
                    {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                </Field>
                <Field label="Cedula">
                  <input type="text" value={formData.cedula} onChange={e => set("cedula", e.target.value)}
                    className="form-input-green" placeholder="Ej: 100000001 " />
                </Field>
              </div>
              <div className="form-grid-2">
                <Field label="Facultad">
                  <input type="text" value={formData.faculty} onChange={e => set("faculty", e.target.value)}
                    className="form-input-green" placeholder="Opcional" />
                </Field>
                <Field label="Programa">
                  <input type="text" value={formData.program} onChange={e => set("program", e.target.value)}
                    className="form-input-green" placeholder="Opcional" />
                </Field>
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setCreatingUser(false)} className="btn-cancel">Cancelar</button>
                <button type="submit" className="btn-save-green" disabled={loadingAction}>
                  {loadingAction ? "Creando…" : "Confirmar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  )
}