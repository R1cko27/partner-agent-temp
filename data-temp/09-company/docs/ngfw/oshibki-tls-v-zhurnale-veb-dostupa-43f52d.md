---
заголовок: Ошибки TLS в журнале веб-доступа
url: https://docs.usergate.com/oshibki-tls-v-zhurnale-veb-dostupa_558.html
источник: портал документации
получено: 2026-11-20 16:14 +0700
продукт: NGFW
раздел: Ошибки TLS в журнале веб-доступа
id_статьи: 558
обновлено: 22 Feb, 2023
ревизия: 7
---

# Ошибки TLS в журнале веб-доступа

KnowledgeBase:
Задача
При использовании инспектирования SSL в журнале веб-доступа появляются ошибки
TLS Server Alert: Fatal - Bad Record Mac
TLS Server Alert: Fatal - Protocol Version
TLS Client Alert: Fatal - Unknown Ca
и т.п.
Решение
Ошибки
TLS Server Alert: Fatal - Bad Record Mac
TLS Server Alert: Fatal - Protocol Version
возвращают браузеры пользователей вследствие наличия ошибок конфигурации. Для обеспечения максимальной совместимости UserGate поставляется с созданными по умолчанию профилями SSL (подробнее читайте в главе
Профили SSL
Ошибка
TLS Client Alert: Fatal - Unknown Ca
возникает, если в браузеры пользователей не установлен сертификат для дешифрования SSL-трафика. Подробнее об установке сертификата читайте соответствующей
главе
руководства администратора.
v6.x
v7.x
Блокировка доступа через VPN
Выбор протокола PAP на MacOs

## Источник

https://docs.usergate.com/oshibki-tls-v-zhurnale-veb-dostupa_558.html
