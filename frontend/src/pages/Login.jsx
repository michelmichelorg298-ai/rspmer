import { useState, useEffect } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { Fish, Mail, Lock, Eye, EyeOff, Loader2 } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext.jsx'
import { ToastContainer } from '../components/Toast.jsx'

export default function Login() {
  const { login, token, user, loading } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@gmail.com')
  const [password, setPassword] = useState('adminpass')
  const [showPass, setShowPass] = useState(false)
  const [toasts, setToasts] = useState([])
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (token) {
      const dest = user?.role === 'directeur' ? '/kpi-dashboard' : '/dashboard'
      navigate(dest, { replace: true })
    }
  }, [token, user, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (submitting) return
    setSubmitting(true)
    const res = await login(email, password)
    setSubmitting(false)
    if (!res.ok) {
      const id = Date.now()
      const onClose = () => setToasts(t => t.filter(x => x.id !== id))
      setToasts([{ id, type: 'error', message: res.error, onClose }])
    }
  }

  if (token) {
    const dest = user?.role === 'directeur' ? '/kpi-dashboard' : '/dashboard'
    return <Navigate to={dest} replace />
  }

  return (
    <div className="min-h-screen flex relative overflow-hidden bg-slate-50">
      <ToastContainer toasts={toasts} />

      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-slate-900 via-primary-900 to-primary-800 overflow-hidden">
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: 'radial-gradient(circle at 20% 20%, rgba(16,185,129,.4) 0, transparent 40%), radial-gradient(circle at 80% 70%, rgba(249,115,22,.35) 0, transparent 45%)'
        }} />
        <div className="relative z-10 w-full flex flex-col justify-center px-16 text-white">
          <div className="flex items-center gap-3 mb-10">
            <div className="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur flex items-center justify-center border border-white/20">
              <Fish className="w-7 h-7 text-primary-300" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">FruitMer</h1>
              <p className="text-primary-200/80 text-sm">Gestion Poissonnerie 3.0</p>
            </div>
          </div>

          <h2 className="text-4xl font-bold leading-tight mb-4 max-w-md">
            Pilotez votre activité avec simplicité et précision.
          </h2>
          <p className="text-white/70 text-lg max-w-md mb-10">
            Gérez vos stocks, fournisseurs, ventes et retours depuis une interface moderne conçue pour les professionnels.
          </p>

          <div className="space-y-4">
            {[
              { t: 'Tableau de bord en temps réel', d: 'Suivez vos KPIs quotidiens en un coup d’œil.' },
              { t: 'Gestion complète des stocks', d: 'Alerte seuil, mouvements et inventaire.' },
              { t: 'Traçabilité fournisseurs & clients', d: 'Historique détaillé de toutes les opérations.' },
            ].map(f => (
              <div key={f.t} className="flex gap-4 p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur">
                <div className="w-10 h-10 rounded-xl bg-primary-500/30 flex items-center justify-center flex-shrink-0">
                  <div className="w-2.5 h-2.5 rounded-full bg-primary-400" />
                </div>
                <div>
                  <p className="font-semibold">{f.t}</p>
                  <p className="text-white/60 text-sm">{f.d}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6">
        <form onSubmit={handleSubmit} className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 justify-center mb-10">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-lg">
              <Fish className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-slate-800">FruitMer</h1>
          </div>

          <div className="mb-8">
            <h2 className="text-3xl font-bold text-slate-800 mb-2">Bienvenue 👋</h2>
            <p className="text-slate-500">Connectez-vous pour accéder à votre espace.</p>
          </div>

          <div className="space-y-5">
            <div>
              <label className="input-label">Adresse email</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  className="input pl-11"
                  placeholder="vous@exemple.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="input-label">Mot de passe</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="input pl-11 pr-11"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPass(s => !s)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded text-slate-400 hover:text-slate-600 transition"
                  tabIndex={-1}
                >
                  {showPass ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting || loading}
            className="w-full btn-primary mt-8 py-3 text-base"
          >
            {submitting ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Connexion...</>
            ) : 'Se connecter'}
          </button>

          <div className="mt-8 pt-6 border-t border-slate-100">
            <p className="text-xs text-slate-400 text-center mb-3 uppercase tracking-wider font-semibold">
              Comptes de démonstration
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
              <button type="button" onClick={() => { setEmail('reader@gmail.com'); setPassword('readerpass') }}
                className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 transition">
                <p className="font-semibold text-slate-700">Lecture</p>
                <p className="text-slate-400">reader</p>
              </button>
              <button type="button" onClick={() => { setEmail('writer@gmail.com'); setPassword('writerpass') }}
                className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 transition">
                <p className="font-semibold text-slate-700">Édition</p>
                <p className="text-slate-400">writer</p>
              </button>
              <button type="button" onClick={() => { setEmail('directeur@gmail.com'); setPassword('directeurpass') }}
                className="p-2 rounded-lg border border-purple-200 bg-purple-50 hover:bg-purple-100 transition">
                <p className="font-semibold text-purple-700">Directeur</p>
                <p className="text-purple-500">directeur</p>
              </button>
              <button type="button" onClick={() => { setEmail('admin@gmail.com'); setPassword('adminpass') }}
                className="p-2 rounded-lg border border-primary-200 bg-primary-50 hover:bg-primary-100 transition">
                <p className="font-semibold text-primary-700">Admin</p>
                <p className="text-primary-500">admin</p>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
