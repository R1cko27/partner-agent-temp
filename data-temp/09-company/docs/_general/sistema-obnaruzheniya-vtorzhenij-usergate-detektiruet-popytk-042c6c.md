---
заголовок: Система обнаружения вторжений UserGate детектирует попытки эксплуатации уязвимости в реализации ICMP для ОС Windows
url: https://usergate.com/security-reports/cve-2023-23415-6242/
источник: основной сайт
получено: 2026-11-20 17:34 +0700
раздел: Новости
крошки: uFactor / Новости
---

# Система обнаружения вторжений UserGate детектирует попытки эксплуатации уязвимости в реализации ICMP для ОС Windows

29.03.2023
Центр Мониторинга и реагирования UserGate добавил в Систему обнаружения вторжений UserGate (IDPS) в версии NGFW 7.0 новую сигнатуру, позволяющую детектировать эксплуатацию уязвимости в реализации Internet Control Message Protocol (ICMP) от Microsoft в ОС Windows.
В подверженных версиях Windows, драйвер tcpip.sys имеет уязвимость в управлении памятью. Она возникает при обработке фрагментированных ICMP-пакетов с сообщением об ошибке, которые содержат вредоносные параметры IP-заголовка. Эта уязвимость позволяет удаленному злоумышленнику вызвать сбой системы Windows или может привести к удаленному выполнению вредоносного кода в случае, если на целевой машине запущено приложение, которое использует сырой сокет (raw socket).
Рейтинг согласно CVSSv3.1 — 9.8
Уязвимости присвоены идентификаторы CVE-2023-23415;BDU:2023-01227
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
Специалисты Центра мониторинга и реагирования на киберугрозы UserGate рекомендуют пользователям следующие действия:
Пользователям UserGate NGFW v. 7:
- установить последние обновления с сайта производителя ОС;
- проверить актуальность подписки на модуль Security Updates;
- добавить в блокирующее правило IDPS сигнатуру "Windows tcpip.sys driver Remote Code Execution".
UserGate NGFW 7.0 c подпиской на Систему обнаружения вторжений (СОВ) детектируют и блокируют сеансы, связанные с этой уязвимостью.
Пользователям UserGate NGFW v. 6:
– установить последние обновления с сайта производителя ОС;
– убедиться, что на зоне внутренней сети отсутствует разрешение для ICMP-трафика или создать запрещающее ICMP-трафик правило МЭ на внутренней зоне.
За дополнительной информацией обращайтесь к нашим специалистам:
ufactor@usergate.com

## �?сточник

https://usergate.com/security-reports/cve-2023-23415-6242/
