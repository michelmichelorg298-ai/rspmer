import { useEffect, useState } from 'react'
import { ArrowLeftRight, Plus, CalendarDays } from 'lucide-react'
import Modal from '../components/Modal.jsx'
import { ToastContainer, useToasts } from '../components/Toast.jsx'
import { retoursApi, fournituresApi, productsApi } from '../api/client.js'

const emptyForm = {
  product_id: '',
  nom_produit_texte: '',
  fourniture_id: '',
  origine: '',
  kilo: '',
  cause: '',
}

function kg(v) {
  return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 }).format(v || 0) + ' kg'
}
function dateFr(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

export default function CommandesRetour() {
  const [items, setItems] = useState([])
  const [fourns, setFourns] = useState([])
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
      const [r, f, p] = await Promise.all([
        retoursApi.list(),
        fournituresApi.list().catch(() => []),
        productsApi.list().catch(() => []),
      ])
      setItems(r)
      setFourns(f)
      setProducts(p)
    } catch (err) {
      push(toasts, setToasts, 'error', err.response?.data?.detail || 'Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const today = new Date().toISOString().slice(0, 10)
  const recentEntries = [...items]
    .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
    .slice(0, 6)

  const todaysCount = items.filter(item => (item.created_at || '').slice(0, 10) === today).length
  const lastEntry = recentEntries[0]

  const dailyCounts = Array.from({ length: 7 }).map((_, index) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - index))
    const iso = d.toISOString().slice(0, 10)
    const count = items.filter(item => (item.created_at || '').slice(0, 10) === iso).length
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
        fourniture_id: form.fourniture_id ? Number(form.fourniture_id) : null,
        kilo: Number(form.kilo || 0),
      }
      await retoursApi.create(payload)
      push(toasts, setToasts, 'success', 'Retour ajouté en base')
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
            <ArrowLeftRight className="w-7 h-7 text-primary-600" />
            Saisie retour
          </h1>
          <p className="text-slate-500 mt-1">Saisie de retour, nombre de saisies par jour et aperçu des dernières saisies</p>
        </div>
        <button onClick={() => setOpen(true)} className="btn-primary">
          <Plus className="w-5 h-5" /> Nouveau retour
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
          <p className="mt-2 text-lg font-bold text-slate-800">{lastEntry ? lastEntry.origine : 'Aucune'}</p>
          <p className="text-sm text-slate-500">{lastEntry ? dateFr(lastEntry.created_at) : '—'}</p>
        </div>
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold text-slate-800">Nombre de saisies par jour</h3>
            <p className="text-xs text-slate-500 mt-0.5">Suivi des retours sur les 7 derniers jours</p>
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
            <p className="text-xs text-slate-500 mt-0.5">Derniers retours enregistrés en base</p>
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
                    Retour
                  </span>
                  <p className="text-sm font-semibold text-slate-800">{item.origine}</p>
                </div>
                <p className="text-xs text-slate-500">{item.nom_produit_texte} • {kg(item.kilo)} • {item.cause}</p>
              </div>
              <span className="text-[11px] font-medium text-slate-500 whitespace-nowrap">{dateFr(item.created_at)}</span>
            </div>
          ))}
        </div>
      </div>

      <Modal open={open} onClose={() => setOpen(false)} title="Nouveau retour" size="lg">
        <form onSubmit={save} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="input-label">Produit catalogué</label>
              <select value={form.product_id} onChange={e => {
                const id = e.target.value
                setForm(f => ({ ...f, product_id: id, nom_produit_texte: id ? (products.find(p => String(p.id) === String(id))?.nom || f.nom_produit_texte) : f.nom_produit_texte }))
              }} className="input">
                <option value="">— Aucun —</option>
                {products.map(p => <option key={p.id} value={p.id}>{p.nom}</option>)}
              </select>
            </div>
            <div>
              <label className="input-label">Nom du produit *</label>
              <input required value={form.nom_produit_texte} onChange={e => setForm({ ...form, nom_produit_texte: e.target.value })} className="input" />
            </div>
            <div className="md:col-span-2">
              <label className="input-label">Fourniture liée</label>
              <select value={form.fourniture_id} onChange={e => {
                const id = e.target.value
                setForm(f => {
                  const next = { ...f, fourniture_id: id }
                  if (id) {
                    const fn = fourns.find(x => String(x.id) === String(id))
                    if (fn) {
                      next.nom_produit_texte = fn.nom_produit_texte
                      next.origine = fn.origine
                    }
                  }
                  return next
                })
              }} className="input">
                <option value="">— Aucune —</option>
                {fourns.map(f => <option key={f.id} value={f.id}>{f.nom_produit_texte} — {f.origine}</option>)}
              </select>
            </div>
            <div>
              <label className="input-label">Origine *</label>
              <input required value={form.origine} onChange={e => setForm({ ...form, origine: e.target.value })} className="input" />
            </div>
            <div>
              <label className="input-label">Kilos retournés *</label>
              <input required type="number" step="0.01" min="0" value={form.kilo} onChange={e => setForm({ ...form, kilo: e.target.value })} className="input" />
            </div>
            <div className="md:col-span-2">
              <label className="input-label">Cause / motif *</label>
              <textarea required rows={3} value={form.cause} onChange={e => setForm({ ...form, cause: e.target.value })} className="input resize-none" />
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
