import { useScanStore } from '../../state/useScanStore'
import { severityDot } from '../results/severity'

export function LiveResultFeed() {
  const results = useScanStore((s) => s.results)
  const status = useScanStore((s) => s.status)

  if (status !== 'pending' && status !== 'running') return null
  if (results.length === 0) return null

  return (
    <div className="max-h-48 overflow-y-auto rounded-md border border-neutral-800 divide-y divide-neutral-800">
      {[...results].reverse().map((r) => (
        <div key={r.id} className="flex items-center gap-2 px-3 py-1.5 text-xs">
          <span className={`h-2 w-2 rounded-full shrink-0 ${severityDot(r.severity)}`} />
          <span className="text-neutral-500">{r.category}</span>
          <span>{r.name}</span>
          <span className="ml-auto text-neutral-500">
            {r.error ? 'error' : r.success ? 'succeeded' : 'resisted'}
          </span>
        </div>
      ))}
    </div>
  )
}
