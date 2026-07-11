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

const dashboardCards = [
  {
    title: 'Активные долги',
    value: '0 ₽',
    description: 'Долги сотрудников',
  },
  {
    title: 'Лотерейки',
    value: '0 ₽',
    description: 'Ожидают списания',
  },
  {
    title: 'Недостача',
    value: '0 ₽',
    description: 'По текущей ревизии',
  },
  {
    title: 'Активная смена',
    value: 'Нет',
    description: 'Смена не открыта',
  },
]

const recentActions = [
  {
    action: 'Backend подключён к PostgreSQL',
    user: 'System',
    date: 'Сегодня',
    status: 'Готово',
  },
  {
    action: 'Создан модуль товаров',
    user: 'System',
    date: 'Сегодня',
    status: 'Готово',
  },
  {
    action: 'Настроены автоматические тесты',
    user: 'GitHub Actions',
    date: 'Сегодня',
    status: 'Готово',
  },
]

function App() {
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
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />

                <span className="text-xs text-slate-400">
                  Подключение активно
                </span>
              </div>
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
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:text-white"
              >
                Обновить
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
                      История изменений системы
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
                          Пользователь
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
                            <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400">
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