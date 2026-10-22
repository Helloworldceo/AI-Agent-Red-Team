import type { ScanResultItem } from '../../types/api'
import { TraceStep } from './TraceStep'

/**
 * The portfolio differentiator: a step-by-step timeline of a single scan
 * result — payload message, each tool call the agent made (colored by
 * sensitivity), and the agent's responses — so an excessive-agency incident
 * is visually unmissable rather than a log line.
 */
export function ToolCallTrace({ result }: { result: ScanResultItem }) {
  const isIncident = result.severity === 'high' || result.severity === 'critical'

  if (result.turns.length === 0) return null

  return (
    <div
      className={`rounded-lg p-3 space-y-3 ${
        isIncident ? 'border-2 border-red-500/50 bg-red-500/[0.03]' : 'border border-neutral-800'
      }`}
    >
      {result.turns.map((turn, i) => (
        <TraceStep key={i} turn={turn} />
      ))}
    </div>
  )
}
