# Скрипт для просмотра логов бота в реальном времени
Write-Host "=== Логи бота systtechbot ===" -ForegroundColor Cyan
Write-Host "Нажмите Ctrl+C для остановки" -ForegroundColor Yellow
Write-Host ""
Get-Content bot.log -Wait -Tail 20

