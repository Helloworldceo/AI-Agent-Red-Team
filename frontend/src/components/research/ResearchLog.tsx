import { useEffect, useState } from 'react'
import { getFinding, getFindings } from '../../api/research'
import type { FindingDetail, FindingSummary } from '../../types/api'
import { severityBadgeClass, severityLabel } from '../results/severity'

function ResultBadge({ succeeded }: { succeeded: boolean }) {
  return (
    <span
      className={`text-xs px-2.5 py-1 rounded-full border shrink-0 ${
        succeeded
          ? 'bg-amber-400/15 text-amber-300 border-amber-400/30'
          : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
      }`}
    >
      {succeeded ? '⚠️ Succeeded' : '✅ Resisted'}
    </span>
  )
}

export function ResearchLog() {
  const [findings, setFindings] = useState<FindingSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [detail, setDetail] = useState<FindingDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  useEffect(() => {
    getFindings()
      .then((data) => {
        setFindings(data)
        if (data.length > 0) setSelectedDate(data[0].date)
      })
      .catch(() => setError('Could not load the research log.'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedDate) {
      setDetail(null)
      return
    }
    setDetailLoading(true)
    getFinding(selectedDate)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setDetailLoading(false))
  }, [selectedDate])

  if (loading) return <p className="text-sm text-neutral-500">Loading research log…</p>
  if (error) return <p className="text-sm text-red-400">{error}</p>
  if (findings.length === 0) {
    return (
      <p className="text-sm text-neutral-500">
        No findings yet — a new one gets brainstormed and tested every day. Check back tomorrow.
      </p>
    )
  }

  return (
    <div className="space-y-3">
      <p className="text-xs text-neutral-500">
        One new adversarial technique, brainstormed and tested for real against this tool's own
        targets, every day — pass or fail, published as-is.
      </p>

      <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <ul className="space-y-2">
          {findings.map((f) => (
            <li key={f.date}>
              <button
                type="button"
                onClick={() => setSelectedDate(f.date)}
                className={`w-full text-left rounded-md border px-3 py-2 transition-colors ${
                  selectedDate === f.date
                    ? 'border-indigo-400 bg-indigo-500/10'
                    : 'border-neutral-700 hover:border-neutral-500'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs text-neutral-500">{f.date}</span>
                  <ResultBadge succeeded={f.succeeded} />
                </div>
                <div className="text-sm font-medium mt-1">{f.technique}</div>
                <div className="text-xs text-neutral-500">{f.category}</div>
              </button>
            </li>
          ))}
        </ul>

        <div className="rounded-md border border-neutral-800 p-4 space-y-3 self-start">
          {detailLoading && <p className="text-sm text-neutral-500">Loading…</p>}
          {!detailLoading && detail && (
            <>
              <div className="flex items-center justify-between gap-2">
                <h3 className="text-sm font-semibold">{detail.technique}</h3>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full border shrink-0 ${severityBadgeClass(detail.severity)}`}
                >
                  {severityLabel(detail.severity)}
                </span>
              </div>
              <p className="text-xs text-neutral-500">
                {detail.category} · {detail.date}
              </p>
              <p className="text-sm text-neutral-300">{detail.hypothesis}</p>
              <div>
                <p className="text-xs font-medium text-neutral-400 mb-1">Generated payload</p>
                <pre className="text-xs bg-neutral-900 border border-neutral-700 rounded-md p-3 overflow-x-auto whitespace-pre-wrap">
                  {detail.template}
                </pre>
              </div>
              <ResultBadge succeeded={detail.succeeded} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
