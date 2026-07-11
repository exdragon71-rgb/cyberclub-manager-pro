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
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    let message = `Ошибка сервера: ${response.status}`

    try {
      const errorBody = (await response.json()) as ApiErrorBody

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

export function getDatabaseHealth(): Promise<DatabaseHealth> {
  return apiRequest<DatabaseHealth>('/health/database')
}

export function getProducts(
  
  includeInactive = false,
): Promise<Product[]> {
  const query = new URLSearchParams({
    include_inactive: String(includeInactive),
  })

  return apiRequest<Product[]>(`/products?${query.toString()}`)
}
export function getProduct(
  productId: string,
): Promise<Product> {
  return apiRequest<Product>(`/products/${productId}`)
}
export function createProduct(
  product: ProductCreate,
): Promise<Product> {
  return apiRequest<Product>('/products', {
    method: 'POST',
    body: JSON.stringify(product),
  })
}

export function updateProduct(
  productId: string,
  product: ProductUpdate,
): Promise<Product> {
  return apiRequest<Product>(`/products/${productId}`, {
    method: 'PATCH',
    body: JSON.stringify(product),
  })
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