interface Props {
  label: string
  value: string | number
  sub?: string
  accent?: boolean
}

export default function StatCard({ label, value, sub, accent }: Props) {
  return (
    <div className="card p-5">
      <p className="text-xs text-neutral-500 uppercase tracking-widest font-medium">{label}</p>
      <p className={`text-3xl font-bold mt-1 font-display ${accent ? 'text-primary-700' : 'text-neutral-900'}`}>
        {value}
      </p>
      {sub && <p className="text-xs text-neutral-400 mt-1">{sub}</p>}
    </div>
  )
}
