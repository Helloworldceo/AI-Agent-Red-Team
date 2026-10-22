import { Play, Square } from 'lucide-react'
import { useScanStore } from '../../state/useScanStore'

export function RunScanButton() {
  const status = useScanStore((s) => s.status)
  const apiKey = useScanStore((s) => s.apiKey)
  const systemPrompt = useScanStore((s) => s.systemPrompt)
  const goal = useScanStore((s) => s.goal)
  const selectedPayloadIds = useScanStore((s) => s.selectedPayloadIds)
  const runScan = useScanStore((s) => s.runScan)
  const cancel = useScanStore((s) => s.cancel)
  const reset = useScanStore((s) => s.reset)

  const running = status === 'pending' || status === 'running'
  const canRun = !!apiKey && !!systemPrompt && !!goal && !!selectedPayloadIds?.length

  if (running) {
    return (
      <button
        onClick={cancel}
        className="w-full flex items-center justify-center gap-2 rounded-md bg-red-600/90 hover:bg-red-600 px-4 py-2.5 text-sm font-medium"
      >
        <Square size={14} /> Cancel scan
      </button>
    )
  }

  if (status === 'completed' || status === 'cancelled' || status === 'error') {
    return (
      <button
        onClick={reset}
        className="w-full flex items-center justify-center gap-2 rounded-md bg-neutral-700 hover:bg-neutral-600 px-4 py-2.5 text-sm font-medium"
      >
        Run another scan
      </button>
    )
  }

  return (
    <button
      onClick={runScan}
      disabled={!canRun}
      className="w-full flex items-center justify-center gap-2 rounded-md bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2.5 text-sm font-medium"
    >
      <Play size={14} /> Run scan
    </button>
  )
}
