---
заголовок: DNS-настройки
url: https://docs.usergate.com/dns-nastrojki_803.html
получено: 2026-11-20 16:15 +0700
продукт: NGFW
версия: 7.x
раздел: DNS-настройки
id_статьи: 803
обновлено: 27 Jun, 2025
ревизия: 14
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
Admin@nodename# set network dns system-dns-servers ip [ <ip> <ip> ... ]
Для удаления всего списка адресов серверов DNS:
Admin@nodename# delete network dns system-dns-servers
Для удаления определённых серверов:
Admin@nodename# delete network dns system-dns-servers ip [ <ip> <ip> ... ]
Для отображения списка системных DNS-серверов используется команда:
Admin@nodename# show network dns system-dns-servers
Настройка DNS-прокси
DNS-прокси настраивается на уровне
network dns proxy-settings
Для редактирования настроек DNS-прокси используется следующая команда:
Admin@nodename# set network dns proxy-settings
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
Пример команды редактирования параметров DNS-proxy:
Admin@nodename# set network dns proxy-settings limit 10 dns-timeout 10
Чтобы просмотреть настройки DNS-прокси:
Admin@nodename# show network dns proxy-settings
Настройка правил DNS
Внимание!
NGFW не может работать в роли DNS сервера. Предусмотрена только роль DNS proxy. При указании в правилах DNS адреса самого NGFW, возможно образование DNS петли, со всеми вытекающими последствиями.
Правила DNS настраиваются на уровне
network dns rules
с использованием UPL. Подробнее о структуре команд читайте в разделе
UserGate Policy Language
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
Пример создания правила DNS c использованием UPL:
Admin@nodename# create network dns rules 1 upl-rule OK \
...url.domain = "*.example.com" \
...dns_server(1.2.3.4) \
...name("DNS rule example") \
...desc("DNS rule example description over CLI") \
...enabled(true) \
...
Admin@nodename#
Admin@nodename# show network dns rules
% ----------------- 1 -----------------
OK \
url.domain = "*.example.com" \
dns_server(1.2.3.4) \
desc("DNS rule example description over CLI") \
enabled(true) \
id("0f83e1bb-0aa5-4f42-8eeb-9c4ffa30c04a") \
name("DNS rule example")
Настройка статических записей DNS-прокси
Раздел находится на уровне
network dns static-records
Для добавления статической DNS-записи предназначена команда:
Admin@nodename# create network dns static-records
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
ips
Список IP-адресов, которые сервер UserGate будет возвращать при запросе данного FQDN.
Команда
Admin@nodename# show network dns static-records
отобразит информацию о всех существующих статических DNS-записях. Для отображения информации об определённой записи:
Admin@nodename# show network dns static-records <static-record-name>
Пример создания статической записи DNS:
Admin@nodename# create network dns static-records name "Test DNS static record" description "Test DNS static record description" enabled on domain example.com ips [ 10.10.0.100 ]
Admin@nodename#
Admin@nodename# show network dns static-records
Test DNS static record
name             : Test DNS static record
description      : Test DNS static record description
domain           : example.com
ips              : 10.10.0.100
enabled          : on
Для редактирования информации о статических записях DNS:
Admin@nodename# set network dns static-records <static-record-name>
Список параметров, доступных для изменения, аналогичен списку команды
create
Пример редактирования ранее созданной статической записи DNS:
Admin@nodename# set network dns static-records "Test DNS static record" ips [ 10.10.0.101 ]
Admin@nodename# show network dns static-records "Test DNS static record"
name             : Test DNS static record
description      : Test DNS static record description
domain           : example.com
ips              : 10.10.0.100; 10.10.0.101
enabled          : on
Для удаления статической записи:
Admin@nodename# delete network dns static-records <static-record-name>
Также возможно удаление из статической записи только значений параметра
ips
Пример удаления значения параметра
ips
в ранее созданной записи и удаления всей статической записи DNS.
Admin@nodename# delete network dns static-records "Test DNS static record" ips [ 10.10.0.101 ]
Admin@nodename# show network dns static-records "Test DNS static record"
name             : Test DNS static record
description      : Test DNS static record description
domain           : example.com
ips              : 10.10.0.100
enabled          : on
Admin@nodename# delete network dns static-records "Test DNS static record"
Admin@nodename# show network dns static-records
Admin@nodename#
v7.x
DHCP
Настройка виртуальных маршрутизаторов

## Источник

https://docs.usergate.com/dns-nastrojki_803.html
