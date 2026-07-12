import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import { Link } from 'react-router-dom'

import {
  getInventoryBalances,
  updateInventoryBalance,
} from '../api/client'
import type {
  InventoryBalance,
} from '../types/inventoryBalance'

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

interface BalanceDraft {
  programQuantity: string
  actualQuantity: string
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

export function InventoryPage() {
  const [
    balances,
    setBalances,
  ] = useState<InventoryBalance[]>([])

  const [
    drafts,
    setDrafts,
  ] = useState<
    Record<string, BalanceDraft>
  >({})

  const [
    loadingStatus,
    setLoadingStatus,
  ] = useState<LoadingStatus>(
    'loading',
  )

  const [
    savingProductId,
    setSavingProductId,
  ] = useState<string | null>(null)

  const [
    errorMessage,
    setErrorMessage,
  ] = useState('')

  const [
    successMessage,
    setSuccessMessage,
  ] = useState('')

  const loadBalances =
    useCallback(async () => {
      try {
        const loadedBalances =
          await getInventoryBalances()

        const loadedDrafts =
          Object.fromEntries(
            loadedBalances.map(
              (balance) => [
                balance.product_id,
                {
                  programQuantity:
                    Number(
                      balance.program_quantity,
                    ).toString(),

                  actualQuantity:
                    Number(
                      balance.actual_quantity,
                    ).toString(),
                },
              ],
            ),
          )

        setBalances(loadedBalances)
        setDrafts(loadedDrafts)
        setErrorMessage('')
        setLoadingStatus('success')
      } catch (error) {
        setBalances([])
        setLoadingStatus('error')

        if (error instanceof Error) {
          setErrorMessage(
            error.message,
          )
        } else {
          setErrorMessage(
            'Не удалось загрузить ревизию',
          )
        }
      }
    }, [])

  useEffect(() => {
    const timeoutId =
      window.setTimeout(() => {
        void loadBalances()
      }, 0)

    return () => {
      window.clearTimeout(
        timeoutId,
      )
    }
  }, [loadBalances])

  function handleDraftChange(
    productId: string,
    field: keyof BalanceDraft,
    value: string,
  ) {
    setDrafts(
      (currentDrafts) => ({
        ...currentDrafts,

        [productId]: {
          ...currentDrafts[
            productId
          ],

          [field]: value,
        },
      }),
    )

    setSuccessMessage('')
  }

  async function handleSave(
    balance: InventoryBalance,
  ) {
    const draft =
      drafts[
        balance.product_id
      ]

    if (!draft) {
      return
    }

    const programQuantity =
      Number(
        draft.programQuantity,
      )

    const actualQuantity =
      Number(
        draft.actualQuantity,
      )

    if (
      !Number.isFinite(
        programQuantity,
      )
      || !Number.isFinite(
        actualQuantity,
      )
      || programQuantity < 0
      || actualQuantity < 0
    ) {
      setErrorMessage(
        'Остатки должны быть числами не меньше нуля.',
      )

      return
    }

    setSavingProductId(
      balance.product_id,
    )

    setErrorMessage('')
    setSuccessMessage('')

    try {
      const updatedBalance =
        await updateInventoryBalance(
          balance.product_id,
          {
            program_quantity:
              programQuantity,

            actual_quantity:
              actualQuantity,
          },
        )

      setBalances(
        (currentBalances) =>
          currentBalances.map(
            (currentBalance) =>
              currentBalance.product_id
              === balance.product_id
                ? updatedBalance
                : currentBalance,
          ),
      )

      setDrafts(
        (currentDrafts) => ({
          ...currentDrafts,

          [balance.product_id]: {
            programQuantity:
              Number(
                updatedBalance
                  .program_quantity,
              ).toString(),

            actualQuantity:
              Number(
                updatedBalance
                  .actual_quantity,
              ).toString(),
          },
        }),
      )

      setSuccessMessage(
        `Остатки товара «${balance.product.name}» сохранены.`,
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(
          error.message,
        )
      } else {
        setErrorMessage(
          'Не удалось сохранить остатки',
        )
      }
    } finally {
      setSavingProductId(
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

    void loadBalances()
  }

  const totalLosses =
    balances.reduce(
      (
        total,
        balance,
      ) => {
        const draft =
          drafts[
            balance.product_id
          ]

        const programQuantity =
          Number(
            draft?.programQuantity
            ?? balance.program_quantity,
          )

        const actualQuantity =
          Number(
            draft?.actualQuantity
            ?? balance.actual_quantity,
          )

        const activeDebtQuantity =
          Number(
            balance.active_debt_quantity,
          )

        const activePrizeQuantity =
          Number(
            balance.active_prize_quantity,
          )

        const expectedQuantity =
          programQuantity
          - activeDebtQuantity
          - activePrizeQuantity

        const difference =
          actualQuantity
          - expectedQuantity

        const lossQuantity =
          difference < 0
            ? Math.abs(difference)
            : 0

        return (
          total
          + lossQuantity
          * Number(
            balance.product.price,
          )
        )
      },
      0,
    )

  return (
    <main className="min-h-screen bg-[#070a10] p-6 text-slate-100">
      <div className="mx-auto max-w-[1600px]">
        <header className="flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              to="/"
              className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
            >
              ← Главная панель
            </Link>

            <h1 className="mt-3 text-3xl font-bold text-white">
              Ревизия
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Программный остаток,
              долги, лотерейные призы
              и фактическое количество
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Link
              to="/inventory/import"
              className="rounded-xl bg-cyan-500 px-4 py-2.5 text-center text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
            >
              Импорт из LightShell
            </Link>

            <button
              type="button"
              onClick={handleRefresh}
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

        <section className="mt-6 grid gap-4 sm:grid-cols-2">
          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Товаров в ревизии
            </p>

            <p className="mt-2 text-3xl font-bold text-white">
              {loadingStatus
                === 'loading'
                ? '...'
                : balances.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Необъяснённые потери
            </p>

            <p className="mt-2 text-3xl font-bold text-red-400">
              {loadingStatus
                === 'loading'
                ? '...'
                : formatPrice(
                    totalLosses,
                  )}
            </p>
          </div>
        </section>

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

        <section className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-[#0b0f17]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[1550px] text-left">
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
                    Лотерейки
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
                    Потери
                  </th>

                  <th className="px-5 py-4 text-right">
                    Действия
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {balances.map(
                  (balance) => {
                    const draft =
                      drafts[
                        balance.product_id
                      ]

                    const programQuantity =
                      Number(
                        draft?.programQuantity
                        ?? balance
                          .program_quantity,
                      )

                    const actualQuantity =
                      Number(
                        draft?.actualQuantity
                        ?? balance
                          .actual_quantity,
                      )

                    const activeDebtQuantity =
                      Number(
                        balance
                          .active_debt_quantity,
                      )

                    const activePrizeQuantity =
                      Number(
                        balance
                          .active_prize_quantity,
                      )

                    const expectedQuantity =
                      programQuantity
                      - activeDebtQuantity
                      - activePrizeQuantity

                    const difference =
                      actualQuantity
                      - expectedQuantity

                    const losses =
                      difference < 0
                        ? (
                            Math.abs(
                              difference,
                            )
                            * Number(
                                balance
                                  .product
                                  .price,
                              )
                          )
                        : 0

                    const isSaving =
                      savingProductId
                      === balance.product_id

                    return (
                      <tr
                        key={balance.id}
                        className="transition hover:bg-slate-900/70"
                      >
                        <td className="px-5 py-4">
                          <p className="font-medium text-white">
                            {
                              balance
                                .product
                                .name
                            }
                          </p>

                          <p className="mt-1 text-xs text-slate-500">
                            {
                              balance
                                .product
                                .unit
                            }
                          </p>
                        </td>

                        <td className="px-5 py-4 text-slate-300">
                          {formatPrice(
                            Number(
                              balance
                                .product
                                .price,
                            ),
                          )}
                        </td>

                        <td className="px-5 py-4">
                          <input
                            type="number"
                            min="0"
                            step="0.001"
                            value={
                              draft
                                ?.programQuantity
                              ?? ''
                            }
                            onChange={(
                              event,
                            ) => {
                              handleDraftChange(
                                balance
                                  .product_id,
                                'programQuantity',
                                event
                                  .currentTarget
                                  .value,
                              )
                            }}
                            className="w-28 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none transition focus:border-cyan-500"
                          />
                        </td>

                        <td className="px-5 py-4 font-medium text-amber-400">
                          {activeDebtQuantity > 0
                            ? (
                                `−${formatQuantity(
                                  activeDebtQuantity,
                                )}`
                              )
                            : '—'}
                        </td>

                        <td className="px-5 py-4 font-medium text-violet-400">
                          {activePrizeQuantity > 0
                            ? (
                                `−${formatQuantity(
                                  activePrizeQuantity,
                                )}`
                              )
                            : '—'}
                        </td>

                        <td className="px-5 py-4 font-medium text-cyan-300">
                          {formatQuantity(
                            expectedQuantity,
                          )}
                        </td>

                        <td className="px-5 py-4">
                          <input
                            type="number"
                            min="0"
                            step="0.001"
                            value={
                              draft
                                ?.actualQuantity
                              ?? ''
                            }
                            onChange={(
                              event,
                            ) => {
                              handleDraftChange(
                                balance
                                  .product_id,
                                'actualQuantity',
                                event
                                  .currentTarget
                                  .value,
                              )
                            }}
                            className="w-28 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none transition focus:border-cyan-500"
                          />
                        </td>

                        <td
                          className={
                            difference < 0
                              ? (
                                  'px-5 py-4 '
                                  + 'font-semibold '
                                  + 'text-red-400'
                                )
                              : difference > 0
                                ? (
                                    'px-5 py-4 '
                                    + 'font-semibold '
                                    + 'text-emerald-400'
                                  )
                                : (
                                    'px-5 py-4 '
                                    + 'text-slate-400'
                                  )
                          }
                        >
                          {difference > 0
                            ? '+'
                            : ''}

                          {formatQuantity(
                            difference,
                          )}
                        </td>

                        <td className="px-5 py-4 font-medium text-red-400">
                          {losses > 0
                            ? formatPrice(
                                losses,
                              )
                            : '—'}
                        </td>

                        <td className="px-5 py-4 text-right">
                          <button
                            type="button"
                            onClick={() => {
                              void handleSave(
                                balance,
                              )
                            }}
                            disabled={isSaving}
                            className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            {isSaving
                              ? 'Сохранение...'
                              : 'Сохранить'}
                          </button>
                        </td>
                      </tr>
                    )
                  },
                )}

                {loadingStatus
                  === 'success'
                  && balances.length
                  === 0 && (
                    <tr>
                      <td
                        colSpan={10}
                        className="px-6 py-12 text-center text-slate-500"
                      >
                        Активных товаров пока нет
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