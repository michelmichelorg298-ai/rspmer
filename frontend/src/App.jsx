import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import KpiDashboard from './pages/KpiDashboard.jsx'
import Users from './pages/Users.jsx'
import Products from './pages/Products.jsx'
import Fournitures from './pages/Fournitures.jsx'
import Ventes from './pages/Ventes.jsx'
import CommandesRetour from './pages/CommandesRetour.jsx'
import Layout from './components/Layout.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'

import { useAuth } from './contexts/AuthContext.jsx'

export default function App() {
  const { user } = useAuth()
  const defaultRoute = user?.role === 'directeur' ? '/kpi-dashboard' : '/dashboard'

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Navigate to={defaultRoute} replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/kpi-dashboard" element={<KpiDashboard />} />
        <Route path="/users" element={<Users />} />
        <Route path="/products" element={<Products />} />
        <Route path="/fournitures" element={<Fournitures />} />
        <Route path="/ventes" element={<Ventes />} />
        <Route path="/retours" element={<CommandesRetour />} />
      </Route>
      <Route path="*" element={<Navigate to={defaultRoute} replace />} />
    </Routes>
  )
}
