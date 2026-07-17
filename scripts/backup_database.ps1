param(
    [int]$RetentionDays = 7
)

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

    throw "$ToolName не найден. Проверьте папку C:\Program Files\PostgreSQL\<версия>\bin."
}

$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot "backend\.env"

$envValues = Get-EnvValues -Path $envPath

$dbHost = Get-RequiredValue -Values $envValues -Name "DB_HOST"
$dbPort = Get-RequiredValue -Values $envValues -Name "DB_PORT"
$dbName = Get-RequiredValue -Values $envValues -Name "DB_NAME"
$dbUser = Get-RequiredValue -Values $envValues -Name "DB_USER"
$dbPassword = Get-RequiredValue -Values $envValues -Name "DB_PASSWORD"

$pgDumpPath = Find-PostgreSqlTool -ToolName "pg_dump.exe"

$documentsPath = [Environment]::GetFolderPath("MyDocuments")
$backupRoot = Join-Path $documentsPath "CyberClub Manager Pro Backups"
$databaseBackupPath = Join-Path $backupRoot "PostgreSQL"
$logPath = Join-Path $backupRoot "Logs"

New-Item -ItemType Directory -Path $databaseBackupPath -Force | Out-Null
New-Item -ItemType Directory -Path $logPath -Force | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$safeDatabaseName = $dbName -replace '[^a-zA-Z0-9_.-]', "_"
$backupFile = Join-Path $databaseBackupPath "${safeDatabaseName}_${timestamp}.backup"
$logFile = Join-Path $logPath "backup_${timestamp}.log"

$previousPassword = $env:PGPASSWORD
$env:PGPASSWORD = $dbPassword

try {
    @(
        "CyberClub Manager Pro PostgreSQL backup"
        "Дата: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        "База: $dbName"
        "Сервер: ${dbHost}:${dbPort}"
        "Файл: $backupFile"
        ""
    ) | Out-File -LiteralPath $logFile -Encoding utf8

    $arguments = @(
        "--host=$dbHost"
        "--port=$dbPort"
        "--username=$dbUser"
        "--dbname=$dbName"
        "--format=custom"
        "--compress=6"
        "--no-password"
        "--file=$backupFile"
    )

    & $pgDumpPath @arguments 2>> $logFile

    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump завершился с кодом $LASTEXITCODE."
    }

    $backupExists = Test-Path -LiteralPath $backupFile

    if (-not $backupExists) {
        throw "Файл резервной копии не был создан."
    }

    $backupItem = Get-Item -LiteralPath $backupFile

    if ($backupItem.Length -le 0) {
        throw "Файл резервной копии оказался пустым."
    }

    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)

    Get-ChildItem -Path $databaseBackupPath -Filter "*.backup" -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.LastWriteTime -lt $cutoffDate
        } |
        Remove-Item -Force -ErrorAction SilentlyContinue

    Get-ChildItem -Path $logPath -Filter "*.log" -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.LastWriteTime -lt $cutoffDate
        } |
        Remove-Item -Force -ErrorAction SilentlyContinue

    $backupSizeMb = [Math]::Round($backupItem.Length / 1MB, 2)

    "Успешно. Размер: $backupSizeMb МБ" |
        Out-File -LiteralPath $logFile -Encoding utf8 -Append

    Write-Host ""
    Write-Host "Резервная копия создана." -ForegroundColor Green
    Write-Host "Файл: $backupFile"
    Write-Host "Размер: $backupSizeMb МБ"
    Write-Host "Хранение: последние $RetentionDays дней"
    Write-Host ""

    exit 0
}
catch {
    if (Test-Path -LiteralPath $backupFile) {
        Remove-Item -LiteralPath $backupFile -Force -ErrorAction SilentlyContinue
    }

    $errorText = $_.Exception.Message

    "ОШИБКА: $errorText" |
        Out-File -LiteralPath $logFile -Encoding utf8 -Append

    Write-Host ""
    Write-Host "Не удалось создать резервную копию." -ForegroundColor Red
    Write-Host $errorText
    Write-Host "Лог: $logFile"
    Write-Host ""

    exit 1
}
finally {
    if ($null -eq $previousPassword) {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }
    else {
        $env:PGPASSWORD = $previousPassword
    }
}
