import {
  useCallback,
  useEffect,
  useState,
} from 'react'

import {
  getDatabaseHealth,
  getProducts,
  type DatabaseHealth,
} from './api/client'

import type { Product } from './types/product'


const navigationItems = [
  { name: 'Главная', active: true },
  { name: 'Ревизия', active: false },
  { name: 'Долги', active: false },
  { name: 'Лотерейки', active: false },
  { name: 'Смены', active: false },
  { name: 'Отчёты', active: false },
  { name: 'Журнал', active: false },
  { name: 'Настройки', active: false },
]


type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'


function App() {
  const [databaseHealth, setDatabaseHealth] =
    useState<DatabaseHealth | null>(null)

  const [products, setProducts] =
    useState<Product[]>([])

  const [loadingStatus, setLoadingStatus] =
    useState<LoadingStatus>('loading')

  const [errorMessage, setErrorMessage] =
    useState('')


  const loadDashboard = useCallback(async () => {
    setLoadingStatus('loading')
    setErrorMessage('')

    try {
      const [
        databaseResponse,
        productsResponse,
      ] = await Promise.all([
        getDatabaseHealth(),
        getProducts(),
      ])

      setDatabaseHealth(databaseResponse)
      setProducts(productsResponse)
      setLoadingStatus('success')
    } catch (error) {
      setDatabaseHealth(null)
      setProducts([])
      setLoadingStatus('error')

      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось подключиться к backend',
        )
      }
    }
  }, [])


  useEffect(() => {
    void loadDashboard()
  }, [loadDashboard])


  const databaseIsConnected =
    loadingStatus === 'success'
    && databaseHealth?.status === 'ok'


  const databaseStatusText = (() => {
    if (loadingStatus === 'loading') {
      return 'Проверка подключения...'
    }

    if (databaseIsConnected) {
      return 'Подключение активно'
    }

    return 'Нет подключения'
  })()


  const dashboardCards = [
    {
      title: 'Активные товары',
      value:
        loadingStatus === 'loading'
          ? '...'
          : String(products.length),
      description: 'Товары в PostgreSQL',
    },
    {
      title: 'Активные долги',
      value: '0 ₽',
      description: 'Модуль в разработке',
    },
    {
      title: 'Лотерейки',
      value: '0 ₽',
      description: 'Модуль в разработке',
    },
    {
      title: 'Недостача',
      value: '0 ₽',
      description: 'Модуль в разработке',
    },
  ]


  const recentActions = [
    {
      action: databaseIsConnected
        ? 'Frontend подключён к FastAPI'
        : 'Ожидание подключения к FastAPI',
      user: 'System',
      date: 'Сегодня',
      status: databaseIsConnected
        ? 'Готово'
        : 'Проверка',
    },
    {
      action: `Загружено товаров: ${products.length}`,
      user: 'PostgreSQL',
      date: 'Сегодня',
      status: databaseIsConnected
        ? 'Готово'
        : 'Ожидание',
    },
    {
      action: 'Настроены автоматические тесты',
      user: 'GitHub Actions',
      date: 'Сегодня',
      status: 'Готово',
    },
  ]


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
            {navigationItems.map((item) => (
              <button
                key={item.name}
                type="button"
                className={[
                  'w-full rounded-xl px-4 py-3 text-left text-sm font-medium transition',
                  item.active
                    ? 'bg-cyan-500/15 text-cyan-300 ring-1 ring-cyan-400/30'
                    : 'text-slate-400 hover:bg-slate-800/70 hover:text-white',
                ].join(' ')}
              >
                {item.name}
              </button>
            ))}
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
                    loadingStatus === 'loading'
                      ? 'animate-pulse bg-amber-400'
                      : databaseIsConnected
                        ? 'bg-emerald-400'
                        : 'bg-red-400',
                  ].join(' ')}
                />

                <span className="text-xs text-slate-400">
                  {databaseStatusText}
                </span>
              </div>

              {databaseHealth && (
                <p className="mt-2 truncate text-xs text-slate-600">
                  {databaseHealth.database}
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

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => {
                  void loadDashboard()
                }}
                disabled={loadingStatus === 'loading'}
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:text-white disabled:cursor-wait disabled:opacity-50"
              >
                {loadingStatus === 'loading'
                  ? 'Загрузка...'
                  : 'Обновить'}
              </button>

              <button
                type="button"
                className="rounded-xl bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
              >
                Открыть смену
              </button>
            </div>
          </header>

          <div className="space-y-8 p-8">
            {loadingStatus === 'error' && (
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
              {dashboardCards.map((card) => (
                <article
                  key={card.title}
                  className="rounded-2xl border border-slate-800 bg-[#0d131d] p-5 shadow-lg shadow-black/10"
                >
                  <p className="text-sm font-medium text-slate-400">
                    {card.title}
                  </p>

                  <p className="mt-4 text-3xl font-bold text-white">
                    {card.value}
                  </p>

                  <p className="mt-2 text-sm text-slate-500">
                    {card.description}
                  </p>
                </article>
              ))}
            </section>

            <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
              <article className="overflow-hidden rounded-2xl border border-slate-800 bg-[#0d131d]">
                <div className="flex items-center justify-between border-b border-slate-800 px-6 py-5">
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      Последние действия
                    </h3>

                    <p className="mt-1 text-sm text-slate-500">
                      Состояние модулей системы
                    </p>
                  </div>

                  <button
                    type="button"
                    className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
                  >
                    Открыть журнал
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                      <tr>
                        <th className="px-6 py-4 font-semibold">
                          Действие
                        </th>

                        <th className="px-6 py-4 font-semibold">
                          Источник
                        </th>

                        <th className="px-6 py-4 font-semibold">
                          Дата
                        </th>

                        <th className="px-6 py-4 font-semibold">
                          Статус
                        </th>
                      </tr>
                    </thead>

                    <tbody className="divide-y divide-slate-800">
                      {recentActions.map((item) => (
                        <tr
                          key={item.action}
                          className="transition hover:bg-slate-800/30"
                        >
                          <td className="px-6 py-4 text-sm font-medium text-slate-200">
                            {item.action}
                          </td>

                          <td className="px-6 py-4 text-sm text-slate-400">
                            {item.user}
                          </td>

                          <td className="px-6 py-4 text-sm text-slate-400">
                            {item.date}
                          </td>

                          <td className="px-6 py-4">
                            <span
                              className={[
                                'rounded-full px-3 py-1 text-xs font-semibold',
                                item.status === 'Готово'
                                  ? 'bg-emerald-500/10 text-emerald-400'
                                  : 'bg-amber-500/10 text-amber-400',
                              ].join(' ')}
                            >
                              {item.status}
                            </span>
                          </td>
                        </tr>
                      ))}
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
                  {[
                    'Добавить товар',
                    'Добавить долг',
                    'Выдать приз',
                    'Открыть ревизию',
                  ].map((action) => (
                    <button
                      key={action}
                      type="button"
                      className="w-full rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-left text-sm font-medium text-slate-300 transition hover:border-cyan-500/40 hover:bg-cyan-500/10 hover:text-cyan-300"
                    >
                      {action}
                    </button>
                  ))}
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