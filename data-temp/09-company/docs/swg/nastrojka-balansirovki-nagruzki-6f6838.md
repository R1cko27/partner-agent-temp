---
заголовок: Настройка балансировки нагрузки
url: https://docs.usergate.com/nastrojka-balansirovki-nagruzki_2682.html
источник: портал документации
получено: 2026-11-20 16:27 +0700
продукт: SWG
версия: 7.5.x
раздел: Настройка балансировки нагрузки
id_статьи: 2682
обновлено: 17 Mar, 2026
ревизия: 5
---

# Настройка балансировки нагрузки

Содержание:
Technology: Firewall
Правила балансировки нагрузки настраиваются на уровне
network-policy load-balancing
с использованием синтаксиса UPL. Подробнее о структуре команд — в разделе «
UserGate Policy Language
Для отображения информации о всех балансировщиках используется команда:
Admin@nodename# show network-policy load-balancing
Настройка балансировщика TCP/UDP
Настройка балансировщика TPC/UDP выполняется на уровне
network-policy load-balancing tcp-udp
Для создания балансировщика нагрузки TCP/UDP используется команда:
Admin@nodename# create network-policy load-balancing tcp-udp <position> upl-rule
Параметры правил балансировки нагрузки TCP/UDP.
Параметр
Описание
Действие для создания правила с помощью UPL
name
Название правила балансировки.
Например:
name("TCP_UDP balancer")
enabled
Включение/отключение правила:
enabled(yes)
или
enabled(true)
enabled(no)
или
enabled(false)
desc
Описание правила.
Например:
desc("TCP_UDP balancing rule")
src.zone
Зона источника трафика.
Для указания зоны источника, например, Trusted:
src.zone = Trusted
Подробнее о настройке зон с использованием интерфейса командной строки — в разделе «
Зоны
src.ip
Добавление списков IP-адресов или доменов источника.
Для указания списка IP-адресов:
src.ip = lib.network()
; в скобках необходимо указать название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI — в разделе «
Настройка IP-адресов
Для указания списка доменов источника:
src.ip = lib.url()
; в скобках необходимо указать название URL, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки — в разделе «
Настройка списков URL
Например:
src.ip = lib.network("Test ip-list")
src.geoip
Указание Geo IP в качестве источника.
Например:
src.geoip = RU
url.address
IP-адрес виртуального сервера.
Например:
url.address = 10.10.0.20
url.port
Порт, для которого необходимо производить балансировку нагрузки.
Например:
url.port = 1812
service
Протокол — TCP или UDP, для которого необходимо производить балансировку нагрузки.
Например:
service = udp
scheduler
Методы распределения нагрузки на реальные серверы:
— round robin, каждое новое подключение передается на следующий сервер в списке, равномерно загружая все серверы.
wrr
— weighted round robin, работает аналогично Round robin, но загрузка реальных серверов осуществляется с учетом весовых коэффициентов, что позволяет распределить нагрузку с учетом производительности каждого сервера.
— least connections, новое подключение передается на сервер, на который в данный момент установлено наименьшее число соединений.
wlc
— weighted least connections, работает аналогично Least connections, но загрузка реальных серверов осуществляется с учетом весовых коэффициентов, что позволяет распределить нагрузку с учетом производительности каждого сервера.
Например:
scheduler(rr)
real_server
Реальные сервера, на которые будет перенаправляться трафик. Для сервера необходимо указать:
— IP-адрес сервера.
port
— порт сервера, на который будут перенаправлять запросы пользователей.
weight
— коэффициент, использующийся для неравномерного распределения нагрузки на реальные серверы.
mode
— режим:
gate
— режим Шлюз: для перенаправления трафика на виртуальный сервер используется маршрутизация.
masq
— режим Маскарадинг: для перенаправления трафика на виртуальный сервер используется DNAT.
masq-snat
— режим Маскарадинг с подменой IP-источника: режим аналогичен режиму Маскарадинг, но UserGate SWG подменяет IP-адрес источника на свой.
Например:
real_server(masq, 10.10.0.9:1812, 50)
ipvs_fallback
Настройка аварийного режима:
— IP-адрес сервера.
port
— порт сервера, на который будут пересылаться запросы пользователей.
mode
— режим:
gate
— режим Шлюз: для перенаправления трафика на виртуальный сервер используется маршрутизация.
masq
— режим Маскарадинг: для перенаправления трафика на виртуальный сервер используется DNAT.
masq-snat
— режим Маскарадинг с подменой IP-источника: режим аналогичен режиму Маскарадинг, но UserGate SWG подменяет IP-адрес источника на свой.
Например:
ipvs_fallback(masq, 10.10.100.100:1812)
monitor
Настройка мониторинга реальных серверов:
kind
— тип проверки:
ping
: проверка доступности узла с использованием утилиты ping.
connect
: проверка работоспособности узла путём установления TCP-соединения на определённый порт.
negotiate
: проверка работоспособности узла посылкой определенного HTTP- или DNS-запроса и сравнением полученного ответа с ожидаемым ответом.
service
— необходимо указать (HTTP или DNS) при использовании проверки типа
negotiate
request
— запрос необходимо указать при использовании проверки типа
negotiate
response
— ожидаемый ответ; необходимо указать при использовании проверки типа
negotiate
interval
— интервал времени, через который должна выполняться проверка.
timeout
— интервал времени ожидания ответа на проверку.
max-failures
— количество попыток проверки реальных серверов, по истечению которого сервер будет считаться неработоспособным и будет исключен из балансировки.
Например:
monitor_kind(ping) \
monitor_interval(60) \
monitor_timeout(60) \
monitor_failurecount(10) \
Команда для редактирования существующего правила балансировки нагрузки:
Admin@nodename# set network-policy load-balancing tcp-udp <position> upl-rule
Команда для отображения информации о всех правилах балансировки TCP/UDP:
Admin@nodename# show network-policy load-balancing tcp-udp
Команда для отображения информации об определённом правиле балансировки TCP/UDP:
Admin@nodename# show network-policy load-balancing tcp-udp <position>
Пример создания правила балансировщика нагрузки с использованием UPL:
Admin@nodename# create network-policy load-balancing tcp-udp 1 upl-rule OK \
...src.zone = Trusted \
...url.address = 10.10.0.20 \
...url.port = 1812 \
...service = udp \
...scheduler(rr) \
...real_server((gate, 10.10.0.9, 50), (gate, 10.10.0.8, 50)) \
...name(tcpudp_balancer1) \
...enabled(true)
...
Admin@nodename# show network-policy load-balancing tcp-udp
% ----------------- 1 -----------------
OK \
src.zone = Trusted \
url.address = 10.10.0.20 \
url.port = 1812 \
service = udp \
scheduler(rr) \
real_server((gate, 10.10.0.9, 50), (gate, 10.10.0.8, 50)) \
monitor_kind(ping) \
monitor_interval(60) \
monitor_timeout(60) \
monitor_failurecount(10) \
enabled(true) \
id(cbed6ed7-901e-4641-83a1-a05f82dae177) \
name(tcpudp_balancer1)
Команда для удаления существующего балансировщика нагрузки:
Admin@nodename# delete network-policy load-balancing tcp-udp <position>
Настройка балансировщика reverse-прокси
Настройка правил балансировки reverse-прокси выполняется на уровне
network-policy load-balancing reverse-proxy
Для создания правила балансировки reverse-прокси используется команда:
Admin@nodename# create network-policy load-balancing reverse-proxy <position> upl-rule
Параметры правил балансировки нагрузки reverse-proxy.
Параметр
Описание
PASS
Действие для создания правила с помощью UPL
enabled
Включение/отключение правила:
enabled(yes)
или
enabled(true)
enabled(no)
или
enabled(false)
name
Название правила балансировки.
Например:
name("RP balancer")
desc
Описание правила.
Например:
desc("Test reverse-proxy balancing rule")
profile
Указание профилей серверов reverse-proxy, на которые будет распределяться нагрузка. Подробнее о создании и настройке серверов  reverse-proxy с использованием CLI — в разделе «
Настройка серверов reverse-прокси
Например,
profile("Reverse proxy server1", "Reverse proxy server2")
Команда для редактирования параметров правила балансировки reverse-прокси:
Admin@nodename# set network-policy load-balancing reverse-proxy <position> upl-rule
Параметры, доступные для обновления, аналогичны параметрам, доступным при создании правила балансировки серверов reverse-прокси.
Команды для отображения информации о всех правилах балансировки reverse-proxy:
Admin@nodename# show network-policy load-balancing reverse-proxy
Команда для отображения информации об определённом правиле балансировки reverse-proxy:
Admin@nodename# show network-policy load-balancing reverse-proxy <position>
Пример создания правила балансировщика нагрузки reverse-proxy с использованием UPL:
Admin@nodename# create network-policy load-balancing reverse-proxy 1 upl-rule OK \
...profile("Reverse proxy server1", "Reverse proxy server2") \
...desc("Test reverse proxy balancing rule") \
...name(test_reversep1) \
...enabled(true)
...
Admin@nodename# show network-policy load-balancing reverse-proxy
% ----------------- 1 -----------------
OK \
profile("Reverse proxy server1", "Reverse proxy server2") \
desc("Test reverse proxy balancing rule") \
enabled(true) \
id("1ed892bb-26ee-4ab1-8a55-2f412ce8b55a") \
name(test_reversep1)
Команда для удаления существующего правила балансировки нагрузки reverse-proxy:
Admin@nodename# delete network-policy load-balancing reverse-proxy <position>
v7.x
Настройка правил NAT и маршрутизации
Настройка правил управления пропускной способностью

## Источник

https://docs.usergate.com/nastrojka-balansirovki-nagruzki_2682.html
