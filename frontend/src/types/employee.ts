export interface Employee {
  id: string
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EmployeeCreate {
  name: string
}

export interface EmployeeUpdate {
  name?: string
  is_active?: boolean
}