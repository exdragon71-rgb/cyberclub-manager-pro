$ErrorActionPreference = "Stop"

function Get-EnvValues {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Файл .env не найден: $Path"
    }

    $values = @{}

    foreach ($rawLine in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $line = $rawLine.Trim()

        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            continue
        }

        $parts = $line.Split("=", 2)
        $key = $parts[0].Trim().ToUpperInvariant()
        $value = $parts[1].Trim()

        $hasDoubleQuotes = $value.StartsWith('"') -and $value.EndsWith('"')
        $hasSingleQuotes = $value.StartsWith("'") -and $value.EndsWith("'")

        if ($hasDoubleQuotes -or $hasSingleQuotes) {
            if ($value.Length -ge 2) {
                $value = $value.Substring(1, $value.Length - 2)
            }
        }

        $values[$key] = $value
    }

    return $values
}

function Get-RequiredValue {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Values,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    if (-not $Values.ContainsKey($Name) -or [string]::IsNullOrWhiteSpace($Values[$Name])) {
        throw "В backend\.env не найдена переменная $Name."
    }

    return $Values[$Name]
}

function Find-PostgreSqlTool {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ToolName
    )

    $command = Get-Command $ToolName -ErrorAction SilentlyContinue

    if ($command) {
        return $command.Source
    }

    $postgresRoot = Join-Path $env:ProgramFiles "PostgreSQL"

    if (Test-Path -LiteralPath $postgresRoot) {
        $candidate = Get-ChildItem -Path $postgresRoot -Directory -ErrorAction SilentlyContinue |
            ForEach-Object {
                Join-Path $_.FullName "bin\$ToolName"
            } |
            Where-Object {
                Test-Path -LiteralPath $_
            } |
            Sort-Object -Descending |
            Select-Object -First 1

        if ($candidate) {
            return $candidate
        }
    }

    throw "$ToolName не найден. Проверьте установку PostgreSQL."
}

$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot "backend\.env"

$envValues = Get-EnvValues -Path $envPath

$dbHost = Get-RequiredValue -Values $envValues -Name "DB_HOST"
$dbPort = Get-RequiredValue -Values $envValues -Name "DB_PORT"
$dbName = Get-RequiredValue -Values $envValues -Name "DB_NAME"
$dbUser = Get-RequiredValue -Values $envValues -Name "DB_USER"
$dbPassword = Get-RequiredValue -Values $envValues -Name "DB_PASSWORD"

$pgRestorePath = Find-PostgreSqlTool -ToolName "pg_restore.exe"
$psqlPath = Find-PostgreSqlTool -ToolName "psql.exe"

$documentsPath = [Environment]::GetFolderPath("MyDocuments")
$backupPath = Join-Path $documentsPath "CyberClub Manager Pro Backups\PostgreSQL"

if (-not (Test-Path -LiteralPath $backupPath)) {
    throw "Папка резервных копий не найдена: $backupPath"
}

$latestBackup = Get-ChildItem -Path $backupPath -Filter "*.backup" -File |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $latestBackup) {
    throw "В папке резервных копий нет файлов .backup."
}

$restoreDatabase = "${dbName}_test"

$previousPassword = $env:PGPASSWORD
$env:PGPASSWORD = $dbPassword

try {
    Write-Host ""
    Write-Host "Проверка восстановления последнего бэкапа" -ForegroundColor Cyan
    Write-Host "Бэкап: $($latestBackup.FullName)"
    Write-Host "Тестовая база: $restoreDatabase"
    Write-Host ""
    Write-Host "Основная база '$dbName' не изменяется."
    Write-Host "Тестовая база '$restoreDatabase' будет временно очищена."
    Write-Host ""

    & $psqlPath `
        --host=$dbHost `
        --port=$dbPort `
        --username=$dbUser `
        --dbname=$restoreDatabase `
        --no-password `
        --command="SELECT 1;" `
        1>$null

    if ($LASTEXITCODE -ne 0) {
        $message = "Не удалось подключиться к тестовой базе '$restoreDatabase'. Сначала запустите backend-тесты, чтобы она была создана."
        throw $message
    }

    & $psqlPath `
        --host=$dbHost `
        --port=$dbPort `
        --username=$dbUser `
        --dbname=$restoreDatabase `
        --no-password `
        --command="SET client_min_messages TO warning; DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;" `
        1>$null

    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось очистить тестовую базу. Код: $LASTEXITCODE."
    }

    & $pgRestorePath `
        --host=$dbHost `
        --port=$dbPort `
        --username=$dbUser `
        --dbname=$restoreDatabase `
        --no-owner `
        --no-privileges `
        --exit-on-error `
        --no-password `
        $latestBackup.FullName

    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось восстановить бэкап. Код: $LASTEXITCODE."
    }

    $tableCountRaw = & $psqlPath `
        --host=$dbHost `
        --port=$dbPort `
        --username=$dbUser `
        --dbname=$restoreDatabase `
        --no-password `
        --tuples-only `
        --no-align `
        --command="SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"

    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось проверить восстановленную базу. Код: $LASTEXITCODE."
    }

    $tableCountText = ($tableCountRaw | Out-String).Trim()
    $tableCount = 0

    if (-not [int]::TryParse($tableCountText, [ref]$tableCount)) {
        throw "Не удалось определить количество таблиц в восстановленной базе."
    }

    if ($tableCount -le 0) {
        throw "В восстановленной базе не найдено таблиц."
    }

    $requiredTablesRaw = & $psqlPath `
        --host=$dbHost `
        --port=$dbPort `
        --username=$dbUser `
        --dbname=$restoreDatabase `
        --no-password `
        --tuples-only `
        --no-align `
        --command="SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('products', 'inventory_balances', 'booking_notes', 'prizes', 'debts');"

    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось проверить основные таблицы. Код: $LASTEXITCODE."
    }

    $requiredTablesText = ($requiredTablesRaw | Out-String).Trim()
    $requiredTablesCount = 0

    if (-not [int]::TryParse($requiredTablesText, [ref]$requiredTablesCount)) {
        throw "Не удалось проверить основные таблицы."
    }

    if ($requiredTablesCount -lt 5) {
        throw "В восстановленной базе отсутствует часть основных таблиц."
    }

    Write-Host ""
    Write-Host "Проверка прошла успешно." -ForegroundColor Green
    Write-Host "Найдено таблиц: $tableCount"
    Write-Host "Основные таблицы на месте."
    Write-Host "Основная база '$dbName' не изменялась."
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "Проверка восстановления не пройдена." -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host ""
    exit 1
}
finally {
    $previousErrorActionPreference = (
        $ErrorActionPreference
    )

    $ErrorActionPreference = "Continue"

    & $psqlPath `
        --host=$dbHost `
        --port=$dbPort `
        --username=$dbUser `
        --dbname=$restoreDatabase `
        --no-password `
        --command="SET client_min_messages TO warning; DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;" `
        1>$null `
        2>$null

    $ErrorActionPreference = (
        $previousErrorActionPreference
    )

    if ($null -eq $previousPassword) {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }
    else {
        $env:PGPASSWORD = $previousPassword
    }
}

exit 0
