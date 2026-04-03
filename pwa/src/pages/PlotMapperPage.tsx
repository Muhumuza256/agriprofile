import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { plotMapper } from '@/gps/PlotMapper'
import { db, addToSyncQueue } from '@/offline/db'
import clsx from 'clsx'

export default function PlotMapperPage() {
  const navigate = useNavigate()
  const [points, setPoints] = useState(0)
  const [acres, setAcres] = useState(0)
  const [accuracy, setAccuracy] = useState<number | null>(null)
  const [watching, setWatching] = useState(false)
  const [watchId, setWatchId] = useState<number | null>(null)
  const [farmerId, setFarmerId] = useState('')
  const [landTenure, setLandTenure] = useState('customary')
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  const updateStats = useCallback(() => {
    setPoints(plotMapper.pointCount)
    setAcres(plotMapper.calculateAreaAcres())
    setAccuracy(plotMapper.averageAccuracyM)
  }, [])

  const startWatching = () => {
    if (!navigator.geolocation) {
      setError('Geolocation not supported on this device.')
      return
    }
    const id = navigator.geolocation.watchPosition(
      (pos) => {
        plotMapper.addPoint(pos)
        updateStats()
      },
      (err) => setError(`GPS error: ${err.message}`),
      { enableHighAccuracy: true, maximumAge: 2000 },
    )
    setWatchId(id)
    setWatching(true)
  }

  const stopWatching = () => {
    if (watchId !== null) navigator.geolocation.clearWatch(watchId)
    setWatching(false)
  }

  const handleSave = async () => {
    if (plotMapper.pointCount < 3) {
      setError('You need at least 3 GPS points to define a plot.')
      return
    }
    if (!farmerId.trim()) {
      setError('Farmer ID is required.')
      return
    }

    const localId = `plot_${Date.now()}`
    await db.pendingPlots.add({
      localId,
      farmerId: farmerId.trim(),
      plotName: 'Plot',
      coordinates: plotMapper.getCoordinates().map(({ lat, lon, accuracy }) => ({ lat, lon, accuracy })),
      calculatedAcres: plotMapper.calculateAreaAcres(),
      landTenure,
      data: { farmer: farmerId.trim(), land_tenure: landTenure },
      syncStatus: 'pending',
      createdAt: Date.now(),
    })
    await addToSyncQueue('plot', localId)
    plotMapper.reset()
    setSaved(true)
    setTimeout(() => navigate('/'), 1500)
  }

  useEffect(() => {
    plotMapper.reset()
    return () => { if (watchId !== null) navigator.geolocation.clearWatch(watchId) }
  }, [])

  if (saved) {
    return (
      <div className="min-h-screen bg-primary-900 flex items-center justify-center">
        <div className="text-center text-white">
          <p className="text-4xl mb-2">✓</p>
          <p className="font-medium">Plot saved offline</p>
          <p className="text-sm text-primary-300 mt-1">Will sync when online</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-primary-900 p-4 flex flex-col">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate(-1)} className="text-primary-300 text-sm">← Back</button>
        <h1 className="text-white font-semibold">Map Farm Plot</h1>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        {[
          { label: 'Points', value: points },
          { label: 'Acres', value: acres.toFixed(3) },
          { label: 'Accuracy (m)', value: accuracy?.toFixed(1) ?? '—' },
        ].map((s) => (
          <div key={s.label} className="bg-primary-800/60 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-white font-mono">{s.value}</p>
            <p className="text-xs text-primary-300">{s.label}</p>
          </div>
        ))}
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-700 rounded p-3 mb-4 text-sm text-red-200">
          {error}
        </div>
      )}

      {/* Walk instruction */}
      <div className="bg-primary-800/40 rounded-lg p-4 mb-4 text-sm text-primary-200">
        {!watching ? (
          <p>Walk to the first corner of the plot, then press Start Mapping. Walk the boundary to collect points.</p>
        ) : (
          <p>Walking boundary… {points} point{points !== 1 ? 's' : ''} collected. Press Stop when you return to the start.</p>
        )}
      </div>

      {/* Farmer ID */}
      <div className="mb-3">
        <label className="block text-xs text-primary-300 mb-1">Farmer UUID or ID</label>
        <input
          value={farmerId}
          onChange={(e) => setFarmerId(e.target.value)}
          placeholder="Paste farmer UUID"
          className="w-full bg-primary-800 border border-primary-600 text-white rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Land tenure */}
      <div className="mb-6">
        <label className="block text-xs text-primary-300 mb-1">Land Tenure</label>
        <select
          value={landTenure}
          onChange={(e) => setLandTenure(e.target.value)}
          className="w-full bg-primary-800 border border-primary-600 text-white rounded px-3 py-2 text-sm focus:outline-none"
        >
          <option value="customary">Customary</option>
          <option value="leasehold">Leasehold</option>
          <option value="freehold">Freehold</option>
          <option value="mailo">Mailo</option>
        </select>
      </div>

      {/* Actions */}
      <div className="mt-auto space-y-3">
        <button
          onClick={watching ? stopWatching : startWatching}
          className={clsx(
            'w-full py-4 rounded-xl font-semibold text-white transition-colors',
            watching ? 'bg-red-600 active:bg-red-700' : 'bg-primary-700 active:bg-primary-900',
          )}
        >
          {watching ? '⏹ Stop Mapping' : '▶ Start Mapping'}
        </button>
        {!watching && points >= 3 && (
          <button
            onClick={handleSave}
            className="w-full py-3 rounded-xl bg-accent-700 text-white font-semibold active:opacity-80"
          >
            Save Plot ({acres.toFixed(2)} ac)
          </button>
        )}
      </div>
    </div>
  )
}
