import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getPendingCount } from '@/offline/db'
import { runSync } from '@/offline/sync'
import clsx from 'clsx'

export default function DashboardPage() {
  const [pending, setPending] = useState({ groups: 0, farmers: 0, plots: 0, total: 0 })
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [syncing, setSyncing] = useState(false)
  const [lastSync, setLastSync] = useState<string | null>(null)

  useEffect(() => {
    const refresh = async () => {
      const counts = await getPendingCount()
      setPending(counts)
    }
    refresh()

    const onOnline  = () => setIsOnline(true)
    const onOffline = () => setIsOnline(false)
    window.addEventListener('online',  onOnline)
    window.addEventListener('offline', onOffline)
    return () => {
      window.removeEventListener('online',  onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [])

  const handleSync = async () => {
    if (!isOnline) return
    setSyncing(true)
    try {
      const result = await runSync()
      setLastSync(new Date().toLocaleTimeString())
      const counts = await getPendingCount()
      setPending(counts)
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="min-h-screen bg-primary-900 p-4 pb-24">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-lg font-bold text-white">AgriProfile</h1>
          <p className="text-xs text-primary-200">Field Agent</p>
        </div>
        <div className={clsx(
          'flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full',
          isOnline ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300',
        )}>
          <span className={clsx('w-1.5 h-1.5 rounded-full', isOnline ? 'bg-green-400' : 'bg-red-400')} />
          {isOnline ? 'Online' : 'Offline'}
        </div>
      </div>

      {/* Sync status */}
      {pending.total > 0 && (
        <div className="bg-amber-900/50 border border-amber-700 rounded-lg p-3 mb-4 flex items-center justify-between">
          <p className="text-sm text-amber-200">
            {pending.total} record{pending.total !== 1 ? 's' : ''} awaiting sync
          </p>
          <button
            onClick={handleSync}
            disabled={!isOnline || syncing}
            className="text-xs bg-amber-600 text-white px-3 py-1 rounded disabled:opacity-50"
          >
            {syncing ? 'Syncing…' : 'Sync Now'}
          </button>
        </div>
      )}

      {lastSync && (
        <p className="text-xs text-primary-400 mb-4">Last synced: {lastSync}</p>
      )}

      {/* Action grid */}
      <div className="grid grid-cols-2 gap-3">
        {[
          { to: '/new-group',   label: 'Register Group', icon: '🏘️', color: 'bg-primary-700' },
          { to: '/new-farmer',  label: 'Add Farmer',     icon: '👤', color: 'bg-primary-700' },
          { to: '/map-plot',    label: 'Map Plot',        icon: '📍', color: 'bg-accent-700' },
          { to: '/pending',     label: 'Pending Uploads', icon: '📤', color: 'bg-neutral-700' },
        ].map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className={`${item.color} rounded-xl p-5 text-white flex flex-col items-center justify-center gap-2 active:opacity-80`}
          >
            <span className="text-2xl">{item.icon}</span>
            <span className="text-sm font-medium text-center">{item.label}</span>
          </Link>
        ))}
      </div>

      {/* Pending counts */}
      <div className="mt-6 grid grid-cols-3 gap-3">
        {[
          { label: 'Groups', count: pending.groups },
          { label: 'Farmers', count: pending.farmers },
          { label: 'Plots', count: pending.plots },
        ].map((item) => (
          <div key={item.label} className="bg-primary-800/50 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-white font-mono">{item.count}</p>
            <p className="text-xs text-primary-300">{item.label} pending</p>
          </div>
        ))}
      </div>
    </div>
  )
}
