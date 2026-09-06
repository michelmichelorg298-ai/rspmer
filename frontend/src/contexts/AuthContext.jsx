import { createContext, useContext, useState, useEffect, useMemo } from 'react'
import { authApi } from '../api/client.js'
import { Navigate } from 'react-router-dom'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('fruitmer_token'))
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('fruitmer_user') || 'null')
    } catch { return null }
  })
  const [loading, setLoading] = useState(false)
  const [initializing, setInitializing] = useState(true)

  useEffect(() => {
    if (token) localStorage.setItem('fruitmer_token', token)
    else localStorage.removeItem('fruitmer_token')
  }, [token])

  useEffect(() => {
    if (user) localStorage.setItem('fruitmer_user', JSON.stringify(user))
    else localStorage.removeItem('fruitmer_user')
  }, [user])

  useEffect(() => {
    let canceled = false
    const loadUser = async () => {
      if (!token) { setInitializing(false); return }
      try {
        const me = await authApi.me()
        if (!canceled) setUser(me)
      } catch {
        if (!canceled) { setToken(null); setUser(null) }
      } finally {
        if (!canceled) setInitializing(false)
      }
    }
    loadUser()
    return () => { canceled = true }
  }, [token])

  const login = async (email, password) => {
    setLoading(true)
    try {
      const { data } = await authApi.login(email, password)
      const newToken = data.access_token
      localStorage.setItem('fruitmer_token', newToken)
      setToken(newToken)
      const me = await authApi.me(newToken)
      setUser(me)
      return { ok: true }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erreur de connexion'
      return { ok: false, error: msg }
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
  }

  const canWrite = user?.role === 'read_write' || user?.role === 'directeur' || user?.role === 'admin'
  const isDirecteur = user?.role === 'directeur'
  const isAdmin = user?.role === 'admin'

  const value = useMemo(() => ({
    token, user, loading, initializing, login, logout, canWrite, isDirecteur, isAdmin,
  }), [token, user, loading, initializing])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export default function ProtectedRoute({ children, role }) {
  const { token, user, initializing } = useAuth()
  if (initializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-slate-500 text-sm">Chargement…</div>
      </div>
    )
  }
  if (!token) return <Navigate to="/login" replace />
  if (role === 'write' && !(user?.role === 'read_write' || user?.role === 'admin')) {
    return <Navigate to="/dashboard" replace />
  }
  if (role === 'admin' && user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }
  return children
}
