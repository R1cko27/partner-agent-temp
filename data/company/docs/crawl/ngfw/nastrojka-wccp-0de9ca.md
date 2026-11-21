---
заголовок: Настройка WCCP
url: https://docs.usergate.com/nastrojka-wccp_805.html
источник: портал документации
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка WCCP
id_статьи: 805
обновлено: 26 Mar, 2024
ревизия: 11
---

# Настройка WCCP

Documentation:
Настройка WCCP (Web Cache Communication Protocol) производится на уровне
network wccp
. Для создания сервисной группы WCCP используется следующая команда:
Admin@nodename# create network wccp <parameter>
Доступны параметры:
Параметр
Описание
enabled
Включение/отключение сервисной группы:
off
name
Название сервисной группы WCCP.
description
Описание сервисной группы.
password
Пароль, необходимый для аутентификации UserGate в сервисной группе. Пароль должен совпадать с паролем, указанным на серверах WCCP.
fwd-type
Способ перенаправления трафика с серверов WCCP на UserGate:
— используя перенаправление L2.В этом случае роутер (WCCP сервер) изменяет MAC-адрес назначения в пакете на адрес UserGate.
gre
— используя туннель GRE (Generic Routing Encapsulation).
Перенаправление L2 как правило требует меньшее количество ресурсов, чем GRE, но сервер WCCP и UserGate должны находиться в одном L2 сегменте. Не все типы серверов WCCP поддерживают работу с WCCP клиентами по L2.
ret-type
Способ перенаправления трафика с UserGate на серверы WCCP:
— используя перенаправление L2. В этом случае UserGate (WCCP клиент) изменяет MAC-адрес назначения в пакете на адрес роутера (WCCP сервер).
gre
— используя туннель GRE (Generic Routing Encapsulation).
Перенаправление L2 как правило требует меньшее количество ресурсов, чем GRE, но сервер WCCP и UserGate должны находиться в одном L2 сегменте. Не все типы серверов WCCP поддерживают работу с WCCP клиентами по L2.
service-group
Числовой идентификатор сервисной группы. Идентификатор сервисной группы должен быть одинаков на всех устройствах, входящих в группу.
priority
Приоритет группы. Если несколько сервисных групп применимы к трафику на сервере WCCP, то приоритет определяет порядок, в котором сервер будет распределять трафик на клиенты WCCP.
ports
Порты для перенаправления (порты назначения трафика). При необходимости указываются несколько портов в формате:
ports-to-redirect + [ 80 442 ]
Важно!
UserGate может применять фильтрацию только для перенаправленного TCP трафика с портами назначения 80, 443 (HTTP/HTTPS). Трафик, переданный на UserGate с другими портами, будет отправляться в интернет без фильтрации.
ports-source
Перенаправление трафика на основании значений портов источника:
off
protocol
Выбор протокола:
tcp
— Transmission Control Protocol (TCP).
udp
— User Datagram Protocol (UDP).
routers-lists
Список IP-адресов серверов WCCP.
Подробнее о создании списков IP-адресов с помощью CLI читайте в разделе
Настройка IP-адресов
routers-ips
IP-адреса серверов WCCP.
assignment-type
При наличии в сервисной группе нескольких WCCP-клиентов способ назначения определяет распределение трафика от WCCP-серверов по WCCP-клиентам.
hash
— распределение трафика на основе хэша, вычисляемому по указанным полям IP-пакета:
source-ip
— вычисление хэша по IP-адресу источника.
source-port
— вычисление хэша по порту источника.
dest-ip
— вычисление хэша по IP-адресу назначения.
dest-port
— вычисление хэша по порту назначения.
alt-source-ip
— вычисление альтернативного хэша по IP-адресу источника.
alt-source-port
– вычисление альтернативного хэша по порту источника.
alt-dest-ip
— вычисление альтернативного хэша по IP-адресу назначения.
alt-dest-port
— вычисление альтернативного хэша по порту назначения.
mask
— распределение трафика на основе вычисления операции AND между маской и выбранным заголовком пакета. При выборе маски проконсультируйтесь с документацией производителя сервера WCCP.
source-ip
— схема маскирования по IP-адресу источника.
source-port
— схема маскирования по порту источника.
dest-ip
— схема маскирования по IP-адресу назначения.
dest-port
— схема маскирования по порту назначения.
mask-value
— значение маски схемы маскирования. Для схемы маскирования по порту — 16 бит; по IP-адресу — 32 бита; указываются в шестнадцатеричном формате.
Для задания значений сервисной группы WCCP или обновления информации о ней:
Admin@nodename# set network wccp <service-group-name> <parameter>
Далее указываются параметры, значения которых необходимо обновить; параметры представлены в таблице выше.
Для просмотра информации о сервисной группе WCCP:
Admin@nodename# show network wccp <service-group-name>
Примеры команд создания и редактирования WCCP:
Admin@nodename# create network wccp name "Test service group" protocol tcp service-group 1 routers-ips [ 192.168.100.120 ] fwd-type l2 ret-type l2 ports [ 80 ] priority 1 password 12345
Admin@nodename# show network wccp "Test service group"
name               : Test service group
enabled            : off
fwd-type           : l2
ret-type           : l2
service-group      : 1
priority           : 1
protocol           : tcp
ports              : 80
assignment-type    : hash
source-ip          : off
source-port        : off
dest-ip            : off
dest-port          : off
alt-source-ip      : off
alt-source-port    : off
alt-dest-ip        : off
alt-dest-port      : off
routers-ips        : 192.168.100.120
Admin@nodename# set network wccp "Test service group" description "Test service group description" service-group 100
Admin@nodename# show network wccp "Test service group"
name               : Test service group
description        : Test service group description
enabled            : off
fwd-type           : l2
ret-type           : l2
service-group      : 100
priority           : 1
protocol           : tcp
ports              : 80
assignment-type    : hash
source-ip          : off
source-port        : off
dest-ip            : off
dest-port          : off
alt-source-ip      : off
alt-source-port    : off
alt-dest-ip        : off
alt-dest-port      : off
routers-ips        : 192.168.100.120
Удаление сервисной группы полностью или некоторых её параметров:
Admin@nodename# delete network wccp <service-group-name>
Параметры, доступные для удаления:
routers-lists
routers
ips
ports
v7.x
Настройка виртуальных маршрутизаторов
Настройка раздела Пользователи и устройства

## Источник

https://docs.usergate.com/nastrojka-wccp_805.html
