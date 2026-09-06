import { useEffect, useState } from 'react'
import { Truck, Plus, CalendarDays } from 'lucide-react'
import Modal from '../components/Modal.jsx'
import { ToastContainer, useToasts } from '../components/Toast.jsx'
import { fournituresApi, productsApi } from '../api/client.js'

const todayIso = () => new Date().toISOString().slice(0, 10)
const emptyForm = {
  product_id: '',
  nom_produit_texte: '',
  date_obtenu: todayIso(),
  origine: '',
  nom_fournisseur: '',
  kilo_produit: '',
  prix_par_kg: '',
}

function euro(v) {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(v || 0)
}
function kg(v) {
  return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 }).format(v || 0) + ' kg'
}
function dateFr(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

export default function Fournitures() {
  const [items, setItems] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [toasts, setToasts] = useState([])
  const { push } = useToasts()

  const load = async () => {
    setLoading(true)
    try {
      const [f, p] = await Promise.all([fournituresApi.list(), productsApi.list().catch(() => [])])
      setItems(f)
      setProducts(p)
    } catch (err) {
      push(toasts, setToasts, 'error', err.response?.data?.detail || 'Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const today = todayIso()
  const recentEntries = [...items]
    .sort((a, b) => new Date(b.created_at || b.date_obtenu || 0) - new Date(a.created_at || a.date_obtenu || 0))
    .slice(0, 6)

  const todaysCount = items.filter(item => (item.date_obtenu || item.created_at || '').slice(0, 10) === today).length
  const lastEntry = recentEntries[0]

  const dailyCounts = Array.from({ length: 7 }).map((_, index) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - index))
    const iso = d.toISOString().slice(0, 10)
    const count = items.filter(item => (item.date_obtenu || item.created_at || '').slice(0, 10) === iso).length
    return { iso, label: d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' }), count }
  })
  const last7DaysCount = dailyCounts.reduce((sum, item) => sum + item.count, 0)
  const maxCount = Math.max(1, ...dailyCounts.map(item => item.count))

  const save = async (e) => {
    e.preventDefault()
    if (saving) return
    setSaving(true)
    try {
      const payload = {
        ...form,
        product_id: form.product_id ? Number(form.product_id) : null,
        kilo_produit: Number(form.kilo_produit || 0),
        prix_par_kg: Number(form.prix_par_kg || 0),
      }
      await fournituresApi.create(payload)
      push(toasts, setToasts, 'success', 'Fourniture ajoutée en base')
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
            <Truck className="w-7 h-7 text-primary-600" />
            Saisie fourniture
          </h1>
          <p className="text-slate-500 mt-1">Saisie d’arrivage, nombre de saisies par jour et aperçu des dernières saisies</p>
        </div>
        <button onClick={() => setOpen(true)} className="btn-primary">
          <Plus className="w-5 h-5" /> Nouvelle fourniture
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
          <p className="mt-2 text-lg font-bold text-slate-800">{lastEntry ? lastEntry.nom_fournisseur : 'Aucune'}</p>
          <p className="text-sm text-slate-500">{lastEntry ? dateFr(lastEntry.date_obtenu || lastEntry.created_at) : '—'}</p>
        </div>
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold text-slate-800">Nombre de saisies par jour</h3>
            <p className="text-xs text-slate-500 mt-0.5">Suivi des arrivages sur les 7 derniers jours</p>
          </div>
          <span className="badge-blue">{last7DaysCount} total</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-7 gap-3">
          {dailyCounts.map(item => (
            <div key={item.iso} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
              <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
                <span>{item.label}</span>
                <span>{item.count}</span>
              </div>
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-blue-500"
                  style={{ width: `${Math.max(10, (item.count / maxCount) * 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold text-slate-800">Aperçu des dernières saisies</h3>
            <p className="text-xs text-slate-500 mt-0.5">Derniers arrivages enregistrés en base</p>
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
                    Arrivage
                  </span>
                  <p className="text-sm font-semibold text-slate-800">{item.nom_fournisseur}</p>
                </div>
                <p className="text-xs text-slate-500">{item.nom_produit_texte} • {item.origine} • {kg(item.kilo_produit)}</p>
              </div>
              <span className="text-[11px] font-medium text-slate-500 whitespace-nowrap">{dateFr(item.date_obtenu || item.created_at)}</span>
            </div>
          ))}
        </div>
      </div>

      <Modal open={open} onClose={() => setOpen(false)} title="Nouvelle fourniture" size="lg">
        <form onSubmit={save} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="input-label">Date d’arrivée *</label>
              <input required type="date" value={form.date_obtenu} onChange={e => setForm({ ...form, date_obtenu: e.target.value })} className="input" />
            </div>
            <div>
              <label className="input-label">Produit catalogué (optionnel)</label>
              <select value={form.product_id} onChange={e => {
                const id = e.target.value
                setForm(f => {
                  const next = { ...f, product_id: id }
                  if (id) {
                    const p = products.find(x => String(x.id) === String(id))
                    if (p) next.nom_produit_texte = p.nom
                  }
                  return next
                })
              }} className="input">
                <option value="">— Aucun —</option>
                {products.map(p => <option key={p.id} value={p.id}>{p.nom}</option>)}
              </select>
            </div>
            <div>
              <label className="input-label">Nom du produit *</label>
              <input required value={form.nom_produit_texte} onChange={e => setForm({ ...form, nom_produit_texte: e.target.value })} className="input" />
            </div>
            <div>
              <label className="input-label">Origine *</label>
              <input required value={form.origine} onChange={e => setForm({ ...form, origine: e.target.value })} className="input" placeholder="Ex : Bretagne" />
            </div>
            <div>
              <label className="input-label">Fournisseur *</label>
              <input required value={form.nom_fournisseur} onChange={e => setForm({ ...form, nom_fournisseur: e.target.value })} className="input" />
            </div>
            <div>
              <label className="input-label">Kilos reçus *</label>
              <input required type="number" step="0.01" min="0" value={form.kilo_produit} onChange={e => setForm({ ...form, kilo_produit: e.target.value })} className="input" />
            </div>
            <div className="md:col-span-2">
              <label className="input-label">Prix d’achat par kg (€) *</label>
              <input required type="number" step="0.01" min="0" value={form.prix_par_kg} onChange={e => setForm({ ...form, prix_par_kg: e.target.value })} className="input" />
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
