export interface CsvColumn<Row> {
  header: string

  getValue: (
    row: Row,
  ) =>
    | string
    | number
    | null
    | undefined
}

interface DownloadCsvOptions<Row> {
  filename: string
  columns: CsvColumn<Row>[]
  rows: Row[]
}

function escapeCsvValue(
  value:
    | string
    | number
    | null
    | undefined,
) {
  const text =
    value === null
    || value === undefined
      ? ''
      : String(value)

  return `"${text.replaceAll(
    '"',
    '""',
  )}"`
}

export function downloadCsv<Row>({
  filename,
  columns,
  rows,
}: DownloadCsvOptions<Row>) {
  const separator = ';'

  const headerLine =
    columns
      .map(
        (column) =>
          escapeCsvValue(
            column.header,
          ),
      )
      .join(separator)

  const dataLines =
    rows.map(
      (row) =>
        columns
          .map(
            (column) =>
              escapeCsvValue(
                column.getValue(
                  row,
                ),
              ),
          )
          .join(separator),
    )

  const csvContent = [
    headerLine,
    ...dataLines,
  ].join('\r\n')

  const blob = new Blob(
    [
      '\uFEFF',
      csvContent,
    ],
    {
      type: (
        'text/csv;'
        + 'charset=utf-8'
      ),
    },
  )

  const downloadUrl =
    URL.createObjectURL(
      blob,
    )

  const link =
    document.createElement(
      'a',
    )

  link.href = downloadUrl
  link.download = filename

  document.body.appendChild(
    link,
  )

  link.click()
  link.remove()

  window.setTimeout(
    () => {
      URL.revokeObjectURL(
        downloadUrl,
      )
    },
    0,
  )
}