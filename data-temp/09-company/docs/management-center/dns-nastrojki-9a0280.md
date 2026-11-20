---
заголовок: DNS-настройки
url: https://docs.usergate.com/dns-nastrojki_1409.html
получено: 2026-11-20 16:32 +0700
продукт: Management Center
версия: 7.x
раздел: Настройка сети
id_статьи: 1409
обновлено: 21 Mar, 2024
ревизия: 4
крошки: Главная / Документация / Management Center / Management Center 7.x Руководство администратора / Интерфейс командной строки / Настройка сети / DNS-настройки
---

# DNS-настройки

Documentation:
Настройка системных серверов DNS производится на уровне
network dns system-dns-servers
Для добавления новых DNS-серверов или обновления существующего списка используются следующие команды:
Admin/system@nodename# set network dns system-dns-servers ip [ <ip> <ip> ... ]
Для удаления всего списка адресов серверов DNS:
Admin/system@nodename# delete network dns system-dns-servers
Для удаления определённых серверов:
Admin/system@nodename# delete network dns system-dns-servers ip [ <ip> <ip> ... ]
Для отображения списка системных DNS-серверов используется команда:
Admin/system@nodename# show network dns
v7.x
Настройка маршрутизации
Настройка мониторинга

## Источник

https://docs.usergate.com/dns-nastrojki_1409.html
