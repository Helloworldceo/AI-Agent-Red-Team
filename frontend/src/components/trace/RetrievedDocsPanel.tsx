import { ShieldAlert } from 'lucide-react'
import type { ScanResultItem } from '../../types/api'

export function RetrievedDocsPanel({ result }: { result: ScanResultItem }) {
  if (!result.retrieved_documents || result.retrieved_documents.length === 0) return null

  return (
    <div className="space-y-1.5">
      <div className="text-[10px] uppercase tracking-wide text-neutral-500">
        Retrieved documents
      </div>
      {result.retrieved_documents.map((doc, i) => {
        const metadata = (doc.metadata ?? {}) as Record<string, unknown>
        const poisoned = metadata.injected === true
        const content = String(doc.page_content ?? '')
        return (
          <div
            key={i}
            className={`rounded-md px-3 py-2 text-xs font-mono ${
              poisoned
                ? 'border border-red-500/40 bg-red-500/[0.05]'
                : 'border border-neutral-800 bg-neutral-900/60'
            }`}
          >
            {poisoned && (
              <div className="flex items-center gap-1 text-red-300 mb-1 font-sans">
                <ShieldAlert size={11} /> Untrusted — injected for this test
              </div>
            )}
            {content}
          </div>
        )
      })}
    </div>
  )
}
