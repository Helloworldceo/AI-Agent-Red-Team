import { apiGet, apiPost, apiUrl } from './client'
import type { ScanRequest, ScanResultItem, ScanStatusResponse } from '../types/api'

export async function startScan(req: ScanRequest): Promise<{ scan_id: string }> {
  return apiPost('/scans', req)
}

export async function getScan(scanId: string): Promise<ScanStatusResponse> {
  return apiGet(`/scans/${scanId}`)
}

export async function cancelScan(scanId: string): Promise<void> {
  await apiPost(`/scans/${scanId}/cancel`, {})
}

export function exportScanUrl(scanId: string, format: 'json' | 'csv'): string {
  return apiUrl(`/scans/${scanId}/export?format=${format}`)
}

/**
 * Wraps the backend's SSE stream. Calls `onResult` for each payload result
 * as it arrives and `onDone` once with the final status when the stream
 * closes (completed/cancelled/error).
 */
export function streamScan(
  scanId: string,
  onResult: (item: ScanResultItem) => void,
  onDone: (status: ScanStatusResponse) => void,
  onError: (err: Event) => void,
): () => void {
  const source = new EventSource(apiUrl(`/scans/${scanId}/stream`))

  source.addEventListener('result', (e) => {
    onResult(JSON.parse((e as MessageEvent).data) as ScanResultItem)
  })

  source.addEventListener('done', (e) => {
    onDone(JSON.parse((e as MessageEvent).data) as ScanStatusResponse)
    source.close()
  })

  source.onerror = (e) => {
    onError(e)
    source.close()
  }

  return () => source.close()
}
