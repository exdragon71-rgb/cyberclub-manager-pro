import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from 'react'
import { Link } from 'react-router-dom'

import {
  confirmPrizeReflected,
  createPrize,
  getClubSettings,
  getEmployees,
  getPrizes,
  getProducts,
} from '../api/client'
import type {
  ClubSetting,
} from '../types/clubSetting'
import type { Employee } from '../types/employee'
import type {
  Prize,
  PrizeStatus,
} from '../types/prize'
import type { Product } from '../types/product'

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

type StatusFilter =
  | 'all'
  | PrizeStatus

function formatPrice(
  value: string | number,
) {
  return Number(value).toLocaleString(
    'ru-RU',
    {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    },
  )
}

function formatDate(
  value: string,
) {
  return new Date(value).toLocaleString(
    'ru-RU',
    {
      dateStyle: 'short',
      timeStyle: 'short',
    },
  )
}

export function PrizesPage() {
  const [
    prizes,
    setPrizes,
  ] = useState<Prize[]>([])

  const [
    employees,
    setEmployees,
  ] = useState<Employee[]>([])

  const [
    products,
    setProducts,
  ] = useState<Product[]>([])

  const [
    clubSettings,
    setClubSettings,
  ] = useState<ClubSetting | null>(
    null,
  )

  const [
    employeeId,
    setEmployeeId,
  ] = useState('')

  const [
    productId,
    setProductId,
  ] = useState('')

  const [
    note,
    setNote,
  ] = useState('')

  const [
    statusFilter,
    setStatusFilter,
  ] = useState<StatusFilter>(
    'active',
  )

  const [
    loadingStatus,
    setLoadingStatus,
  ] = useState<LoadingStatus>(
    'loading',
  )

  const [
    isCreating,
    setIsCreating,
  ] = useState(false)

  const [
    confirmingPrizeId,
    setConfirmingPrizeId,
  ] = useState<string | null>(
    null,
  )

  const [
    errorMessage,
    setErrorMessage,
  ] = useState('')

  const [
    successMessage,
    setSuccessMessage,
  ] = useState('')

  const loadPageData =
    useCallback(async () => {
      try {
        const [
          loadedPrizes,
          loadedEmployees,
          loadedProducts,
          loadedClubSettings,
        ] = await Promise.all([
          getPrizes(),
          getEmployees(),
          getProducts(),
          getClubSettings(),
        ])

        setPrizes(
          loadedPrizes,
        )

        setEmployees(
          loadedEmployees,
        )

        setProducts(
          loadedProducts,
        )

        setClubSettings(
          loadedClubSettings,
        )

        setErrorMessage('')
        setLoadingStatus(
          'success',
        )
      } catch (error) {
        setPrizes([])
        setEmployees([])
        setProducts([])
        setClubSettings(null)

        setLoadingStatus(
          'error',
        )

        if (error instanceof Error) {
          setErrorMessage(
            error.message,
          )
        } else {
          setErrorMessage(
            'Не удалось загрузить лотерейки.',
          )
        }
      }
    }, [])

  useEffect(() => {
    const timeoutId =
      window.setTimeout(() => {
        void loadPageData()
      }, 0)

    return () => {
      window.clearTimeout(
        timeoutId,
      )
    }
  }, [loadPageData])

  async function handleCreate(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!employeeId) {
      setErrorMessage(
        'Выберите сотрудника.',
      )
      return
    }

    if (!productId) {
      setErrorMessage(
        'Выберите выигранный товар.',
      )
      return
    }

    setIsCreating(true)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const createdPrize =
        await createPrize({
          employee_id:
            employeeId,

          product_id:
            productId,

          quantity: 1,

          note:
            note.trim()
            || null,
        })

      setPrizes(
        (currentPrizes) => [
          createdPrize,
          ...currentPrizes,
        ],
      )

      setProductId('')
      setNote('')

      setSuccessMessage(
        `Приз «${createdPrize.product.name}» добавлен в журнал.`,
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(
          error.message,
        )
      } else {
        setErrorMessage(
          'Не удалось добавить приз.',
        )
      }
    } finally {
      setIsCreating(false)
    }
  }

  async function handleConfirmReflected(
    prize: Prize,
  ) {
    const isConfirmed =
      window.confirm(
        (
          `Подтвердить, что приз `
          + `«${prize.product.name}» `
          + `уже учтён в LightShell?\n\n`
          + `Остатки «По программе» `
          + `и «Факт» изменены не будут.`
        ),
      )

    if (!isConfirmed) {
      return
    }

    setConfirmingPrizeId(
      prize.id,
    )

    setErrorMessage('')
    setSuccessMessage('')

    try {
      const confirmedPrize =
        await confirmPrizeReflected(
          prize.id,
        )

      setPrizes(
        (currentPrizes) =>
          currentPrizes.map(
            (currentPrize) =>
              currentPrize.id
              === prize.id
                ? confirmedPrize
                : currentPrize,
          ),
      )

      setSuccessMessage(
        (
          `Приз «${prize.product.name}» `
          + `перенесён в историю.`
        ),
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(
          error.message,
        )
      } else {
        setErrorMessage(
          'Не удалось подтвердить учёт приза.',
        )
      }
    } finally {
      setConfirmingPrizeId(
        null,
      )
    }
  }

  function handleRefresh() {
    setLoadingStatus(
      'loading',
    )

    setErrorMessage('')
    setSuccessMessage('')

    void loadPageData()
  }

  function handleStatusFilterChange(
    value: string,
  ) {
    if (
      value === 'all'
      || value === 'active'
      || value === 'written_off'
    ) {
      setStatusFilter(
        value,
      )
    }
  }

  const filteredPrizes =
    prizes.filter(
      (prize) =>
        statusFilter === 'all'
        || prize.status
        === statusFilter,
    )

  const activePrizes =
    prizes.filter(
      (prize) =>
        prize.status
        === 'active',
    )

  const lotteryTicketPrice =
    Number(
      clubSettings
        ?.lottery_ticket_price
      ?? 85,
    )

  const totalLotteryRevenue =
    prizes.reduce(
      (
        total,
        prize,
      ) =>
        total
        + Number(
          prize.ticket_price,
        ),
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
              Лотерейки
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Учёт товаров,
              выданных в качестве призов
            </p>
          </div>

          <button
            type="button"
            onClick={
              handleRefresh
            }
            disabled={
              loadingStatus
              === 'loading'
            }
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loadingStatus
              === 'loading'
                ? 'Загрузка...'
                : 'Обновить'}
          </button>
        </header>

        <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Продано лотереек
            </p>

            <p className="mt-2 text-3xl font-bold text-white">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : prizes.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Не учтено в LightShell
            </p>

            <p className="mt-2 text-3xl font-bold text-violet-400">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : activePrizes.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Выручка по лотерейкам
            </p>

            <p className="mt-2 text-3xl font-bold text-cyan-400">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : formatPrice(
                      totalLotteryRevenue,
                    )}
            </p>

            <p className="mt-2 text-sm text-slate-500">
              По сохранённым ценам билетов
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Цена лотерейного билета
            </p>

            <p className="mt-2 text-3xl font-bold text-emerald-400">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : formatPrice(
                      lotteryTicketPrice,
                    )}
            </p>

            <Link
              to="/settings"
              className="mt-2 inline-block text-sm text-slate-500 transition hover:text-cyan-400"
            >
              Изменить в настройках
            </Link>
          </div>
        </section>

        <form
          onSubmit={
            handleCreate
          }
          className="mt-6 rounded-2xl border border-slate-800 bg-[#0b0f17] p-6"
        >
          <h2 className="text-xl font-semibold text-white">
            Добавить выданный приз
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Одна запись соответствует одной
            проданной лотерейке и одному призу.
            Запись уменьшит ожидаемый остаток
            выигранного товара в ревизии,
            но не изменит значения
            «По программе» и «Факт».
          </p>

          <p className="mt-2 text-sm text-emerald-400">
            Текущая цена билета:
            {' '}
            {formatPrice(
              lotteryTicketPrice,
            )}
          </p>

          <div className="mt-5 grid gap-5 md:grid-cols-2">
            <div>
              <label
                htmlFor="prize-employee"
                className="text-sm font-medium text-slate-300"
              >
                Сотрудник
              </label>

              <select
                id="prize-employee"
                value={
                  employeeId
                }
                onChange={(
                  event,
                ) => {
                  setEmployeeId(
                    event.currentTarget
                      .value,
                  )
                }}
                required
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              >
                <option value="">
                  Выберите сотрудника
                </option>

                {employees.map(
                  (employee) => (
                    <option
                      key={
                        employee.id
                      }
                      value={
                        employee.id
                      }
                    >
                      {employee.name}
                    </option>
                  ),
                )}
              </select>
            </div>

            <div>
              <label
                htmlFor="prize-product"
                className="text-sm font-medium text-slate-300"
              >
                Выигранный товар
              </label>

              <select
                id="prize-product"
                value={
                  productId
                }
                onChange={(
                  event,
                ) => {
                  setProductId(
                    event.currentTarget
                      .value,
                  )
                }}
                required
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              >
                <option value="">
                  Выберите товар
                </option>

                {products.map(
                  (product) => (
                    <option
                      key={
                        product.id
                      }
                      value={
                        product.id
                      }
                    >
                      {product.name}
                    </option>
                  ),
                )}
              </select>
            </div>

            <div className="md:col-span-2">
              <label
                htmlFor="prize-note"
                className="text-sm font-medium text-slate-300"
              >
                Примечание
              </label>

              <input
                id="prize-note"
                type="text"
                value={
                  note
                }
                onChange={(
                  event,
                ) => {
                  setNote(
                    event.currentTarget
                      .value,
                  )
                }}
                maxLength={2000}
                placeholder="Необязательно"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
              />
            </div>
          </div>

          {employees.length
            === 0 && (
              <p className="mt-4 text-sm text-amber-400">
                Сначала добавьте
                активного сотрудника.
              </p>
            )}

          {products.length
            === 0 && (
              <p className="mt-2 text-sm text-amber-400">
                Сначала добавьте
                активный товар.
              </p>
            )}

          <div className="mt-6 flex justify-end">
            <button
              type="submit"
              disabled={
                isCreating
                || employees.length
                === 0
                || products.length
                === 0
              }
              className="rounded-xl bg-violet-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isCreating
                ? 'Добавление...'
                : 'Добавить приз'}
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
              Журнал лотереек
            </h2>

            <select
              value={
                statusFilter
              }
              onChange={(
                event,
              ) => {
                handleStatusFilterChange(
                  event.currentTarget
                    .value,
                )
              }}
              className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-white outline-none transition focus:border-cyan-500"
            >
              <option value="active">
                Не учтённые в LightShell
              </option>

              <option value="written_off">
                Уже учтённые
              </option>

              <option value="all">
                Все записи
              </option>
            </select>
          </div>

          <div className="mt-4 overflow-hidden rounded-2xl border border-slate-800 bg-[#0b0f17]">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1250px] text-left">
                <thead className="border-b border-slate-800 bg-slate-950/60 text-xs uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="px-6 py-4">
                      Сотрудник
                    </th>

                    <th className="px-6 py-4">
                      Товар
                    </th>

                    <th className="px-6 py-4">
                      Цена билета
                    </th>

                    <th className="px-6 py-4">
                      Статус
                    </th>

                    <th className="px-6 py-4">
                      Дата выдачи
                    </th>

                    <th className="px-6 py-4">
                      Примечание
                    </th>

                    <th className="px-6 py-4 text-right">
                      Действия
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-800">
                  {filteredPrizes.map(
                    (prize) => {
                      const isConfirming =
                        confirmingPrizeId
                        === prize.id

                      return (
                        <tr
                          key={
                            prize.id
                          }
                          className="transition hover:bg-slate-900/70"
                        >
                          <td className="px-6 py-4 font-medium text-white">
                            {
                              prize.employee
                                .name
                            }
                          </td>

                          <td className="px-6 py-4 text-slate-300">
                            {
                              prize.product
                                .name
                            }
                          </td>

                          <td className="whitespace-nowrap px-6 py-4 font-medium text-emerald-400">
                            {formatPrice(
                              prize.ticket_price,
                            )}
                          </td>

                          <td className="px-6 py-4">
                            <span
                              className={
                                prize.status
                                === 'active'
                                  ? (
                                      'rounded-full '
                                      + 'bg-violet-500/10 '
                                      + 'px-3 py-1 '
                                      + 'text-xs font-medium '
                                      + 'text-violet-400'
                                    )
                                  : (
                                      'rounded-full '
                                      + 'bg-emerald-500/10 '
                                      + 'px-3 py-1 '
                                      + 'text-xs font-medium '
                                      + 'text-emerald-400'
                                    )
                              }
                            >
                              {prize.status
                                === 'active'
                                  ? (
                                      'Не учтён '
                                      + 'в LightShell'
                                    )
                                  : (
                                      'Учтён '
                                      + 'в LightShell'
                                    )}
                            </span>
                          </td>

                          <td className="px-6 py-4 text-sm text-slate-400">
                            {formatDate(
                              prize.created_at,
                            )}
                          </td>

                          <td className="px-6 py-4 text-sm text-slate-400">
                            {prize.note
                              || '—'}
                          </td>

                          <td className="px-6 py-4 text-right">
                            {prize.status
                            === 'active' ? (
                              <button
                                type="button"
                                onClick={() => {
                                  void handleConfirmReflected(
                                    prize,
                                  )
                                }}
                                disabled={
                                  isConfirming
                                }
                                className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                {isConfirming
                                  ? 'Подтверждение...'
                                  : (
                                      'Уже учтено '
                                      + 'в LightShell'
                                    )}
                              </button>
                            ) : (
                              <div className="text-sm text-slate-500">
                                <p>
                                  В истории
                                </p>

                                {prize.written_off_at && (
                                  <p className="mt-1 text-xs text-slate-600">
                                    {formatDate(
                                      prize.written_off_at,
                                    )}
                                  </p>
                                )}
                              </div>
                            )}
                          </td>
                        </tr>
                      )
                    },
                  )}

                  {loadingStatus
                    === 'success'
                    && filteredPrizes.length
                    === 0 && (
                      <tr>
                        <td
                          colSpan={7}
                          className="px-6 py-12 text-center text-slate-500"
                        >
                          Подходящих записей
                          пока нет
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