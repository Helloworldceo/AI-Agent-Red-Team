import { useScanStore } from '../../state/useScanStore'

export function SummaryCards() {
  const summary = useScanStore((s) => s.summary)
  if (!summary) return null

  const cards = [
    { label: 'Total payloads', value: summary.total },
    { label: 'Attacks succeeded', value: summary.succeeded, tone: 'text-red-400' },
    { label: 'Target resisted', value: summary.failed, tone: 'text-emerald-400' },
    { label: 'Errors', value: summary.errors, tone: 'text-neutral-400' },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {cards.map((c) => (
        <div key={c.label} className="rounded-lg border border-neutral-800 p-3">
          <div className={`text-2xl font-semibold ${c.tone ?? ''}`}>{c.value}</div>
          <div className="text-xs text-neutral-500 mt-0.5">{c.label}</div>
        </div>
      ))}
      {summary.control_total > 0 && (
        <div className="rounded-lg border border-neutral-800 p-3 col-span-2 sm:col-span-4">
          <div className="text-sm">
            <span className="font-semibold">
              {summary.control_passed}/{summary.control_total}
            </span>{' '}
            control payloads passed — sanity check that the target agent actually uses its tools
            for legitimate requests (excluded from the vulnerability score above).
          </div>
        </div>
      )}
    </div>
  )
}
