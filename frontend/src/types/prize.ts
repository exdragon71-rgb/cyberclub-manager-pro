import type {
  Employee,
} from './employee'
import type {
  Product,
} from './product'

export type PrizeStatus =
  | 'active'
  | 'written_off'

export interface Prize {
  id: string

  employee_id: string
  product_id: string

  quantity: string

  status: PrizeStatus
  note: string | null

  created_at: string
  updated_at: string
  written_off_at: string | null

  employee: Employee
  product: Product
}

export interface PrizeCreate {
  employee_id: string
  product_id: string

  quantity: number

  note?: string | null
}

export interface PrizeUpdate {
  quantity?: number

  note?: string | null
}