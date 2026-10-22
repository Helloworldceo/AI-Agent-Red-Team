import { useScanStore } from '../../state/useScanStore'

export function ScanProgressBar() {
  const progress = useScanStore((s) => s.progress)
  const status = useScanStore((s) => s.status)

  if (status !== 'pending' && status !== 'running') return null

  const pct = progress.total > 0 ? Math.round((progress.completed / progress.total) * 100) : 0

  return (
    <div className="space-y-1.5">
      <div className="h-2 rounded-full bg-neutral-800 overflow-hidden">
        <div
          className="h-full bg-indigo-500 transition-all duration-200"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="text-xs text-neutral-400">
        {status === 'pending'
          ? 'Starting scan…'
          : `Testing payload ${progress.completed}/${progress.total}${
              progress.currentPayloadName ? `: ${progress.currentPayloadName}` : ''
            }`}
      </div>
    </div>
  )
}
