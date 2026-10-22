import { useState } from 'react'
import { useScanStore } from '../../state/useScanStore'
import { ResultCard } from './ResultCard'
import { ResultsFilterBar, type ShowFilter } from './ResultsFilterBar'
import type { Severity } from '../../types/api'

export function ResultList() {
  const results = useScanStore((s) => s.results)
  const [show, setShow] = useState<ShowFilter>('all')
  const [category, setCategory] = useState('all')
  const [severity, setSeverity] = useState<Severity | 'all'>('all')

  if (results.length === 0) return null

  const filtered = results.filter((r) => {
    if (show === 'succeeded' && !(r.success && !r.error)) return false
    if (show === 'resisted' && !(!r.success && !r.error)) return false
    if (show === 'errors' && !r.error) return false
    if (category !== 'all' && r.category !== category) return false
    if (severity !== 'all' && r.severity !== severity) return false
    return true
  })

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-neutral-300">
          Detailed results ({filtered.length})
        </h3>
        <ResultsFilterBar
          show={show}
          onShowChange={setShow}
          category={category}
          onCategoryChange={setCategory}
          severity={severity}
          onSeverityChange={setSeverity}
        />
      </div>
      <div className="space-y-2">
        {filtered.map((r) => (
          <ResultCard key={r.id} result={r} />
        ))}
      </div>
    </div>
  )
}
