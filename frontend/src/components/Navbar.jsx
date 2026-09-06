import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogOut, Search, Bell, Shield, ShieldHalf, Eye, Briefcase, Key, X, CheckCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext.jsx'
import { authApi } from '../api/client.js'
import Modal from './Modal.jsx'

function initialsFromUser(user) {
  if (!user) return '??'
  const src = user.full_name || user.email || ''
  const parts = src.trim().split(/[\s@.]+/).filter(Boolean).slice(0, 2)
  return parts.map(p => p[0]?.toUpperCase() || '').join('') || 'U'
}

function roleBadge(role) {
  switch (role) {
    case 'admin': return {
      label: 'Administrateur',
      Icon: Shield,
      className: 'bg-red-50 text-red-700 border-red-200',
    }
    case 'directeur': return {
      label: 'Directeur',
      Icon: Briefcase,
      className: 'bg-purple-50 text-purple-700 border-purple-200',
    }
    case 'read_write': return {
      label: 'Éditeur',
      Icon: ShieldHalf,
      className: 'bg-blue-50 text-blue-700 border-blue-200',
    }
    default: return {
      label: 'Lecture seule',
      Icon: Eye,
      className: 'bg-slate-50 text-slate-600 border-slate-200',
    }
  }
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg('')
    setSuccessMsg('')
    if (newPassword !== confirmPassword) {
      setErrorMsg('Les nouveaux mots de passe ne correspondent pas')
      return
    }
    if (newPassword.length < 4) {
      setErrorMsg('Le nouveau mot de passe doit contenir au moins 4 caractères')
      return
    }

    setLoading(true)
    try {
      await authApi.changePassword(oldPassword, newPassword)
      setSuccessMsg('Mot de passe modifié avec succès !')
      setOldPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setTimeout(() => {
        setShowPasswordModal(false)
        setSuccessMsg('')
      }, 1500)
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Erreur lors de la modification du mot de passe')
    } finally {
      setLoading(false)
    }
  }

  const today = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  })

  const badge = roleBadge(user?.role)
  const BadgeIcon = badge.Icon

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 flex-shrink-0">
      <div>
        <h2 className="text-sm font-medium text-slate-500">{today}</h2>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            placeholder="Rechercher..."
            className="input pl-9 w-64"
          />
        </div>

        <button className="relative p-2 rounded-lg hover:bg-slate-100 text-slate-500 transition">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        <div className="h-8 w-px bg-slate-200" />

        <div className="flex items-center gap-3 pl-1">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shadow-sm border ${
              user?.role === 'admin' ? 'bg-gradient-to-br from-red-500 to-rose-600 text-white border-red-500/20' :
              user?.role === 'directeur' ? 'bg-gradient-to-br from-purple-500 to-indigo-600 text-white border-purple-500/20' :
              user?.role === 'read_write' ? 'bg-gradient-to-br from-blue-500 to-cyan-600 text-white border-blue-500/20' :
              'bg-gradient-to-br from-slate-400 to-slate-500 text-white border-slate-400/20'
            }`}>
              {initialsFromUser(user)}
            </div>
            <div className="text-right hidden sm:block">
              <p className="text-sm font-semibold text-slate-800 leading-tight">
                {user?.full_name || user?.email || 'Utilisateur'}
              </p>
              <div className={`inline-flex items-center gap-1 mt-0.5 px-2 py-0.5 rounded-full border text-[11px] font-medium ${badge.className}`}>
                <BadgeIcon className="w-3 h-3" />
                {badge.label}
              </div>
            </div>
          </div>

          <button
            onClick={() => setShowPasswordModal(true)}
            className="p-2 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-primary-600 transition"
            title="Changer mon mot de passe"
          >
            <Key className="w-5 h-5" />
          </button>

          <button
            onClick={handleLogout}
            className="p-2 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-red-600 transition"
            title="Se déconnecter"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>

      <Modal isOpen={showPasswordModal} onClose={() => setShowPasswordModal(false)} title="Changer de mot de passe">
        <form onSubmit={handlePasswordSubmit} className="space-y-4">
          {errorMsg && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg flex items-center gap-2">
              <X className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm rounded-lg flex items-center gap-2">
              <CheckCircle className="w-4 h-4 flex-shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Ancien mot de passe
            </label>
            <input
              type="password"
              required
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              className="input w-full"
              placeholder="Votre mot de passe actuel"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Nouveau mot de passe
            </label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="input w-full"
              placeholder="Au moins 4 caractères"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Confirmer le nouveau mot de passe
            </label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="input w-full"
              placeholder="Répétez le nouveau mot de passe"
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t">
            <button
              type="button"
              onClick={() => setShowPasswordModal(false)}
              className="btn btn-secondary"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Modification...' : 'Enregistrer'}
            </button>
          </div>
        </form>
      </Modal>
    </header>
  )
}
