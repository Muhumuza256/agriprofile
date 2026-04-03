import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/api/endpoints'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts'

export default function AnalyticsPage() {
  const { data: crops } = useQuery({
    queryKey: ['analytics', 'crops'],
    queryFn: () => analyticsApi.cropIntelligence().then((r) => r.data),
  })

  return (
    <div className="space-y-8">
      <h1 className="text-xl font-bold font-display">Analytics</h1>

      {/* Crop Intelligence */}
      <div className="card p-6">
        <h2 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide mb-4">
          Crop Intelligence — Top 10 by Acreage
        </h2>
        {crops ? (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={(crops as unknown[]).slice(0, 10)} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="crop_name"
                width={100}
                tick={{ fontSize: 11 }}
              />
              <Tooltip
                formatter={(val, name) => [
                  name === 'total_acreage' ? `${Number(val).toFixed(1)} ac` : val,
                  name === 'total_acreage' ? 'Total Acres' : 'Farmers',
                ]}
              />
              <Bar dataKey="total_acreage" fill="#2D6A4F" radius={[0, 3, 3, 0]} name="total_acreage" />
              <Bar dataKey="farmer_count" fill="#B7E4C7" radius={[0, 3, 3, 0]} name="farmer_count" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-neutral-400 text-sm">Loading crop data…</p>
        )}
      </div>
    </div>
  )
}
