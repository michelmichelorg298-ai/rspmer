import { NavLink, useLocation } from 'react-router-dom'
import {
  ListPlus,
  TrendingUp,
  Users,
  Package,
  Truck,
  ShoppingCart,
  ArrowLeftRight,
  Fish,
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext.jsx'

export default function Sidebar() {
  const location = useLocation()
  const { user } = useAuth()

  const isDirecteur = user?.role === 'directeur'
  const isAdmin = user?.role === 'admin'

  const entryItems = [
    { to: '/dashboard', label: 'Vue globale', icon: ListPlus },
    { to: '/products', label: 'Produits', icon: Package },
    { to: '/fournitures', label: 'Fournitures', icon: Truck },
    { to: '/ventes', label: 'Ventes', icon: ShoppingCart },
    { to: '/retours', label: 'Retours', icon: ArrowLeftRight },
  ]

  const adminItems = isAdmin ? [{ to: '/users', label: 'Gestion utilisateurs', icon: Users }] : []

  const navItems = isDirecteur
    ? [{ to: '/kpi-dashboard', label: 'Tableau KPI directeur', icon: TrendingUp }]
    : [...entryItems, ...adminItems]

  return (
    <aside className="w-64 bg-gradient-to-b from-slate-900 to-slate-800 text-white flex flex-col flex-shrink-0">
      <div className="px-6 py-5 border-b border-slate-700/60 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-lg">
          <Fish className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold leading-tight">FruitMer</h1>
          <p className="text-xs text-slate-400">Gestion Poissonnerie</p>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {!isDirecteur && (
          <div className="mb-2 rounded-xl border border-slate-700/60 bg-slate-800/60 p-2">
            <div className="px-2 pb-2">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">Saisie de données</p>
            </div>

            <div className="space-y-1">
              {navItems.map(({ to, label, icon: Icon }) => {
                const active = location.pathname === to
                return (
                  <NavLink
                    key={to}
                    to={to}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                      active
                        ? 'bg-primary-600/20 text-primary-300 shadow-inner ring-1 ring-primary-500/30 font-semibold'
                        : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
                    }`}
                  >
                    <Icon className={`w-5 h-5 ${active ? 'text-primary-300' : 'text-slate-400'}`} />
                    {label}
                  </NavLink>
                )
              })}
            </div>
          </div>
        )}

        {isDirecteur && (
          <div className="space-y-1">
            {navItems.map(({ to, label, icon: Icon }) => {
              const active = location.pathname === to
              return (
                <NavLink
                  key={to}
                  to={to}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    active
                      ? 'bg-primary-600/20 text-primary-300 shadow-inner ring-1 ring-primary-500/30 font-semibold'
                      : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${active ? 'text-primary-300' : 'text-slate-400'}`} />
                  {label}
                </NavLink>
              )
            })}
          </div>
        )}
      </nav>

      <div className="px-4 py-4 border-t border-slate-700/60">
        <div className="flex items-center gap-3 px-2">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-accent-400 to-accent-600 flex items-center justify-center text-white font-semibold text-sm shadow">
            {user?.full_name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium truncate">{user?.full_name || 'Utilisateur'}</p>
            <p className="text-xs text-slate-400 truncate capitalize">{user?.role}</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
