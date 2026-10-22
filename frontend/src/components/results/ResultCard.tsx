import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import type { ScanResultItem } from '../../types/api'
import { severityBadgeClass, severityLabel } from './severity'
import { ToolCallTrace } from '../trace/ToolCallTrace'
import { RetrievedDocsPanel } from '../trace/RetrievedDocsPanel'

export function ResultCard({ result }: { result: ScanResultItem }) {
  const [open, setOpen] = useState(result.severity === 'high' || result.severity === 'critical')

  const statusText = result.error ? 'ERROR' : result.success ? 'SUCCEEDED' : 'Resisted'
  const statusColor = result.error
    ? 'text-neutral-400'
    : result.success
      ? 'text-red-400'
      : 'text-emerald-400'

  return (
    <div className="rounded-lg border border-neutral-800 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-3 py-2.5 text-left hover:bg-neutral-900/60"
      >
        {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <span className="text-xs text-neutral-500">
          {result.is_control ? '[control] ' : ''}
          {result.category}
        </span>
        <span className="text-sm font-medium">{result.name}</span>
        <span className={`text-xs font-medium ml-auto ${statusColor}`}>{statusText}</span>
        <span className={`text-[10px] px-2 py-0.5 rounded-full border ${severityBadgeClass(result.severity)}`}>
          {severityLabel(result.severity)}
        </span>
      </button>

      {open && (
        <div className="px-3 pb-3 space-y-3 border-t border-neutral-800 pt-3">
          <p className="text-xs text-neutral-400">{result.description}</p>
          <p className="text-xs">
            <span className="text-neutral-500">Judgment: </span>
            {result.reason}
          </p>
          {result.duration_ms > 0 && (
            <p className="text-[11px] text-neutral-600">Response time: {result.duration_ms}ms</p>
          )}

          <ToolCallTrace result={result} />
          <RetrievedDocsPanel result={result} />
        </div>
      )}
    </div>
  )
}
