import { useScanStore } from '../../state/useScanStore'
import { SEVERITY_ORDER, severityBadgeClass, severityLabel } from './severity'

export function SeverityBreakdown() {
  const summary = useScanStore((s) => s.summary)
  if (!summary) return null

  return (
    <div>
      <h3 className="text-sm font-medium text-neutral-300 mb-2">By severity</h3>
      <div className="flex flex-wrap gap-2">
        {SEVERITY_ORDER.map((sev) => {
          const count = summary.by_severity[sev] ?? 0
          if (count === 0) return null
          return (
            <span
              key={sev}
              className={`text-xs px-2.5 py-1 rounded-full border ${severityBadgeClass(sev)}`}
            >
              {severityLabel(sev)}: {count}
            </span>
          )
        })}
      </div>
    </div>
  )
}
