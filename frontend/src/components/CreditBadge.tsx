import type { CreditBand } from '@/types'
import clsx from 'clsx'

interface Props {
  band: CreditBand
  score?: number
}

const BAND_LABELS: Record<CreditBand, string> = {
  platinum: 'Platinum',
  gold:     'Gold',
  silver:   'Silver',
  bronze:   'Bronze',
  unscored: 'Unscored',
}

export default function CreditBadge({ band, score }: Props) {
  return (
    <span className={clsx('badge-' + band, 'inline-flex items-center gap-1')}>
      {score !== undefined && (
        <span className="font-mono">{score.toFixed(1)}</span>
      )}
      {BAND_LABELS[band]}
    </span>
  )
}
