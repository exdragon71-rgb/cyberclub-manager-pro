import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from 'react'
import { Link } from 'react-router-dom'

import {
  createDebt,
  getDebts,
  getEmployees,
  getProducts,
  payDebt,
} from '../api/client'
import type {
  Debt,
  DebtStatus,
} from '../types/debt'
import type { Employee } from '../types/employee'
import type { Product } from '../types/product'

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

type StatusFilter =
  | 'all'
  | DebtStatus

function formatPrice(value: string | number) {
  return Number(value).toLocaleString('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })
}

function formatQuantity(value: string) {
  return Number(value).toLocaleString('ru-RU', {
    maximumFractionDigits: 3,
  })
}

function formatDate(value: string) {
  return new Date(value).toLocaleString('ru-RU', {
    dateStyle: 'short',
    timeStyle: 'short',
  })
}

export function DebtsPage() {
  const [debts, setDebts] = useState<Debt[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [products, setProducts] = useState<Product[]>([])

  const [employeeId, setEmployeeId] = useState('')
  const [productId, setProductId] = useState('')
  const [quantity, setQuantity] = useState('1')
  const [note, setNote] = useState('')

  const [statusFilter, setStatusFilter] =
    useState<StatusFilter>('active')
  const [loadingStatus, setLoadingStatus] =
    useState<LoadingStatus>('loading')
  const [isCreating, setIsCreating] =
    useState(false)
  const [payingDebtId, setPayingDebtId] =
    useState<string | null>(null)

  const [errorMessage, setErrorMessage] =
    useState('')
  const [successMessage, setSuccessMessage] =
    useState('')

  const loadPageData = useCallback(async () => {
    try {
      const [
        loadedDebts,
        loadedEmployees,
        loadedProducts,
      ] = await Promise.all([
        getDebts(),
        getEmployees(),
        getProducts(),
      ])

      setDebts(loadedDebts)
      setEmployees(loadedEmployees)
      setProducts(loadedProducts)
      setErrorMessage('')
      setLoadingStatus('success')
    } catch (error) {
      setDebts([])
      setEmployees([])
      setProducts([])
      setLoadingStatus('error')

      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось загрузить долги',
        )
      }
    }
  }, [])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadPageData()
    }, 0)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [loadPageData])

  async function handleCreate(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const normalizedQuantity = Number(quantity)

    if (!employeeId) {
      setErrorMessage(
        'Выберите сотрудника.',
      )
      return
    }

    if (!productId) {
      setErrorMessage(
        'Выберите товар.',
      )
      return
    }

    if (
      !Number.isFinite(normalizedQuantity)
      || normalizedQuantity <= 0
    ) {
      setErrorMessage(
        'Количество должно быть больше нуля.',
      )
      return
    }

    setIsCreating(true)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const createdDebt = await createDebt({
        employee_id: employeeId,
        product_id: productId,
        quantity: normalizedQuantity,
        note: note.trim() || null,
      })

      setDebts((currentDebts) => [
        createdDebt,
        ...currentDebts,
      ])

      setProductId('')
      setQuantity('1')
      setNote('')

      setSuccessMessage(
        `Долг сотрудника «${createdDebt.employee.name}» добавлен.`,
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось добавить долг',
        )
      }
    } finally {
      setIsCreating(false)
    }
  }

  async function handlePay(debt: Debt) {
    const isConfirmed = window.confirm(
      `Погасить долг сотрудника «${debt.employee.name}» на сумму ${formatPrice(debt.total_amount)}?`,
    )

    if (!isConfirmed) {
      return
    }

    setPayingDebtId(debt.id)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const paidDebt = await payDebt(debt.id)

      setDebts((currentDebts) =>
        currentDebts.map((currentDebt) =>
          currentDebt.id === debt.id
            ? paidDebt
            : currentDebt,
        ),
      )

      setSuccessMessage(
        `Долг сотрудника «${debt.employee.name}» погашен.`,
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось погасить долг',
        )
      }
    } finally {
      setPayingDebtId(null)
    }
  }

  function handleRefresh() {
    setLoadingStatus('loading')
    setErrorMessage('')
    setSuccessMessage('')
    void loadPageData()
  }

  const filteredDebts = debts.filter(
    (debt) =>
      statusFilter === 'all'
      || debt.status === statusFilter,
  )

  const activeDebts = debts.filter(
    (debt) => debt.status === 'active',
  )

  const activeDebtAmount = activeDebts.reduce(
    (total, debt) =>
      total + Number(debt.total_amount),
    0,
  )

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
              Долги
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Учёт товаров, взятых сотрудниками
            </p>
          </div>

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
        </header>

        <section className="mt-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Всего записей
            </p>

            <p className="mt-2 text-3xl font-bold text-white">
              {loadingStatus === 'loading'
                ? '...'
                : debts.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Активные долги
            </p>

            <p className="mt-2 text-3xl font-bold text-amber-400">
              {loadingStatus === 'loading'
                ? '...'
                : activeDebts.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Общая задолженность
            </p>

            <p className="mt-2 text-3xl font-bold text-red-400">
              {loadingStatus === 'loading'
                ? '...'
                : formatPrice(activeDebtAmount)}
            </p>
          </div>
        </section>

        <form
          onSubmit={handleCreate}
          className="mt-6 rounded-2xl border border-slate-800 bg-[#0b0f17] p-6"
        >
          <h2 className="text-xl font-semibold text-white">
            Добавить долг
          </h2>

          <div className="mt-5 grid gap-5 md:grid-cols-2">
            <div>
              <label
                htmlFor="debt-employee"
                className="text-sm font-medium text-slate-300"
              >
                Сотрудник
              </label>

              <select
                id="debt-employee"
                value={employeeId}
                onChange={(event) =>
                  setEmployeeId(event.target.value)
                }
                required
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              >
                <option value="">
                  Выберите сотрудника
                </option>

                {employees.map((employee) => (
                  <option
                    key={employee.id}
                    value={employee.id}
                  >
                    {employee.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="debt-product"
                className="text-sm font-medium text-slate-300"
              >
                Товар
              </label>

              <select
                id="debt-product"
                value={productId}
                onChange={(event) =>
                  setProductId(event.target.value)
                }
                required
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              >
                <option value="">
                  Выберите товар
                </option>

                {products.map((product) => (
                  <option
                    key={product.id}
                    value={product.id}
                  >
                    {product.name}
                    {' · '}
                    {formatPrice(product.price)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="debt-quantity"
                className="text-sm font-medium text-slate-300"
              >
                Количество
              </label>

              <input
                id="debt-quantity"
                type="number"
                min="0.001"
                step="0.001"
                value={quantity}
                onChange={(event) =>
                  setQuantity(event.target.value)
                }
                required
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              />
            </div>

            <div>
              <label
                htmlFor="debt-note"
                className="text-sm font-medium text-slate-300"
              >
                Примечание
              </label>

              <input
                id="debt-note"
                type="text"
                value={note}
                onChange={(event) =>
                  setNote(event.target.value)
                }
                maxLength={2000}
                placeholder="Необязательно"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
              />
            </div>
          </div>

          {employees.length === 0 && (
            <p className="mt-4 text-sm text-amber-400">
              Сначала добавьте активного сотрудника.
            </p>
          )}

          {products.length === 0 && (
            <p className="mt-2 text-sm text-amber-400">
              Сначала добавьте активный товар.
            </p>
          )}

          <div className="mt-6 flex justify-end">
            <button
              type="submit"
              disabled={
                isCreating
                || employees.length === 0
                || products.length === 0
              }
              className="rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isCreating
                ? 'Добавление...'
                : 'Добавить долг'}
            </button>
          </div>
        </form>

        {errorMessage && (
          <div className="mt-6 rounded-2xl border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">
            {errorMessage}
          </div>
        )}

        {successMessage && (
          <div className="mt-6 rounded-2xl border border-emerald-900 bg-emerald-950/40 p-4 text-sm text-emerald-300">
            {successMessage}
          </div>
        )}

        <section className="mt-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-xl font-semibold text-white">
              История долгов
            </h2>

            <select
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(
                  event.target.value as StatusFilter,
                )
              }
              className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-white outline-none transition focus:border-cyan-500"
            >
              <option value="active">
                Только активные
              </option>

              <option value="paid">
                Только погашенные
              </option>

              <option value="all">
                Все долги
              </option>
            </select>
          </div>

          <div className="mt-4 overflow-hidden rounded-2xl border border-slate-800 bg-[#0b0f17]">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1150px] text-left">
                <thead className="border-b border-slate-800 bg-slate-950/60 text-xs uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="px-6 py-4">
                      Сотрудник
                    </th>

                    <th className="px-6 py-4">
                      Товар
                    </th>

                    <th className="px-6 py-4">
                      Количество
                    </th>

                    <th className="px-6 py-4">
                      Цена
                    </th>

                    <th className="px-6 py-4">
                      Сумма
                    </th>

                    <th className="px-6 py-4">
                      Статус
                    </th>

                    <th className="px-6 py-4">
                      Дата
                    </th>

                    <th className="px-6 py-4 text-right">
                      Действия
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-800">
                  {filteredDebts.map((debt) => {
                    const isPaying =
                      payingDebtId === debt.id

                    return (
                      <tr
                        key={debt.id}
                        className="transition hover:bg-slate-900/70"
                      >
                        <td className="px-6 py-4">
                          <p className="font-medium text-white">
                            {debt.employee.name}
                          </p>

                          {debt.note && (
                            <p className="mt-1 max-w-xs text-xs text-slate-500">
                              {debt.note}
                            </p>
                          )}
                        </td>

                        <td className="px-6 py-4 text-slate-300">
                          {debt.product.name}
                        </td>

                        <td className="px-6 py-4 text-slate-300">
                          {formatQuantity(debt.quantity)}
                          {' '}
                          {debt.product.unit}
                        </td>

                        <td className="px-6 py-4 text-slate-300">
                          {formatPrice(debt.unit_price)}
                        </td>

                        <td className="px-6 py-4 font-semibold text-white">
                          {formatPrice(debt.total_amount)}
                        </td>

                        <td className="px-6 py-4">
                          <span
                            className={
                              debt.status === 'active'
                                ? 'rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-400'
                                : 'rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400'
                            }
                          >
                            {debt.status === 'active'
                              ? 'Активен'
                              : 'Погашен'}
                          </span>
                        </td>

                        <td className="px-6 py-4 text-sm text-slate-400">
                          {formatDate(debt.created_at)}
                        </td>

                        <td className="px-6 py-4 text-right">
                          {debt.status === 'active' ? (
                            <button
                              type="button"
                              onClick={() => {
                                void handlePay(debt)
                              }}
                              disabled={isPaying}
                              className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                              {isPaying
                                ? 'Погашение...'
                                : 'Погасить'}
                            </button>
                          ) : (
                            <span className="text-sm text-slate-600">
                              Завершён
                            </span>
                          )}
                        </td>
                      </tr>
                    )
                  })}

                  {loadingStatus === 'success'
                    && filteredDebts.length === 0 && (
                      <tr>
                        <td
                          colSpan={8}
                          className="px-6 py-12 text-center text-slate-500"
                        >
                          Подходящих долгов пока нет
                        </td>
                      </tr>
                    )}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}