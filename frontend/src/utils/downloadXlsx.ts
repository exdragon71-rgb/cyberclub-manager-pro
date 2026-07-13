export interface XlsxColumn<Row> {
  header: string
  width: number

  getValue: (
    row: Row,
  ) =>
    | string
    | number
    | boolean
    | null
    | undefined

  numberFormat?: string

  alignment?:
    | 'left'
    | 'center'
    | 'right'
}

interface DownloadXlsxOptions<Row> {
  filename: string
  sheetName: string

  title?: string
  subtitleLines?: string[]

  columns: XlsxColumn<Row>[]
  rows: Row[]
}

export async function downloadXlsx<Row>({
  filename,
  sheetName,
  title,
  subtitleLines = [],
  columns,
  rows,
}: DownloadXlsxOptions<Row>) {
  const excelJsModule =
    await import('exceljs')

  const ExcelJS =
    excelJsModule.default

  const workbook =
    new ExcelJS.Workbook()

  workbook.creator =
    'CyberClub Manager Pro'

  workbook.created =
    new Date()

  workbook.modified =
    new Date()

  const worksheet =
    workbook.addWorksheet(
      sheetName,
    )

  worksheet.columns =
    columns.map(
      (
        column,
        columnIndex,
      ) => ({
        key:
          `column_${columnIndex}`,

        width:
          column.width,
      }),
    )

  const metadataLines = [
    ...(title ? [title] : []),
    ...subtitleLines,
  ]

  metadataLines.forEach(
    (
      line,
      lineIndex,
    ) => {
      const metadataRow =
        worksheet.addRow([
          line,
        ])

      if (columns.length > 1) {
        worksheet.mergeCells(
          metadataRow.number,
          1,
          metadataRow.number,
          columns.length,
        )
      }

      const metadataCell =
        metadataRow.getCell(1)

      metadataCell.alignment = {
        vertical: 'middle',
        horizontal: 'left',
      }

      if (lineIndex === 0 && title) {
        metadataRow.height = 30

        metadataCell.font = {
          bold: true,
          size: 16,

          color: {
            argb: 'FF0F172A',
          },
        }
      } else {
        metadataRow.height = 22

        metadataCell.font = {
          size: 11,

          color: {
            argb: 'FF475569',
          },
        }
      }
    },
  )

  if (metadataLines.length > 0) {
    worksheet.addRow([])
  }

  const headerRow =
    worksheet.addRow(
      columns.map(
        (column) =>
          column.header,
      ),
    )

  const headerRowNumber =
    headerRow.number

  worksheet.views = [
    {
      state: 'frozen',
      ySplit: headerRowNumber,
    },
  ]

  headerRow.height = 30

  headerRow.eachCell(
    (cell) => {
      cell.font = {
        bold: true,

        color: {
          argb: 'FFFFFFFF',
        },
      }

      cell.fill = {
        type: 'pattern',
        pattern: 'solid',

        fgColor: {
          argb: 'FF0F766E',
        },
      }

      cell.alignment = {
        vertical: 'middle',
        horizontal: 'center',
        wrapText: true,
      }

      cell.border = {
        top: {
          style: 'thin',

          color: {
            argb: 'FF334155',
          },
        },

        left: {
          style: 'thin',

          color: {
            argb: 'FF334155',
          },
        },

        bottom: {
          style: 'thin',

          color: {
            argb: 'FF334155',
          },
        },

        right: {
          style: 'thin',

          color: {
            argb: 'FF334155',
          },
        },
      }
    },
  )

  rows.forEach(
    (
      row,
      rowIndex,
    ) => {
      const excelRow =
        worksheet.addRow(
          columns.map(
            (column) =>
              column.getValue(row)
              ?? '',
          ),
        )

      excelRow.height = 22

      excelRow.eachCell(
        (
          cell,
          columnIndex,
        ) => {
          const column =
            columns[
              columnIndex - 1
            ]

          cell.alignment = {
            vertical: 'middle',

            horizontal:
              column.alignment
              ?? 'left',

            wrapText: true,
          }

          cell.border = {
            bottom: {
              style: 'thin',

              color: {
                argb: 'FFE2E8F0',
              },
            },
          }

          if (
            column.numberFormat
          ) {
            cell.numFmt =
              column.numberFormat
          }

          if (
            rowIndex % 2 === 1
          ) {
            cell.fill = {
              type: 'pattern',
              pattern: 'solid',

              fgColor: {
                argb: 'FFF8FAFC',
              },
            }
          }
        },
      )
    },
  )

  if (columns.length > 0) {
    worksheet.autoFilter = {
      from: {
        row: headerRowNumber,
        column: 1,
      },

      to: {
        row: headerRowNumber,
        column:
          columns.length,
      },
    }
  }

  worksheet.pageSetup = {
    orientation: 'landscape',
    fitToPage: true,
    fitToWidth: 1,
    fitToHeight: 0,

    margins: {
      left: 0.25,
      right: 0.25,
      top: 0.5,
      bottom: 0.5,
      header: 0.2,
      footer: 0.2,
    },
  }

  const workbookBuffer =
    await workbook.xlsx.writeBuffer()

  const blob =
    new Blob(
      [
        new Uint8Array(
          workbookBuffer,
        ),
      ],
      {
        type: (
          'application/'
          + 'vnd.openxmlformats-'
          + 'officedocument.'
          + 'spreadsheetml.sheet'
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