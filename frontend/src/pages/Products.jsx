import { useEffect, useState } from 'react'
import { Package, Plus, ArrowUpRight, CalendarDays } from 'lucide-react'
import Modal from '../components/Modal.jsx'
import { ToastContainer, useToasts } from '../components/Toast.jsx'
import { productsApi } from '../api/client.js'

const CATALOG = ['Poisson frais', 'Fruits de mer', 'Crustacés', 'Coquillages', 'Poisson surgelé', 'Autre']

const emptyForm = {
  nom: '',
  categorie: 'Autre',
  prix_achat_ref: '',
  stock_kg: '0',
  seuil_alerte_kg: '0',
  notes: '',
}

function dateFr(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function kg(v) {
  return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 }).format(v || 0) + ' kg'
}

export default function Products() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [toasts, setToasts] = useState([])
  const { push } = useToasts()

  const load = async () => {
    setLoading(true)
    try {
      const data = await productsApi.list()
      setItems(data)
    } catch (err) {
      push(toasts, setToasts, 'error', err.response?.data?.detail || 'Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const todayIso = new Date().toISOString().slice(0, 10)
  const recentEntries = [...items]
    .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
    .slice(0, 5)

  const todaysCount = items.filter(item => item.created_at?.slice(0, 10) === todayIso).length
  const lastEntry = recentEntries[0]

  const last7DaysCount = Array.from({ length: 7 }).map((_, index) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - index))
    const iso = d.toISOString().slice(0, 10)
    const count = items.filter(item => item.created_at?.slice(0, 10) === iso).length
    return { iso, label: d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' }), count }
  }).reduce((sum, item) => sum + item.count, 0)

  const save = async (e) => {
    e.preventDefault()
    if (saving) return
    setSaving(true)
    try {
      const payload = {
        ...form,
        prix_achat_ref: form.prix_achat_ref === '' ? null : Number(form.prix_achat_ref),
        stock_kg: Number(form.stock_kg || 0),
        seuil_alerte_kg: Number(form.seuil_alerte_kg || 0),
      }
      await productsApi.create(payload)
      push(toasts, setToasts, 'success', `Produit "${form.nom}" ajouté en base`)
      setForm(emptyForm)
      setOpen(false)
      load()
    } catch (err) {
      push(toasts, setToasts, 'error', err.response?.data?.detail || 'Erreur')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <ToastContainer toasts={toasts} />

      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
            <Package className="w-7 h-7 text-primary-600" />
            Saisie produit
          </h1>
          <p className="text-slate-500 mt-1">Saisie de produit, nombre de saisies par jour et aperçu des dernières saisies</p>
        </div>
        <button onClick={() => setOpen(true)} className="btn-primary">
          <Plus className="w-5 h-5" /> Nouveau produit
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="card p-4">
          <p className="text-xs font-medium text-slate-500">Saisies aujourd’hui</p>
          <p className="mt-2 text-3xl font-bold text-slate-800">{todaysCount}</p>
        </div>

        <div className="card p-4">
          <p className="text-xs font-medium text-slate-500">Saisies 7 jours</p>
          <p className="mt-2 text-3xl font-bold text-slate-800">{last7DaysCount}</p>
        </div>

        <div className="card p-4">
          <p className="text-xs font-medium text-slate-500">Dernière saisie</p>
          <p className="mt-2 text-lg font-bold text-slate-800">{lastEntry ? lastEntry.nom : 'Aucune'}</p>
          <p className="text-sm text-slate-500">{lastEntry ? dateFr(lastEntry.created_at) : '—'}</p>
        </div>
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold text-slate-800">Nombre de saisies par jour</h3>
            <p className="text-xs text-slate-500 mt-0.5">Suivi des produits ajoutés sur les 7 derniers jours</p>
          </div>
          <span className="badge-blue">{last7DaysCount} total</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-7 gap-3">
          {Array.from({ length: 7 }).map((_, index) => {
            const d = new Date()
            d.setDate(d.getDate() - (6 - index))
            const iso = d.toISOString().slice(0, 10)
            const count = items.filter(item => item.created_at?.slice(0, 10) === iso).length
            const max = Math.max(1, ...Array.from({ length: 7 }).map((_, i) => {
              const x = new Date()
              x.setDate(x.getDate() - (6 - i))
              return items.filter(item => item.created_at?.slice(0, 10) === x.toISOString().slice(0, 10)).length
            }))

            return (
              <div key={iso} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
                  <span>{d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })}</span>
                  <span>{count}</span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-blue-500"
                    style={{ width: `${Math.max(10, (count / max) * 100)}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold text-slate-800">Aperçu des dernières saisies</h3>
            <p className="text-xs text-slate-500 mt-0.5">Derniers produits ajoutés dans la base</p>
          </div>
          <CalendarDays className="w-5 h-5 text-blue-500" />
        </div>

        <div className="space-y-3">
          {loading && <p className="text-sm text-slate-400 py-4 text-center">Chargement...</p>}
          {!loading && recentEntries.length === 0 && <p className="text-sm text-slate-400 py-4 text-center">Aucune saisie enregistrée</p>}
          {recentEntries.map(item => (
            <div key={item.id} className="flex items-start justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="inline-flex items-center rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-emerald-700">
                    Produit
                  </span>
                  <p className="text-sm font-semibold text-slate-800">{item.nom}</p>
                </div>
                <p className="text-xs text-slate-500">{item.categorie} • {kg(item.stock_kg)}</p>
              </div>
              <span className="text-[11px] font-medium text-slate-500 whitespace-nowrap">{dateFr(item.created_at)}</span>
            </div>
          ))}
        </div>
      </div>

      <Modal open={open} onClose={() => setOpen(false)} title="Nouveau produit" size="lg">
        <form onSubmit={save} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="input-label">Nom du produit *</label>
              <input required value={form.nom} onChange={e => setForm({ ...form, nom: e.target.value })} className="input" placeholder="Ex : Saumon frais" />
            </div>
            <div>
              <label className="input-label">Catégorie</label>
              <select value={form.categorie} onChange={e => setForm({ ...form, categorie: e.target.value })} className="input">
                {CATALOG.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="input-label">Prix d'achat (€/kg)</label>
              <input type="number" step="0.01" min="0" value={form.prix_achat_ref} onChange={e => setForm({ ...form, prix_achat_ref: e.target.value })} className="input" placeholder="Ex : 12.50" />
            </div>
            <div>
              <label className="input-label">Stock actuel (kg)</label>
              <input type="number" step="0.01" min="0" value={form.stock_kg} onChange={e => setForm({ ...form, stock_kg: e.target.value })} className="input" />
            </div>
            <div>
              <label className="input-label">Seuil d'alerte (kg)</label>
              <input type="number" step="0.01" min="0" value={form.seuil_alerte_kg} onChange={e => setForm({ ...form, seuil_alerte_kg: e.target.value })} className="input" />
            </div>
            <div className="md:col-span-2">
              <label className="input-label">Notes</label>
              <textarea rows={3} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} className="input resize-none" placeholder="Informations complémentaires..." />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
            <button type="button" onClick={() => setOpen(false)} className="btn-secondary">Annuler</button>
            <button type="submit" disabled={saving} className="btn-primary">{saving ? 'Enregistrement...' : 'Créer'}</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
