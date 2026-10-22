import { useEffect, useState } from 'react'
import { getTargets } from '../../api/meta'
import { useScanStore } from '../../state/useScanStore'
import type { TargetInfo } from '../../types/api'

export function TargetTypeSelector() {
  const [targets, setTargets] = useState<TargetInfo[]>([])
  const targetType = useScanStore((s) => s.targetType)
  const setTargetType = useScanStore((s) => s.setTargetType)
  const disabled = useScanStore((s) => s.status === 'pending' || s.status === 'running')

  useEffect(() => {
    getTargets().then(setTargets).catch(() => setTargets([]))
  }, [])

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
      {targets.map((t) => (
        <button
          key={t.type}
          type="button"
          disabled={disabled}
          onClick={() => setTargetType(t.type)}
          className={`text-left rounded-lg border p-3 transition-colors disabled:opacity-50 ${
            targetType === t.type
              ? 'border-indigo-400 bg-indigo-500/10'
              : 'border-neutral-700 hover:border-neutral-500'
          }`}
        >
          <div className="font-medium text-sm">{t.label}</div>
          <div className="text-xs text-neutral-400 mt-1">{t.blurb}</div>
        </button>
      ))}
    </div>
  )
}
