import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
} from 'react'
import { Link } from 'react-router-dom'

import {
  getBookingNote,
  updateBookingNote,
} from '../api/client'

type LoadingStatus =
  | 'loading'
  | 'success'
  | 'error'

type SaveStatus =
  | 'idle'
  | 'saving'
  | 'saved'
  | 'error'

interface LocalBookingDraft {
  content: string
  savedAt: string
}

const AUTO_SAVE_DELAY_MS = 700

function formatDateForInput(
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

  return `${year}-${month}-${day}`
}

function parseDate(
  value: string,
) {
  const [
    year,
    month,
    day,
  ] = value
    .split('-')
    .map(Number)

  return new Date(
    year,
    month - 1,
    day,
    12,
  )
}

function addDays(
  value: string,
  amount: number,
) {
  const date =
    parseDate(value)

  date.setDate(
    date.getDate() + amount,
  )

  return formatDateForInput(
    date,
  )
}

function formatDisplayDate(
  value: string,
) {
  return parseDate(
    value,
  ).toLocaleDateString(
    'ru-RU',
    {
      weekday: 'long',
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    },
  )
}

function getLocalStorageKey(
  bookingDate: string,
) {
  return (
    'cyberclub-booking-note:'
    + bookingDate
  )
}

function readLocalDraft(
  bookingDate: string,
): LocalBookingDraft | null {
  const storedValue =
    window.localStorage.getItem(
      getLocalStorageKey(
        bookingDate,
      ),
    )

  if (!storedValue) {
    return null
  }

  try {
    const parsedValue =
      JSON.parse(
        storedValue,
      ) as LocalBookingDraft

    if (
      typeof parsedValue.content
      !== 'string'
      || typeof parsedValue.savedAt
      !== 'string'
    ) {
      return null
    }

    return parsedValue
  } catch {
    return null
  }
}

function writeLocalDraft(
  bookingDate: string,
  content: string,
) {
  const draft: LocalBookingDraft = {
    content,
    savedAt:
      new Date().toISOString(),
  }

  window.localStorage.setItem(
    getLocalStorageKey(
      bookingDate,
    ),
    JSON.stringify(
      draft,
    ),
  )
}

export function BookingNotesPage() {
  const [
    selectedDate,
    setSelectedDate,
  ] = useState(
    formatDateForInput(
      new Date(),
    ),
  )

  const [
    content,
    setContent,
  ] = useState('')

  const [
    loadingStatus,
    setLoadingStatus,
  ] = useState<LoadingStatus>(
    'loading',
  )

  const [
    saveStatus,
    setSaveStatus,
  ] = useState<SaveStatus>(
    'idle',
  )

  const [
    errorMessage,
    setErrorMessage,
  ] = useState('')

  const [
    hasUnsavedChanges,
    setHasUnsavedChanges,
  ] = useState(false)

  const activeLoadId =
    useRef(0)

  const loadBookingNote =
    useCallback(
      async (
        bookingDate: string,
      ) => {
        const loadId =
          activeLoadId.current + 1

        activeLoadId.current =
          loadId

        setLoadingStatus(
          'loading',
        )

        setSaveStatus(
          'idle',
        )

        setErrorMessage('')

        const localDraft =
          readLocalDraft(
            bookingDate,
          )

        if (localDraft) {
          setContent(
            localDraft.content,
          )
        } else {
          setContent('')
        }

        try {
          const bookingNote =
            await getBookingNote(
              bookingDate,
            )

          if (
            activeLoadId.current
            !== loadId
          ) {
            return
          }

          const serverUpdatedAt =
            new Date(
              bookingNote.updated_at,
            ).getTime()

          const localUpdatedAt =
            localDraft
              ? new Date(
                  localDraft.savedAt,
                ).getTime()
              : 0

          if (
            localDraft
            && Number.isFinite(
              localUpdatedAt,
            )
            && localUpdatedAt
            > serverUpdatedAt
          ) {
            setContent(
              localDraft.content,
            )

            setHasUnsavedChanges(
              true,
            )

            setSaveStatus(
              'saving',
            )
          } else {
            setContent(
              bookingNote.content,
            )

            writeLocalDraft(
              bookingDate,
              bookingNote.content,
            )

            setHasUnsavedChanges(
              false,
            )

            setSaveStatus(
              'saved',
            )
          }

          setLoadingStatus(
            'success',
          )
        } catch (error) {
          if (
            activeLoadId.current
            !== loadId
          ) {
            return
          }

          if (localDraft) {
            setContent(
              localDraft.content,
            )

            setLoadingStatus(
              'success',
            )

            setHasUnsavedChanges(
              true,
            )

            setSaveStatus(
              'error',
            )

            setErrorMessage(
              'Сервер недоступен. '
              + 'Показана локальная копия, '
              + 'она будет отправлена '
              + 'после восстановления связи.',
            )

            return
          }

          setLoadingStatus(
            'error',
          )

          setSaveStatus(
            'error',
          )

          if (error instanceof Error) {
            setErrorMessage(
              error.message,
            )
          } else {
            setErrorMessage(
              'Не удалось загрузить брони.',
            )
          }
        }
      },
      [],
    )

  useEffect(() => {
    const timeoutId =
      window.setTimeout(() => {
        void loadBookingNote(
          selectedDate,
        )
      }, 0)

    return () => {
      window.clearTimeout(
        timeoutId,
      )
    }
  }, [
    loadBookingNote,
    selectedDate,
  ])

  useEffect(() => {
    if (
      !hasUnsavedChanges
      || loadingStatus
      !== 'success'
    ) {
      return
    }

    const timeoutId =
      window.setTimeout(
        () => {
          void (
            async () => {
              try {
                const savedNote =
                  await updateBookingNote(
                    selectedDate,
                    {
                      content,
                    },
                  )

                writeLocalDraft(
                  selectedDate,
                  savedNote.content,
                )

                setHasUnsavedChanges(
                  false,
                )

                setSaveStatus(
                  'saved',
                )

                setErrorMessage('')
              } catch (error) {
                setSaveStatus(
                  'error',
                )

                if (
                  error instanceof Error
                ) {
                  setErrorMessage(
                    'Локальная копия сохранена. '
                    + 'Сервер: '
                    + error.message,
                  )
                } else {
                  setErrorMessage(
                    'Локальная копия сохранена, '
                    + 'но сервер недоступен.',
                  )
                }
              }
            }
          )()
        },
        AUTO_SAVE_DELAY_MS,
      )

    return () => {
      window.clearTimeout(
        timeoutId,
      )
    }
  }, [
    content,
    hasUnsavedChanges,
    loadingStatus,
    selectedDate,
  ])

  function handleContentChange(
    event:
      ChangeEvent<HTMLTextAreaElement>,
  ) {
    const nextContent =
      event.currentTarget.value

    setContent(
      nextContent,
    )

    writeLocalDraft(
      selectedDate,
      nextContent,
    )

    setHasUnsavedChanges(
      true,
    )

    setSaveStatus(
      'saving',
    )
  }

  function changeDate(
    nextDate: string,
  ) {
    setSelectedDate(
      nextDate,
    )
  }

  const today =
    formatDateForInput(
      new Date(),
    )

  return (
    <main className="min-h-screen bg-[#070a10] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <header className="border-b border-slate-800 pb-6">
          <Link
            to="/"
            className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
          >
            ← Главная панель
          </Link>

          <h1 className="mt-3 text-3xl font-bold text-white">
            Брони
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Простой блокнот броней
            с автоматическим сохранением
          </p>
        </header>

        <section className="mt-6 rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <label
                htmlFor="booking-date"
                className="text-sm font-medium text-slate-300"
              >
                Дата
              </label>

              <input
                id="booking-date"
                type="date"
                value={
                  selectedDate
                }
                onChange={(
                  event,
                ) => {
                  changeDate(
                    event.currentTarget
                      .value,
                  )
                }}
                className="mt-2 block rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              />
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => {
                  changeDate(
                    addDays(
                      selectedDate,
                      -1,
                    ),
                  )
                }}
                className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:text-white"
              >
                ← Вчера
              </button>

              <button
                type="button"
                onClick={() => {
                  changeDate(
                    today,
                  )
                }}
                className="rounded-xl border border-cyan-500/40 bg-cyan-500/10 px-4 py-3 text-sm font-medium text-cyan-300 transition hover:border-cyan-400 hover:bg-cyan-500/20"
              >
                Сегодня
              </button>

              <button
                type="button"
                onClick={() => {
                  changeDate(
                    addDays(
                      selectedDate,
                      1,
                    ),
                  )
                }}
                className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:text-white"
              >
                Завтра →
              </button>
            </div>
          </div>

          <div className="mt-5 flex flex-col gap-2 border-t border-slate-800 pt-5 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-xl font-semibold capitalize text-white">
              {formatDisplayDate(
                selectedDate,
              )}
            </h2>

            <p
              className={
                saveStatus === 'error'
                  ? 'text-sm font-medium text-amber-400'
                  : saveStatus === 'saving'
                    ? 'text-sm font-medium text-cyan-400'
                    : 'text-sm font-medium text-emerald-400'
              }
            >
              {loadingStatus
                === 'loading'
                  ? 'Загрузка...'
                  : saveStatus
                    === 'saving'
                    ? 'Сохранение...'
                    : saveStatus
                      === 'error'
                      ? 'Сохранено локально'
                      : 'Сохранено'}
            </p>
          </div>
        </section>

        {errorMessage && (
          <div className="mt-6 rounded-2xl border border-amber-900 bg-amber-950/30 p-4 text-sm text-amber-300">
            {errorMessage}
          </div>
        )}

        <section className="mt-6 rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
          <textarea
            value={
              content
            }
            onChange={
              handleContentChange
            }
            disabled={
              loadingStatus
              === 'loading'
            }
            maxLength={20000}
            spellCheck={false}
            placeholder={
              '30-34 22:00\n'
              + '15-18 19:30'
            }
            className="min-h-[560px] w-full resize-y rounded-xl border border-slate-700 bg-slate-950 p-5 font-mono text-lg leading-8 text-white outline-none transition placeholder:text-slate-700 focus:border-cyan-500 disabled:cursor-wait disabled:opacity-60"
          />

          <p className="mt-3 text-xs text-slate-500">
            Текст мгновенно сохраняется
            в браузере и через долю секунды
            отправляется в PostgreSQL.
          </p>
        </section>
      </div>
    </main>
  )
}
