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
  ticket_price: string

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

  quantity: 1

  note?: string | null
}

export interface PrizeUpdate {
  quantity?: 1

  note?: string | null
}