import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import { Link } from 'react-router-dom'

import { getProducts } from '../api/client'
import type { Product } from '../types/product'

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

function formatPrice(price: string) {
  return Number(price).toLocaleString('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
  })
}

export function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [loadingStatus, setLoadingStatus] =
    useState<LoadingStatus>('loading')
  const [errorMessage, setErrorMessage] = useState('')

  const loadProducts = useCallback(async () => {
    try {
      const loadedProducts = await getProducts(true)

      setProducts(loadedProducts)
      setLoadingStatus('success')
    } catch (error) {
      setProducts([])
      setLoadingStatus('error')

      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось загрузить товары',
        )
      }
    }
  }, [])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadProducts()
    }, 0)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [loadProducts])

  const activeProductsCount = products.filter(
    (product) => product.is_active,
  ).length

  function handleRefresh() {
    setLoadingStatus('loading')
    setErrorMessage('')
    void loadProducts()
  }

  return (
    <main className="min-h-screen bg-[#070a10] p-6 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <header className="flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              to="/"
              className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
            >
              ← Главная панель
            </Link>

            <h1 className="mt-3 text-3xl font-bold text-white">
              Товары
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Управление товарами клуба
            </p>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleRefresh}
              disabled={loadingStatus === 'loading'}
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loadingStatus === 'loading'
                ? 'Загрузка...'
                : 'Обновить'}
            </button>

            <button
              type="button"
              className="rounded-xl bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
            >
              Добавить товар
            </button>
          </div>
        </header>

        <section className="mt-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Всего товаров
            </p>

            <p className="mt-2 text-3xl font-bold text-white">
              {loadingStatus === 'loading'
                ? '...'
                : products.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Активные
            </p>

            <p className="mt-2 text-3xl font-bold text-emerald-400">
              {loadingStatus === 'loading'
                ? '...'
                : activeProductsCount}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              В архиве
            </p>

            <p className="mt-2 text-3xl font-bold text-amber-400">
              {loadingStatus === 'loading'
                ? '...'
                : products.length -
                  activeProductsCount}
            </p>
          </div>
        </section>

        {errorMessage && (
          <div className="mt-6 rounded-2xl border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">
            {errorMessage}
          </div>
        )}

        <section className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-[#0b0f17]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[800px] text-left">
              <thead className="border-b border-slate-800 bg-slate-950/60 text-xs uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-6 py-4">
                    Товар
                  </th>

                  <th className="px-6 py-4">
                    Цена
                  </th>

                  <th className="px-6 py-4">
                    Единица
                  </th>

                  <th className="px-6 py-4">
                    Минимум
                  </th>

                  <th className="px-6 py-4">
                    Статус
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {products.map((product) => (
                  <tr
                    key={product.id}
                    className="transition hover:bg-slate-900/70"
                  >
                    <td className="px-6 py-4">
                      <p className="font-medium text-white">
                        {product.name}
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        {product.lightshell_id
                          ? `LightShell: ${product.lightshell_id}`
                          : 'Без LightShell ID'}
                      </p>
                    </td>

                    <td className="px-6 py-4 text-slate-300">
                      {formatPrice(product.price)}
                    </td>

                    <td className="px-6 py-4 text-slate-300">
                      {product.unit}
                    </td>

                    <td className="px-6 py-4 text-slate-300">
                      {product.minimum_stock}
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={
                          product.is_active
                            ? 'rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400'
                            : 'rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-400'
                        }
                      >
                        {product.is_active
                          ? 'Активен'
                          : 'В архиве'}
                      </span>
                    </td>
                  </tr>
                ))}

                {loadingStatus === 'success' &&
                  products.length === 0 && (
                    <tr>
                      <td
                        colSpan={5}
                        className="px-6 py-12 text-center text-slate-500"
                      >
                        Товаров пока нет
                      </td>
                    </tr>
                  )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  )
}