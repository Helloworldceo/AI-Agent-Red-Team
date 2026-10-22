import { useEffect, useState } from 'react'
import { getPayloads } from '../../api/meta'
import { useScanStore } from '../../state/useScanStore'
import type { Payload } from '../../types/api'

export function PayloadCategorySelector() {
  const targetType = useScanStore((s) => s.targetType)
  const selectedIds = useScanStore((s) => s.selectedPayloadIds)
  const setSelectedPayloadIds = useScanStore((s) => s.setSelectedPayloadIds)
  const disabled = useScanStore((s) => s.status === 'pending' || s.status === 'running')
  const [payloads, setPayloads] = useState<Payload[]>([])

  useEffect(() => {
    getPayloads(targetType).then((all) => {
      setPayloads(all)
      setSelectedPayloadIds(all.map((p) => p.id))
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetType])

  const byCategory = payloads.reduce<Record<string, Payload[]>>((acc, p) => {
    ;(acc[p.category] ??= []).push(p)
    return acc
  }, {})

  const selected = new Set(selectedIds ?? [])

  function toggleCategory(category: string, on: boolean) {
    const ids = byCategory[category].map((p) => p.id)
    const next = new Set(selected)
    for (const id of ids) {
      if (on) next.add(id)
      else next.delete(id)
    }
    setSelectedPayloadIds([...next])
  }

  return (
    <div>
      <label className="block text-xs font-medium text-neutral-400 mb-2">
        Attack categories ({selected.size}/{payloads.length} payloads selected)
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
        {Object.entries(byCategory).map(([category, items]) => {
          const allOn = items.every((p) => selected.has(p.id))
          return (
            <label
              key={category}
              className="flex items-center gap-2 text-xs rounded-md border border-neutral-800 px-2.5 py-1.5"
            >
              <input
                type="checkbox"
                checked={allOn}
                disabled={disabled}
                onChange={(e) => toggleCategory(category, e.target.checked)}
              />
              <span>{category}</span>
              <span className="text-neutral-500 ml-auto">{items.length}</span>
            </label>
          )
        })}
      </div>
    </div>
  )
}
