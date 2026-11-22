# Запуск связки «сайт на хостинге → агент на этом ПК».
#
#   .\deploy\start.ps1              # поднять агента и туннель, обновить config.js
#   .\deploy\start.ps1 -DryRun      # только проверить токен и config.js, без туннеля
#   .\deploy\start.ps1 -Port 8001   # другой порт агента
#
# Скрипт сам:
#   1. берёт (или создаёт) API_TOKEN и прописывает его в .env;
#   2. проверяет, запущен ли app.py, и при необходимости запускает;
#   3. поднимает временный туннель cloudflared и ловит выданный адрес;
#   4. записывает base и token в deploy\host\config.js.

param(
    [int]$Port = 8001,
    [switch]$Hosted,
    [switch]$DryRun,
    [string]$Cloudflared = "tools\cloudflared.exe"
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Get-Token {
    $line = Select-String -Path '.env' -Pattern '^API_TOKEN=' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($line) {
        $value = ($line.Line -replace '^API_TOKEN=', '').Trim()
        if ($value) { return $value }
    }
    $token = & ..\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
    $token = $token.Trim()
    if (Select-String -Path '.env' -Pattern '^API_TOKEN=' -Quiet -ErrorAction SilentlyContinue) {
        (Get-Content '.env' -Encoding utf8) -replace '^API_TOKEN=.*$', "API_TOKEN=$token" | Set-Content '.env' -Encoding utf8
    } else {
        Add-Content '.env' -Value "`n# Токен доступа к API из интернета`nAPI_TOKEN=$token" -Encoding utf8
    }
    Write-Host "Создан новый API_TOKEN и записан в .env" -ForegroundColor Yellow
    return $token
}

function Write-Config([string]$Base, [string]$Token) {
    $path = 'deploy\host\config.js'
    $escaped = $Base.TrimEnd('/')
    @"
// Адрес агента (туннель до вашего ПК) и токен доступа.
// Файл перезаписывается скриптом deploy\start.ps1.
window.__AGENT_API__ = {
  base: "$escaped",
  token: "$Token",
};
"@ | Set-Content $path -Encoding utf8
    Write-Host "Обновлён $path" -ForegroundColor Green
    Write-Host "  base:  $escaped"
    Write-Host "  token: $($Token.Substring(0, [Math]::Min(8, $Token.Length)))…"
}

function Test-Port([int]$Value) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Value/api/health" -UseBasicParsing -TimeoutSec 3
        return $response.StatusCode -eq 200
    } catch { return $false }
}

$token = Get-Token
Write-Host "API_TOKEN готов" -ForegroundColor Green

if ($DryRun) {
    Write-Config "https://REPLACE-ME.trycloudflare.com" $token
    Write-Host "`nПробный режим: туннель не запускался." -ForegroundColor Cyan
    exit 0
}

if (-not (Test-Path $Cloudflared)) {
    Write-Host "Не найден $Cloudflared." -ForegroundColor Red
    Write-Host "Скачайте: Invoke-WebRequest 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile $Cloudflared"
    exit 1
}

if (-not (Test-Port $Port)) {
    Write-Host "Агент не отвечает на 127.0.0.1:$Port — запускаю app.py в отдельном окне …"
    Start-Process -FilePath 'py' -ArgumentList 'app.py' -WorkingDirectory $root
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Seconds 1
        if (Test-Port $Port) { break }
    }
}
if (-not (Test-Port $Port)) {
    Write-Host "Агент так и не поднялся. Запустите вручную: py app.py" -ForegroundColor Red
    exit 1
}
Write-Host "Агент отвечает на 127.0.0.1:$Port" -ForegroundColor Green

$log = 'tools\_tunnel.log'
if (Test-Path $log) { Remove-Item $log -Force }

Write-Host "`nЗапускаю туннель. Адрес появится ниже через 5–15 секунд …`n" -ForegroundColor Cyan
$proc = Start-Process -FilePath $Cloudflared -ArgumentList 'tunnel', '--url', "http://127.0.0.1:$Port" -RedirectStandardOutput $log -RedirectStandardError "$log.err" -PassThru -WindowStyle Hidden

$url = $null
for ($i = 0; $i -lt 40; $i++) {
    Start-Sleep -Seconds 1
    foreach ($file in @($log, "$log.err")) {
        if (-not (Test-Path $file)) { continue }
        $match = Select-String -Path $file -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' -AllMatches | Select-Object -First 1
        if ($match) { $url = $matches = $match.Matches[0].Value; break }
    }
    if ($url) { break }
    if ($proc.HasExited) { break }
}

if (-not $url) {
    Write-Host "Не удалось получить адрес туннеля. Лог: $log" -ForegroundColor Red
    if (Test-Path $log) { Get-Content $log -Tail 20 }
    exit 1
}

# Если страница загружается с этого же туннеля или с localhost, API находится
# на том же источнике и base должен быть пустым. Адрес туннеля нужен только
# когда сама страница лежит на другом домене — на вашем сайте.
if ($Hosted) {
    Write-Config $url $token
} else {
    Write-Config "" $token
}

Write-Host "`nГотово. Проверьте адрес:" -ForegroundColor Cyan
Write-Host "  $url/api/health"
Write-Host "  Открыть интерфейс: $url"
Write-Host "  base в config.js: пустой, потому что страница на этом же адресе"
Write-Host "  Страница на своём домене: .\deploy\start.ps1 -Hosted"
Write-Host "`nСтраница на сайте должна открываться с base из config.js." -ForegroundColor Cyan
Write-Host "Туннель живёт, пока открыто это окно. Ctrl+C — остановить." -ForegroundColor Yellow
Write-Host "Процесс туннеля: PID $($proc.Id)"

try {
    while (-not $proc.HasExited) { Start-Sleep -Seconds 5 }
} finally {
    if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
}
