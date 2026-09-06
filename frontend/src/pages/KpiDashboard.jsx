import { useEffect, useState } from 'react'
import {
  TrendingUp,
  Package,
  Calendar,
  Truck,
  ArrowUpRight,
  Clock,
  CheckCircle,
  AlertTriangle,
  ArrowLeftRight,
  Filter,
  DollarSign,
} from 'lucide-react'
import StatCard from '../components/StatCard.jsx'
import { productsApi, kpisApi } from '../api/client.js'
import { ToastContainer, useToasts } from '../components/Toast.jsx'

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

export default function KpiDashboard() {
  const [products, setProducts] = useState([])
  const [lots, setLots] = useState([])
  const [selectedProductId, setSelectedProductId] = useState('')
  const [selectedLotId, setSelectedLotId] = useState('')
  const [analytics, setAnalytics] = useState(null)
  const [loadingProducts, setLoadingProducts] = useState(true)
  const [loadingLots, setLoadingLots] = useState(false)
  const [loadingAnalytics, setLoadingAnalytics] = useState(false)
  const [toasts, setToasts] = useState([])
  const { push } = useToasts()

  // Load products list on mount
  useEffect(() => {
    (async () => {
      try {
        setLoadingProducts(true)
        const prods = await productsApi.list()
        setProducts(prods)
      } catch (err) {
        push(toasts, setToasts, 'error', 'Erreur lors du chargement des produits')
      } finally {
        setLoadingProducts(false)
      }
    })()
  }, [])

  // Load lots when product selection changes
  useEffect(() => {
    (async () => {
      try {
        setLoadingLots(true)
        const pId = selectedProductId ? parseInt(selectedProductId) : null
        const lotsData = await kpisApi.getLots(pId)
        setLots(lotsData)
        if (lotsData.length > 0) {
          setSelectedLotId(lotsData[0].id.toString())
        } else {
          setSelectedLotId('')
          setAnalytics(null)
        }
      } catch (err) {
        push(toasts, setToasts, 'error', 'Erreur lors du chargement des arrivages/lots')
      } finally {
        setLoadingLots(false)
      }
    })()
  }, [selectedProductId])

  // Load analytics when lot selection changes
  useEffect(() => {
    if (!selectedLotId) {
      setAnalytics(null)
      return
    }
    (async () => {
      try {
        setLoadingAnalytics(true)
        const data = await kpisApi.getAnalytics(parseInt(selectedLotId))
        setAnalytics(data)
      } catch (err) {
        push(toasts, setToasts, 'error', 'Impossible de charger l\'analyse KPI du lot')
      } finally {
        setLoadingAnalytics(false)
      }
    })()
  }, [selectedLotId])

  const fournitureInfo = analytics?.fourniture
  const kpis = analytics?.kpis

  return (
    <div className="space-y-6">
      <ToastContainer toasts={toasts} />

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
            <TrendingUp className="w-7 h-7 text-purple-600" />
            Tableau de Bord KPI Strategique
          </h1>
          <p className="text-slate-500 mt-1">
            Analyse détaillée par produit et date d'arrivée (Ventes, Écoulement du stock, Bénéfices & Retours)
          </p>
        </div>
        <span className="badge-purple font-medium px-3 py-1 text-xs rounded-full border border-purple-200">
          Supervision Direction & Admin
        </span>
      </div>

      {/* Selectors Panel */}
      <div className="card p-5 bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-xl">
        <div className="flex items-center gap-2 mb-4 text-purple-300 font-semibold text-sm tracking-wide uppercase">
          <Filter className="w-4 h-4" />
          Sélection du produit et du lot d'arrivage
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              1. Choisir le Produit
            </label>
            <select
              value={selectedProductId}
              onChange={(e) => setSelectedProductId(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg text-white px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Tous les produits ({products.length})</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nom} ({p.categorie})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              2. Sélectionner la Date d'arrivée / Lot
            </label>
            <select
              value={selectedLotId}
              onChange={(e) => setSelectedLotId(e.target.value)}
              disabled={lots.length === 0}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg text-white px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
            >
              {lots.length === 0 ? (
                <option value="">Aucun lot disponible</option>
              ) : (
                lots.map((l) => (
                  <option key={l.id} value={l.id}>
                    Arrivée du {dateFr(l.date_obtenu)} — {l.nom_produit_texte} ({kg(l.kilo_produit)} - {l.origine})
                  </option>
                ))
              )}
            </select>
          </div>
        </div>
      </div>

      {loadingAnalytics && (
        <div className="p-12 text-center text-slate-400">
          Chargement des indicateurs clés de performance...
        </div>
      )}

      {!loadingAnalytics && !analytics && (
        <div className="card p-8 text-center text-slate-500 space-y-2">
          <Package className="w-12 h-12 text-slate-300 mx-auto" />
          <p className="font-semibold text-slate-700">Aucun lot de fourniture sélectionné</p>
          <p className="text-sm">Veuillez sélectionner un produit et une date d'arrivée ci-dessus pour consulter ses KPI.</p>
        </div>
      )}

      {!loadingAnalytics && analytics && fournitureInfo && kpis && (
        <>
          {/* Main Arrivage Summary Header */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center text-purple-700 font-bold text-xl flex-shrink-0">
                <Truck className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-800">
                  {fournitureInfo.nom_produit_texte}
                </h2>
                <p className="text-sm text-slate-500 flex items-center gap-3 mt-0.5">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" /> Date d'arrivée : <b>{dateFr(fournitureInfo.date_obtenu)}</b>
                  </span>
                  <span>•</span>
                  <span>Fournisseur : <b>{fournitureInfo.nom_fournisseur}</b> ({fournitureInfo.origine})</span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 border-t md:border-t-0 pt-3 md:pt-0 border-slate-100">
              <div className="text-right">
                <p className="text-xs text-slate-500 uppercase font-semibold">Stock Reçu</p>
                <p className="text-lg font-extrabold text-slate-800">{kg(fournitureInfo.kilo_produit)}</p>
              </div>
              <div className="h-8 w-px bg-slate-200" />
              <div className="text-right">
                <p className="text-xs text-slate-500 uppercase font-semibold">Coût d'Achat Lot</p>
                <p className="text-lg font-extrabold text-blue-700">{euro(fournitureInfo.cout_total_achat)}</p>
              </div>
            </div>
          </div>

          {/* KPI Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
            {/* 1. Somme kg vendus */}
            <StatCard
              title="Ventes réalisées"
              value={kg(kpis.total_kg_vendus)}
              icon={Package}
              color="emerald"
              subtitle={`${kpis.nb_ventes ?? 0} ventes enregistrées sur ce lot`}
            />

            {/* 2. Jours d'écoulement / Kilos restants */}
            <div className="card p-5 relative overflow-hidden flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Écoulement du Stock
                </span>
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${kpis.est_tout_vendu ? 'bg-emerald-100 text-emerald-600' : 'bg-orange-100 text-orange-600'}`}>
                  {kpis.est_tout_vendu ? <CheckCircle className="w-5 h-5" /> : <Clock className="w-5 h-5" />}
                </div>
              </div>

              <div className="mt-3">
                {kpis.est_tout_vendu ? (
                  <div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-extrabold text-emerald-700">
                        {kpis.jours_pour_tout_vendre} {kpis.jours_pour_tout_vendre === 1 ? 'jour' : 'jours'}
                      </span>
                    </div>
                    <p className="text-xs font-medium text-emerald-600 mt-1 flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5" /> Tout le produit arrivé le {dateFr(fournitureInfo.date_obtenu)} a été vendu !
                    </p>
                  </div>
                ) : (
                  <div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-extrabold text-orange-600">
                        {kg(kpis.kilo_restant)}
                      </span>
                    </div>
                    <p className="text-xs font-medium text-orange-600 mt-1 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" /> Vente toujours en cours (Stock restant)
                    </p>
                  </div>
                )}
              </div>

              {/* Progress bar */}
              <div className="mt-3">
                <div className="flex justify-between text-[11px] text-slate-500 font-medium mb-1">
                  <span>Progression des ventes</span>
                  <span>{fournitureInfo.kilo_produit > 0 ? Math.min(100, Math.round((kpis.total_kg_vendus / fournitureInfo.kilo_produit) * 100)) : 0}%</span>
                </div>
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${kpis.est_tout_vendu ? 'bg-emerald-500' : 'bg-orange-500'}`}
                    style={{ width: `${fournitureInfo.kilo_produit > 0 ? Math.min(100, Math.round((kpis.total_kg_vendus / fournitureInfo.kilo_produit) * 100)) : 0}%` }}
                  />
                </div>
              </div>
            </div>

            {/* 3. Bénéfice Net */}
            <StatCard
              title="Bénéfice Net Lot"
              value={euro(kpis.benefice_net)}
              icon={TrendingUp}
              color={(kpis.benefice_net ?? 0) >= 0 ? "purple" : "red"}
              subtitle={`Marge : ${kpis.marge_pct ?? 0}% (CA: ${euro(kpis.chiffre_affaires)})`}
            />

            {/* 4. Commandes Retournées */}
            <StatCard
              title="Retours Clients"
              value={kg(kpis.total_kg_retours)}
              icon={ArrowLeftRight}
              color={(kpis.total_kg_retours ?? 0) > 0 ? "orange" : "blue"}
              subtitle={`${kpis.nb_retours ?? 0} retour(s) enregistré(s)`}
            />
          </div>

          {/* Table: Commandes Retournées avec Causes de Retour */}
          <div className="card">
            <div className="card-header bg-slate-50/50">
              <div>
                <h3 className="font-bold text-slate-800 flex items-center gap-2">
                  <ArrowLeftRight className="w-5 h-5 text-orange-500" />
                  Commandes Retournées & Causes de Retour pour ce lot
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Liste des retours enregistrés liés à l'arrivage du {dateFr(fournitureInfo.date_obtenu)}
                </p>
              </div>
              <span className="badge-orange">{kpis.commandes_retournees?.length || 0} retours</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="table-th">Quantité Retournée</th>
                    <th className="table-th">Origine / Client</th>
                    <th className="table-th">Date de retour</th>
                    <th className="table-th">Cause / Motif du Retour</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {(!kpis.commandes_retournees || kpis.commandes_retournees.length === 0) ? (
                    <tr>
                      <td colSpan={4} className="table-td text-center text-slate-400 py-8">
                        <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                        Aucune commande retournée sur cet arrivage. Qualité 100% conforme.
                      </td>
                    </tr>
                  ) : (
                    kpis.commandes_retournees.map((ret) => (
                      <tr key={ret.id} className="hover:bg-slate-50/60 transition">
                        <td className="table-td font-bold text-orange-700">
                          {kg(ret.kilo)}
                        </td>
                        <td className="table-td font-medium text-slate-800">
                          {ret.origine}
                        </td>
                        <td className="table-td text-slate-500">
                          {dateFr(ret.date)}
                        </td>
                        <td className="table-td">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4 text-orange-500 flex-shrink-0" />
                            <span className="bg-orange-50 text-orange-900 border border-orange-200 px-3 py-1 rounded-lg text-xs font-semibold">
                              {ret.cause}
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
