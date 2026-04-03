import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { farmersApi } from '@/api/endpoints'
import { formatDate } from '@/utils/format'
import type { FarmerProfile } from '@/types'

const STATUS_COLORS = {
  approved: 'text-green-700 bg-green-50',
  pending:  'text-amber-700 bg-amber-50',
  rejected: 'text-red-700 bg-red-50',
}

export default function FarmersPage() {
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['farmers', search, status],
    queryFn: () => farmersApi.list({
      ...(search && { search }),
      ...(status && { submission_status: status }),
    }).then((r) => r.data),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold font-display">Farmer Profiles</h1>
      </div>

      <div className="flex gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name, NIN, or phone…"
          className="border border-neutral-300 rounded px-3 py-1.5 text-sm w-72 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="border border-neutral-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 border-b border-neutral-200">
            <tr>
              {['Name', 'NIN', 'Gender', 'District', 'Group', 'Completeness', 'Status', 'Submitted'].map((h) => (
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
            {data?.results.map((farmer: FarmerProfile) => (
              <tr key={farmer.id} className="hover:bg-neutral-50 transition-colors">
                <td className="px-4 py-3">
                  <Link to={`/farmers/${farmer.id}`} className="font-medium text-primary-700 hover:underline">
                    {farmer.full_name}
                  </Link>
                </td>
                <td className="px-4 py-3 font-mono text-xs text-neutral-500">{farmer.national_id}</td>
                <td className="px-4 py-3 capitalize text-neutral-500">{farmer.gender}</td>
                <td className="px-4 py-3">{farmer.district}</td>
                <td className="px-4 py-3 text-neutral-500 text-xs">{farmer.group_name}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500 rounded-full"
                        style={{ width: `${farmer.profile_completeness}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-neutral-500">{farmer.profile_completeness}%</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded capitalize ${STATUS_COLORS[farmer.submission_status]}`}>
                    {farmer.submission_status}
                  </span>
                </td>
                <td className="px-4 py-3 text-neutral-400 text-xs">{formatDate(farmer.created_at)}</td>
              </tr>
            ))}
            {!isLoading && !data?.results.length && (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-neutral-400">No farmers found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
      {data && <p className="text-xs text-neutral-400">{data.count} total farmers</p>}
    </div>
  )
}
