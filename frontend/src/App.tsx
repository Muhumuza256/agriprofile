import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import Layout from '@/components/Layout'
import LoginPage        from '@/pages/LoginPage'
import OverviewPage     from '@/pages/OverviewPage'
import GroupsPage       from '@/pages/GroupsPage'
import FarmersPage      from '@/pages/FarmersPage'
import FarmerDetailPage from '@/pages/FarmerDetailPage'
import MapPage          from '@/pages/MapPage'
import AnalyticsPage    from '@/pages/AnalyticsPage'
import ReportsPage      from '@/pages/ReportsPage'
import ParametersPage   from '@/pages/ParametersPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Layout>{children}</Layout>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route path="/" element={<ProtectedRoute><OverviewPage /></ProtectedRoute>} />
      <Route path="/groups" element={<ProtectedRoute><GroupsPage /></ProtectedRoute>} />
      <Route path="/farmers" element={<ProtectedRoute><FarmersPage /></ProtectedRoute>} />
      <Route path="/farmers/:id" element={<ProtectedRoute><FarmerDetailPage /></ProtectedRoute>} />
      <Route path="/map" element={<ProtectedRoute><MapPage /></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
      <Route path="/reports" element={<ProtectedRoute><ReportsPage /></ProtectedRoute>} />
      <Route path="/parameters" element={<ProtectedRoute><ParametersPage /></ProtectedRoute>} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
