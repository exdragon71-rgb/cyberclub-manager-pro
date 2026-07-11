import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from 'react'
import {
  Link,
  useNavigate,
  useParams,
} from 'react-router-dom'

import {
  getProduct,
  updateProduct,
} from '../api/client'

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

export function EditProductPage() {
  const navigate = useNavigate()
  const { productId } = useParams<{
    productId: string
  }>()

  const [name, setName] = useState('')
  const [price, setPrice] = useState('')
  const [unit, setUnit] = useState('')
  const [minimumStock, setMinimumStock] =
    useState('')
  const [lightshellId, setLightshellId] =
    useState('')

  const [loadingStatus, setLoadingStatus] =
    useState<LoadingStatus>('loading')
  const [isSubmitting, setIsSubmitting] =
    useState(false)
  const [errorMessage, setErrorMessage] =
    useState('')

  const loadProduct = useCallback(async () => {
    if (!productId) {
      setLoadingStatus('error')
      setErrorMessage('Не указан ID товара')
      return
    }

    try {
      const product = await getProduct(productId)

      setName(product.name)
      setPrice(Number(product.price).toString())
      setUnit(product.unit)
      setMinimumStock(
        Number(product.minimum_stock).toString(),
      )
      setLightshellId(product.lightshell_id ?? '')
      setLoadingStatus('success')
    } catch (error) {
      setLoadingStatus('error')

      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось загрузить товар',
        )
      }
    }
  }, [productId])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadProduct()
    }, 0)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [loadProduct])

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!productId) {
      setErrorMessage('Не указан ID товара')
      return
    }

    setIsSubmitting(true)
    setErrorMessage('')

    try {
      await updateProduct(productId, {
        name: name.trim(),
        price: Number(price),
        unit: unit.trim(),
        minimum_stock: Number(minimumStock),
        lightshell_id:
          lightshellId.trim() || null,
      })

      navigate('/products')
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось сохранить изменения',
        )
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loadingStatus === 'loading') {
    return (
      <main className="min-h-screen bg-[#070a10] p-6 text-slate-100">
        <div className="mx-auto max-w-3xl">
          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-8 text-slate-400">
            Загрузка товара...
          </div>
        </div>
      </main>
    )
  }

  if (loadingStatus === 'error') {
    return (
      <main className="min-h-screen bg-[#070a10] p-6 text-slate-100">
        <div className="mx-auto max-w-3xl">
          <Link
            to="/products"
            className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
          >
            ← Назад к товарам
          </Link>

          <div className="mt-6 rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-300">
            {errorMessage}
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-[#070a10] p-6 text-slate-100">
      <div className="mx-auto max-w-3xl">
        <Link
          to="/products"
          className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
        >
          ← Назад к товарам
        </Link>

        <header className="mt-5">
          <p className="text-sm font-medium uppercase tracking-wider text-cyan-400">
            Склад
          </p>

          <h1 className="mt-2 text-3xl font-bold text-white">
            Редактировать товар
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Изменения будут сохранены в PostgreSQL.
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="mt-8 rounded-2xl border border-slate-800 bg-[#0b0f17] p-6"
        >
          <div>
            <label
              htmlFor="product-name"
              className="text-sm font-medium text-slate-300"
            >
              Название товара
            </label>

            <input
              id="product-name"
              type="text"
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
              required
              minLength={2}
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
            />
          </div>

          <div className="mt-5 grid gap-5 sm:grid-cols-2">
            <div>
              <label
                htmlFor="product-price"
                className="text-sm font-medium text-slate-300"
              >
                Цена
              </label>

              <input
                id="product-price"
                type="number"
                value={price}
                onChange={(event) =>
                  setPrice(event.target.value)
                }
                required
                min="0"
                step="0.01"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              />
            </div>

            <div>
              <label
                htmlFor="product-unit"
                className="text-sm font-medium text-slate-300"
              >
                Единица измерения
              </label>

              <input
                id="product-unit"
                type="text"
                value={unit}
                onChange={(event) =>
                  setUnit(event.target.value)
                }
                required
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              />
            </div>

            <div>
              <label
                htmlFor="minimum-stock"
                className="text-sm font-medium text-slate-300"
              >
                Минимальный остаток
              </label>

              <input
                id="minimum-stock"
                type="number"
                value={minimumStock}
                onChange={(event) =>
                  setMinimumStock(event.target.value)
                }
                required
                min="0"
                step="0.001"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              />
            </div>

            <div>
              <label
                htmlFor="lightshell-id"
                className="text-sm font-medium text-slate-300"
              >
                LightShell ID
              </label>

              <input
                id="lightshell-id"
                type="text"
                value={lightshellId}
                onChange={(event) =>
                  setLightshellId(event.target.value)
                }
                placeholder="Необязательно"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
              />
            </div>
          </div>

          {errorMessage && (
            <div className="mt-5 rounded-xl border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">
              {errorMessage}
            </div>
          )}

          <div className="mt-7 flex justify-end gap-3">
            <Link
              to="/products"
              className="rounded-xl border border-slate-700 bg-slate-900 px-5 py-3 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:text-white"
            >
              Отмена
            </Link>

            <button
              type="submit"
              disabled={isSubmitting}
              className="rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting
                ? 'Сохранение...'
                : 'Сохранить изменения'}
            </button>
          </div>
        </form>
      </div>
    </main>
  )
}