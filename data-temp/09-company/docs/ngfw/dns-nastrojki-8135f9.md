---
заголовок: DNS-настройки
url: https://docs.usergate.com/dns-nastrojki_214.html
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 7.0.1
раздел: DNS-настройки
id_статьи: 214
обновлено: 03 Nov, 2022
ревизия: 1
---

# DNS-настройки

Содержание:
Documentation:
Раздел находится на уровне
network dns
Настройка системных DNS-серверов
Настройка системных серверов DNS производится на уровне
network dns system-dns-servers
Для добавления новых DNS-серверов или обновления существующего списка используются следующие команды:
Admin@UGOS# set network dns system-dns-servers + [ <ip> <ip> ... ]
Admin@UGOS# set network dns system-dns-servers [ <ip> <ip> ... ]
Для удаления всего списка адресов серверов DNS:
Admin@UGOS# delete network dns system-dns-servers
Для удаления определённых серверов:
Admin@UGOS# delete network dns system-dns-servers [ <ip> <ip> ... ]
Для отображения списка системных DNS-серверов используется команда:
Admin@UGOS# show network dns system-dns-servers
Настройка DNS-прокси
DNS-прокси настраивается на уровне
network dns proxy-settings
Для обновления настроек DNS-прокси используется следующая команда:
Admin@UGOS# set network dns proxy-settings
Далее необходимо указать параметры, значения которых необходимо изменить:
Параметр
Описание
filtering
Фильтрация DNS-запросов:
off
caching
Кэширование ответов DNS:
off
limit
Ограничение количества DNS-запросов в секунду для каждого пользователя (значение по умолчанию: 100).
max-ttl
Максимально возможное время жизни для записей DNS.
recursive
Осуществление рекурсивных DNS-запросов:
off
dns-timeout
Время до следующей попытки отправления запроса на DNS-сервера (указывается в миллисекундах).
a-aaaa-unknown
Ответы только на запросы на записи A и AAAA от неизвестных пользователей. Это позволяет эффективно блокировать попытки организации VPN поверх протокола DNS:
off
retries
Количество попыток DNS-запроса.
factory-defaults
Сброс до заводских настроек значения выбранного параметра (параметры представлены в данной таблице) или всех параметров (
all
Чтобы просмотреть настройки DNS-прокси:
Admin@UGOS# show network dns proxy-settings
Параметры, значения которых можно просмотреть, представлены в таблице выше.
Настройка правил DNS
Правила DNS настраиваются на уровне
network dns rules
с использованием UPL. Подробнее о структуре команд читайте в разделе
Настройка правил с использованием UPL
Параметры правил DNS:
Параметр
Описание
PASS
Действие для создания правила с помощью UPL.
enabled
Включение/отключение использования правила:
enabled(yes)
или
enabled(true)
enabled(no)
или
enabled(false)
name
Название правила.
Например:
name("DNS rule example")
desc
Описание правила DNS-прокси.
Например:
desc("DNS rule example set via CLI")
url.domain
Список доменов, на которые необходимо перенаправлять. Допускается использование звёздочки (*) для указания шаблона доменов.
Чтобы указать список доменов:
url.domain = "*.example.com"
dns_server
Список IP-адресов DNS-серверов, куда необходимо пересылать запросы на указанные домены.
Для указания сервера:
dns_server(1.2.3.4)
Настройка статистических записей DNS-прокси
Раздел находится на уровне
network dns static-records
Для добавления статической DNS-записи предназначена команда:
Admin@UGOS# create network dns static-records
Далее указываются параметры:
Параметр
Описание
enabled
Включение/отключение использования статической записи:
off
name
Название записи.
description
Описание DNS-записи.
domain
FQDN (Fully Qualified Name) статической записи, например,
www.example.com
static-dns-ips
Список IP-адресов, которые сервер UserGate будет возвращать при запросе данного FQDN.
Для обновления информации о статических DNS-записях:
Admin@UGOS# set network dns static-records <static-record-name>
Список параметров, доступных для изменения, аналогичен списку команды
create
Для удаления статической записи:
Admin@UGOS# delete network dns static-records <static-record-name>
Также возможно удаление из статической записи только значений параметра
static-dns-ips
Команда
Admin@UGOS# show network dns static-records
отобразит информацию о всех существующих статических DNS-записях. Для отображения информации об определённой записи:
Admin@UGOS# show network dns static-records <static-record-name>
v7.x
DHCP
Настройка виртуальных маршрутизаторов

## Источник

https://docs.usergate.com/dns-nastrojki_214.html
