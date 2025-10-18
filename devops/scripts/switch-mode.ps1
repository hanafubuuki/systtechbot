# PowerShell версия switch-mode.sh для Windows
# Использование:
#   .\switch-mode.ps1 local  - локальная сборка образов
#   .\switch-mode.ps1 prod   - использование образов из registry

param(
    [Parameter(Position=0)]
    [ValidateSet('local', 'prod', 'status', 'current', '')]
    [string]$Mode = ''
)

$DevopsDir = Split-Path -Parent $PSScriptRoot

function Print-Usage {
    Write-Host "Использование: .\switch-mode.ps1 {local|prod}" -ForegroundColor White
    Write-Host ""
    Write-Host "Режимы:"
    Write-Host "  local  - Локальная сборка образов (build from source)" -ForegroundColor Cyan
    Write-Host "  prod   - Использование образов из GitHub Container Registry" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Примеры:"
    Write-Host "  .\switch-mode.ps1 local   # Переключиться на локальную сборку"
    Write-Host "  .\switch-mode.ps1 prod    # Переключиться на production образы"
}

function Switch-ToLocal {
    Write-Host "Переключение в режим LOCAL (локальная сборка)..." -ForegroundColor Blue

    Push-Location $DevopsDir

    # Удаляем существующий симлинк или файл
    if (Test-Path "docker-compose.current.yml") {
        Remove-Item "docker-compose.current.yml" -Force
    }

    # Создаем симлинк (требует права администратора) или копируем
    try {
        New-Item -ItemType SymbolicLink -Path "docker-compose.current.yml" -Target "docker-compose.yml" -ErrorAction Stop | Out-Null
        Write-Host "* Создана символьная ссылка" -ForegroundColor Green
    }
    catch {
        Copy-Item "docker-compose.yml" "docker-compose.current.yml"
        Write-Host "* Файл скопирован (требуются права администратора для symlink)" -ForegroundColor Yellow
    }

    Pop-Location

    Write-Host "✓ Режим LOCAL активирован" -ForegroundColor Green
    Write-Host ""
    Write-Host "Теперь используется: docker-compose.yml (локальная сборка)"
    Write-Host ""
    Write-Host "Команды для запуска:"
    Write-Host "  cd devops"
    Write-Host "  docker-compose -f docker-compose.current.yml up --build"
}

function Switch-ToProd {
    Write-Host "Переключение в режим PROD (registry образы)..." -ForegroundColor Blue

    Push-Location $DevopsDir

    # Удаляем существующий симлинк или файл
    if (Test-Path "docker-compose.current.yml") {
        Remove-Item "docker-compose.current.yml" -Force
    }

    # Создаем симлинк (требует права администратора) или копируем
    try {
        New-Item -ItemType SymbolicLink -Path "docker-compose.current.yml" -Target "docker-compose.prod.yml" -ErrorAction Stop | Out-Null
        Write-Host "* Создана символьная ссылка" -ForegroundColor Green
    }
    catch {
        Copy-Item "docker-compose.prod.yml" "docker-compose.current.yml"
        Write-Host "* Файл скопирован (требуются права администратора для symlink)" -ForegroundColor Yellow
    }

    Pop-Location

    Write-Host "✓ Режим PROD активирован" -ForegroundColor Green
    Write-Host ""
    Write-Host "Теперь используется: docker-compose.prod.yml (registry образы)"
    Write-Host ""
    Write-Host "Команды для запуска:"
    Write-Host "  cd devops"
    Write-Host "  docker-compose -f docker-compose.current.yml pull  # Скачать образы"
    Write-Host "  docker-compose -f docker-compose.current.yml up    # Запустить"
    Write-Host ""
    Write-Host "Для использования конкретной версии:"
    Write-Host '  $env:IMAGE_TAG="sha-abc1234"; docker-compose -f docker-compose.current.yml up'
}

function Show-CurrentMode {
    Push-Location $DevopsDir

    if (Test-Path "docker-compose.current.yml") {
        $item = Get-Item "docker-compose.current.yml"

        Write-Host "Текущий режим:" -ForegroundColor Blue

        if ($item.LinkType -eq "SymbolicLink") {
            $target = $item.Target
            if ($target -like "*docker-compose.yml") {
                Write-Host "  LOCAL" -ForegroundColor Green -NoNewline
                Write-Host " (локальная сборка)"
            }
            elseif ($target -like "*docker-compose.prod.yml") {
                Write-Host "  PROD" -ForegroundColor Green -NoNewline
                Write-Host " (registry образы)"
            }
            else {
                Write-Host "  Неизвестный режим: $target" -ForegroundColor Yellow
            }
        }
        else {
            # Проверяем содержимое файла
            $content = Get-Content "docker-compose.current.yml" -Raw
            if ($content -match "build:") {
                Write-Host "  LOCAL" -ForegroundColor Green -NoNewline
                Write-Host " (локальная сборка, копия)"
            }
            elseif ($content -match "ghcr.io") {
                Write-Host "  PROD" -ForegroundColor Green -NoNewline
                Write-Host " (registry образы, копия)"
            }
        }
    }
    else {
        Write-Host "Режим не установлен (файл docker-compose.current.yml не создан)" -ForegroundColor Yellow
        Write-Host "Запустите: .\switch-mode.ps1 local  или  .\switch-mode.ps1 prod"
    }

    Pop-Location
}

# Главная логика
switch ($Mode) {
    'local' {
        Switch-ToLocal
    }
    'prod' {
        Switch-ToProd
    }
    { $_ -in 'status', 'current', '' } {
        Show-CurrentMode
    }
    default {
        Write-Host "Ошибка: Неизвестный режим '$Mode'" -ForegroundColor Red
        Write-Host ""
        Print-Usage
        exit 1
    }
}

