import { useState } from 'react'
import { TargetTypeSelector } from '../components/config/TargetTypeSelector'
import { ScanConfigForm } from '../components/config/ScanConfigForm'
import { PayloadCategorySelector } from '../components/config/PayloadCategorySelector'
import { RunScanButton } from '../components/config/RunScanButton'
import { ScanProgressBar } from '../components/progress/ScanProgressBar'
import { LiveResultFeed } from '../components/progress/LiveResultFeed'
import { SummaryCards } from '../components/results/SummaryCards'
import { RiskRatingBanner } from '../components/results/RiskRatingBanner'
import { CategoryBreakdown } from '../components/results/CategoryBreakdown'
import { SeverityBreakdown } from '../components/results/SeverityBreakdown'
import { ResultList } from '../components/results/ResultList'
import { ExportButtons } from '../components/export/ExportButtons'
import { ResearchLog } from '../components/research/ResearchLog'
import { useScanStore } from '../state/useScanStore'

type Tab = 'scanner' | 'research'

export function ScanPage() {
  const status = useScanStore((s) => s.status)
  const error = useScanStore((s) => s.error)
  const summary = useScanStore((s) => s.summary)
  const hasResults = status === 'completed' || status === 'cancelled'
  const [tab, setTab] = useState<Tab>('scanner')

  return (
    <div className="min-h-screen px-4 py-8 sm:py-12">
      <div className="max-w-3xl mx-auto space-y-8">
        <header>
          <h1 className="text-xl font-semibold">AI Agent Red-Team</h1>
          <p className="text-sm text-neutral-500 mt-1">
            Adversarial testing for raw chat completions, tool-calling agents, and
            RAG-backed assistants — not just a system prompt.
          </p>
        </header>

        <div className="flex gap-2 border-b border-neutral-800">
          {([
            ['scanner', 'Scanner'],
            ['research', 'Research log'],
          ] as const).map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => setTab(value)}
              className={`text-sm px-3 py-2 -mb-px border-b-2 transition-colors ${
                tab === value
                  ? 'border-indigo-400 text-neutral-100'
                  : 'border-transparent text-neutral-500 hover:text-neutral-300'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {tab === 'research' && <ResearchLog />}

        {tab === 'scanner' && (
          <>
            <section className="space-y-4">
              <TargetTypeSelector />
              <ScanConfigForm />
              <PayloadCategorySelector />
              <RunScanButton />
              {error && <p className="text-xs text-red-400">{error}</p>}
            </section>

            <section className="space-y-3">
              <ScanProgressBar />
              <LiveResultFeed />
            </section>

            {hasResults && summary && (
              <section className="space-y-6 border-t border-neutral-800 pt-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-semibold">Scan results</h2>
                  <ExportButtons />
                </div>
                <RiskRatingBanner />
                <SummaryCards />
                <SeverityBreakdown />
                <CategoryBreakdown />
                <ResultList />
              </section>
            )}
          </>
        )}

        <footer className="border-t border-neutral-800 pt-6 text-center space-y-1">
          <p className="text-sm text-neutral-300">
            Want this run against <span className="font-medium">your</span> agent, with a full written report?
          </p>
          <p className="text-xs text-neutral-500">
            <a
              href="mailto:davidabdisa40@gmail.com?subject=Red-team%20audit%20request"
              className="text-indigo-400 hover:text-indigo-300 underline"
            >
              davidabdisa40@gmail.com
            </a>{' '}
            — paid audits, one agent at a time.
          </p>
        </footer>
      </div>
    </div>
  )
}
