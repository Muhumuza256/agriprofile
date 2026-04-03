import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/api/endpoints'
import StatCard from '@/components/StatCard'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import type { ScoreBand } from '@/types'

const BAND_COLORS: Record<string, string> = {
  platinum: '#7C3AED',
  gold:     '#D97706',
  silver:   '#6B7280',
  bronze:   '#B45309',
  unscored: '#9CA3AF',
}

export default function OverviewPage() {
  const { data: overview, isLoading } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
  })

  const { data: distribution } = useQuery({
    queryKey: ['analytics', 'score-distribution'],
    queryFn: () => analyticsApi.scoreDistribution().then((r) => r.data),
  })

  if (isLoading) return <div className="text-neutral-500 text-sm">Loading…</div>

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-bold text-neutral-900 font-display">Dashboard</h1>
        <p className="text-sm text-neutral-500 mt-0.5">Platform overview · AgriProfile</p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Farmers"       value={overview?.total_farmers ?? '—'}    accent />
        <StatCard label="Approved Groups"      value={overview?.total_groups ?? '—'} />
        <StatCard label="Districts Covered"    value={overview?.districts_covered ?? '—'} />
        <StatCard
          label="Avg ACS Score"
          value={overview?.avg_acs_score.toFixed(1) ?? '—'}
          sub="across all scored farmers"
        />
      </div>

      {overview?.pending_submissions !== undefined && overview.pending_submissions > 0 && (
        <div className="card p-4 border-l-4 border-amber-500 bg-amber-50">
          <p className="text-sm font-medium text-amber-800">
            {overview.pending_submissions} submission{overview.pending_submissions !== 1 ? 's' : ''} awaiting review
          </p>
        </div>
      )}

      {/* Score distribution */}
      {distribution && (
        <div className="card p-6">
          <h2 className="text-sm font-semibold text-neutral-700 mb-4 uppercase tracking-wide">
            Credit Band Distribution
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={distribution as ScoreBand[]}>
              <XAxis
                dataKey="credit_band"
                tick={{ fontSize: 12 }}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                formatter={(val) => [val, 'Farmers']}
                labelFormatter={(l) => String(l).charAt(0).toUpperCase() + String(l).slice(1)}
              />
              <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                {(distribution as ScoreBand[]).map((entry) => (
                  <Cell
                    key={entry.credit_band}
                    fill={BAND_COLORS[entry.credit_band] ?? '#9CA3AF'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
