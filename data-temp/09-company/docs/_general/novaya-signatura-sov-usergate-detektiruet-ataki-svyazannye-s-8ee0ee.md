---
заголовок: Новая сигнатура СОВ UserGate детектирует атаки, связанные с уязвимостью в продукте Мicrosoft Exchange Server (CVE-2021-42321)
url: https://usergate.com/security-reports/new-signature-cve-2021-42321-6257/
источник: основной сайт
получено: 2026-11-20 17:35 +0700
раздел: Новости
крошки: uFactor / Новости
---

# Новая сигнатура СОВ UserGate детектирует атаки, связанные с уязвимостью в продукте Мicrosoft Exchange Server (CVE-2021-42321)

25.11.2021
Центр мониторинга и реагирования на киберугрозы UserGate добавил в «Систему Обнаружения Вторжений» (СОВ) UserGate новую сигнатуру, позволяющую детектировать атаки с использованием уязвимости нулевого дня CVE-2021-42321.
В октябре компания Microsoft анонсировала новую уязвимость CVSS 8.8 (CVE-2021-42321). Уязвимость позволяет выполнить произвольный код с правами системы при наличии хотя бы одной действующей учетной записи на сервере Microsoft Exchange Server.
Уязвимые продукты:
Microsoft Exchange Server 2016;
Microsoft Exchange Server 2010;
Microsoft Exchange Server 2013;
Microsoft Exchange Server MAPI Client and Collaboration Data Objects 1.2.1;
Microsoft Exchange Server 2000;
Microsoft Exchange Server MAPI Client and Collaboration Data Objects 2.x;
Microsoft Exchange Server 2007;
Microsoft Exchange Server 2003.
Уязвимые версии:
Microsoft Exchange Server версии 2016: 2016 Cumulative Update 19, 2016 Cumulative Update 18, 2016 Cumulative Update 17, 2016 Cumulative Update 16, 2016 Cumulative Update 15, 2016 Cumulative Update 14, 2016 Cumulative Update 13, 2016 Cumulative Update 12, 2016 Cumulative Update 11, 2016 Cumulative Update 10, 2016 Cumulative Update 9, 2016 Cumulative Update 8, 2016 Cumulative Update 7, 2016 Cumulative Update 6, 2016 Cumulative Update 5, 2016 Cumulative Update 4, 2016 Cumulative Update 3, 2016 Cumulative Update 2, 2016 Cumulative Update 1;
Microsoft Exchange Server версии 2019: 2019 Cumulative Update 8, 2019 Cumulative Update 7, 2019 Cumulative Update 6, 2019 Cumulative Update 5, 2019 Cumulative Update 4, 2019 Cumulative Update 3, 2019 Cumulative Update 2, 2019 Cumulative Update 1.
«Система Обнаружения Вторжений» (СОВ) в составе UserGate NGFW детектирует и блокирует сеансы, связанные с этой уязвимостью автоматически.
Специалисты центра мониторинга и реагирования на киберугрозы UserGate рекомендуют пользователям следующие действия:
Установить  последнюю версию ПО с сайта производителя.
Проверить актуальность подписки на модуль Security Updates. При использовании профиля сигнатур UserGate, все новые сигнатуры начинают работать автоматически.
Провести поиск специфичного для данной атаки события командой: «
Get-WinEvent -FilterHashtable @{ LogName='Application'; ProviderName='MSExchange Common'; Level=2 } | Where-Object { $_.Message -like "*BinaryFormatter.Deserialize*" }
За дополнительной информацией обращайтесь к нашим специалистам:
ufactor@usergate.com

## �?сточник

https://usergate.com/security-reports/new-signature-cve-2021-42321-6257/
