import type { RiskFlag } from '@/types'
import clsx from 'clsx'

export default function RiskFlags({ flags }: { flags: RiskFlag[] }) {
  if (!flags.length) return null

  return (
    <div className="space-y-1 mt-2">
      {flags.map((flag, i) => (
        <div
          key={i}
          className={clsx(
            'flex items-start gap-2 text-xs px-2 py-1 rounded',
            flag.level === 'red'
              ? 'bg-red-50 text-red-700 border border-red-200'
              : 'bg-amber-50 text-amber-700 border border-amber-200',
          )}
        >
          <span className="mt-0.5 shrink-0">{flag.level === 'red' ? '●' : '◆'}</span>
          {flag.message}
        </div>
      ))}
    </div>
  )
}
