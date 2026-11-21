"""Добавляет в start.ps1 режим -Hosted и пустой base по умолчанию."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("deploy/start.ps1")

PARAM_OLD = "param(\n    [int]$Port = 8001,"
PARAM_NEW = "param(\n    [int]$Port = 8001,\n    [switch]$Hosted,"

BASE_OLD = "Write-Config $url $token"
BASE_NEW = '''# Если страница загружается с этого же туннеля или с localhost, API находится
# на том же источнике и base должен быть пустым. Адрес туннеля нужен только
# когда сама страница лежит на другом домене — на вашем сайте.
if ($Hosted) {
    Write-Config $url $token
} else {
    Write-Config "" $token
}'''

HINT_OLD = 'Write-Host "  $url/api/health"'
HINT_NEW = '''Write-Host "  $url/api/health"
Write-Host "  Открыть интерфейс: $url"
Write-Host "  base в config.js: пустой, потому что страница на этом же адресе"
Write-Host "  Страница на своём домене: .\\deploy\\start.ps1 -Hosted"'''


def main() -> int:
    text = PATH.read_text(encoding="utf-8-sig")
    changed = []

    if "[switch]$Hosted" not in text:
        text = text.replace(PARAM_OLD, PARAM_NEW, 1)
        changed.append("параметр -Hosted")

    if "if ($Hosted)" not in text:
        text = text.replace(BASE_OLD, BASE_NEW, 1)
        changed.append("выбор base")

    if "Страница на своём домене" not in text:
        text = text.replace(HINT_OLD, HINT_NEW, 1)
        changed.append("подсказки")

    PATH.write_text(text, encoding="utf-8-sig")
    print("start.ps1:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
