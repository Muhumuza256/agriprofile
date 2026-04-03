import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { listenForOnline } from '@/offline/sync'
import DashboardPage  from '@/pages/DashboardPage'
import FarmerFormPage from '@/pages/FarmerFormPage'
import PlotMapperPage from '@/pages/PlotMapperPage'

export default function App() {
  useEffect(() => {
    listenForOnline()
  }, [])

  return (
    <Routes>
      <Route path="/"           element={<DashboardPage />} />
      <Route path="/new-farmer" element={<FarmerFormPage />} />
      <Route path="/map-plot"   element={<PlotMapperPage />} />
    </Routes>
  )
}
