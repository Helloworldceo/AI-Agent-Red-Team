export type TargetType = 'direct_chat' | 'tool_agent' | 'rag'
export type PayloadKind =
  | 'single_shot'
  | 'multi_turn'
  | 'tool_output_injection'
  | 'rag_poisoning'
  | 'excessive_agency'
export type Confidence = 'high' | 'medium' | 'low'
export type Severity = 'info' | 'low' | 'medium' | 'high' | 'critical'
export type EvalMode = 'keyword' | 'llm_judge'
export type Provider = 'deepseek' | 'gemini'

export interface ProviderInfo {
  id: Provider
  label: string
  default_model: string
}
export type ScanStatus = 'pending' | 'running' | 'completed' | 'cancelled' | 'error'
export type ToolSensitivity = 'safe' | 'sensitive'

export interface ToolCallRecord {
  step_index: number
  tool_name: string
  tool_args: Record<string, unknown>
  tool_result: string
  sensitivity: ToolSensitivity
  timestamp: number
}

export interface TurnRecord {
  turn_index: number
  role: 'user' | 'assistant'
  content: string
  tool_calls: ToolCallRecord[]
}

export interface Payload {
  id: string
  category: string
  name: string
  description: string
  kind: PayloadKind
  applicable_targets: TargetType[]
  is_control: boolean
}

export interface TargetInfo {
  type: TargetType
  label: string
  blurb: string
}

export interface ScanRequest {
  target_type: TargetType
  system_prompt: string
  goal: string
  api_key: string
  provider?: Provider
  model?: string
  selected_payload_ids?: string[]
  eval_mode?: EvalMode
}

export interface ScanResultItem {
  id: string
  category: string
  name: string
  description: string
  kind: PayloadKind
  is_control: boolean
  turns: TurnRecord[]
  final_response: string
  retrieved_documents: Record<string, unknown>[] | null
  success: boolean
  confidence: Confidence
  severity: Severity
  reason: string
  triggered_tools: string[]
  error: string | null
  duration_ms: number
}

export interface ScanSummary {
  total: number
  succeeded: number
  failed: number
  errors: number
  success_rate: number
  by_category: Record<string, { total: number; succeeded: number }>
  by_severity: Record<string, number>
  risk_label: string
  risk_level: 'very_resilient' | 'low' | 'medium' | 'high' | 'critical'
  control_total: number
  control_passed: number
}

export interface ScanStatusResponse {
  scan_id: string
  status: ScanStatus
  target_type: TargetType
  progress: {
    completed: number
    total: number
    current_payload_name: string | null
  }
  results: ScanResultItem[]
  summary: ScanSummary | null
  error: string | null
  created_at: string
}
