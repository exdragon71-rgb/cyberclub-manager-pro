export interface Product {
  id: string
  name: string
  price: string
  unit: string
  minimum_stock: string
  lightshell_id: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProductCreate {
  name: string
  price: number
  unit: string
  minimum_stock: number
  lightshell_id: string | null
}

export interface ProductUpdate {
  name?: string
  price?: number
  unit?: string
  minimum_stock?: number
  lightshell_id?: string | null
  is_active?: boolean
}