import { useEffect, useState } from 'react'
import {
  ListPlus,
  ShoppingCart,
  Truck,
  ArrowLeftRight,
  Package,
  PlusCircle,
  TrendingUp,
  AlertTriangle,
  Fish,
  ArrowUpRight,
} from 'lucide-react'
import StatCard from '../components/StatCard.jsx'
import { productsApi, fournituresApi, ventesApi, retoursApi } from '../api/client.js'
import { ToastContainer, useToasts } from '../components/Toast.jsx'
import { useAuth } from '../contexts/AuthContext.jsx'

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

export default function Dashboard() {
  const { user } = useAuth()
  const { push } = useToasts()
  const [activeTab, setActiveTab] = useState('vente')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [toasts, setToasts] = useState([])

  // DB data states
  const [stats, setStats] = useState({ products: 0, fournitures: 0, ventes: 0, retours: 0, ca: 0, achats: 0, lowStock: 0 })
  const [products, setProducts] = useState([])
  const [fournitures, setFournitures] = useState([])
  const [lowStock, setLowStock] = useState([])
  const [recentVentes, setRecentVentes] = useState([])
  const [recentFournitures, setRecentFournitures] = useState([])
  const [recentRetours, setRecentRetours] = useState([])

  // Form states
  const [vProductId, setVProductId] = useState('')
  const [vFournitureId, setVFournitureId] = useState('')
  const [vClient, setVClient] = useState('')
  const [vDate, setVDate] = useState(new Date().toISOString().split('T')[0])
  const [vKilo, setVKilo] = useState('')
  const [vPrix, setVPrix] = useState('')
  const [vLieu, setVLieu] = useState('')
  const [vTel, setVTel] = useState('')

  const [fProductId, setFProductId] = useState('')
  const [fNomProduit, setFNomProduit] = useState('')
  const [fDate, setFDate] = useState(new Date().toISOString().split('T')[0])
  const [fOrigine, setFOrigine] = useState('')
  const [fFournisseur, setFFournisseur] = useState('')
  const [fKilo, setFKilo] = useState('')
  const [fPrix, setFPrix] = useState('')

  const [rProductId, setRProductId] = useState('')
  const [rFournitureId, setRFournitureId] = useState('')
  const [rOrigine, setROrigine] = useState('')
  const [rKilo, setRKilo] = useState('')
  const [rCause, setRCause] = useState('')

  const [pNom, setPNom] = useState('')
  const [pCategorie, setPCategorie] = useState('Poisson')
  const [pStock, setPStock] = useState('')
  const [pSeuil, setPSeuil] = useState('')
  const [pPrixAchat, setPPrixAchat] = useState('')

  const allRecentEntries = [
    ...recentVentes.map(v => ({
      id: `vente-${v.id}`,
      type: 'Vente',
      label: v.nom_ou_restaurant,
      detail: `${v.nom_produit_texte} • ${kg(v.kilo)}`,
      date: v.date_livraison,
    })),
    ...recentFournitures.map(f => ({
      id: `fourniture-${f.id}`,
      type: 'Arrivage',
      label: f.nom_fournisseur,
      detail: `${f.nom_produit_texte} • ${kg(f.kilo_produit)}`,
      date: f.date_obtenu,
    })),
    ...recentRetours.map(r => ({
      id: `retour-${r.id}`,
      type: 'Retour',
      label: r.origine,
      detail: `${r.nom_produit_texte} • ${kg(r.kilo)} • ${r.cause}`,
      date: r.created_at?.slice(0, 10) || new Date().toISOString().slice(0, 10),
    })),
  ].sort((a, b) => new Date(b.date) - new Date(a.date))

  const todayIso = new Date().toISOString().slice(0, 10)
  const todaysEntries = allRecentEntries.filter(entry => entry.date === todayIso).length
  const lastEntry = allRecentEntries[0]
  const dailyEntryCounts = Array.from({ length: 7 }).map((_, index) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - index))
    const iso = d.toISOString().slice(0, 10)
    const count = allRecentEntries.filter(entry => entry.date === iso).length
    return {
      date: iso,
      label: d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' }),
      count,
    }
  })

  // Load all live database records and calculate dashboard KPIs
  const loadAllDatabaseData = async () => {
    try {
      setLoading(true)
      const [prods, fourns, vents, rets] = await Promise.all([
        productsApi.list(),
        fournituresApi.list(),
        ventesApi.list(),
        retoursApi.list(),
      ])

      setProducts(prods)
      setFournitures(fourns)
      setRecentVentes([...vents].sort((a, b) => new Date(b.date_livraison) - new Date(a.date_livraison)).slice(0, 5))
      setRecentFournitures([...fourns].sort((a, b) => new Date(b.date_obtenu) - new Date(a.date_obtenu)).slice(0, 5))
      setRecentRetours([...rets].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5))

      const low = prods.filter(p => p.stock_kg <= p.seuil_alerte_kg && p.seuil_alerte_kg > 0)
      const totalCA = vents.reduce((sum, v) => sum + (v.kilo * v.prix || 0), 0)
      const totalAchats = fourns.reduce((sum, f) => sum + (f.kilo_produit * f.prix_par_kg || 0), 0)

      setStats({
        products: prods.length,
        fournitures: fourns.length,
        ventes: vents.length,
        retours: rets.length,
        ca: totalCA,
        achats: totalAchats,
        lowStock: low.length,
      })

      setLowStock(low)
    } catch (err) {
      push(toasts, setToasts, 'error', 'Erreur de synchronisation avec la base de données')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAllDatabaseData()
  }, [])

  const filteredFournitures = fournitures.filter(
    f => !vProductId || f.product_id === parseInt(vProductId)
  )

  const margin = stats.achats > 0 ? Math.round(((stats.ca - stats.achats) / stats.achats) * 100) : 0

  // 1. Submit Vente to DB
  const handleVenteSubmit = async (e) => {
    e.preventDefault()
    if (!vProductId || !vKilo || !vPrix || !vClient) {
      push(toasts, setToasts, 'error', 'Veuillez remplir les champs obligatoires')
      return
    }
    const selectedProd = products.find(p => p.id === parseInt(vProductId))
    const selectedFourn = fournitures.find(f => f.id === parseInt(vFournitureId))

    setSubmitting(true)
    try {
      await ventesApi.create({
        product_id: parseInt(vProductId),
        nom_produit_texte: selectedProd?.nom || 'Produit',
        fourniture_id: selectedFourn ? selectedFourn.id : null,
        date_obtenu_fourniture: selectedFourn ? selectedFourn.date_obtenu : null,
        date_livraison: vDate,
        nom_ou_restaurant: vClient,
        kilo: parseFloat(vKilo),
        prix: parseFloat(vPrix),
        lieu: vLieu || null,
        numero_telephone: vTel || null,
      })
      push(toasts, setToasts, 'success', 'Vente sauvegardée dans la base de données !')
      setVKilo('')
      setVPrix('')
      setVClient('')
      setVLieu('')
      setVTel('')
      await loadAllDatabaseData()
    } catch (err) {
      push(toasts, setToasts, 'error', err.response?.data?.detail || 'Erreur d\'enregistrement de la vente')
    } finally {
      setSubmitting(false)
    }
  }

  // 2. Submit Fourniture to DB
  const handleFournitureSubmit = async (e) => {
    e.preventDefault()
    if (!fKilo || !fPrix || !fFournisseur || !fOrigine) {
      push(toasts, setToasts, 'error', 'Veuillez remplir les champs obligatoires')
      return
    }
    const selectedProd = products.find(p => p.id === parseInt(fProductId))

    setSubmitting(true)
    try {
      await fournituresApi.create({
        product_id: fProductId ? parseInt(fProductId) : null,
        nom_produit_texte: selectedProd ? selectedProd.nom : fNomProduit,
        date_obtenu: fDate,
        origine: fOrigine,
        nom_fournisseur: fFournisseur,
        kilo_produit: parseFloat(fKilo),
        prix_par_kg: parseFloat(fPrix),
      })
      push(toasts, setToasts, 'success', 'Fourniture / Arrivage sauvegardé dans la base de données !')
      setFKilo('')
      setFPrix('')
      setFOrigine('')
      setFFournisseur('')
      setFNomProduit('')
      await loadAllDatabaseData()
    } catch (err) {
      push(toasts, setToasts, 'error', err.response?.data?.detail || 'Erreur d\'enregistrement de la fourniture')
    } finally {
      setSubmitting(false)
    }
  }

  // 3. Submit Retour to DB
  const handleRetourSubmit = async (e) => {
    e.preventDefault()
    if (!rKilo || !rCause || !rOrigine) {
      push(toasts, setToasts, 'error', 'Veuillez remplir les champs obligatoires')
      return
    }
    const selectedProd = products.find(p => p.id === parseInt(rProductId))
    const selectedFourn = fournitures.find(f => f.id === parseInt(rFournitureId))

    setSubmitting(true)
    try {
      await retoursApi.create({
        product_id: rProductId ? parseInt(rProductId) : null,
        nom_produit_texte: selectedProd ? selectedProd.nom : 'Produit',
        fourniture_id: selectedFourn ? selectedFourn.id : null,
        origine: rOrigine,
        kilo: parseFloat(rKilo),
        cause: rCause,
      })
      push(toasts, setToasts, 'success', 'Commande retournée enregistrée dans la base de données !')
      setRKilo('')
      setRCause('')
      setROrigine('')
      await loadAllDatabaseData()
    } catch (err) {
      push(toasts, setToasts, 'error', err.response?.data?.detail || 'Erreur d\'enregistrement du retour')
    } finally {
      setSubmitting(false)
    }
  }

  // 4. Submit Produit to DB
  const handleProduitSubmit = async (e) => {
    e.preventDefault()
    if (!pNom) {
      push(toasts, setToasts, 'error', 'Nom du produit obligatoire')
      return
    }
    setSubmitting(true)
    try {
      await productsApi.create({
        nom: pNom,
        categorie: pCategorie,
        stock_kg: pStock ? parseFloat(pStock) : 0.0,
        seuil_alerte_kg: pSeuil ? parseFloat(pSeuil) : 0.0,
        prix_achat_ref: pPrixAchat ? parseFloat(pPrixAchat) : null,
      })
      push(toasts, setToasts, 'success', `Produit "${pNom}" ajouté dans la base de données !`)
      setPNom('')
      setPStock('')
      setPSeuil('')
      setPPrixAchat('')
      await loadAllDatabaseData()
    } catch (err) {
      push(toasts, setToasts, 'error', err.response?.data?.detail || 'Erreur lors de l\'ajout du produit')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <ToastContainer toasts={toasts} />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
            <ListPlus className="w-7 h-7 text-primary-600" />
            Saisie de données
          </h1>
          <p className="text-slate-500 mt-1">
            Saisie directe en base, nombre d’entrées par jour et aperçu des dernières saisies
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm font-medium">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Synchronisation DB Active
        </div>
      </div>

      {/* Live DB Calculated Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
        <StatCard title="Saisies aujourd’hui" value={todaysEntries} icon={ListPlus} color="emerald" subtitle="Total des entrées enregistrées aujourd’hui" />
        <StatCard title="Saisies 7 jours" value={dailyEntryCounts.reduce((sum, item) => sum + item.count, 0)} icon={ShoppingCart} color="blue" subtitle="Toutes entrées regroupées" />
        <StatCard title="Dernière saisie" value={lastEntry ? lastEntry.type : 'Aucune'} icon={ArrowUpRight} color="purple" subtitle={lastEntry ? `${lastEntry.label} • ${dateFr(lastEntry.date)}` : 'Aucune entrée'} />
        <StatCard title="Total en base" value={(stats.products ?? 0) + (stats.fournitures ?? 0) + (stats.ventes ?? 0) + (stats.retour ?? 0)} icon={Package} color="orange" subtitle="Produits + arrivages + ventes + retours" />
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold text-slate-800">Aperçu des dernières saisies</h3>
            <p className="text-xs text-slate-500 mt-0.5">Vue rapide des dernières entrées enregistrées</p>
          </div>
          <span className="badge-blue">{allRecentEntries.length} entrées</span>
        </div>

        <div className="space-y-3">
          {allRecentEntries.length === 0 && (
            <p className="text-sm text-slate-400 text-center py-6">Aucune saisie enregistrée</p>
          )}

          {allRecentEntries.slice(0, 6).map((entry) => (
            <div key={entry.id} className="flex items-start justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="inline-flex items-center rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-emerald-700">
                    {entry.type}
                  </span>
                  <p className="text-sm font-semibold text-slate-800">{entry.label}</p>
                </div>
                <p className="text-xs text-slate-500">{entry.detail}</p>
              </div>
              <span className="text-[11px] font-medium text-slate-500 whitespace-nowrap">{dateFr(entry.date)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-slate-800">Résumé des dernières lignes</h3>
              <p className="text-xs text-slate-500 mt-0.5">Dernière activité saisie dans la base</p>
            </div>
            <Truck className="w-5 h-5 text-blue-500" />
          </div>

          <div className="space-y-3">
            {recentVentes.slice(0, 2).map((v) => (
              <div key={`mini-vente-${v.id}`} className="rounded-xl border border-slate-200 p-3">
                <p className="text-sm font-semibold text-slate-800">Vente</p>
                <p className="text-xs text-slate-500 mt-1">{v.nom_ou_restaurant} • {v.nom_produit_texte}</p>
                <p className="text-xs text-slate-500">{kg(v.kilo)} • {dateFr(v.date_livraison)}</p>
              </div>
            ))}

            {recentFournitures.slice(0, 2).map((f) => (
              <div key={`mini-fourniture-${f.id}`} className="rounded-xl border border-slate-200 p-3">
                <p className="text-sm font-semibold text-slate-800">Arrivage</p>
                <p className="text-xs text-slate-500 mt-1">{f.nom_fournisseur} • {f.nom_produit_texte}</p>
                <p className="text-xs text-slate-500">{kg(f.kilo_produit)} • {dateFr(f.date_obtenu)}</p>
              </div>
            ))}

            {recentRetours.slice(0, 2).map((r) => (
              <div key={`mini-retour-${r.id}`} className="rounded-xl border border-slate-200 p-3">
                <p className="text-sm font-semibold text-slate-800">Retour</p>
                <p className="text-xs text-slate-500 mt-1">{r.origine} • {r.nom_produit_texte}</p>
                <p className="text-xs text-slate-500">{kg(r.kilo)} • {r.cause}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Section : Formulaires de Saisie Rapide dans la DB */}
      <div className="space-y-3">
        <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
          <button
            onClick={() => setActiveTab('vente')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm transition ${
              activeTab === 'vente'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            <ShoppingCart className="w-4 h-4" />
            1. Formulaire Saisie Vente
          </button>

          <button
            onClick={() => setActiveTab('fourniture')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm transition ${
              activeTab === 'fourniture'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            <Truck className="w-4 h-4" />
            2. Formulaire Saisie Arrivage / Fourniture
          </button>

          <button
            onClick={() => setActiveTab('retour')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm transition ${
              activeTab === 'retour'
                ? 'bg-orange-600 text-white shadow-md'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            <ArrowLeftRight className="w-4 h-4" />
            3. Formulaire Saisie Retour (avec cause)
          </button>

          <button
            onClick={() => setActiveTab('produit')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm transition ${
              activeTab === 'produit'
                ? 'bg-purple-600 text-white shadow-md'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            <Package className="w-4 h-4" />
            4. Formulaire Saisie Produit
          </button>
        </div>

        {/* Card containing the selected data entry form */}
        <div className="card p-6 border-t-4 border-t-primary-600 shadow-lg">
          {/* TAB 1: SAISIE VENTE */}
          {activeTab === 'vente' && (
            <form onSubmit={handleVenteSubmit} className="space-y-4">
              <div className="flex items-center justify-between border-b pb-3">
                <h3 className="font-bold text-slate-800 text-lg flex items-center gap-2">
                  <ShoppingCart className="w-5 h-5 text-emerald-600" />
                  Saisie d'une Vente (Ecriture directe en Base de Données)
                </h3>
                <span className="badge-emerald">Enregistrement DB</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Produit Vendu *
                  </label>
                  <select
                    required
                    value={vProductId}
                    onChange={(e) => {
                      setVProductId(e.target.value)
                      setVFournitureId('')
                    }}
                    className="input w-full bg-white"
                  >
                    <option value="">-- Sélectionner le produit --</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.nom} (Stock DB actuel: {p.stock_kg} kg)
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Arrivage / Lot de Fourniture (Optionnel)
                  </label>
                  <select
                    value={vFournitureId}
                    onChange={(e) => setVFournitureId(e.target.value)}
                    className="input w-full bg-white"
                  >
                    <option value="">-- Auto-liaison au dernier arrivage --</option>
                    {filteredFournitures.map((f) => (
                      <option key={f.id} value={f.id}>
                        Lot du {dateFr(f.date_obtenu)} ({f.origine} - {f.nom_fournisseur})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Client / Restaurant *
                  </label>
                  <input
                    type="text"
                    required
                    value={vClient}
                    onChange={(e) => setVClient(e.target.value)}
                    placeholder="ex: Chez Paul / Ocean Resto"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Date de Livraison *
                  </label>
                  <input
                    type="date"
                    required
                    value={vDate}
                    onChange={(e) => setVDate(e.target.value)}
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Quantité Vendue (Kg) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={vKilo}
                    onChange={(e) => setVKilo(e.target.value)}
                    placeholder="ex: 15.5"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Prix de Vente Unitaire (€ / kg) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={vPrix}
                    onChange={(e) => setVPrix(e.target.value)}
                    placeholder="ex: 22.00"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Lieu de livraison
                  </label>
                  <input
                    type="text"
                    value={vLieu}
                    onChange={(e) => setVLieu(e.target.value)}
                    placeholder="ex: Port-Louis"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Numéro de téléphone
                  </label>
                  <input
                    type="text"
                    value={vTel}
                    onChange={(e) => setVTel(e.target.value)}
                    placeholder="ex: 034 00 000 00"
                    className="input w-full"
                  />
                </div>

                <div className="flex items-end">
                  <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3 w-full text-right">
                    <span className="text-xs text-slate-500 font-medium">Montant Total Vente :</span>
                    <p className="text-lg font-bold text-emerald-700">
                      {euro((parseFloat(vKilo) || 0) * (parseFloat(vPrix) || 0))}
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end pt-3 border-t">
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-2 shadow-lg px-6 py-2.5 font-semibold"
                >
                  <PlusCircle className="w-5 h-5" />
                  {submitting ? 'Enregistrement en DB...' : 'Enregistrer la Vente dans la DB'}
                </button>
              </div>
            </form>
          )}

          {/* TAB 2: SAISIE FOURNITURE / ARRIVAGE */}
          {activeTab === 'fourniture' && (
            <form onSubmit={handleFournitureSubmit} className="space-y-4">
              <div className="flex items-center justify-between border-b pb-3">
                <h3 className="font-bold text-slate-800 text-lg flex items-center gap-2">
                  <Truck className="w-5 h-5 text-blue-600" />
                  Saisie d'une Fourniture / Arrivage (Ecriture directe en Base de Données)
                </h3>
                <span className="badge-blue">Entrée de Stock DB</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Produit du Catalogue (Optionnel)
                  </label>
                  <select
                    value={fProductId}
                    onChange={(e) => setFProductId(e.target.value)}
                    className="input w-full bg-white"
                  >
                    <option value="">-- Création / Détection auto par nom --</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.nom}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Nom du Produit (Texte)
                  </label>
                  <input
                    type="text"
                    value={fNomProduit}
                    onChange={(e) => setFNomProduit(e.target.value)}
                    placeholder="ex: Mérou rouge fraichement péché"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Date d'arrivée *
                  </label>
                  <input
                    type="date"
                    required
                    value={fDate}
                    onChange={(e) => setFDate(e.target.value)}
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Nom du Fournisseur *
                  </label>
                  <input
                    type="text"
                    required
                    value={fFournisseur}
                    onChange={(e) => setFFournisseur(e.target.value)}
                    placeholder="ex: Pêcheurs de Tuléar"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Origine *
                  </label>
                  <input
                    type="text"
                    required
                    value={fOrigine}
                    onChange={(e) => setFOrigine(e.target.value)}
                    placeholder="ex: Tuléar / Majunga"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Quantité reçue (Kg) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={fKilo}
                    onChange={(e) => setFKilo(e.target.value)}
                    placeholder="ex: 100.00"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Prix d'achat par Kg (€) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={fPrix}
                    onChange={(e) => setFPrix(e.target.value)}
                    placeholder="ex: 12.50"
                    className="input w-full"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-3 border-t">
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2 shadow-lg px-6 py-2.5 font-semibold"
                >
                  <PlusCircle className="w-5 h-5" />
                  {submitting ? 'Enregistrement en DB...' : 'Enregistrer la Fourniture dans la DB'}
                </button>
              </div>
            </form>
          )}

          {/* TAB 3: SAISIE RETOUR */}
          {activeTab === 'retour' && (
            <form onSubmit={handleRetourSubmit} className="space-y-4">
              <div className="flex items-center justify-between border-b pb-3">
                <h3 className="font-bold text-slate-800 text-lg flex items-center gap-2">
                  <ArrowLeftRight className="w-5 h-5 text-orange-600" />
                  Saisie d'un Retour Client avec Cause (Ecriture directe en Base de Données)
                </h3>
                <span className="badge-orange">Enregistrement Motif DB</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Produit retourné
                  </label>
                  <select
                    value={rProductId}
                    onChange={(e) => setRProductId(e.target.value)}
                    className="input w-full bg-white"
                  >
                    <option value="">-- Sélectionner le produit --</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.nom}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Lot / Arrivage concerné (Optionnel)
                  </label>
                  <select
                    value={rFournitureId}
                    onChange={(e) => setRFournitureId(e.target.value)}
                    className="input w-full bg-white"
                  >
                    <option value="">-- Auto-détection / Général --</option>
                    {fournitures.map((f) => (
                      <option key={f.id} value={f.id}>
                        {f.nom_produit_texte} du {dateFr(f.date_obtenu)} ({f.origine})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Client / Origine du retour *
                  </label>
                  <input
                    type="text"
                    required
                    value={rOrigine}
                    onChange={(e) => setROrigine(e.target.value)}
                    placeholder="ex: Resto La Marina"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Quantité Retournée (Kg) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={rKilo}
                    onChange={(e) => setRKilo(e.target.value)}
                    placeholder="ex: 4.5"
                    className="input w-full"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Cause / Motif détaillé du Retour *
                  </label>
                  <input
                    type="text"
                    required
                    value={rCause}
                    onChange={(e) => setRCause(e.target.value)}
                    placeholder="ex: Non respect du calibre / Problème de fraîcheur"
                    className="input w-full border-orange-300 focus:ring-orange-500"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-3 border-t">
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn bg-orange-600 hover:bg-orange-700 text-white flex items-center gap-2 shadow-lg px-6 py-2.5 font-semibold"
                >
                  <PlusCircle className="w-5 h-5" />
                  {submitting ? 'Enregistrement en DB...' : 'Enregistrer le Retour dans la DB'}
                </button>
              </div>
            </form>
          )}

          {/* TAB 4: SAISIE PRODUIT */}
          {activeTab === 'produit' && (
            <form onSubmit={handleProduitSubmit} className="space-y-4">
              <div className="flex items-center justify-between border-b pb-3">
                <h3 className="font-bold text-slate-800 text-lg flex items-center gap-2">
                  <Package className="w-5 h-5 text-purple-600" />
                  Ajouter un Produit au Catalogue DB
                </h3>
                <span className="badge-purple">Catalogue & Seuil DB</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Nom du Produit *
                  </label>
                  <input
                    type="text"
                    required
                    value={pNom}
                    onChange={(e) => setPNom(e.target.value)}
                    placeholder="ex: Crevettes géantes"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Catégorie *
                  </label>
                  <select
                    value={pCategorie}
                    onChange={(e) => setPCategorie(e.target.value)}
                    className="input w-full bg-white"
                  >
                    <option value="Poisson">Poisson</option>
                    <option value="Crustacé">Crustacé</option>
                    <option value="Mollusque">Mollusque</option>
                    <option value="Autre">Autre</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Stock initial (Kg)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={pStock}
                    onChange={(e) => setPStock(e.target.value)}
                    placeholder="0.00"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Seuil d'alerte Rupture (Kg)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={pSeuil}
                    onChange={(e) => setPSeuil(e.target.value)}
                    placeholder="ex: 10.00"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Prix d'achat référence (€/kg)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={pPrixAchat}
                    onChange={(e) => setPPrixAchat(e.target.value)}
                    placeholder="ex: 15.00"
                    className="input w-full"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-3 border-t">
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn bg-purple-600 hover:bg-purple-700 text-white flex items-center gap-2 shadow-lg px-6 py-2.5 font-semibold"
                >
                  <PlusCircle className="w-5 h-5" />
                  {submitting ? 'Enregistrement en DB...' : 'Ajouter le Produit dans la DB'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
