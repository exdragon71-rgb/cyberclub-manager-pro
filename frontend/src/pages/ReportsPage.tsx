import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { Link } from 'react-router-dom'

import {
  getDebts,
  getInventoryBalances,
  getPrizes,
} from '../api/client'

import type { Debt } from '../types/debt'
import type {
  InventoryBalance,
} from '../types/inventoryBalance'
import type { Prize } from '../types/prize'

import {
  downloadCsv,
} from '../utils/downloadCsv'

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

type DifferenceFilter =
  | 'all'
  | 'shortage'
  | 'surplus'
  | 'matching'

interface ReportRow {
  productId: string
  productName: string
  unit: string
  price: number

  programQuantity: number
  debtQuantity: number
  prizeQuantity: number
  expectedQuantity: number
  actualQuantity: number
  difference: number

  shortageAmount: number
  surplusAmount: number
}

const filterFilenameParts:
  Record<DifferenceFilter, string> = {
    all: 'all',
    shortage: 'shortage',
    surplus: 'surplus',
    matching: 'matching',
  }

function formatPrice(
  value: number,
) {
  return value.toLocaleString(
    'ru-RU',
    {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    },
  )
}

function formatQuantity(
  value: number,
) {
  return value.toLocaleString(
    'ru-RU',
    {
      maximumFractionDigits: 3,
    },
  )
}



function formatCsvNumber(
  value: number,
  maximumFractionDigits = 3,
) {
  return value.toLocaleString(
    'ru-RU',
    {
      useGrouping: false,
      minimumFractionDigits: 0,
      maximumFractionDigits,
    },
  )
}

function formatFilenameDate(
  value: Date,
) {
  const year =
    value.getFullYear()

  const month =
    String(
      value.getMonth() + 1,
    ).padStart(2, '0')

  const day =
    String(
      value.getDate(),
    ).padStart(2, '0')

  const hours =
    String(
      value.getHours(),
    ).padStart(2, '0')

  const minutes =
    String(
      value.getMinutes(),
    ).padStart(2, '0')

  return (
    `${year}-${month}-${day}`
    + `_${hours}-${minutes}`
  )
}

function getDifferenceStatus(
  difference: number,
) {
  if (difference < 0) {
    return 'Недостача'
  }

  if (difference > 0) {
    return 'Излишек'
  }

  return 'Сходится'
}

function getDifferenceAmount(
  row: ReportRow,
) {
  if (row.difference < 0) {
    return row.shortageAmount
  }

  if (row.difference > 0) {
    return row.surplusAmount
  }

  return 0
}

function getDifferenceClassName(
  difference: number,
) {
  if (difference < 0) {
    return (
      'bg-red-500/10 '
      + 'text-red-400'
    )
  }

  if (difference > 0) {
    return (
      'bg-amber-500/10 '
      + 'text-amber-400'
    )
  }

  return (
    'bg-emerald-500/10 '
    + 'text-emerald-400'
  )
}

export function ReportsPage() {
  const [
    balances,
    setBalances,
  ] = useState<InventoryBalance[]>([])

  const [
    debts,
    setDebts,
  ] = useState<Debt[]>([])

  const [
    prizes,
    setPrizes,
  ] = useState<Prize[]>([])

  const [
    differenceFilter,
    setDifferenceFilter,
  ] = useState<DifferenceFilter>(
    'all',
  )

  const [
    loadingStatus,
    setLoadingStatus,
  ] = useState<LoadingStatus>(
    'loading',
  )

  const [
    errorMessage,
    setErrorMessage,
  ] = useState('')

  const loadReport =
    useCallback(async () => {
      try {
        const [
          balancesResponse,
          debtsResponse,
          prizesResponse,
        ] = await Promise.all([
          getInventoryBalances(),
          getDebts(),
          getPrizes(),
        ])

        setBalances(
          balancesResponse,
        )

        setDebts(
          debtsResponse,
        )

        setPrizes(
          prizesResponse,
        )

        setErrorMessage('')
        setLoadingStatus('success')
      } catch (error) {
        setBalances([])
        setDebts([])
        setPrizes([])

        setLoadingStatus('error')

        if (error instanceof Error) {
          setErrorMessage(
            error.message,
          )
        } else {
          setErrorMessage(
            'Не удалось загрузить отчёт.',
          )
        }
      }
    }, [])

  useEffect(() => {
    const timeoutId =
      window.setTimeout(() => {
        void loadReport()
      }, 0)

    return () => {
      window.clearTimeout(
        timeoutId,
      )
    }
  }, [loadReport])

  const reportRows =
    useMemo<ReportRow[]>(
      () =>
        balances
          .map(
            (
              balance,
            ): ReportRow => {
              const price =
                Number(
                  balance.product.price,
                )

              const programQuantity =
                Number(
                  balance.program_quantity,
                )

              const debtQuantity =
                Number(
                  balance.active_debt_quantity,
                )

              const prizeQuantity =
                Number(
                  balance.active_prize_quantity,
                )

              const actualQuantity =
                Number(
                  balance.actual_quantity,
                )

              const expectedQuantity =
                programQuantity
                - debtQuantity
                - prizeQuantity

              const difference =
                actualQuantity
                - expectedQuantity

              const shortageAmount =
                difference < 0
                  ? Math.abs(
                      difference,
                    ) * price
                  : 0

              const surplusAmount =
                difference > 0
                  ? difference * price
                  : 0

              return {
                productId:
                  balance.product_id,

                productName:
                  balance.product.name,

                unit:
                  balance.product.unit,

                price,

                programQuantity,
                debtQuantity,
                prizeQuantity,
                expectedQuantity,
                actualQuantity,
                difference,

                shortageAmount,
                surplusAmount,
              }
            },
          )
          .sort(
            (
              firstRow,
              secondRow,
            ) =>
              secondRow.shortageAmount
              - firstRow.shortageAmount,
          ),
      [balances],
    )

  const filteredRows =
    useMemo(
      () =>
        reportRows.filter(
          (row) => {
            if (
              differenceFilter
              === 'shortage'
            ) {
              return row.difference < 0
            }

            if (
              differenceFilter
              === 'surplus'
            ) {
              return row.difference > 0
            }

            if (
              differenceFilter
              === 'matching'
            ) {
              return row.difference === 0
            }

            return true
          },
        ),
      [
        differenceFilter,
        reportRows,
      ],
    )

  const activeDebts =
    debts.filter(
      (debt) =>
        debt.status === 'active',
    )

  const activeDebtAmount =
    activeDebts.reduce(
      (
        total,
        debt,
      ) =>
        total
        + Number(
          debt.total_amount,
        ),
      0,
    )

  const activePrizes =
    prizes.filter(
      (prize) =>
        prize.status === 'active',
    )

  const activePrizeValue =
    activePrizes.reduce(
      (
        total,
        prize,
      ) =>
        total
        + Number(
          prize.quantity,
        )
        * Number(
          prize.product.price,
        ),
      0,
    )

  const totalShortageAmount =
    reportRows.reduce(
      (
        total,
        row,
      ) =>
        total
        + row.shortageAmount,
      0,
    )

  const totalSurplusAmount =
    reportRows.reduce(
      (
        total,
        row,
      ) =>
        total
        + row.surplusAmount,
      0,
    )

  const shortageProductCount =
    reportRows.filter(
      (row) =>
        row.difference < 0,
    ).length

  function handleRefresh() {
    setLoadingStatus('loading')
    setErrorMessage('')

    void loadReport()
  }

  function handleDownloadCsv() {
    const filenameDate =
      formatFilenameDate(
        new Date(),
      )

    const filterFilenamePart =
      filterFilenameParts[
        differenceFilter
      ]

    downloadCsv<ReportRow>({
      filename: (
        'cyberclub-report'
        + `_${filterFilenamePart}`
        + `_${filenameDate}.csv`
      ),

      columns: [
        {
          header: 'Товар',

          getValue: (row) =>
            row.productName,
        },
        {
          header: 'Единица',

          getValue: (row) =>
            row.unit,
        },
        {
          header: 'Цена, руб.',

          getValue: (row) =>
            formatCsvNumber(
              row.price,
              2,
            ),
        },
        {
          header: 'По программе',

          getValue: (row) =>
            formatCsvNumber(
              row.programQuantity,
            ),
        },
        {
          header: 'Активные долги',

          getValue: (row) =>
            formatCsvNumber(
              row.debtQuantity,
            ),
        },
        {
          header: 'Неучтённые призы',

          getValue: (row) =>
            formatCsvNumber(
              row.prizeQuantity,
            ),
        },
        {
          header: 'Ожидается',

          getValue: (row) =>
            formatCsvNumber(
              row.expectedQuantity,
            ),
        },
        {
          header: 'Факт',

          getValue: (row) =>
            formatCsvNumber(
              row.actualQuantity,
            ),
        },
        {
          header: 'Разница',

          getValue: (row) =>
            formatCsvNumber(
              row.difference,
            ),
        },
        {
          header:
            'Сумма расхождения, руб.',

          getValue: (row) =>
            formatCsvNumber(
              getDifferenceAmount(
                row,
              ),
              2,
            ),
        },
        {
          header: 'Статус',

          getValue: (row) =>
            getDifferenceStatus(
              row.difference,
            ),
        },
      ],

      rows: filteredRows,
    })
  }

  return (
    <main className="min-h-screen bg-[#070a10] p-6 text-slate-100">
      <div className="mx-auto max-w-[1700px]">
        <header className="flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              to="/"
              className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
            >
              ← Главная панель
            </Link>

            <h1 className="mt-3 text-3xl font-bold text-white">
              Отчёты
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Расхождения, недостачи,
              долги и неучтённые призы
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={
                handleDownloadCsv
              }
              disabled={
                loadingStatus
                !== 'success'
                || filteredRows.length
                === 0
              }
              className="rounded-xl border border-cyan-500/40 bg-cyan-500/10 px-4 py-2.5 text-sm font-medium text-cyan-300 transition hover:border-cyan-400 hover:bg-cyan-500/20 hover:text-cyan-200 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Скачать CSV
            </button>

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
          </div>
        </header>

        {errorMessage && (
          <div className="mt-6 rounded-2xl border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">
            {errorMessage}
          </div>
        )}

        <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <article className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Недостача
            </p>

            <p className="mt-2 text-3xl font-bold text-red-400">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : formatPrice(
                      totalShortageAmount,
                    )}
            </p>

            <p className="mt-2 text-sm text-slate-500">
              {shortageProductCount}
              {' '}
              позиций
            </p>
          </article>

          <article className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Излишки
            </p>

            <p className="mt-2 text-3xl font-bold text-amber-400">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : formatPrice(
                      totalSurplusAmount,
                    )}
            </p>

            <p className="mt-2 text-sm text-slate-500">
              В денежном выражении
            </p>
          </article>

          <article className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Активные долги
            </p>

            <p className="mt-2 text-3xl font-bold text-violet-400">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : formatPrice(
                      activeDebtAmount,
                    )}
            </p>

            <p className="mt-2 text-sm text-slate-500">
              {activeDebts.length}
              {' '}
              записей
            </p>
          </article>

          <article className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Неучтённые призы
            </p>

            <p className="mt-2 text-3xl font-bold text-cyan-400">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : formatPrice(
                      activePrizeValue,
                    )}
            </p>

            <p className="mt-2 text-sm text-slate-500">
              {activePrizes.length}
              {' '}
              записей
            </p>
          </article>

          <article className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Товарных позиций
            </p>

            <p className="mt-2 text-3xl font-bold text-white">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : reportRows.length}
            </p>

            <p className="mt-2 text-sm text-slate-500">
              В текущей ревизии
            </p>
          </article>
        </section>

        <section className="mt-6 rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
          <label
            htmlFor="report-filter"
            className="text-sm font-medium text-slate-300"
          >
            Показать позиции
          </label>

          <select
            id="report-filter"
            value={
              differenceFilter
            }
            onChange={(
              event,
            ) => {
              setDifferenceFilter(
                event.currentTarget
                  .value as DifferenceFilter,
              )
            }}
            className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500 sm:max-w-sm"
          >
            <option value="all">
              Все позиции
            </option>

            <option value="shortage">
              Только недостача
            </option>

            <option value="surplus">
              Только излишки
            </option>

            <option value="matching">
              Только совпадения
            </option>
          </select>

          <p className="mt-3 text-xs text-slate-500">
            В CSV попадут позиции,
            выбранные текущим фильтром.
          </p>
        </section>

        <section className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-[#0b0f17]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[1450px] text-left">
              <thead className="border-b border-slate-800 bg-slate-950/60 text-xs uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-5 py-4">
                    Товар
                  </th>

                  <th className="px-5 py-4">
                    Цена
                  </th>

                  <th className="px-5 py-4">
                    По программе
                  </th>

                  <th className="px-5 py-4">
                    Долги
                  </th>

                  <th className="px-5 py-4">
                    Призы
                  </th>

                  <th className="px-5 py-4">
                    Ожидается
                  </th>

                  <th className="px-5 py-4">
                    Факт
                  </th>

                  <th className="px-5 py-4">
                    Разница
                  </th>

                  <th className="px-5 py-4">
                    Сумма
                  </th>

                  <th className="px-5 py-4">
                    Статус
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {filteredRows.map(
                  (row) => {
                    const differenceAmount =
                      getDifferenceAmount(
                        row,
                      )

                    return (
                      <tr
                        key={
                          row.productId
                        }
                        className="transition hover:bg-slate-900/70"
                      >
                        <td className="px-5 py-4">
                          <p className="font-medium text-white">
                            {row.productName}
                          </p>

                          <p className="mt-1 text-xs text-slate-500">
                            {row.unit}
                          </p>
                        </td>

                        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-300">
                          {formatPrice(
                            row.price,
                          )}
                        </td>

                        <td className="px-5 py-4 text-sm text-slate-300">
                          {formatQuantity(
                            row.programQuantity,
                          )}
                        </td>

                        <td className="px-5 py-4 text-sm text-violet-400">
                          {formatQuantity(
                            row.debtQuantity,
                          )}
                        </td>

                        <td className="px-5 py-4 text-sm text-cyan-400">
                          {formatQuantity(
                            row.prizeQuantity,
                          )}
                        </td>

                        <td className="px-5 py-4 text-sm text-slate-300">
                          {formatQuantity(
                            row.expectedQuantity,
                          )}
                        </td>

                        <td className="px-5 py-4 text-sm font-medium text-white">
                          {formatQuantity(
                            row.actualQuantity,
                          )}
                        </td>

                        <td className="px-5 py-4 text-sm font-semibold">
                          <span
                            className={
                              row.difference < 0
                                ? 'text-red-400'
                                : row.difference > 0
                                  ? 'text-amber-400'
                                  : 'text-emerald-400'
                            }
                          >
                            {row.difference > 0
                              ? '+'
                              : ''}

                            {formatQuantity(
                              row.difference,
                            )}
                          </span>
                        </td>

                        <td className="whitespace-nowrap px-5 py-4 text-sm font-semibold">
                          <span
                            className={
                              row.difference < 0
                                ? 'text-red-400'
                                : row.difference > 0
                                  ? 'text-amber-400'
                                  : 'text-slate-500'
                            }
                          >
                            {row.difference === 0
                              ? '—'
                              : formatPrice(
                                  differenceAmount,
                                )}
                          </span>
                        </td>

                        <td className="px-5 py-4">
                          <span
                            className={[
                              'rounded-full px-3 py-1 text-xs font-medium',

                              getDifferenceClassName(
                                row.difference,
                              ),
                            ].join(' ')}
                          >
                            {getDifferenceStatus(
                              row.difference,
                            )}
                          </span>
                        </td>
                      </tr>
                    )
                  },
                )}

                {loadingStatus
                  === 'success'
                  && filteredRows.length
                  === 0 && (
                    <tr>
                      <td
                        colSpan={10}
                        className="px-6 py-12 text-center text-slate-500"
                      >
                        Подходящих позиций нет
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