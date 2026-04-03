import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { farmersApi } from '@/api/endpoints'
import CreditBadge from '@/components/CreditBadge'
import RiskFlags from '@/components/RiskFlags'
import { formatUGX, monthName } from '@/utils/format'
import type { CreditBand } from '@/types'

export default function FarmerDetailPage() {
  const { id } = useParams<{ id: string }>()
  const qc = useQueryClient()

  const { data: farmer } = useQuery({
    queryKey: ['farmer', id],
    queryFn: () => farmersApi.detail(id!).then((r) => r.data),
    enabled: !!id,
  })

  const { data: score } = useQuery({
    queryKey: ['farmer-score', id],
    queryFn: () => farmersApi.latestScore(id!).then((r) => r.data),
    enabled: !!id,
  })

  const { data: loan } = useQuery({
    queryKey: ['farmer-loan', id],
    queryFn: () => farmersApi.latestLoanCeiling(id!).then((r) => r.data),
    enabled: !!id,
  })

  const calculateScore = useMutation({
    mutationFn: () => farmersApi.calculateScore(id!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['farmer-score', id] }),
  })

  const calculateLoan = useMutation({
    mutationFn: () => farmersApi.calculateLoanCeiling(id!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['farmer-loan', id] }),
  })

  if (!farmer) return <div className="text-neutral-400 text-sm">Loading…</div>

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold font-display">{farmer.full_name}</h1>
          <p className="text-sm text-neutral-500 font-mono mt-0.5">{farmer.national_id} · {farmer.district}</p>
        </div>
        <div className="flex gap-2">
          {score && (
            <CreditBadge
              band={score.credit_band as CreditBand}
              score={Number(score.acs_with_saf)}
            />
          )}
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Score card */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide">ACS Breakdown</h2>
            <button
              onClick={() => calculateScore.mutate()}
              disabled={calculateScore.isPending}
              className="text-xs text-primary-700 hover:underline disabled:opacity-50"
            >
              Recalculate
            </button>
          </div>
          {score ? (
            <div className="space-y-2">
              {(
                [
                  ['Identity (IVS)', score.ivs_score],
                  ['Land & Assets (LAS)', score.las_score],
                  ['Crop & Production (CPS)', score.cps_score],
                  ['Group & Social (GSS)', score.gss_score],
                  ['Financial Behaviour (FBS)', score.fbs_score],
                  ['Household Stability (HSS)', score.hss_score],
                ] as [string, number][]
              ).map(([label, val]) => (
                <div key={label} className="flex items-center gap-3">
                  <span className="text-xs text-neutral-500 w-44 shrink-0">{label}</span>
                  <div className="flex-1 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 rounded-full"
                      style={{ width: `${val}%` }}
                    />
                  </div>
                  <span className="text-xs font-mono w-8 text-right">{Number(val).toFixed(0)}</span>
                </div>
              ))}
              <RiskFlags flags={score.risk_flags} />
            </div>
          ) : (
            <p className="text-sm text-neutral-400">No score yet.</p>
          )}
        </div>

        {/* Loan ceiling */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide">Loan Ceiling</h2>
            <button
              onClick={() => calculateLoan.mutate()}
              disabled={calculateLoan.isPending}
              className="text-xs text-primary-700 hover:underline disabled:opacity-50"
            >
              Calculate
            </button>
          </div>
          {loan ? (
            <div className="space-y-2">
              <p className="text-2xl font-bold text-primary-700 font-mono">
                {loan.loan_ceiling_ugx_formatted}
              </p>
              <div className="text-xs text-neutral-500 space-y-1 mt-2">
                <div className="flex justify-between">
                  <span>Agricultural Surplus</span>
                  <span className="font-mono">{formatUGX(loan.agricultural_surplus_ugx)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Disbursement window</span>
                  <span className="font-mono">{monthName(loan.disbursement_month)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Repayment starts</span>
                  <span className="font-mono">{monthName(loan.repayment_start_month)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Loan term</span>
                  <span className="font-mono">{loan.recommended_loan_term_months} months</span>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-sm text-neutral-400">No calculation yet.</p>
          )}
        </div>

        {/* Profile info */}
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide mb-3">Profile</h2>
          <dl className="space-y-1.5 text-sm">
            {[
              ['Phone', farmer.primary_phone],
              ['Gender', farmer.gender],
              ['Household size', farmer.household_size],
              ['Dependant ratio', `${(farmer.dependant_ratio * 100).toFixed(0)}%`],
              ['Submission status', farmer.submission_status],
              ['Profile completeness', `${farmer.profile_completeness}%`],
            ].map(([k, v]) => (
              <div key={String(k)} className="flex justify-between">
                <dt className="text-neutral-500">{k}</dt>
                <dd className="font-medium capitalize">{String(v)}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  )
}
