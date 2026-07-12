import { useState } from 'react'
import type {
  ChangeEvent,
  FormEvent,
} from 'react'
import { Link } from 'react-router-dom'

import {
  applyLightShellImport,
  getProducts,
  previewLightShellImport,
} from '../api/client'
import type {
  LightShellImportApplyResult,
  LightShellImportPreview,
  LightShellImportPreviewItem,
  LightShellImportResolution,
  LightShellMatchStatus,
  LightShellResolutionAction,
} from '../types/lightshellImport'
import type { Product } from '../types/product'

const MAX_PDF_SIZE = 10 * 1024 * 1024

const STATUS_LABELS: Record<
  LightShellMatchStatus,
  string
> = {
  exact: 'Точное совпадение',
  mapped: 'Сохранённая связь',
  unmatched: 'Не найден',
  ambiguous: 'Несколько совпадений',
}

const STATUS_CLASS_NAMES: Record<
  LightShellMatchStatus,
  string
> = {
  exact:
    'border-emerald-900 bg-emerald-950/50 text-emerald-300',

  mapped:
    'border-cyan-900 bg-cyan-950/50 text-cyan-300',

  unmatched:
    'border-red-900 bg-red-950/50 text-red-300',

  ambiguous:
    'border-amber-900 bg-amber-950/50 text-amber-300',
}

function formatQuantity(
  value: string,
) {
  return Number(value).toLocaleString(
    'ru-RU',
    {
      maximumFractionDigits: 3,
    },
  )
}

function formatDateTime(
  value: string,
) {
  return new Date(value).toLocaleString(
    'ru-RU',
  )
}

export function LightShellImportPage() {
  const [
    selectedFile,
    setSelectedFile,
  ] = useState<File | null>(null)

  const [
    preview,
    setPreview,
  ] = useState<
    LightShellImportPreview | null
  >(null)

  const [
    products,
    setProducts,
  ] = useState<Product[]>([])

  const [
    resolutions,
    setResolutions,
  ] = useState<
    Record<
      number,
      LightShellImportResolution
    >
  >({})

  const [
    applyResult,
    setApplyResult,
  ] = useState<
    LightShellImportApplyResult | null
  >(null)

  const [
    isLoading,
    setIsLoading,
  ] = useState(false)

  const [
    isApplying,
    setIsApplying,
  ] = useState(false)

  const [
    errorMessage,
    setErrorMessage,
  ] = useState('')

  const [
    successMessage,
    setSuccessMessage,
  ] = useState('')

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file =
      event.target.files?.[0]
      ?? null

    setPreview(null)
    setProducts([])
    setResolutions({})
    setApplyResult(null)
    setErrorMessage('')
    setSuccessMessage('')

    if (!file) {
      setSelectedFile(null)
      return
    }

    if (
      !file.name
        .toLowerCase()
        .endsWith('.pdf')
    ) {
      setSelectedFile(null)

      setErrorMessage(
        'Можно выбрать только PDF-файл.',
      )

      event.target.value = ''
      return
    }

    if (file.size > MAX_PDF_SIZE) {
      setSelectedFile(null)

      setErrorMessage(
        'Размер PDF превышает 10 МБ.',
      )

      event.target.value = ''
      return
    }

    setSelectedFile(file)
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!selectedFile) {
      setErrorMessage(
        'Сначала выбери PDF-файл.',
      )
      return
    }

    setIsLoading(true)
    setErrorMessage('')
    setSuccessMessage('')
    setPreview(null)
    setApplyResult(null)
    setResolutions({})

    try {
      const [
        loadedPreview,
        loadedProducts,
      ] = await Promise.all([
        previewLightShellImport(
          selectedFile,
        ),

        getProducts(),
      ])

      const initialResolutions: Record<
        number,
        LightShellImportResolution
      > = {}

      for (
        const item
        of loadedPreview.items
      ) {
        initialResolutions[
          item.source_number
        ] = item.product_id
          ? {
              source_number:
                item.source_number,

              action:
                'use_existing',

              product_id:
                item.product_id,
            }
          : {
              source_number:
                item.source_number,

              action:
                'skip',

              product_id:
                null,
            }
      }

      setPreview(loadedPreview)
      setProducts(loadedProducts)

      setResolutions(
        initialResolutions,
      )

      setSuccessMessage(
        'PDF успешно прочитан. '
        + 'Проверь решения перед применением.',
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(
          error.message,
        )
      } else {
        setErrorMessage(
          'Не удалось прочитать PDF.',
        )
      }
    } finally {
      setIsLoading(false)
    }
  }

  function handleActionChange(
    item: LightShellImportPreviewItem,
    action: LightShellResolutionAction,
  ) {
    const currentResolution =
      resolutions[
        item.source_number
      ]

    const productId =
      action === 'use_existing'
        ? (
            currentResolution
              ?.product_id
            ?? item.product_id
            ?? null
          )
        : null

    setResolutions(
      (currentResolutions) => ({
        ...currentResolutions,

        [item.source_number]: {
          source_number:
            item.source_number,

          action,

          product_id:
            productId,
        },
      }),
    )

    setApplyResult(null)
    setSuccessMessage('')
    setErrorMessage('')
  }

  function handleProductChange(
    item: LightShellImportPreviewItem,
    productId: string,
  ) {
    setResolutions(
      (currentResolutions) => ({
        ...currentResolutions,

        [item.source_number]: {
          source_number:
            item.source_number,

          action:
            'use_existing',

          product_id:
            productId || null,
        },
      }),
    )

    setApplyResult(null)
    setSuccessMessage('')
    setErrorMessage('')
  }

  function setUnresolvedAction(
    action: 'create_new' | 'skip',
  ) {
    if (!preview) {
      return
    }

    setResolutions(
      (currentResolutions) => {
        const updatedResolutions = {
          ...currentResolutions,
        }

        for (
          const item
          of preview.items
        ) {
          if (
            item.status === 'unmatched'
            || item.status === 'ambiguous'
          ) {
            updatedResolutions[
              item.source_number
            ] = {
              source_number:
                item.source_number,

              action,

              product_id:
                null,
            }
          }
        }

        return updatedResolutions
      },
    )

    setApplyResult(null)
    setSuccessMessage('')
    setErrorMessage('')
  }

  async function handleApply() {
    if (
      !selectedFile
      || !preview
    ) {
      setErrorMessage(
        'Сначала сформируй предпросмотр.',
      )
      return
    }

    const orderedResolutions:
      LightShellImportResolution[] = []

    for (
      const item
      of preview.items
    ) {
      const resolution =
        resolutions[
          item.source_number
        ]

      if (!resolution) {
        setErrorMessage(
          `Не указано решение для позиции №${item.source_number}.`,
        )
        return
      }

      if (
        resolution.action
          === 'use_existing'
        && !resolution.product_id
      ) {
        setErrorMessage(
          `Выбери товар для позиции №${item.source_number}.`,
        )
        return
      }

      orderedResolutions.push(
        resolution,
      )
    }

    setIsApplying(true)
    setErrorMessage('')
    setSuccessMessage('')
    setApplyResult(null)

    try {
      const result =
        await applyLightShellImport(
          selectedFile,
          orderedResolutions,
        )

      setApplyResult(result)

      setSuccessMessage(
        'Импорт успешно применён. '
        + 'Фактические остатки и долги '
        + 'не изменялись.',
      )
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(
          error.message,
        )
      } else {
        setErrorMessage(
          'Не удалось применить импорт.',
        )
      }
    } finally {
      setIsApplying(false)
    }
  }

  const unresolvedItems = preview
    ? (
        preview.unmatched_items
        + preview.ambiguous_items
      )
    : 0

  const resolutionValues =
    Object.values(resolutions)

  const createNewCount =
    resolutionValues.filter(
      (resolution) =>
        resolution.action
        === 'create_new',
    ).length

  const useExistingCount =
    resolutionValues.filter(
      (resolution) =>
        resolution.action
        === 'use_existing',
    ).length

  const skipCount =
    resolutionValues.filter(
      (resolution) =>
        resolution.action
        === 'skip',
    ).length

  return (
    <main className="min-h-screen bg-[#070a10] p-6 text-slate-100">
      <div className="mx-auto max-w-[1600px]">
        <header className="flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              to="/inventory"
              className="text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
            >
              ← Вернуться к ревизии
            </Link>

            <h1 className="mt-3 text-3xl font-bold text-white">
              Импорт из LightShell
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Загрузка программных
              остатков из PDF-отчёта
            </p>
          </div>

          <Link
            to="/"
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-center text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:text-white"
          >
            Главная панель
          </Link>
        </header>

        <section className="mt-6 rounded-2xl border border-slate-800 bg-[#0b0f17] p-6">
          <div className="max-w-3xl">
            <h2 className="text-xl font-semibold text-white">
              Загрузить отчёт ревизии
            </h2>

            <p className="mt-2 text-sm leading-6 text-slate-400">
              Сначала приложение покажет
              позиции PDF и найденные товары.
              Изменения будут внесены только
              после отдельного подтверждения.
            </p>

            <form
              onSubmit={(event) => {
                void handleSubmit(event)
              }}
              className="mt-6 flex flex-col gap-4 sm:flex-row sm:items-end"
            >
              <label className="flex-1">
                <span className="mb-2 block text-sm font-medium text-slate-300">
                  PDF-файл
                </span>

                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileChange}
                  disabled={
                    isLoading
                    || isApplying
                  }
                  className="block w-full cursor-pointer rounded-xl border border-slate-700 bg-slate-950 text-sm text-slate-400 file:mr-4 file:border-0 file:border-r file:border-slate-700 file:bg-slate-900 file:px-4 file:py-3 file:font-medium file:text-slate-200 hover:file:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </label>

              <button
                type="submit"
                disabled={
                  isLoading
                  || isApplying
                  || !selectedFile
                }
                className="rounded-xl bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isLoading
                  ? 'Чтение PDF...'
                  : 'Показать предпросмотр'}
              </button>
            </form>

            {selectedFile && (
              <p className="mt-3 text-sm text-slate-500">
                Выбран файл:{' '}

                <span className="text-slate-300">
                  {selectedFile.name}
                </span>
              </p>
            )}
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

        {applyResult && (
          <section className="mt-6 rounded-2xl border border-emerald-800 bg-emerald-950/20 p-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-emerald-300">
                  Импорт завершён
                </h2>

                <p className="mt-2 text-sm text-slate-300">
                  Обновлено позиций:{' '}
                  {applyResult.updated_items}.
                  Создано товаров:{' '}
                  {applyResult.created_products}.
                  Пропущено:{' '}
                  {applyResult.skipped_items}.
                </p>
              </div>

              <Link
                to="/inventory"
                className="rounded-xl bg-emerald-500 px-5 py-3 text-center text-sm font-semibold text-slate-950 transition hover:bg-emerald-400"
              >
                Открыть ревизию
              </Link>
            </div>
          </section>
        )}

        {preview && (
          <>
            <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
                <p className="text-sm text-slate-400">
                  Всего позиций
                </p>

                <p className="mt-2 text-3xl font-bold text-white">
                  {preview.total_items}
                </p>
              </div>

              <div className="rounded-2xl border border-emerald-900/70 bg-emerald-950/20 p-5">
                <p className="text-sm text-emerald-300">
                  Найдено
                </p>

                <p className="mt-2 text-3xl font-bold text-emerald-400">
                  {preview.matched_items}
                </p>
              </div>

              <div className="rounded-2xl border border-red-900/70 bg-red-950/20 p-5">
                <p className="text-sm text-red-300">
                  Не найдено
                </p>

                <p className="mt-2 text-3xl font-bold text-red-400">
                  {preview.unmatched_items}
                </p>
              </div>

              <div className="rounded-2xl border border-amber-900/70 bg-amber-950/20 p-5">
                <p className="text-sm text-amber-300">
                  Требуют решения
                </p>

                <p className="mt-2 text-3xl font-bold text-amber-400">
                  {unresolvedItems}
                </p>
              </div>
            </section>

            <section className="mt-6 rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
              <div className="grid gap-4 text-sm sm:grid-cols-3">
                <div>
                  <p className="text-slate-500">
                    Филиал
                  </p>

                  <p className="mt-1 font-medium text-white">
                    {preview.branch}
                  </p>
                </div>

                <div>
                  <p className="text-slate-500">
                    Отчёт сформирован
                  </p>

                  <p className="mt-1 font-medium text-white">
                    {formatDateTime(
                      preview.generated_at,
                    )}
                  </p>
                </div>

                <div>
                  <p className="text-slate-500">
                    Файл
                  </p>

                  <p className="mt-1 font-medium text-white">
                    {preview.source_filename}
                  </p>
                </div>
              </div>
            </section>

            <section className="mt-6 rounded-2xl border border-slate-800 bg-[#0b0f17] p-5">
              <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-white">
                    Решения по импорту
                  </h2>

                  <p className="mt-2 text-sm text-slate-400">
                    Существующие:{' '}
                    {useExistingCount}.
                    Новые:{' '}
                    {createNewCount}.
                    Пропустить:{' '}
                    {skipCount}.
                  </p>
                </div>

                <div className="flex flex-col gap-3 sm:flex-row">
                  <button
                    type="button"
                    onClick={() => {
                      setUnresolvedAction(
                        'create_new',
                      )
                    }}
                    disabled={
                      isApplying
                      || unresolvedItems === 0
                    }
                    className="rounded-xl border border-cyan-800 bg-cyan-950/30 px-4 py-2.5 text-sm font-medium text-cyan-300 transition hover:bg-cyan-950/60 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Создать все ненайденные
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setUnresolvedAction(
                        'skip',
                      )
                    }}
                    disabled={
                      isApplying
                      || unresolvedItems === 0
                    }
                    className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Пропустить все ненайденные
                  </button>
                </div>
              </div>
            </section>

            <section className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-[#0b0f17]">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[1500px] text-left">
                  <thead className="border-b border-slate-800 bg-slate-950/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-5 py-4">
                        №
                      </th>

                      <th className="px-5 py-4">
                        Позиция LightShell
                      </th>

                      <th className="px-5 py-4">
                        Категория
                      </th>

                      <th className="px-5 py-4">
                        По программе
                      </th>

                      <th className="px-5 py-4">
                        Совпадение
                      </th>

                      <th className="px-5 py-4">
                        Действие
                      </th>

                      <th className="px-5 py-4">
                        Товар в приложении
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-800">
                    {preview.items.map(
                      (item) => {
                        const resolution =
                          resolutions[
                            item.source_number
                          ]

                        return (
                          <tr
                            key={
                              item.source_number
                            }
                            className="transition hover:bg-slate-900/70"
                          >
                            <td className="px-5 py-4 text-slate-500">
                              {
                                item.source_number
                              }
                            </td>

                            <td className="px-5 py-4">
                              <p className="font-medium text-white">
                                {
                                  item.source_name
                                }
                              </p>
                            </td>

                            <td className="px-5 py-4 text-slate-400">
                              {
                                item.source_category
                              }
                            </td>

                            <td className="px-5 py-4 font-semibold text-cyan-300">
                              {formatQuantity(
                                item.program_quantity,
                              )}
                            </td>

                            <td className="px-5 py-4">
                              <span
                                className={
                                  'inline-flex rounded-full '
                                  + 'border px-3 py-1 '
                                  + 'text-xs font-semibold '
                                  + STATUS_CLASS_NAMES[
                                    item.status
                                  ]
                                }
                              >
                                {
                                  STATUS_LABELS[
                                    item.status
                                  ]
                                }
                              </span>
                            </td>

                            <td className="px-5 py-4">
                              <select
                                value={
                                  resolution?.action
                                  ?? 'skip'
                                }
                                onChange={(event) => {
  const action =
    event.currentTarget.value

  if (
    action === 'use_existing'
    || action === 'create_new'
    || action === 'skip'
  ) {
    handleActionChange(
      item,
      action,
    )
  }
}}
                                disabled={
                                  isApplying
                                }
                                className="w-52 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none transition focus:border-cyan-500 disabled:opacity-50"
                              >
                                <option value="use_existing">
                                  Использовать товар
                                </option>

                                <option value="create_new">
                                  Создать новый
                                </option>

                                <option value="skip">
                                  Пропустить
                                </option>
                              </select>
                            </td>

                            <td className="px-5 py-4">
                              {resolution?.action
                                === 'use_existing'
                                ? (
                                    <select
                                      value={
                                        resolution
                                          .product_id
                                        ?? ''
                                      }
                                      onChange={(
                                        event,
                                      ) => {
                                        handleProductChange(
                                          item,
                                          event
                                            .currentTarget
                                            .value,
                                        )
                                      }}
                                      disabled={
                                        isApplying
                                      }
                                      className="w-72 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none transition focus:border-cyan-500 disabled:opacity-50"
                                    >
                                      <option value="">
                                        Выбери товар
                                      </option>

                                      {products.map(
                                        (
                                          product,
                                        ) => (
                                          <option
                                            key={
                                              product.id
                                            }
                                            value={
                                              product.id
                                            }
                                          >
                                            {
                                              product.name
                                            }
                                          </option>
                                        ),
                                      )}
                                    </select>
                                  )
                                : (
                                    <span className="text-sm text-slate-500">
                                      {resolution
                                        ?.action
                                        === 'create_new'
                                        ? (
                                            'Будет создан '
                                            + 'с ценой 0 ₽'
                                          )
                                        : (
                                            'Не изменяется'
                                          )}
                                    </span>
                                  )}
                            </td>
                          </tr>
                        )
                      },
                    )}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="sticky bottom-4 mt-6 rounded-2xl border border-cyan-900 bg-[#0b0f17]/95 p-5 shadow-2xl backdrop-blur">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-semibold text-white">
                    Применить импорт
                  </p>

                  <p className="mt-1 text-sm text-slate-400">
                    Изменится только остаток
                    «По программе». Факт и долги
                    останутся без изменений.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    void handleApply()
                  }}
                  disabled={
                    isApplying
                    || applyResult !== null
                  }
                  className="rounded-xl bg-cyan-500 px-7 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isApplying
                    ? 'Применение...'
                    : applyResult
                      ? 'Импорт применён'
                      : 'Применить импорт'}
                </button>
              </div>
            </section>
          </>
        )}
      </div>
    </main>
  )
}