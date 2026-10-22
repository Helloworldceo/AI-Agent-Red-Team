import { useScanStore } from '../../state/useScanStore'

export function CategoryBreakdown() {
  const summary = useScanStore((s) => s.summary)
  if (!summary || Object.keys(summary.by_category).length === 0) return null

  return (
    <div>
      <h3 className="text-sm font-medium text-neutral-300 mb-2">By category</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {Object.entries(summary.by_category).map(([cat, counts]) => {
          const rate = Math.round((counts.succeeded / counts.total) * 100)
          return (
            <div key={cat} className="rounded-md border border-neutral-800 p-2.5">
              <div className="text-xs text-neutral-400">{cat}</div>
              <div className="text-sm font-medium">
                {counts.succeeded}/{counts.total}{' '}
                <span className="text-neutral-500 font-normal">({rate}%)</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
