import { ShieldAlert } from 'lucide-react'
import type { ToolCallRecord, TurnRecord } from '../../types/api'

function ToolCallNode({ call }: { call: ToolCallRecord }) {
  const sensitive = call.sensitivity === 'sensitive'
  return (
    <div
      className={`ml-4 border-l-2 pl-3 py-2 ${
        sensitive ? 'border-red-500' : 'border-emerald-500'
      }`}
    >
      <div className="flex items-center gap-2 text-xs">
        <span className="font-mono">{call.tool_name}({JSON.stringify(call.tool_args)})</span>
        {sensitive && (
          <span className="inline-flex items-center gap-1 text-red-300 bg-red-500/15 border border-red-500/30 rounded-full px-2 py-0.5">
            <ShieldAlert size={11} /> Excessive Agency
          </span>
        )}
      </div>
      <div className="mt-1 font-mono text-xs text-neutral-400 bg-neutral-900/60 rounded px-2 py-1">
        {call.tool_result}
      </div>
    </div>
  )
}

export function TraceStep({ turn }: { turn: TurnRecord }) {
  return (
    <div className="space-y-1.5">
      <div
        className={`rounded-md px-3 py-2 text-xs ${
          turn.role === 'user'
            ? 'bg-neutral-800/80'
            : 'bg-indigo-500/10 border border-indigo-500/20'
        }`}
      >
        <div className="text-[10px] uppercase tracking-wide text-neutral-500 mb-1">
          {turn.role === 'user' ? 'Payload / user' : 'Agent response'}
        </div>
        {turn.content}
      </div>
      {turn.tool_calls.map((tc, i) => (
        <ToolCallNode key={i} call={tc} />
      ))}
    </div>
  )
}
