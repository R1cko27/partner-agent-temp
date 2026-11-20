---
заголовок: Трассировка пакетов
url: https://docs.usergate.com/trassirovka-paketov_2319.html
получено: 2026-11-20 16:24 +0700
продукт: DCFW
версия: 8.x
раздел: Трассировка пакетов
id_статьи: 2319
обновлено: 15 Oct, 2025
ревизия: 21
---

# Трассировка пакетов

С помощью механизма трассировки можно анализировать прохождение сетевых пакетов через IP-стек и фильтрующие правила межсетевого экрана.
Настраивать режимы трассировки и просматривать ее результаты можно в режиме диагностики и мониторинга CLI на уровне
packet-tracing
Для настройки параметров трассировки используется команда:
Admin@nodename> setup packet-tracing <n> <parameters>
<n>
— порядковый номер задачи трассировки (0–9).
Параметры трассировки пакетов определены в таблице.
Параметр
Описание
bidir
Режим отслеживания пакетов:
off — отслеживаются пакеты с заданными параметрами.
on — отслеживаются пакеты с заданными значениями параметров и с инверсией значений источника и назначения для параметров IP-адреса и порта без учета входного интерфейса (ответные пакеты соединения)
count
Трассировка заданного количества пакетов (1–16)
device
Имя сетевого интерфейса (portX, tunnelX и т. д.), на котором включается отслеживание входящих пакетов с заданными параметрами
dport
Порт назначения трафика (1–65 535)
dst
IP-адрес назначения трафика. Форматы значений:
<ip> — например, 192.168.0.1;
<ip/mask> — например, 192.168.0.1/24
fin
Фильтрация TCP-пакетов с FIN-флагом (корректное завершение соединения):
on — включено;
off — отключено
mark
Фильтрация пакетов по меткам:
<xx> — метка в виде десятичного числа (10);
<0xx> — метка в виде восьмеричного числа (04);
<0xXX> — метка в виде шестнадцатеричного числа (0xAA);
<mark/mask> — метка и битовая маска в виде шестнадцатеричных чисел (0xAA/0xBB)
proto
Фильтрация пакетов по типу протокола:
udp;
tcp;
icmp;
<num> — номер протокола
rst
Фильтрация TCP-пакетов с RST-флагом (обрыв соединения):
on — включено;
off — отключено
syn
Фильтрация TCP-пакетов с SYN-флагом (инициация установки соединения):
on — включено;
off — отключено
sport
Порт источника трафика (1–65 535)
src
IP-адрес источника трафика. Форматы значений:
<ip> — например, 192.168.0.1;
<ip/mask> — например, 192.168.0.1/24
tout
Общий тайм-аут включения режима трассировки в минутах (1–60). При отсутствии параметра в команде трассировки используется значение по умолчанию — 5 минут
tout1
Тайм-аут включения режима трассировки в минутах (1–60). При активации параметра tout2 параметр tout1 задает время ожидания первого пакета
tout2
Время ожидания последующих пакетов после получения первого в минутах (1–60)
vlan
Идентификатор VLAN. Форматы значений:
<num> — для указания конкретного идентификатора VLAN (например, 10);
<num/0xN> — для указания диапазона идентификаторов VLAN с помощью битовой маски (например, 10/0x5)
Для просмотра результатов трассировки используется команда:
Admin@nodename> show packet-tracing <n> <full|short>
<n>
— порядковый номер задачи трассировки (0–9).
<full|short>
— выбор режима отображения отфильтрованных пакетов (полный или сокращенный).
Полный режим вывода демонстрирует весь путь пакета через стек протоколов, включая временные метки и промежуточные решения. В сокращенном режиме отображается итоговый результат, ключевые точки обработки пакета, а при блокировке — соответствующий фрагмент журнала.
В выводе результатов трассировки указываются только сработавшие правила межсетевого экрана.
Пример прохождения пакета через разрешающее правило межсетевого экрана:
Admin@nodename> show packet-tracing 0 short
Tracing task: 1 packet(s)
SRC=ANY DST=10.255.4.6 VLAN=ANY InDev:ANY
Mark:ANY Proto:ANY SrcPort:ANY DstPort:ANY
INPUT direction with 5min timeout
processing time 186.771us FINAL Result -> SUCCESS
Direction path: Forwarding
DEV=port3 ifindex=10 ZONE=4
IPv4 SRC=10.255.3.6 DST=10.255.4.6
LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=22977 DF
PROTO=TCP
SPT=58698 DPT=80 SYN
conntrack state: CT_NEW ctid:0000000060be4ad8 dir:ORIGINAL
TCP connection state: SYN_SENT
jiff:64982901 timeout:+1250 no guid
cssid: 165488077E38F85C
SNAT: off
DNAT: off
rtable: type=UNICAST (1) GW:0.0.0.0 OUTDEV=port4 outZONE=4
FireWall: VFW Stage3 Rule=8 Verdict=ACCEPT_CP1
Neighbour Type:01 Flags:00
OUTDEV=port4 ifindex=3 ZONE=4 mtu=1500
Пример отбрасывания пакета правилом межсетевого экрана:
Admin@nodename> show packet-tracing 0 short
Tracing task: 1 packet(s)
SRC=ANY DST=10.255.4.6 VLAN=ANY InDev:ANY
Mark:ANY Proto:ANY SrcPort:ANY DstPort:ANY
INPUT direction with 5min timeout
processing time 145.262us FINAL Result -> ERROR(-1)
Direction path: UNKNOWN
DEV=port3 ifindex=10 ZONE=4
IPv4 SRC=10.255.3.6 DST=10.255.4.6
LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=59745 DF
PROTO=TCP
SPT=58810 DPT=80 SYN
conntrack state: CT_NEW ctid:000000000ed7dc4d dir:ORIGINAL
TCP connection state: SYN_SENT
jiff:65332391 timeout:1250 no guid
cssid: 1337BC6AB9570671
SNAT: off
DNAT: off
FireWall: VFW Stage2 Rule=8 Verdict=DROP_CP1
Point of failure:
[261625.445465] t14p01c00 RECEIVE stage start 130.845us -> ERROR(-1)
[261625.445465] t14p01c00  ...
[261625.445470] t14p01c00 | NF IPV4 PRE_ROUTING INDEV=port3 from entry 0 of 10 125.426us -> ERROR(-1)
[261625.445470] t14p01c00    ...
[261625.445585] t14p01c00 | | hook#9 pri=+2147483647 vfw_ipv4_prert_last [utm_vfw]  4.559us -> DROP
(err=0)
[261625.445589] t14p01c00 | | | VFW Stage2 Rule=8 Verdict=DROP_CP1
Пример отбрасывания пакета модулем IDPS:
Packet #3 processing time 83.727us FINAL Result -> ERROR(-1)
Direction path: Forwarding
DEV=port3 ifindex=10 ZONE=4
IPv4 SRC=10.255.3.6 DST=10.255.4.6
LEN=123 TOS=0x00 PREC=0x00 TTL=64 ID=41034 DF
PROTO=TCP
SPT=58814 DPT=80 ACK PSH
conntrack state: CT_ESTABLISHED ctid:00000000e1574f38 dir:ORIGINAL
TCP connection state: ESTABLISHED
jiff:123262 timeout:4623262 guid:44035455-46AD-4A70-9615-CDD72BFF15C7
cssid: 79B4F1075D450351
SNAT: off
DNAT: off
rtable: type=UNICAST (1) GW:0.0.0.0 OUTDEV=port4 outZONE=4
Last seen header
IPv4 SRC=10.255.3.6 DST=10.255.4.6
LEN=123 TOS=0x00 PREC=0x00 TTL=63 ID=41034 DF
PROTO=TCP
SPT=58814 DPT=80 ACK PSH
Point of failure:
[   793.270366] t02p03c00 OUTPUT stage start 49.793us -> ERROR(-1)
[   793.270366] t02p03c00  ...
[   793.270366] t02p03c00 | NF IPV4 POST_ROUTING OUTDEV=port4 from entry 0 of 9 48.812us -> ERROR(-1)
[   793.270366] t02p03c00    ...
[   793.270372] t02p03c00 | | hook#6 pri=+2147483627 utm_ipsv3_hook [utm_ipsv3]  42.189us -> DROP (err=0)
Пример отбрасывания пакета по причине отсутствия маршрута до адреса назначения:
Tracing task: 1 packet(s)
SRC=ANY DST=10.255.5.6 VLAN=ANY InDev:ANY
Mark:ANY Proto:ANY SrcPort:ANY DstPort:ANY
INPUT direction with 5min timeout
processing time 218.180us FINAL Result -> ERROR(-101)
Direction path: UNREACHABLE
DEV=port3 ifindex=10 ZONE=4
IPv4 SRC=10.255.3.6 DST=10.255.5.6
LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=62293 DF
PROTO=TCP
SPT=56688 DPT=80 SYN
conntrack state: CT_NEW ctid:000000004878a2bc dir:ORIGINAL
TCP connection state: SYN_SENT
jiff:453314 timeout:1250 no guid
cssid: 5475B8894DAF1161
SNAT: off
DNAT: off
rtable: type=UNREACHABLE (7) GW:0.0.0.0 OUTDEV=lo outZONE=0
destination ERROR code 101
Point of failure:
[  2113.457413] t03p01c00 ROUTING stage start 8.716us -> ERROR(-101)
[  2113.457413] t03p01c00  ...
[  2113.457413] t03p01c00 | call ip_route_input 7.644us -> ERROR(-101) routing unsuccessful
Для отключения задачи трассировки пакетов используется команда:
Admin@nodename> clear packet-tracing <n>
<n>
— порядковый номер задачи трассировки (0–9).
v8.x
Команды диагностики и мониторинга (Описание)
Режим конфигурации

## Источник

https://docs.usergate.com/trassirovka-paketov_2319.html
