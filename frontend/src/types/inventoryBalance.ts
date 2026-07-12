import type { Product } from './product'

export interface InventoryBalance {
  id: string
  product_id: string

  program_quantity: string
  actual_quantity: string

  active_debt_quantity: string
  active_prize_quantity: string

  created_at: string
  updated_at: string

  product: Product
}

export interface InventoryBalanceUpdate {
  program_quantity?: number
  actual_quantity?: number
}