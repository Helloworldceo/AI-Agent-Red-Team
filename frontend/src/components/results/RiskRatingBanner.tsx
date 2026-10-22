import { useScanStore } from '../../state/useScanStore'

const RISK_STYLES: Record<string, string> = {
  very_resilient: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
  low: 'bg-yellow-300/10 border-yellow-300/30 text-yellow-200',
  medium: 'bg-amber-400/10 border-amber-400/30 text-amber-300',
  high: 'bg-orange-500/10 border-orange-500/30 text-orange-300',
  critical: 'bg-red-500/10 border-red-500/30 text-red-300',
}

export function RiskRatingBanner() {
  const summary = useScanStore((s) => s.summary)
  if (!summary) return null

  return (
    <div className={`rounded-lg border p-4 ${RISK_STYLES[summary.risk_level]}`}>
      <div className="text-lg font-semibold">{summary.risk_label}</div>
      <div className="text-sm opacity-80 mt-0.5">
        {summary.success_rate}% attack success rate
        {summary.by_severity.high || summary.by_severity.critical
          ? ' — escalated due to a sensitive tool being triggered, independent of raw success rate'
          : ''}
      </div>
    </div>
  )
}
