import { apiGet } from './client'
import type { Payload, ProviderInfo, TargetInfo, TargetType } from '../types/api'

export async function getTargets(): Promise<TargetInfo[]> {
  const data = await apiGet<{ targets: TargetInfo[] }>('/targets')
  return data.targets
}

export async function getProviders(): Promise<ProviderInfo[]> {
  const data = await apiGet<{ providers: ProviderInfo[] }>('/providers')
  return data.providers
}

export async function getPayloads(targetType?: TargetType): Promise<Payload[]> {
  const qs = targetType ? `?target_type=${targetType}` : ''
  const data = await apiGet<{ payloads: Payload[] }>(`/payloads${qs}`)
  return data.payloads
}
