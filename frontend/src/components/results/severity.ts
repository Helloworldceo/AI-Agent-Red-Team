import type { Severity } from '../../types/api'

export const SEVERITY_ORDER: Severity[] = ['info', 'low', 'medium', 'high', 'critical']

export function severityDot(sev: Severity): string {
  switch (sev) {
    case 'critical':
      return 'bg-red-500'
    case 'high':
      return 'bg-orange-500'
    case 'medium':
      return 'bg-amber-400'
    case 'low':
      return 'bg-yellow-300'
    default:
      return 'bg-emerald-500'
  }
}

export function severityBadgeClass(sev: Severity): string {
  switch (sev) {
    case 'critical':
      return 'bg-red-500/15 text-red-300 border-red-500/30'
    case 'high':
      return 'bg-orange-500/15 text-orange-300 border-orange-500/30'
    case 'medium':
      return 'bg-amber-400/15 text-amber-300 border-amber-400/30'
    case 'low':
      return 'bg-yellow-300/15 text-yellow-200 border-yellow-300/30'
    default:
      return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
  }
}

export function severityLabel(sev: Severity): string {
  return sev.charAt(0).toUpperCase() + sev.slice(1)
}
