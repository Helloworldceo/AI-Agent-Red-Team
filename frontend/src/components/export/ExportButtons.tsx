import { Download } from 'lucide-react'
import { exportScanUrl } from '../../api/scans'
import { useScanStore } from '../../state/useScanStore'

export function ExportButtons() {
  const scanId = useScanStore((s) => s.scanId)
  const status = useScanStore((s) => s.status)

  if (!scanId || (status !== 'completed' && status !== 'cancelled')) return null

  return (
    <div className="flex gap-2">
      <a
        href={exportScanUrl(scanId, 'json')}
        download
        className="flex items-center gap-1.5 text-xs rounded-md border border-neutral-700 hover:border-neutral-500 px-3 py-1.5"
      >
        <Download size={12} /> JSON report
      </a>
      <a
        href={exportScanUrl(scanId, 'csv')}
        download
        className="flex items-center gap-1.5 text-xs rounded-md border border-neutral-700 hover:border-neutral-500 px-3 py-1.5"
      >
        <Download size={12} /> CSV report
      </a>
    </div>
  )
}
