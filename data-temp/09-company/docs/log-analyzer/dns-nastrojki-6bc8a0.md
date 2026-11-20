---
заголовок: DNS-настройки
url: https://docs.usergate.com/dns-nastrojki_1442.html
получено: 2026-11-20 16:33 +0700
продукт: Log Analyzer
версия: 7.x
раздел: Настройка сети
id_статьи: 1442
обновлено: 21 Mar, 2024
ревизия: 1
крошки: Главная / Документация / Log Analyzer / Log Analyzer 7.x Руководство администратора / Интерфейс командной строки / Настройка сети / DNS-настройки
---

# DNS-настройки

Documentation:
Настройка системных серверов DNS производится на уровне
network dns system-dns-servers
Для добавления новых DNS-серверов или обновления существующего списка используются следующие команды:
Admin@nodename# set network dns system-dns-servers ip [ <ip> <ip> ... ]
Для удаления всего списка адресов серверов DNS:
Admin@nodename# delete network dns system-dns-servers
Для удаления определённых серверов:
Admin@nodename# delete network dns system-dns-servers ip [ <ip> <ip> ... ]
Для отображения списка системных DNS-серверов используется команда:
Admin@nodename# show network dns
v7.x
Настройка маршрутизации
Настройка библиотек

## Источник

https://docs.usergate.com/dns-nastrojki_1442.html
