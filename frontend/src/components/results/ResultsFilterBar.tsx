import { useState } from 'react'
import { useScanStore } from '../../state/useScanStore'
import type { Severity } from '../../types/api'

export type ShowFilter = 'all' | 'succeeded' | 'resisted' | 'errors'

interface Props {
  show: ShowFilter
  onShowChange: (v: ShowFilter) => void
  category: string
  onCategoryChange: (v: string) => void
  severity: Severity | 'all'
  onSeverityChange: (v: Severity | 'all') => void
}

export function ResultsFilterBar({
  show,
  onShowChange,
  category,
  onCategoryChange,
  severity,
  onSeverityChange,
}: Props) {
  const results = useScanStore((s) => s.results)
  const [categories] = useState(() => [...new Set(results.map((r) => r.category))].sort())

  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <select
        value={show}
        onChange={(e) => onShowChange(e.target.value as ShowFilter)}
        className="rounded-md bg-neutral-900 border border-neutral-700 px-2 py-1.5"
      >
        <option value="all">All results</option>
        <option value="succeeded">Succeeded only</option>
        <option value="resisted">Resisted only</option>
        <option value="errors">Errors only</option>
      </select>

      <select
        value={category}
        onChange={(e) => onCategoryChange(e.target.value)}
        className="rounded-md bg-neutral-900 border border-neutral-700 px-2 py-1.5"
      >
        <option value="all">All categories</option>
        {categories.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      <select
        value={severity}
        onChange={(e) => onSeverityChange(e.target.value as Severity | 'all')}
        className="rounded-md bg-neutral-900 border border-neutral-700 px-2 py-1.5"
      >
        <option value="all">All severities</option>
        {(['critical', 'high', 'medium', 'low', 'info'] as const).map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
    </div>
  )
}
