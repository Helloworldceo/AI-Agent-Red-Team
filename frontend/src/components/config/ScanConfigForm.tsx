import { useEffect, useState } from 'react'
import { getProviders } from '../../api/meta'
import { useScanStore } from '../../state/useScanStore'
import type { ProviderInfo } from '../../types/api'

export function ScanConfigForm() {
  const apiKey = useScanStore((s) => s.apiKey)
  const provider = useScanStore((s) => s.provider)
  const model = useScanStore((s) => s.model)
  const systemPrompt = useScanStore((s) => s.systemPrompt)
  const goal = useScanStore((s) => s.goal)
  const evalMode = useScanStore((s) => s.evalMode)
  const setApiKey = useScanStore((s) => s.setApiKey)
  const setProvider = useScanStore((s) => s.setProvider)
  const setModel = useScanStore((s) => s.setModel)
  const setSystemPrompt = useScanStore((s) => s.setSystemPrompt)
  const setGoal = useScanStore((s) => s.setGoal)
  const setEvalMode = useScanStore((s) => s.setEvalMode)
  const disabled = useScanStore((s) => s.status === 'pending' || s.status === 'running')

  const [providers, setProviders] = useState<ProviderInfo[]>([])

  useEffect(() => {
    getProviders().then(setProviders).catch(() => setProviders([]))
  }, [])

  return (
    <div className="space-y-3">
      <div>
        <label className="block text-xs font-medium text-neutral-400 mb-1">Provider</label>
        <div className="flex gap-2">
          {providers.map((p) => (
            <button
              key={p.id}
              type="button"
              disabled={disabled}
              onClick={() => setProvider(p.id)}
              className={`text-xs px-3 py-1.5 rounded-md border disabled:opacity-50 ${
                provider === p.id
                  ? 'border-indigo-400 bg-indigo-500/10'
                  : 'border-neutral-700 hover:border-neutral-500'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-neutral-400 mb-1">
            {provider === 'gemini' ? 'Gemini API key' : 'DeepSeek API key'}
          </label>
          <input
            type="password"
            value={apiKey}
            disabled={disabled}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm"
            placeholder={provider === 'gemini' ? 'AIza...' : 'sk-...'}
          />
          <p className="mt-1 text-[11px] text-neutral-500">
            Sent straight to {provider === 'gemini' ? 'Google' : 'DeepSeek'} for this scan only — never stored on our server.
          </p>
        </div>

        <div>
          <label className="block text-xs font-medium text-neutral-400 mb-1">Model</label>
          <input
            value={model}
            disabled={disabled}
            onChange={(e) => setModel(e.target.value)}
            className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-neutral-400 mb-1">
          System prompt (what the target is told to do)
        </label>
        <textarea
          value={systemPrompt}
          disabled={disabled}
          onChange={(e) => setSystemPrompt(e.target.value)}
          rows={4}
          className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-neutral-400 mb-1">Attack goal</label>
        <input
          value={goal}
          disabled={disabled}
          onChange={(e) => setGoal(e.target.value)}
          className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-neutral-400 mb-1">Evaluation mode</label>
        <div className="flex gap-2">
          {(['llm_judge', 'keyword'] as const).map((m) => (
            <button
              key={m}
              type="button"
              disabled={disabled}
              onClick={() => setEvalMode(m)}
              className={`text-xs px-3 py-1.5 rounded-md border disabled:opacity-50 ${
                evalMode === m
                  ? 'border-indigo-400 bg-indigo-500/10'
                  : 'border-neutral-700 hover:border-neutral-500'
              }`}
            >
              {m === 'llm_judge' ? 'LLM Judge (accurate)' : 'Keyword (fast, offline)'}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
