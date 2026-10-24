import { apiGet } from './client'
import type { FindingDetail, FindingSummary } from '../types/api'

export async function getFindings(): Promise<FindingSummary[]> {
  const data = await apiGet<{ findings: FindingSummary[] }>('/research/findings')
  return data.findings
}

export async function getFinding(date: string): Promise<FindingDetail> {
  return apiGet<FindingDetail>(`/research/findings/${date}`)
}
