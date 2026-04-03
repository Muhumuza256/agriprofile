import { useState } from 'react'
import { reportsApi } from '@/api/endpoints'

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default function ReportsPage() {
  const [farmerId, setFarmerId] = useState('')
  const [groupId, setGroupId] = useState('')
  const [loading, setLoading] = useState<string | null>(null)

  const run = async (key: string, fn: () => Promise<{ data: Blob }>, filename: string) => {
    setLoading(key)
    try {
      const res = await fn()
      downloadBlob(res.data, filename)
    } catch {
      alert('Report generation failed.')
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="space-y-8 max-w-2xl">
      <h1 className="text-xl font-bold font-display">Reports</h1>

      {/* Individual Credit Report */}
      <div className="card p-6 space-y-4">
        <h2 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide">
          Individual Farmer Credit Report
        </h2>
        <div className="flex gap-3">
          <input
            value={farmerId}
            onChange={(e) => setFarmerId(e.target.value)}
            placeholder="Farmer UUID"
            className="border border-neutral-300 rounded px-3 py-1.5 text-sm flex-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            disabled={!farmerId || loading === 'farmer'}
            onClick={() => run('farmer', () => reportsApi.farmerCredit(farmerId), `credit-report-${farmerId}.pdf`)}
            className="btn-primary text-sm disabled:opacity-50"
          >
            {loading === 'farmer' ? 'Generating…' : 'Generate PDF'}
          </button>
        </div>
      </div>

      {/* Group Credit Report */}
      <div className="card p-6 space-y-4">
        <h2 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide">
          Group Credit Profile
        </h2>
        <div className="flex gap-3">
          <input
            value={groupId}
            onChange={(e) => setGroupId(e.target.value)}
            placeholder="Group UUID"
            className="border border-neutral-300 rounded px-3 py-1.5 text-sm flex-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            disabled={!groupId || loading === 'group'}
            onClick={() => run('group', () => reportsApi.groupCredit(groupId), `group-profile-${groupId}.pdf`)}
            className="btn-primary text-sm disabled:opacity-50"
          >
            {loading === 'group' ? 'Generating…' : 'Generate PDF'}
          </button>
        </div>
      </div>

      {/* Bulk Excel exports */}
      <div className="card p-6 space-y-4">
        <h2 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide">
          Data Exports
        </h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Crop Intelligence</p>
              <p className="text-xs text-neutral-400">Crop distribution, harvest windows, acreage by crop</p>
            </div>
            <button
              disabled={loading === 'crops'}
              onClick={() => run('crops', reportsApi.cropIntelligenceExcel, 'crop-intelligence.xlsx')}
              className="btn-secondary text-sm disabled:opacity-50"
            >
              {loading === 'crops' ? '…' : 'Export Excel'}
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Unbanked Farmers</p>
              <p className="text-xs text-neutral-400">Farmers without bank account or mobile money</p>
            </div>
            <button
              disabled={loading === 'unbanked'}
              onClick={() => run('unbanked', reportsApi.unbankedFarmers, 'unbanked-farmers.xlsx')}
              className="btn-secondary text-sm disabled:opacity-50"
            >
              {loading === 'unbanked' ? '…' : 'Export Excel'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
