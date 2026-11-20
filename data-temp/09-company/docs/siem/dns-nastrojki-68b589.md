---
заголовок: DNS-настройки
url: https://docs.usergate.com/dns-nastrojki_1462.html
получено: 2026-11-20 16:27 +0700
продукт: SIEM
версия: 7.1.x
раздел: DNS-настройки
id_статьи: 1462
обновлено: 25 Mar, 2024
ревизия: 1
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

https://docs.usergate.com/dns-nastrojki_1462.html
