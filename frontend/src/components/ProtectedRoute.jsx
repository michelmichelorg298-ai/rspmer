import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext.jsx'

export default function ProtectedRoute({ children, role }) {
  const { token, user, initializing } = useAuth()
  const location = useLocation()

  if (initializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-slate-500 text-sm">Chargement…</div>
      </div>
    )
  }
  if (!token) return <Navigate to="/login" replace />

  // Le rôle Directeur accède uniquement au Tableau de Bord KPI
  if (user?.role === 'directeur' && location.pathname !== '/kpi-dashboard') {
    return <Navigate to="/kpi-dashboard" replace />
  }

  if (role === 'write' && !(user?.role === 'read_write' || user?.role === 'directeur' || user?.role === 'admin')) {
    return <Navigate to="/dashboard" replace />
  }
  if (role === 'admin' && user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }
  return children
}
