import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from 'react'
import { Link } from 'react-router-dom'

import {
  archiveEmployee,
  createEmployee,
  getEmployees,
  restoreEmployee,
  updateEmployee,
} from '../api/client'
import type { Employee } from '../types/employee'

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

export function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loadingStatus, setLoadingStatus] =
    useState<LoadingStatus>('loading')

  const [newEmployeeName, setNewEmployeeName] =
    useState('')
  const [editingEmployeeId, setEditingEmployeeId] =
    useState<string | null>(null)
  const [editingName, setEditingName] =
    useState('')
  const [actionEmployeeId, setActionEmployeeId] =
    useState<string | null>(null)

  const [isCreating, setIsCreating] =
    useState(false)
  const [errorMessage, setErrorMessage] =
    useState('')
  const [successMessage, setSuccessMessage] =
    useState('')

  const loadEmployees = useCallback(async () => {
    try {
      const loadedEmployees = await getEmployees(true)

      setEmployees(loadedEmployees)
      setErrorMessage('')
      setLoadingStatus('success')
    } catch (error) {
      setEmployees([])
      setLoadingStatus('error')

      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось загрузить сотрудников',
        )
      }
    }
  }, [])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadEmployees()
    }, 0)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [loadEmployees])

  async function handleCreate(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const normalizedName =
      newEmployeeName.trim()

    if (!normalizedName) {
      setErrorMessage(
        'Введите имя сотрудника.',
      )
      return
    }

    setIsCreating(true)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const createdEmployee =
        await createEmployee({
          name: normalizedName,
        })

      setEmployees((currentEmployees) =>
        [...currentEmployees, createdEmployee].sort(
          (firstEmployee, secondEmployee) =>
            firstEmployee.name.localeCompare(
              secondEmployee.name,
              'ru',
            ),
        ),
      )

      setNewEmployeeName('')
      setSuccessMessage(
        `Сотрудник «${createdEmployee.name}» добавлен.`,
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось добавить сотрудника',
        )
      }
    } finally {
      setIsCreating(false)
    }
  }

  function startEditing(employee: Employee) {
    setEditingEmployeeId(employee.id)
    setEditingName(employee.name)
    setErrorMessage('')
    setSuccessMessage('')
  }

  function cancelEditing() {
    setEditingEmployeeId(null)
    setEditingName('')
  }

  async function handleUpdate(
    employee: Employee,
  ) {
    const normalizedName = editingName.trim()

    if (!normalizedName) {
      setErrorMessage(
        'Имя сотрудника не может быть пустым.',
      )
      return
    }

    setActionEmployeeId(employee.id)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const updatedEmployee =
        await updateEmployee(
          employee.id,
          {
            name: normalizedName,
          },
        )

      setEmployees((currentEmployees) =>
        currentEmployees
          .map((currentEmployee) =>
            currentEmployee.id === employee.id
              ? updatedEmployee
              : currentEmployee,
          )
          .sort(
            (firstEmployee, secondEmployee) =>
              firstEmployee.name.localeCompare(
                secondEmployee.name,
                'ru',
              ),
          ),
      )

      setEditingEmployeeId(null)
      setEditingName('')
      setSuccessMessage(
        `Сотрудник переименован в «${updatedEmployee.name}».`,
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось изменить сотрудника',
        )
      }
    } finally {
      setActionEmployeeId(null)
    }
  }

  async function handleArchive(
    employee: Employee,
  ) {
    const isConfirmed = window.confirm(
      `Переместить сотрудника «${employee.name}» в архив?`,
    )

    if (!isConfirmed) {
      return
    }

    setActionEmployeeId(employee.id)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const archivedEmployee =
        await archiveEmployee(employee.id)

      setEmployees((currentEmployees) =>
        currentEmployees.map((currentEmployee) =>
          currentEmployee.id === employee.id
            ? archivedEmployee
            : currentEmployee,
        ),
      )

      setSuccessMessage(
        `Сотрудник «${employee.name}» перемещён в архив.`,
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось архивировать сотрудника',
        )
      }
    } finally {
      setActionEmployeeId(null)
    }
  }

  async function handleRestore(
    employee: Employee,
  ) {
    setActionEmployeeId(employee.id)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const restoredEmployee =
        await restoreEmployee(employee.id)

      setEmployees((currentEmployees) =>
        currentEmployees.map((currentEmployee) =>
          currentEmployee.id === employee.id
            ? restoredEmployee
            : currentEmployee,
        ),
      )

      setSuccessMessage(
        `Сотрудник «${employee.name}» восстановлен.`,
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage(
          'Не удалось восстановить сотрудника',
        )
      }
    } finally {
      setActionEmployeeId(null)
    }
  }

  function handleRefresh() {
    setLoadingStatus('loading')
    setErrorMessage('')
    setSuccessMessage('')
    void loadEmployees()
  }

  const activeEmployeesCount =
    employees.filter(
      (employee) => employee.is_active,
    ).length

  return (
    <main className="min-h-screen bg-[#070a10] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              to="/"
              className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
            >
              ← Главная панель
            </Link>

            <h1 className="mt-3 text-3xl font-bold text-white">
              Сотрудники
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Справочник администраторов клуба
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
              Всего сотрудников
            </p>

            <p className="mt-2 text-3xl font-bold text-white">
              {loadingStatus === 'loading'
                ? '...'
                : employees.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              Активные
            </p>

            <p className="mt-2 text-3xl font-bold text-emerald-400">
              {loadingStatus === 'loading'
                ? '...'
                : activeEmployeesCount}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
            <p className="text-sm text-slate-400">
              В архиве
            </p>

            <p className="mt-2 text-3xl font-bold text-amber-400">
              {loadingStatus === 'loading'
                ? '...'
                : employees.length
                  - activeEmployeesCount}
            </p>
          </div>
        </section>

        <form
          onSubmit={handleCreate}
          className="mt-6 flex flex-col gap-3 rounded-2xl border border-slate-800 bg-[#0b0f17] p-5 sm:flex-row"
        >
          <input
            type="text"
            value={newEmployeeName}
            onChange={(event) =>
              setNewEmployeeName(
                event.target.value,
              )
            }
            placeholder="Имя нового сотрудника"
            minLength={1}
            maxLength={255}
            className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
          />

          <button
            type="submit"
            disabled={isCreating}
            className="rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isCreating
              ? 'Добавление...'
              : 'Добавить сотрудника'}
          </button>
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

        <section className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-[#0b0f17]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[750px] text-left">
              <thead className="border-b border-slate-800 bg-slate-950/60 text-xs uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-6 py-4">
                    Сотрудник
                  </th>

                  <th className="px-6 py-4">
                    Статус
                  </th>

                  <th className="px-6 py-4 text-right">
                    Действия
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {employees.map((employee) => {
                  const isEditing =
                    editingEmployeeId === employee.id

                  const isProcessing =
                    actionEmployeeId === employee.id

                  return (
                    <tr
                      key={employee.id}
                      className="transition hover:bg-slate-900/70"
                    >
                      <td className="px-6 py-4">
                        {isEditing ? (
                          <input
                            type="text"
                            value={editingName}
                            onChange={(event) =>
                              setEditingName(
                                event.target.value,
                              )
                            }
                            minLength={1}
                            maxLength={255}
                            className="w-full max-w-sm rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none transition focus:border-cyan-500"
                          />
                        ) : (
                          <p className="font-medium text-white">
                            {employee.name}
                          </p>
                        )}
                      </td>

                      <td className="px-6 py-4">
                        <span
                          className={
                            employee.is_active
                              ? 'rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400'
                              : 'rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-400'
                          }
                        >
                          {employee.is_active
                            ? 'Активен'
                            : 'В архиве'}
                        </span>
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex justify-end gap-2">
                          {isEditing ? (
                            <>
                              <button
                                type="button"
                                onClick={() => {
                                  void handleUpdate(
                                    employee,
                                  )
                                }}
                                disabled={isProcessing}
                                className="rounded-lg bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                {isProcessing
                                  ? 'Сохранение...'
                                  : 'Сохранить'}
                              </button>

                              <button
                                type="button"
                                onClick={cancelEditing}
                                disabled={isProcessing}
                                className="rounded-lg border border-slate-700 px-3 py-2 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:text-white disabled:opacity-50"
                              >
                                Отмена
                              </button>
                            </>
                          ) : (
                            <>
                              <button
                                type="button"
                                onClick={() =>
                                  startEditing(employee)
                                }
                                disabled={isProcessing}
                                className="rounded-lg border border-slate-700 px-3 py-2 text-sm font-medium text-slate-300 transition hover:border-cyan-500 hover:text-cyan-400 disabled:opacity-50"
                              >
                                Переименовать
                              </button>

                              {employee.is_active ? (
                                <button
                                  type="button"
                                  onClick={() => {
                                    void handleArchive(
                                      employee,
                                    )
                                  }}
                                  disabled={isProcessing}
                                  className="rounded-lg border border-amber-900 px-3 py-2 text-sm font-medium text-amber-400 transition hover:border-amber-600 hover:bg-amber-950/40 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                  {isProcessing
                                    ? 'Архивация...'
                                    : 'В архив'}
                                </button>
                              ) : (
                                <button
                                  type="button"
                                  onClick={() => {
                                    void handleRestore(
                                      employee,
                                    )
                                  }}
                                  disabled={isProcessing}
                                  className="rounded-lg border border-emerald-900 px-3 py-2 text-sm font-medium text-emerald-400 transition hover:border-emerald-600 hover:bg-emerald-950/40 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                  {isProcessing
                                    ? 'Восстановление...'
                                    : 'Восстановить'}
                                </button>
                              )}
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}

                {loadingStatus === 'success'
                  && employees.length === 0 && (
                    <tr>
                      <td
                        colSpan={3}
                        className="px-6 py-12 text-center text-slate-500"
                      >
                        Сотрудников пока нет
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