import type {
  ActionLog,
  ActionLogFilters,
} from '../types/actionLog'
import type {
  BookingNote,
  BookingNoteUpdate,
} from '../types/bookingNote'
import type {
  ClubSetting,
  ClubSettingUpdate,
} from '../types/clubSetting'
import type {
  Debt,
  DebtCreate,
  DebtStatus,
  DebtUpdate,
} from '../types/debt'
import type {
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
} from '../types/employee'
import type {
  InventoryBalance,
  InventoryBalanceUpdate,
} from '../types/inventoryBalance'
import type {
  LightShellImportApplyResult,
  LightShellImportPreview,
  LightShellImportResolution,
} from '../types/lightshellImport'
import type {
  Prize,
  PrizeCreate,
  PrizeStatus,
  PrizeUpdate,
} from '../types/prize'
import type {
  Product,
  ProductCreate,
  ProductUpdate,
} from '../types/product'

const API_BASE_URL = 'http://127.0.0.1:8000'

interface ApiErrorBody {
  detail?: string
}

async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const headers = new Headers(
    options?.headers,
  )

  if (
    !(options?.body instanceof FormData)
    && !headers.has('Content-Type')
  ) {
    headers.set(
      'Content-Type',
      'application/json',
    )
  }

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
    },
  )

  if (!response.ok) {
    let message =
      `Ошибка сервера: ${response.status}`

    try {
      const errorBody =
        (await response.json()) as ApiErrorBody

      if (errorBody.detail) {
        message = errorBody.detail
      }
    } catch {
      // Сервер вернул ответ без JSON.
    }

    throw new Error(message)
  }

  return response.json() as Promise<T>
}

export interface DatabaseHealth {
  status: string
  database: string
  user: string
}

export function getDatabaseHealth():
Promise<DatabaseHealth> {
  return apiRequest<DatabaseHealth>(
    '/health/database',
  )
}

export function getProducts(
  includeInactive = false,
): Promise<Product[]> {
  const query = new URLSearchParams({
    include_inactive: String(
      includeInactive,
    ),
  })

  return apiRequest<Product[]>(
    `/products?${query.toString()}`,
  )
}

export function getProduct(
  productId: string,
): Promise<Product> {
  return apiRequest<Product>(
    `/products/${productId}`,
  )
}

export function createProduct(
  product: ProductCreate,
): Promise<Product> {
  return apiRequest<Product>(
    '/products',
    {
      method: 'POST',
      body: JSON.stringify(product),
    },
  )
}

export function updateProduct(
  productId: string,
  product: ProductUpdate,
): Promise<Product> {
  return apiRequest<Product>(
    `/products/${productId}`,
    {
      method: 'PATCH',
      body: JSON.stringify(product),
    },
  )
}

export function archiveProduct(
  productId: string,
): Promise<Product> {
  return apiRequest<Product>(
    `/products/${productId}/archive`,
    {
      method: 'POST',
    },
  )
}

export function restoreProduct(
  productId: string,
): Promise<Product> {
  return apiRequest<Product>(
    `/products/${productId}/restore`,
    {
      method: 'POST',
    },
  )
}

export function getInventoryBalances(
  includeInactive = false,
): Promise<InventoryBalance[]> {
  const query = new URLSearchParams({
    include_inactive: String(
      includeInactive,
    ),
  })

  return apiRequest<InventoryBalance[]>(
    `/inventory-balances?${query.toString()}`,
  )
}

export function getInventoryBalance(
  productId: string,
): Promise<InventoryBalance> {
  return apiRequest<InventoryBalance>(
    `/inventory-balances/${productId}`,
  )
}

export function updateInventoryBalance(
  productId: string,
  balance: InventoryBalanceUpdate,
): Promise<InventoryBalance> {
  return apiRequest<InventoryBalance>(
    `/inventory-balances/${productId}`,
    {
      method: 'PATCH',
      body: JSON.stringify(balance),
    },
  )
}

export function getEmployees(
  includeInactive = false,
): Promise<Employee[]> {
  const query = new URLSearchParams({
    include_inactive: String(
      includeInactive,
    ),
  })

  return apiRequest<Employee[]>(
    `/employees?${query.toString()}`,
  )
}

export function getEmployee(
  employeeId: string,
): Promise<Employee> {
  return apiRequest<Employee>(
    `/employees/${employeeId}`,
  )
}

export function createEmployee(
  employee: EmployeeCreate,
): Promise<Employee> {
  return apiRequest<Employee>(
    '/employees',
    {
      method: 'POST',
      body: JSON.stringify(employee),
    },
  )
}

export function updateEmployee(
  employeeId: string,
  employee: EmployeeUpdate,
): Promise<Employee> {
  return apiRequest<Employee>(
    `/employees/${employeeId}`,
    {
      method: 'PATCH',
      body: JSON.stringify(employee),
    },
  )
}

export function archiveEmployee(
  employeeId: string,
): Promise<Employee> {
  return apiRequest<Employee>(
    `/employees/${employeeId}/archive`,
    {
      method: 'POST',
    },
  )
}

export function restoreEmployee(
  employeeId: string,
): Promise<Employee> {
  return apiRequest<Employee>(
    `/employees/${employeeId}/restore`,
    {
      method: 'POST',
    },
  )
}

export function getDebts(
  status?: DebtStatus,
): Promise<Debt[]> {
  const query = new URLSearchParams()

  if (status) {
    query.set(
      'status',
      status,
    )
  }

  const queryString =
    query.toString()

  return apiRequest<Debt[]>(
    `/debts${queryString ? `?${queryString}` : ''}`,
  )
}

export function getDebt(
  debtId: string,
): Promise<Debt> {
  return apiRequest<Debt>(
    `/debts/${debtId}`,
  )
}

export function createDebt(
  debt: DebtCreate,
): Promise<Debt> {
  return apiRequest<Debt>(
    '/debts',
    {
      method: 'POST',
      body: JSON.stringify(debt),
    },
  )
}

export function updateDebt(
  debtId: string,
  debt: DebtUpdate,
): Promise<Debt> {
  return apiRequest<Debt>(
    `/debts/${debtId}`,
    {
      method: 'PATCH',
      body: JSON.stringify(debt),
    },
  )
}

export function payDebt(
  debtId: string,
): Promise<Debt> {
  return apiRequest<Debt>(
    `/debts/${debtId}/pay`,
    {
      method: 'POST',
    },
  )
}

export function getPrizes(
  status?: PrizeStatus,
): Promise<Prize[]> {
  const query = new URLSearchParams()

  if (status) {
    query.set(
      'status',
      status,
    )
  }

  const queryString =
    query.toString()

  return apiRequest<Prize[]>(
    `/prizes${queryString ? `?${queryString}` : ''}`,
  )
}

export function getPrize(
  prizeId: string,
): Promise<Prize> {
  return apiRequest<Prize>(
    `/prizes/${prizeId}`,
  )
}

export function createPrize(
  prize: PrizeCreate,
): Promise<Prize> {
  return apiRequest<Prize>(
    '/prizes',
    {
      method: 'POST',
      body: JSON.stringify(prize),
    },
  )
}

export function updatePrize(
  prizeId: string,
  prize: PrizeUpdate,
): Promise<Prize> {
  return apiRequest<Prize>(
    `/prizes/${prizeId}`,
    {
      method: 'PATCH',
      body: JSON.stringify(prize),
    },
  )
}

export function confirmPrizeReflected(
  prizeId: string,
): Promise<Prize> {
  return apiRequest<Prize>(
    `/prizes/${prizeId}/confirm-reflected`,
    {
      method: 'POST',
    },
  )
}

export function getBookingNote(
  bookingDate: string,
): Promise<BookingNote> {
  return apiRequest<BookingNote>(
    `/booking-notes/${bookingDate}`,
  )
}

export function updateBookingNote(
  bookingDate: string,
  bookingNote: BookingNoteUpdate,
): Promise<BookingNote> {
  return apiRequest<BookingNote>(
    `/booking-notes/${bookingDate}`,
    {
      method: 'PUT',
      body: JSON.stringify(
        bookingNote,
      ),
    },
  )
}

export function previewLightShellImport(
  file: File,
): Promise<LightShellImportPreview> {
  const formData = new FormData()

  formData.append(
    'file',
    file,
  )

  return apiRequest<LightShellImportPreview>(
    '/lightshell-imports/preview',
    {
      method: 'POST',
      body: formData,
    },
  )
}

export function applyLightShellImport(
  file: File,
  resolutions: LightShellImportResolution[],
): Promise<LightShellImportApplyResult> {
  const formData = new FormData()

  formData.append(
    'file',
    file,
  )

  formData.append(
    'resolutions_json',
    JSON.stringify(resolutions),
  )

  return apiRequest<LightShellImportApplyResult>(
    '/lightshell-imports/apply',
    {
      method: 'POST',
      body: formData,
    },
  )
}

export function getActionLogs(
  filters: ActionLogFilters = {},
): Promise<ActionLog[]> {
  const query = new URLSearchParams()

  if (filters.event_type) {
    query.set(
      'event_type',
      filters.event_type,
    )
  }

  if (filters.entity_type) {
    query.set(
      'entity_type',
      filters.entity_type,
    )
  }

  if (filters.limit !== undefined) {
    query.set(
      'limit',
      String(filters.limit),
    )
  }

  if (filters.offset !== undefined) {
    query.set(
      'offset',
      String(filters.offset),
    )
  }

  const queryString =
    query.toString()

  return apiRequest<ActionLog[]>(
    `/action-logs${queryString ? `?${queryString}` : ''}`,
  )
}

export function getClubSettings():
Promise<ClubSetting> {
  return apiRequest<ClubSetting>(
    '/club-settings',
  )
}

export function updateClubSettings(
  settings: ClubSettingUpdate,
): Promise<ClubSetting> {
  return apiRequest<ClubSetting>(
    '/club-settings',
    {
      method: 'PATCH',
      body: JSON.stringify(settings),
    },
  )
}
