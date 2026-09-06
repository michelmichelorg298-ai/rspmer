import { useState, useEffect } from 'react'
import { Users as UsersIcon, UserPlus, Trash2, Shield, Briefcase, ShieldHalf, Eye, CheckCircle, AlertTriangle } from 'lucide-react'
import { usersApi } from '../api/client.js'
import { ToastContainer, useToasts } from '../components/Toast.jsx'
import Modal from '../components/Modal.jsx'
import { useAuth } from '../contexts/AuthContext.jsx'

export default function Users() {
  const { user: currentUser } = useAuth()
  const [usersList, setUsersList] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [userToDelete, setUserToDelete] = useState(null)
  const [toasts, setToasts] = useState([])
  const { push } = useToasts()

  // Form state
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('read')
  const [formSubmitting, setFormSubmitting] = useState(false)

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const data = await usersApi.list()
      setUsersList(data)
    } catch (err) {
      push(toasts, setToasts, 'error', 'Impossible de charger la liste des utilisateurs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleAddSubmit = async (e) => {
    e.preventDefault()
    setFormSubmitting(true)
    try {
      await usersApi.create({
        email,
        full_name: fullName,
        password,
        role,
      })
      push(toasts, setToasts, 'success', `Utilisateur ${email} créé avec succès`)
      setShowAddModal(false)
      setEmail('')
      setFullName('')
      setPassword('')
      setRole('read')
      fetchUsers()
    } catch (err) {
      push(toasts, setToasts, 'error', err.response?.data?.detail || 'Erreur lors de la création de l\'utilisateur')
    } finally {
      setFormSubmitting(false)
    }
  }

  const handleDeleteConfirm = async () => {
    if (!userToDelete) return
    try {
      await usersApi.remove(userToDelete.id)
      push(toasts, setToasts, 'success', `Utilisateur ${userToDelete.email} supprimé`)
      setUserToDelete(null)
      fetchUsers()
    } catch (err) {
      push(toasts, setToasts, 'error', err.response?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const roleLabel = (r) => {
    switch (r) {
      case 'admin': return { label: 'Administrateur', icon: Shield, badgeClass: 'bg-red-50 text-red-700 border-red-200' }
      case 'directeur': return { label: 'Directeur', icon: Briefcase, badgeClass: 'bg-purple-50 text-purple-700 border-purple-200' }
      case 'read_write': return { label: 'Éditeur (Lecture/Écriture)', icon: ShieldHalf, badgeClass: 'bg-blue-50 text-blue-700 border-blue-200' }
      default: return { label: 'Lecture seule', icon: Eye, badgeClass: 'bg-slate-50 text-slate-600 border-slate-200' }
    }
  }

  return (
    <div className="space-y-6">
      <ToastContainer toasts={toasts} />

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
            <UsersIcon className="w-7 h-7 text-primary-600" />
            Gestion des Utilisateurs
          </h1>
          <p className="text-slate-500 mt-1">Ajoutez, consultez et gérez les comptes d'accès à la plateforme</p>
        </div>

        {currentUser?.role === 'admin' && (
          <button
            onClick={() => setShowAddModal(true)}
            className="btn btn-primary flex items-center gap-2 shadow-md hover:shadow-lg transition"
          >
            <UserPlus className="w-4 h-4" />
            Nouvel utilisateur
          </button>
        )}
      </div>

      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="table-th">Utilisateur</th>
                <th className="table-th">Email</th>
                <th className="table-th">Rôle</th>
                <th className="table-th">Statut</th>
                <th className="table-th text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading && (
                <tr>
                  <td colSpan={5} className="table-td text-center text-slate-400 py-8">
                    Chargement des utilisateurs...
                  </td>
                </tr>
              )}

              {!loading && usersList.length === 0 && (
                <tr>
                  <td colSpan={5} className="table-td text-center text-slate-400 py-8">
                    Aucun utilisateur trouvé
                  </td>
                </tr>
              )}

              {usersList.map((u) => {
                const rInfo = roleLabel(u.role)
                const RIcon = rInfo.icon
                const isSelf = currentUser?.id === u.id

                return (
                  <tr key={u.id} className="hover:bg-slate-50/60 transition">
                    <td className="table-td font-medium text-slate-900">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-600 text-sm">
                          {u.full_name?.[0] || u.email[0]?.toUpperCase()}
                        </div>
                        <div>
                          <p className="font-semibold text-slate-800">{u.full_name || 'Sans nom'}</p>
                          {isSelf && <span className="text-[11px] font-bold text-primary-600">(Vous)</span>}
                        </div>
                      </div>
                    </td>

                    <td className="table-td text-slate-600">{u.email}</td>

                    <td className="table-td">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-semibold ${rInfo.badgeClass}`}>
                        <RIcon className="w-3.5 h-3.5" />
                        {rInfo.label}
                      </span>
                    </td>

                    <td className="table-td">
                      {u.disabled ? (
                        <span className="badge-red">Désactivé</span>
                      ) : (
                        <span className="badge-emerald">Actif</span>
                      )}
                    </td>

                    <td className="table-td text-right">
                      {currentUser?.role === 'admin' && !isSelf && (
                        <button
                          onClick={() => setUserToDelete(u)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition"
                          title="Supprimer cet utilisateur"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Ajout Utilisateur */}
      <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Créer un nouvel utilisateur">
        <form onSubmit={handleAddSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Adresse Email *
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input w-full"
              placeholder="ex: jean.dupont@fruitmer.com"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Nom complet
            </label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="input w-full"
              placeholder="ex: Jean Dupont"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Mot de passe initial *
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input w-full"
              placeholder="Mot de passe temporaire"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Rôle attribué *
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="input w-full bg-white"
            >
              <option value="read">Lecture seule (Consultation standard)</option>
              <option value="read_write">Éditeur (Saisie des ventes/fournitures)</option>
              <option value="directeur">Directeur (Accès aux KPI stratégiques)</option>
              <option value="admin">Administrateur (Accès total + gestion comptes)</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t">
            <button
              type="button"
              onClick={() => setShowAddModal(false)}
              className="btn btn-secondary"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={formSubmitting}
              className="btn btn-primary"
            >
              {formSubmitting ? 'Création...' : 'Créer l\'utilisateur'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Modal Confirmation Suppression */}
      <Modal isOpen={!!userToDelete} onClose={() => setUserToDelete(null)} title="Confirmer la suppression">
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl">
            <AlertTriangle className="w-6 h-6 flex-shrink-0" />
            <p className="text-sm font-medium">
              Êtes-vous sûr de vouloir supprimer définitivement le compte de <b>{userToDelete?.email}</b> ? Cette action est irréversible.
            </p>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={() => setUserToDelete(null)}
              className="btn btn-secondary"
            >
              Annuler
            </button>
            <button
              onClick={handleDeleteConfirm}
              className="btn bg-red-600 hover:bg-red-700 text-white font-medium px-4 py-2 rounded-lg"
            >
              Supprimer le compte
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
