import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import { Link } from 'react-router-dom'

import {
  getActionLogs,
  getDatabaseHealth,
  getDebts,
  getInventoryBalances,
  getPrizes,
  getProducts,
  type DatabaseHealth,
} from './api/client'

import type { ActionLog } from './types/actionLog'
import type { Debt } from './types/debt'
import type {
  InventoryBalance,
} from './types/inventoryBalance'
import type { Prize } from './types/prize'
import type { Product } from './types/product'

const navigationItems = [
  {
    name: 'Главная',
    path: '/',
    active: true,
  },
  {
    name: 'Товары',
    path: '/products',
    active: false,
  },
  {
    name: 'Ревизия',
    path: '/inventory',
    active: false,
  },
  {
    name: 'Сотрудники',
    path: '/employees',
    active: false,
  },
  {
    name: 'Долги',
    path: '/debts',
    active: false,
  },
  {
    name: 'Лотерейки',
    path: '/prizes',
    active: false,
  },
  {
    name: 'Смены',
    path: null,
    active: false,
  },
  {
  name: 'Отчёты',
  path: '/reports',
  active: false,
  },
  {
    name: 'Журнал',
    path: '/action-logs',
    active: false,
  },
  {
    name: 'Настройки',
    path: null,
    active: false,
  },
] as const

const quickActions = [
  {
    name: 'Добавить товар',
    path: '/products/new',
  },
  {
    name: 'Добавить долг',
    path: '/debts',
  },
  {
    name: 'Выдать приз',
    path: '/prizes',
  },
  {
    name: 'Открыть ревизию',
    path: '/inventory',
  },
] as const

const entityLabels: Record<string, string> = {
  product: 'Товары',
  employee: 'Сотрудники',
  debt: 'Долги',
  prize: 'Лотерейки',
  inventory_balance: 'Ревизия',
  lightshell_import: 'LightShell',
}

const eventLabels: Record<string, string> = {
  product_created: 'Товар добавлен',
  product_updated: 'Товар изменён',
  product_archived: 'Товар архивирован',
  product_restored: 'Товар восстановлен',

  employee_created: 'Сотрудник добавлен',
  employee_updated: 'Сотрудник изменён',
  employee_archived: 'Сотрудник архивирован',
  employee_restored: 'Сотрудник восстановлен',

  debt_created: 'Долг добавлен',
  debt_updated: 'Долг изменён',
  debt_paid: 'Долг погашен',

  prize_created: 'Приз выдан',
  prize_updated: 'Приз изменён',
  prize_reflected: 'Приз учтён',

  inventory_balance_updated: 'Остатки изменены',

  lightshell_import_applied: 'Импорт LightShell',
}

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

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

function App() {
  const [
    databaseHealth,
    setDatabaseHealth,
  ] = useState<DatabaseHealth | null>(
    null,
  )

  const [
    products,
    setProducts,
  ] = useState<Product[]>([])

  const [
    debts,
    setDebts,
  ] = useState<Debt[]>([])

  const [
    prizes,
    setPrizes,
  ] = useState<Prize[]>([])

  const [
    balances,
    setBalances,
  ] = useState<InventoryBalance[]>([])

  const [
    actionLogs,
    setActionLogs,
  ] = useState<ActionLog[]>([])

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

  const loadDashboard =
    useCallback(async () => {
      try {
        const [
          databaseResponse,
          productsResponse,
          debtsResponse,
          prizesResponse,
          balancesResponse,
          actionLogsResponse,
        ] = await Promise.all([
          getDatabaseHealth(),
          getProducts(),
          getDebts(),
          getPrizes(),
          getInventoryBalances(),
          getActionLogs({
            limit: 5,
          }),
        ])

        setDatabaseHealth(
          databaseResponse,
        )

        setProducts(
          productsResponse,
        )

        setDebts(
          debtsResponse,
        )

        setPrizes(
          prizesResponse,
        )

        setBalances(
          balancesResponse,
        )

        setActionLogs(
          actionLogsResponse,
        )

        setErrorMessage('')

        setLoadingStatus(
          'success',
        )
      } catch (error) {
        setDatabaseHealth(null)
        setProducts([])
        setDebts([])
        setPrizes([])
        setBalances([])
        setActionLogs([])

        setLoadingStatus(
          'error',
        )

        if (error instanceof Error) {
          setErrorMessage(
            error.message,
          )
        } else {
          setErrorMessage(
            'Не удалось подключиться к backend',
          )
        }
      }
    }, [])

  useEffect(() => {
    const timeoutId =
      window.setTimeout(() => {
        void loadDashboard()
      }, 0)

    return () => {
      window.clearTimeout(
        timeoutId,
      )
    }
  }, [loadDashboard])

  const databaseIsConnected =
    loadingStatus === 'success'
    && databaseHealth?.status === 'ok'

  const databaseStatusText = (() => {
    if (
      loadingStatus === 'loading'
    ) {
      return 'Проверка подключения...'
    }

    if (databaseIsConnected) {
      return 'Подключение активно'
    }

    return 'Нет подключения'
  })()

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

  const activePrizeQuantity =
    activePrizes.reduce(
      (
        total,
        prize,
      ) =>
        total
        + Number(
          prize.quantity,
        ),
      0,
    )

  const unexplainedLosses =
    balances.reduce(
      (
        total,
        balance,
      ) => {
        const programQuantity =
          Number(
            balance.program_quantity,
          )

        const actualQuantity =
          Number(
            balance.actual_quantity,
          )

        const activeDebtQuantity =
          Number(
            balance.active_debt_quantity,
          )

        const activePrizeQuantityForProduct =
          Number(
            balance.active_prize_quantity,
          )

        const expectedQuantity =
          programQuantity
          - activeDebtQuantity
          - activePrizeQuantityForProduct

        const difference =
          actualQuantity
          - expectedQuantity

        const missingQuantity =
          difference < 0
            ? Math.abs(
                difference,
              )
            : 0

        return (
          total
          + missingQuantity
          * Number(
            balance.product.price,
          )
        )
      },
      0,
    )

  const dashboardCards = [
    {
      title: 'Активные товары',

      value:
        loadingStatus === 'loading'
          ? '...'
          : String(
              products.length,
            ),

      description:
        'Товары в PostgreSQL',
    },
    {
      title: 'Активные долги',

      value:
        loadingStatus === 'loading'
          ? '...'
          : formatPrice(
              activeDebtAmount,
            ),

      description:
        `${activeDebts.length} активных записей`,
    },
    {
      title: 'Лотерейки',

      value:
        loadingStatus === 'loading'
          ? '...'
          : formatQuantity(
              activePrizeQuantity,
            ),

      description:
        `${activePrizes.length} не учтено в LightShell`,
    },
    {
      title: 'Недостача',

      value:
        loadingStatus === 'loading'
          ? '...'
          : formatPrice(
              unexplainedLosses,
            ),

      description:
        'После учёта долгов и призов',
    },
  ]

  function handleRefresh() {
    setLoadingStatus(
      'loading',
    )

    setErrorMessage('')

    void loadDashboard()
  }

  return (
    <div className="min-h-screen bg-[#070a10] text-slate-100">
      <div className="flex min-h-screen">
        <aside className="flex w-64 shrink-0 flex-col border-r border-slate-800 bg-[#0b1018]">
          <div className="border-b border-slate-800 px-6 py-6">
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
              CyberClub
            </p>

            <h1 className="mt-2 text-xl font-bold text-white">
              Manager Pro
            </h1>

            <p className="mt-1 text-sm text-slate-500">
              Control Center
            </p>
          </div>

          <nav className="flex-1 space-y-2 px-4 py-6">
            {navigationItems.map(
              (item) => {
                const className = [
                  'block w-full rounded-xl px-4 py-3 text-left text-sm font-medium transition',

                  item.active
                    ? (
                        'bg-cyan-500/15 '
                        + 'text-cyan-300 '
                        + 'ring-1 '
                        + 'ring-cyan-400/30'
                      )
                    : (
                        'text-slate-400 '
                        + 'hover:bg-slate-800/70 '
                        + 'hover:text-white'
                      ),

                  item.path
                    ? ''
                    : (
                        'cursor-not-allowed '
                        + 'opacity-40'
                      ),
                ].join(' ')

                if (item.path) {
                  return (
                    <Link
                      key={
                        item.name
                      }
                      to={
                        item.path
                      }
                      className={
                        className
                      }
                    >
                      {item.name}
                    </Link>
                  )
                }

                return (
                  <button
                    key={
                      item.name
                    }
                    type="button"
                    disabled
                    className={
                      className
                    }
                  >
                    {item.name}
                  </button>
                )
              },
            )}
          </nav>

          <div className="border-t border-slate-800 p-4">
            <div className="rounded-xl bg-slate-900/80 p-4">
              <p className="text-sm font-semibold text-white">
                PostgreSQL
              </p>

              <div className="mt-2 flex items-center gap-2">
                <span
                  className={[
                    'h-2.5 w-2.5 rounded-full',

                    loadingStatus
                    === 'loading'
                      ? (
                          'animate-pulse '
                          + 'bg-amber-400'
                        )
                      : databaseIsConnected
                        ? 'bg-emerald-400'
                        : 'bg-red-400',
                  ].join(' ')}
                />

                <span className="text-xs text-slate-400">
                  {
                    databaseStatusText
                  }
                </span>
              </div>

              {databaseHealth && (
                <p className="mt-2 truncate text-xs text-slate-600">
                  {
                    databaseHealth
                      .database
                  }
                </p>
              )}
            </div>
          </div>
        </aside>

        <main className="min-w-0 flex-1">
          <header className="flex items-center justify-between border-b border-slate-800 bg-[#090d14] px-8 py-5">
            <div>
              <h2 className="text-2xl font-bold text-white">
                Главная панель
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Состояние компьютерного клуба
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
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:text-white disabled:cursor-wait disabled:opacity-50"
            >
              {loadingStatus
                === 'loading'
                  ? 'Загрузка...'
                  : 'Обновить'}
            </button>
          </header>

          <div className="space-y-8 p-8">
            {loadingStatus
              === 'error' && (
                <div className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4">
                  <p className="font-semibold text-red-300">
                    Backend недоступен
                  </p>

                  <p className="mt-1 text-sm text-red-300/70">
                    {errorMessage}
                  </p>
                </div>
              )}

            <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
              {dashboardCards.map(
                (card) => (
                  <article
                    key={
                      card.title
                    }
                    className="rounded-2xl border border-slate-800 bg-[#0d131d] p-5 shadow-lg shadow-black/10"
                  >
                    <p className="text-sm font-medium text-slate-400">
                      {card.title}
                    </p>

                    <p className="mt-4 text-3xl font-bold text-white">
                      {card.value}
                    </p>

                    <p className="mt-2 text-sm text-slate-500">
                      {
                        card.description
                      }
                    </p>
                  </article>
                ),
              )}
            </section>

            <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
              <article className="overflow-hidden rounded-2xl border border-slate-800 bg-[#0d131d]">
                <div className="flex items-center justify-between border-b border-slate-800 px-6 py-5">
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      Последние действия
                    </h3>

                    <p className="mt-1 text-sm text-slate-500">
                      Последние записи из журнала
                    </p>
                  </div>

                  <Link
                    to="/action-logs"
                    className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
                  >
                    Открыть журнал
                  </Link>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                      <tr>
                        <th className="px-6 py-4 font-semibold">
                          Действие
                        </th>

                        <th className="px-6 py-4 font-semibold">
                          Модуль
                        </th>

                        <th className="px-6 py-4 font-semibold">
                          Дата
                        </th>

                        <th className="px-6 py-4 font-semibold">
                          Тип
                        </th>
                      </tr>
                    </thead>

                    <tbody className="divide-y divide-slate-800">
                      {loadingStatus
                        === 'loading' && (
                          <tr>
                            <td
                              colSpan={4}
                              className="px-6 py-10 text-center text-sm text-slate-500"
                            >
                              Загрузка последних действий...
                            </td>
                          </tr>
                        )}

                      {loadingStatus
                        !== 'loading'
                        && actionLogs.map(
                          (actionLog) => (
                            <tr
                              key={
                                actionLog.id
                              }
                              className="transition hover:bg-slate-800/30"
                            >
                              <td className="px-6 py-4 text-sm font-medium text-slate-200">
                                {
                                  actionLog.message
                                }
                              </td>

                              <td className="px-6 py-4 text-sm text-slate-400">
                                {
                                  entityLabels[
                                    actionLog.entity_type
                                  ]
                                  ?? actionLog.entity_type
                                }
                              </td>

                              <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-400">
                                {
                                  formatDate(
                                    actionLog.created_at,
                                  )
                                }
                              </td>

                              <td className="px-6 py-4">
                                <span className="rounded-full bg-violet-500/10 px-3 py-1 text-xs font-semibold text-violet-400">
                                  {
                                    eventLabels[
                                      actionLog.event_type
                                    ]
                                    ?? actionLog.event_type
                                  }
                                </span>
                              </td>
                            </tr>
                          ),
                        )}

                      {loadingStatus
                        === 'success'
                        && actionLogs.length
                        === 0 && (
                          <tr>
                            <td
                              colSpan={4}
                              className="px-6 py-10 text-center text-sm text-slate-500"
                            >
                              Действий пока нет
                            </td>
                          </tr>
                        )}
                    </tbody>
                  </table>
                </div>
              </article>

              <article className="rounded-2xl border border-slate-800 bg-[#0d131d] p-6">
                <h3 className="text-lg font-semibold text-white">
                  Быстрые действия
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Основные операции
                </p>

                <div className="mt-6 space-y-3">
                  {quickActions.map(
                    (action) => (
                      <Link
                        key={
                          action.name
                        }
                        to={
                          action.path
                        }
                        className="block w-full rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-left text-sm font-medium text-slate-300 transition hover:border-cyan-500/40 hover:bg-cyan-500/10 hover:text-cyan-300"
                      >
                        {
                          action.name
                        }
                      </Link>
                    ),
                  )}
                </div>
              </article>
            </section>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App