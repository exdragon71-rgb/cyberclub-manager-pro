export interface ActionLog {
  id: string

  event_type: string
  entity_type: string
  entity_id: string | null

  message: string

  details: Record<string, unknown>

  created_at: string
}

export interface ActionLogFilters {
  event_type?: string
  entity_type?: string
  limit?: number
  offset?: number
}