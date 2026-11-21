---
заголовок: Система обнаружения вторжений UserGate детектирует попытку эксплуатации уязвимости «QueueJumper» в сервисе Message Queuing для ОС Windows
url: https://usergate.com/security-reports/cve-2023-21554-6241/
источник: основной сайт
получено: 2026-11-20 17:34 +0700
раздел: Новости
крошки: uFactor / Новости
---

# Система обнаружения вторжений UserGate детектирует попытку эксплуатации уязвимости «QueueJumper» в сервисе Message Queuing для ОС Windows

17.04.2023
Центр мониторинга и реагирования UserGate добавил в Систему обнаружения вторжений UserGate (IDPS) новую сигнатуру, позволяющую детектировать попытку эксплуатации уязвимости  CVE-2023-21554 «QueueJumper» в сервисе Message Queuing в ОС Windows.
Microsoft Message Queuing (MSMQ) — это технология для асинхронной коммуникации между приложениями. По умолчанию сервис не установлен. MSMQ применяется при разработке приложений, которые работают в разнородных сетях или автономно. MSMQ широко используется как компонент middleware в enterprise-приложениях и полностью интегрирован в Microsoft.Net Framework. Уязвимость может быть использована как для первичного проникновения в сеть, так и для горизонтального перемещения.
Рейтинг согласно CVSSv3.1 — 9.8
Уязвимости присвоен идентификатор CVE-2023-21554
Подверженные версии:
Windows 10 for 32-bit Systems
Windows 10 for x64-based Systems
Windows 10 Version 1607 for 32-bit Systems
Windows 10 Version 1607 for x64-based Systems
Windows 10 Version 1809 for 32-bit Systems
Windows 10 Version 1809 for ARM64-based Systems
Windows 10 Version 1809 for x64-based Systems
Windows 10 Version 20H2 for 32-bit System
Windows 10 Version 20H2 for x64-based Systems
Windows 10 Version 21H2 for 32-bit Systems
Windows 10 Version 21H2 for ARM64-based Systems
Windows 10 Version 21H2 for x64-based Systems
Windows 10 Version 22H2 for 32-bit Systems
Windows 10 Version 22H2 for ARM64-based Systems
Windows 10 Version 22H2 for x64-based Systems
Windows 11 version 21H2 for ARM64-based Systems
Windows 11 version 21H2 for x64-based Systems
Windows 11 Version 22H2 for ARM64-based Systems
Windows 11 Version 22H2 for x64-based Systems
Windows Server 2008 for 32-bit Systems Service Pack 2
Windows Server 2008 for 32-bit Systems Service Pack 2 (Server Core installation)
Windows Server 2008 for x64-based Systems Service Pack 2
Windows Server 2008 for x64-based Systems Service Pack 2 (Server Core installation)
Windows Server 2008 R2 for x64-based Systems Service Pack 1
Windows Server 2008 R2 for x64-based Systems Service Pack 1 (Server Core installation)
Windows Server 2012
Windows Server 2012 (Server Core installation)
Windows Server 2012 R2
Windows Server 2012 R2 (Server Core installation)
Windows Server 2016
Windows Server 2016 (Server Core installation)
Windows Server 2019
Windows Server 2019 (Server Core installation)
Windows Server 2022
Windows Server 2022 (Server Core installation)
Рекомендации по защите:
— Установить последние обновления с сайта производителя ОС (
https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-21554
— Провести аудит информационных систем на предмет ПО, использующего данный сервис (processes.name = «mqsvc.exe», cmd.exe /c sc query mqsvc). На серверах во внутренней сети, где используется сервис, необходимо усилить мониторинг событий до установки патчей. Убедиться, что TCP порт 1801 не доступен из внешней сети (например, c помощью сканирования «nmap -Pn -p 1801 --open -n -vvv 192.168.0.0/24»).
— Проверить актуальность подписки на модуль Security Updates. При использовании профиля сигнатур UserGate все новые сигнатуры начинают работать автоматически.
— Создать правило СОВ с новой сигнатурой
Windows QueueJumper RCE
, если используется собственный профиль сигнатур.
За дополнительной информацией обращайтесь к нашим специалистам:
ufactor@usergate.com

## �?сточник

https://usergate.com/security-reports/cve-2023-21554-6241/
