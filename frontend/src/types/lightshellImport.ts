export type LightShellMatchStatus =
  | 'exact'
  | 'mapped'
  | 'unmatched'
  | 'ambiguous'

export interface LightShellImportPreviewItem {
  source_number: number
  source_name: string
  normalized_source_name: string
  source_category: string
  program_quantity: string

  status: LightShellMatchStatus

  product_id: string | null
  product_name: string | null
}

export interface LightShellImportPreview {
  branch: string
  generated_at: string
  source_filename: string

  total_items: number
  matched_items: number
  unmatched_items: number
  ambiguous_items: number

  items: LightShellImportPreviewItem[]
}

export type LightShellResolutionAction =
  | 'use_existing'
  | 'create_new'
  | 'skip'

export interface LightShellImportResolution {
  source_number: number
  action: LightShellResolutionAction
  product_id: string | null
}

export interface LightShellImportApplyResult {
  import_id: string

  branch: string
  generated_at: string
  source_filename: string

  total_items: number
  updated_items: number
  created_products: number
  skipped_items: number
  created_mappings: number
}