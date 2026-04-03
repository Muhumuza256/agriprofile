export const MONTHS = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

export function formatUGX(amount: number): string {
  return `UGX ${Math.round(amount).toLocaleString('en-UG')}`
}

export function formatAcres(acres: number): string {
  return `${Number(acres).toFixed(2)} ac`
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-UG', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

export function monthName(month: number): string {
  return MONTHS[month] ?? `Month ${month}`
}

export function creditBandColor(band: string): string {
  const map: Record<string, string> = {
    platinum: 'text-purple-700',
    gold:     'text-amber-600',
    silver:   'text-gray-500',
    bronze:   'text-orange-600',
    unscored: 'text-gray-400',
  }
  return map[band] ?? 'text-gray-400'
}

export function creditBandBadgeClass(band: string): string {
  return `badge-${band}`
}
