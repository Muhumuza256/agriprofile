import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { groupsApi } from '@/api/endpoints'
import CreditBadge from '@/components/CreditBadge'
import { formatAcres, formatDate } from '@/utils/format'
import type { FarmerGroup, CreditBand } from '@/types'

export default function GroupsPage() {
  const [search, setSearch] = useState('')
  const [district, setDistrict] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['groups', search, district],
    queryFn: () => groupsApi.list({
      ...(search && { search }),
      ...(district && { district }),
    }).then((r) => r.data),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold font-display">Farmer Groups</h1>
        <Link to="/groups/new" className="btn-primary text-sm">+ Register Group</Link>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or district…"
          className="border border-neutral-300 rounded px-3 py-1.5 text-sm w-72 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <input
          value={district}
          onChange={(e) => setDistrict(e.target.value)}
          placeholder="Filter by district"
          className="border border-neutral-300 rounded px-3 py-1.5 text-sm w-48 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 border-b border-neutral-200">
            <tr>
              {['Group Name', 'Type', 'District', 'Members', 'Land', 'GACS', 'Status', 'Registered'].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wide">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading && (
              <tr><td colSpan={8} className="px-4 py-6 text-center text-neutral-400">Loading…</td></tr>
            )}
            {data?.results.map((group: FarmerGroup) => (
              <tr key={group.id} className="hover:bg-neutral-50 transition-colors">
                <td className="px-4 py-3">
                  <Link
                    to={`/groups/${group.id}`}
                    className="font-medium text-primary-700 hover:underline"
                  >
                    {group.name}
                  </Link>
                </td>
                <td className="px-4 py-3 text-neutral-500 capitalize">{group.group_type.replace('_', ' ')}</td>
                <td className="px-4 py-3">{group.district}</td>
                <td className="px-4 py-3 font-mono">{group.member_count}</td>
                <td className="px-4 py-3 font-mono">{formatAcres(group.total_land_acres)}</td>
                <td className="px-4 py-3">
                  {group.gacs != null ? (
                    <CreditBadge band={'gold' as CreditBand} score={group.gacs} />
                  ) : (
                    <span className="text-neutral-300 text-xs">—</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  {group.is_approved ? (
                    <span className="text-xs text-green-700 bg-green-50 px-2 py-0.5 rounded">Approved</span>
                  ) : (
                    <span className="text-xs text-amber-700 bg-amber-50 px-2 py-0.5 rounded">Pending</span>
                  )}
                </td>
                <td className="px-4 py-3 text-neutral-400 text-xs">{formatDate(group.created_at)}</td>
              </tr>
            ))}
            {!isLoading && !data?.results.length && (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-neutral-400">No groups found.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {data && (
        <p className="text-xs text-neutral-400">{data.count} total groups</p>
      )}
    </div>
  )
}
