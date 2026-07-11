import type { Employee } from './employee'
import type { Product } from './product'

export type DebtStatus =
  | 'active'
  | 'paid'

export interface Debt {
  id: string
  employee_id: string
  product_id: string

  quantity: string
  unit_price: string
  total_amount: string

  status: DebtStatus
  note: string | null

  created_at: string
  updated_at: string
  paid_at: string | null

  employee: Employee
  product: Product
}

export interface DebtCreate {
  employee_id: string
  product_id: string
  quantity: number
  note: string | null
}

export interface DebtUpdate {
  quantity?: number
  note?: string | null
}