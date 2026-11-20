---
заголовок: DHCP
url: https://docs.usergate.com/dhcp_213.html
источник: портал документации
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 7.0.1
раздел: DHCP
id_статьи: 213
обновлено: 12 Jan, 2023
ревизия: 3
---

# DHCP

Documentation:
Раздел находится на уровне
network dhcp
Для создания подсети DHCP, используется команда:
Admin@UGOS# create network dhcp
Далее необходимо указание параметров:
Параметр
Описание
enabled
Включение/отключение использования данного диапазона IP-адресов:
off
name
Название подсети.
description
Описание подсети.
node-name
Выбор узла кластера, на котором создается данный диапазон.
interface
Интерфейс сервера, на котором будут раздаваться IP-адреса из создаваемого диапазона.
ip-range
Диапазон IP-адресов, выдаваемый клиентам DHCP. Диапазон задаётся в формате: <IP_start-IP_end>.
mask
Маска подсети, выдаваемая клиентам DHCP.
expiration-time
Время в секундах, на которое выдаются IP-адреса.
domain
Название домена, выдаваемое клиентам DHCP.
gateway-address
IP-адрес шлюза, выдаваемый клиентам DHCP.
dns-servers
IP-адрес DNS-серверов, выдаваемых клиентам DHCP.
reserved-hosts
MAC-адреса и сопоставленные с ними IP-адреса:
mac
: MAC-адрес.
: IP-адрес, сопоставленный MAC-адресу.
hostname
: имя хоста.
ignored-mac
Список MAC-адресов, игнорируемых DHCP-сервером.
pxe-boot-ip
Адрес сервера PXE.
pxe-boot-filename
Название файла для загрузки с PXE-сервера.
options
Номер опции и ее значение:
code
: номер опции DHCP.
values
: значение опции.
Обновление существующей DHCP-подсети:
Admin@UGOS# set network dhcp <dhcp-name>
Параметры, информацию о которых можно обновить, аналогичны параметрам, доступным при создании, кроме параметров
node-name
interface
- изменение значений данных параметров недоступно.
Для удаления подсети:
Admin@UGOS# delete network dhcp <dhcp-name>
Также доступно удаление отдельных параметров подсети DHCP:
dns-servers
ignored-mac
reserved-hosts
(необходимо указать все три значения:
mac
hostname
options
(необходимо указать оба значения:
code
values
Чтобы отобразить информацию о всех созданных подсетях:
Admin@UGOS# show network dhcp
или об определённой подсети DHCP:
Admin@UGOS# show network dhcp <dhcp-name>
v7.x
Шлюзы
DNS-настройки

## Источник

https://docs.usergate.com/dhcp_213.html
