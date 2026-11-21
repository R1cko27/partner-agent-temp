# Чистая пересборка Chroma с нуля.
#
#   .\tools\rebuild_chroma.ps1
#
# Скрипт:
#   1. проверяет, что порт 8001 свободен (сервер остановлен);
#   2. удаляет повреждённые storage\chroma и storage\chroma-v2;
#   3. ставит в .env CHROMA_SUBDIR=chroma;
#   4. запускает полную сборку py ingest.py;
#   5. показывает итоговые счётчики и подсказывает, что проверить.

param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$busy = Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue
if ($busy) {
    Write-Host "Порт 8001 занят — похоже, запущен app.py." -ForegroundColor Yellow
    Write-Host "Остановите сервер (Ctrl+C в его окне) и повторите." -ForegroundColor Yellow
    if (-not $Force) { exit 1 }
    Write-Host "Включён -Force: продолжаю, но удаление может не сработать." -ForegroundColor Yellow
}

foreach ($dir in @('storage\chroma', 'storage\chroma-v2', 'storage\_chroma_check', 'storage\chroma-probe', 'storage\chroma-probe2')) {
    if (Test-Path $dir) {
        try {
            Remove-Item $dir -Recurse -Force
            Write-Host "удалено: $dir"
        } catch {
            Write-Host "не удалось удалить $dir — вероятно, файл занят процессом" -ForegroundColor Red
            exit 1
        }
    }
}

$envPath = '.env'
$envText = Get-Content $envPath -Raw -Encoding utf8
if ($envText -match '(?m)^CHROMA_SUBDIR=') {
    $envText = $envText -replace '(?m)^CHROMA_SUBDIR=.*$', 'CHROMA_SUBDIR=chroma'
} else {
    $envText = $envText.TrimEnd() + "`r`n`r`n# Хранилище векторов`r`nCHROMA_SUBDIR=chroma`r`n"
}
Set-Content -Path $envPath -Value $envText -Encoding utf8
Write-Host "в .env: CHROMA_SUBDIR=chroma"

Write-Host "`nЗапускаю полную сборку. Векторы возьмутся из кеша, запись в Chroma займёт несколько минут.`n" -ForegroundColor Cyan
py ingest.py
$code = $LASTEXITCODE
if ($code -ne 0) {
    Write-Host "Сборка завершилась с кодом $code" -ForegroundColor Red
    exit $code
}

Write-Host "`nПроверка:`n" -ForegroundColor Cyan
py -c "import json,pathlib; m=json.loads(pathlib.Path('storage/index/meta.json').read_text(encoding='utf-8')); print('фрагментов:', m.get('chunks'), '| векторов:', m.get('vectors'), '| embedding:', m.get('embedding'))"
py tools\check_chroma.py

Write-Host "`nДальше: запустите py app.py и задайте вопрос. В логе не должно быть строки «Chroma недоступна»." -ForegroundColor Green
