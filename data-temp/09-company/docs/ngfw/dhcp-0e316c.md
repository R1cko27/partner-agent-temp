---
заголовок: DHCP
url: https://docs.usergate.com/dhcp_802.html
получено: 2026-11-20 16:15 +0700
продукт: NGFW
версия: 7.x
раздел: DHCP
id_статьи: 802
обновлено: 26 Mar, 2024
ревизия: 3
---

# DHCP

Documentation:
Раздел находится на уровне
network dhcp
Для создания подсети DHCP, используется команда:
Admin@nodename# create network dhcp
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
gateway
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
Admin@nodename# set network dhcp <dhcp-name>
Параметры, информацию о которых можно обновить, аналогичны параметрам, доступным при создании.
Для удаления подсети:
Admin@nodename# delete network dhcp <dhcp-name>
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
Admin@nodename# show network dhcp
или об определённой подсети DHCP:
Admin@nodename# show network dhcp <dhcp-name>
v7.x
Шлюзы
DNS-настройки

## Источник

https://docs.usergate.com/dhcp_802.html
