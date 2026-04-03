import { useQuery } from '@tanstack/react-query'
import { parametersApi } from '@/api/endpoints'

export default function ParametersPage() {
  const { data: crops, isLoading } = useQuery({
    queryKey: ['parameters', 'crops'],
    queryFn: () => parametersApi.crops().then((r) => r.data),
  })

  const { data: cii } = useQuery({
    queryKey: ['parameters', 'cii'],
    queryFn: () => parametersApi.cii().then((r) => r.data),
  })

  return (
    <div className="space-y-8 max-w-5xl">
      <h1 className="text-xl font-bold font-display">Parameter Panel</h1>
      <p className="text-sm text-neutral-500">
        Crop prices, costs, and CII multipliers. Changes trigger automatic score recalculation.
      </p>

      {/* Crop Parameters */}
      <div className="card overflow-hidden">
        <div className="px-5 py-3 border-b border-neutral-200 bg-neutral-50">
          <h2 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide">Crop Economics</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 border-b border-neutral-100">
            <tr>
              {['Crop', 'Farm Gate (UGX/kg)', 'Seed Cost/ac', 'Land Prep/ac', 'Labour/ac', 'PHL %', 'Volatility'].map((h) => (
                <th key={h} className="px-4 py-2 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wide">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-50">
            {isLoading && (
              <tr><td colSpan={7} className="px-4 py-6 text-center text-neutral-400">Loading…</td></tr>
            )}
            {(crops as unknown[] ?? []).map((p: unknown) => {
              const row = p as Record<string, unknown>
              return (
                <tr key={String(row.id)} className="hover:bg-neutral-50">
                  <td className="px-4 py-2 font-medium">{String(row.crop_name)}</td>
                  <td className="px-4 py-2 font-mono text-xs">{Number(row.farm_gate_price_ugx_per_kg).toLocaleString()}</td>
                  <td className="px-4 py-2 font-mono text-xs">{Number(row.seed_cost_ugx_per_acre).toLocaleString()}</td>
                  <td className="px-4 py-2 font-mono text-xs">{Number(row.land_prep_cost_ugx_per_acre).toLocaleString()}</td>
                  <td className="px-4 py-2 font-mono text-xs">{Number(row.labour_cost_ugx_per_acre).toLocaleString()}</td>
                  <td className="px-4 py-2 font-mono text-xs">{String(row.post_harvest_loss_pct_default)}%</td>
                  <td className="px-4 py-2 capitalize text-neutral-500 text-xs">{String(row.price_volatility)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* CII Table */}
      <div className="card overflow-hidden">
        <div className="px-5 py-3 border-b border-neutral-200 bg-neutral-50">
          <h2 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide">Crop Income Index (CII)</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 border-b border-neutral-100">
            <tr>
              {['Crop', 'Multiplier', 'Tier'].map((h) => (
                <th key={h} className="px-4 py-2 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-50">
            {(cii as unknown[] ?? []).map((c: unknown) => {
              const row = c as Record<string, unknown>
              return (
                <tr key={String(row.id)} className="hover:bg-neutral-50">
                  <td className="px-4 py-2 font-medium">{String(row.crop_name)}</td>
                  <td className="px-4 py-2 font-mono font-bold text-primary-700">×{Number(row.multiplier).toFixed(3)}</td>
                  <td className="px-4 py-2 text-neutral-500 text-xs">{String(row.tier).replace('_', ' ')}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
