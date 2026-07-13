import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import type {
  FormEvent,
} from 'react'
import {
  Link,
} from 'react-router-dom'

import {
  getClubSettings,
  updateClubSettings,
} from '../api/client'

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

export function SettingsPage() {
  const [
    clubName,
    setClubName,
  ] = useState('')

  const [
    branch,
    setBranch,
  ] = useState('')

  const [
    lotteryTicketPrice,
    setLotteryTicketPrice,
  ] = useState('85')

  const [
    loadingStatus,
    setLoadingStatus,
  ] = useState<LoadingStatus>(
    'loading',
  )

  const [
    isSaving,
    setIsSaving,
  ] = useState(false)

  const [
    errorMessage,
    setErrorMessage,
  ] = useState('')

  const [
    successMessage,
    setSuccessMessage,
  ] = useState('')

  const loadSettings =
    useCallback(async () => {
      try {
        const settings =
          await getClubSettings()

        setClubName(
          settings.club_name,
        )

        setBranch(
          settings.branch,
        )

        setLotteryTicketPrice(
          settings.lottery_ticket_price,
        )

        setErrorMessage('')
        setLoadingStatus('success')
      } catch (error) {
        setLoadingStatus('error')

        if (error instanceof Error) {
          setErrorMessage(
            error.message,
          )
        } else {
          setErrorMessage(
            'Не удалось загрузить настройки.',
          )
        }
      }
    }, [])

  useEffect(() => {
    const timeoutId =
      window.setTimeout(() => {
        void loadSettings()
      }, 0)

    return () => {
      window.clearTimeout(
        timeoutId,
      )
    }
  }, [loadSettings])

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const normalizedClubName =
      clubName.trim()

    const normalizedBranch =
      branch.trim()

    const normalizedTicketPrice =
      Number(
        lotteryTicketPrice,
      )

    if (!normalizedClubName) {
      setErrorMessage(
        'Название клуба не может быть пустым.',
      )

      setSuccessMessage('')

      return
    }

    if (!normalizedBranch) {
      setErrorMessage(
        'Название филиала не может быть пустым.',
      )

      setSuccessMessage('')

      return
    }

    if (
      !Number.isFinite(
        normalizedTicketPrice,
      )
      || normalizedTicketPrice < 0
    ) {
      setErrorMessage(
        'Стоимость билета должна быть числом не меньше нуля.',
      )

      setSuccessMessage('')

      return
    }

    setIsSaving(true)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const updatedSettings =
        await updateClubSettings({
          club_name:
            normalizedClubName,

          branch:
            normalizedBranch,

          lottery_ticket_price:
            normalizedTicketPrice,
        })

      setClubName(
        updatedSettings.club_name,
      )

      setBranch(
        updatedSettings.branch,
      )

      setLotteryTicketPrice(
        updatedSettings
          .lottery_ticket_price,
      )

      setSuccessMessage(
        'Настройки сохранены.',
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(
          error.message,
        )
      } else {
        setErrorMessage(
          'Не удалось сохранить настройки.',
        )
      }
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <main className="min-h-screen bg-[#070a10] p-6 text-slate-100">
      <div className="mx-auto max-w-4xl">
        <header className="border-b border-slate-800 pb-6">
          <Link
            to="/"
            className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
          >
            ← Главная панель
          </Link>

          <h1 className="mt-3 text-3xl font-bold text-white">
            Настройки
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Основные параметры компьютерного клуба
          </p>
        </header>

        {loadingStatus === 'loading' && (
          <div className="mt-6 rounded-2xl border border-slate-800 bg-[#0b0f17] p-8 text-center text-slate-500">
            Загрузка настроек...
          </div>
        )}

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

        {loadingStatus !== 'loading' && (
          <form
            onSubmit={
              handleSubmit
            }
            className="mt-6 space-y-6"
          >
            <section className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-6">
              <h2 className="text-lg font-semibold text-white">
                Информация о клубе
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Эти данные будут использоваться в интерфейсе и отчётах
              </p>

              <div className="mt-6 grid gap-5 md:grid-cols-2">
                <div>
                  <label
                    htmlFor="club-name"
                    className="text-sm font-medium text-slate-300"
                  >
                    Название клуба
                  </label>

                  <input
                    id="club-name"
                    type="text"
                    value={
                      clubName
                    }
                    onChange={(
                      event,
                    ) => {
                      setClubName(
                        event.currentTarget.value,
                      )

                      setSuccessMessage('')
                    }}
                    maxLength={255}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
                    placeholder="КиберДом"
                  />
                </div>

                <div>
                  <label
                    htmlFor="club-branch"
                    className="text-sm font-medium text-slate-300"
                  >
                    Филиал
                  </label>

                  <input
                    id="club-branch"
                    type="text"
                    value={
                      branch
                    }
                    onChange={(
                      event,
                    ) => {
                      setBranch(
                        event.currentTarget.value,
                      )

                      setSuccessMessage('')
                    }}
                    maxLength={255}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
                    placeholder="1 этаж"
                  />
                </div>
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-6">
              <h2 className="text-lg font-semibold text-white">
                Лотерейки
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Базовая стоимость одного лотерейного билета
              </p>

              <div className="mt-6 max-w-sm">
                <label
                  htmlFor="lottery-ticket-price"
                  className="text-sm font-medium text-slate-300"
                >
                  Стоимость билета, ₽
                </label>

                <input
                  id="lottery-ticket-price"
                  type="number"
                  min="0"
                  step="0.01"
                  value={
                    lotteryTicketPrice
                  }
                  onChange={(
                    event,
                  ) => {
                    setLotteryTicketPrice(
                      event.currentTarget.value,
                    )

                    setSuccessMessage('')
                  }}
                  className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
                />
              </div>
            </section>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={
                  isSaving
                  || loadingStatus === 'error'
                }
                className="rounded-xl bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSaving
                  ? 'Сохранение...'
                  : 'Сохранить настройки'}
              </button>
            </div>
          </form>
        )}
      </div>
    </main>
  )
}