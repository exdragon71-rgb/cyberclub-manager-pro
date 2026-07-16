import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import { Link } from 'react-router-dom'

import {
  getActionLogs,
} from '../api/client'
import type {
  ActionLog,
} from '../types/actionLog'

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

type EntityFilter =
  | 'all'
  | 'product'
  | 'employee'
  | 'debt'
  | 'prize'
  | 'inventory_balance'
  | 'club_setting'
  | 'lightshell_import'

type EventFilter =
  | 'all'
  | 'product_created'
  | 'product_updated'
  | 'product_archived'
  | 'product_restored'
  | 'employee_created'
  | 'employee_updated'
  | 'employee_archived'
  | 'employee_restored'
  | 'debt_created'
  | 'debt_updated'
  | 'debt_paid'
  | 'prize_created'
  | 'prize_updated'
  | 'prize_reflected'
  | 'inventory_balance_updated'
  | 'club_setting_updated'
  | 'lightshell_import_applied'

const entityLabels: Record<string, string> = {
  product: 'Товары',
  employee: 'Сотрудники',
  debt: 'Долги',
  prize: 'Лотерейки',
  inventory_balance: 'Ревизия',
  club_setting: 'Настройки',
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
  prize_reflected: 'Приз учтён в LightShell',

  inventory_balance_updated: 'Остатки изменены',

  club_setting_updated: 'Настройки изменены',

  lightshell_import_applied: 'Импорт LightShell',
}

function formatDate(
  value: string,
) {
  return new Date(value).toLocaleString(
    'ru-RU',
    {
      dateStyle: 'short',
      timeStyle: 'medium',
    },
  )
}

function formatDetails(
  details: Record<string, unknown>,
) {
  return JSON.stringify(
    details,
    null,
    2,
  )
}

export function ActionLogsPage() {
  const [
    actionLogs,
    setActionLogs,
  ] = useState<ActionLog[]>([])

  const [
    entityFilter,
    setEntityFilter,
  ] = useState<EntityFilter>('all')

  const [
    eventFilter,
    setEventFilter,
  ] = useState<EventFilter>('all')

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

  const loadActionLogs =
    useCallback(async () => {
      try {
        const loadedActionLogs =
          await getActionLogs({
            entity_type:
              entityFilter === 'all'
                ? undefined
                : entityFilter,

            event_type:
              eventFilter === 'all'
                ? undefined
                : eventFilter,

            limit: 200,
          })

        setActionLogs(
          loadedActionLogs,
        )

        setErrorMessage('')

        setLoadingStatus(
          'success',
        )
      } catch (error) {
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
            'Не удалось загрузить журнал действий.',
          )
        }
      }
    }, [
      entityFilter,
      eventFilter,
    ])

  useEffect(() => {
    const timeoutId =
      window.setTimeout(() => {
        void loadActionLogs()
      }, 0)

    return () => {
      window.clearTimeout(
        timeoutId,
      )
    }
  }, [loadActionLogs])

  function handleRefresh() {
    setLoadingStatus(
      'loading',
    )

    setErrorMessage('')

    void loadActionLogs()
  }

  const today = new Date()

  const todayActionCount =
    actionLogs.filter(
      (actionLog) => {
        const actionDate =
          new Date(
            actionLog.created_at,
          )

        return (
          actionDate.getFullYear()
          === today.getFullYear()
          && actionDate.getMonth()
          === today.getMonth()
          && actionDate.getDate()
          === today.getDate()
        )
      },
    ).length

  const moduleCount =
    new Set(
      actionLogs.map(
        (actionLog) =>
          actionLog.entity_type,
      ),
    ).size

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
              Журнал действий
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              История изменений товаров,
              сотрудников, долгов,
              лотереек, ревизии
              и настроек клуба
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

        <section className="mt-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Загружено записей
            </p>

            <p className="mt-2 text-3xl font-bold text-white">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : actionLogs.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Действий сегодня
            </p>

            <p className="mt-2 text-3xl font-bold text-cyan-400">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : todayActionCount}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Затронуто модулей
            </p>

            <p className="mt-2 text-3xl font-bold text-violet-400">
              {loadingStatus
                === 'loading'
                  ? '...'
                  : moduleCount}
            </p>
          </div>
        </section>

        <section className="mt-6 rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label
                htmlFor="action-log-entity"
                className="text-sm font-medium text-slate-300"
              >
                Модуль
              </label>

              <select
                id="action-log-entity"
                value={
                  entityFilter
                }
                onChange={(
                  event,
                ) => {
                  setEntityFilter(
                    event.currentTarget
                      .value as EntityFilter,
                  )
                }}
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              >
                <option value="all">
                  Все модули
                </option>

                <option value="product">
                  Товары
                </option>

                <option value="employee">
                  Сотрудники
                </option>

                <option value="debt">
                  Долги
                </option>

                <option value="prize">
                  Лотерейки
                </option>

                <option value="inventory_balance">
                  Ревизия
                </option>

                <option value="club_setting">
                  Настройки
                </option>

                <option value="lightshell_import">
                  Импорт LightShell
                </option>
              </select>
            </div>

            <div>
              <label
                htmlFor="action-log-event"
                className="text-sm font-medium text-slate-300"
              >
                Тип действия
              </label>

              <select
                id="action-log-event"
                value={
                  eventFilter
                }
                onChange={(
                  event,
                ) => {
                  setEventFilter(
                    event.currentTarget
                      .value as EventFilter,
                  )
                }}
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              >
                <option value="all">
                  Все действия
                </option>

                {Object.entries(
                  eventLabels,
                ).map(
                  ([
                    eventType,
                    label,
                  ]) => (
                    <option
                      key={
                        eventType
                      }
                      value={
                        eventType
                      }
                    >
                      {label}
                    </option>
                  ),
                )}
              </select>
            </div>
          </div>
        </section>

        {errorMessage && (
          <div className="mt-6 rounded-2xl border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">
            {errorMessage}
          </div>
        )}

        <section className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-[#0b0f17]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[1200px] text-left">
              <thead className="border-b border-slate-800 bg-slate-950/60 text-xs uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-6 py-4">
                    Дата
                  </th>

                  <th className="px-6 py-4">
                    Модуль
                  </th>

                  <th className="px-6 py-4">
                    Действие
                  </th>

                  <th className="px-6 py-4">
                    Описание
                  </th>

                  <th className="px-6 py-4">
                    Подробности
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {actionLogs.map(
                  (actionLog) => (
                    <tr
                      key={
                        actionLog.id
                      }
                      className="align-top transition hover:bg-slate-900/70"
                    >
                      <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-400">
                        {formatDate(
                          actionLog.created_at,
                        )}
                      </td>

                      <td className="px-6 py-4">
                        <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-400">
                          {entityLabels[
                            actionLog.entity_type
                          ]
                            ?? actionLog.entity_type}
                        </span>
                      </td>

                      <td className="px-6 py-4 text-sm font-medium text-slate-300">
                        {eventLabels[
                          actionLog.event_type
                        ]
                          ?? actionLog.event_type}
                      </td>

                      <td className="max-w-md px-6 py-4 text-sm text-white">
                        {actionLog.message}
                      </td>

                      <td className="px-6 py-4">
                        <details>
                          <summary className="cursor-pointer text-sm font-medium text-violet-400 transition hover:text-violet-300">
                            Показать данные
                          </summary>

                          <pre className="mt-3 max-h-72 max-w-xl overflow-auto rounded-xl border border-slate-800 bg-slate-950 p-4 text-xs leading-5 text-slate-400">
                            {formatDetails(
                              actionLog.details,
                            )}
                          </pre>
                        </details>
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
                        colSpan={5}
                        className="px-6 py-12 text-center text-slate-500"
                      >
                        Подходящих записей пока нет
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