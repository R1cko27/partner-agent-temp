---
заголовок: Режим просмотра PMC CLI
url: https://docs.usergate.com/rezhim-prosmotra-pmc-cli_2287.html
получено: 2026-11-20 16:29 +0700
раздел: Интерфейс командной строки PMC
id_статьи: 2287
обновлено: 04 Mar, 2026
ревизия: 30
крошки: Главная / Аппаратные платформы / Интерфейс командной строки PMC / Режим просмотра PMC CLI
---

# Режим просмотра PMC CLI

Содержание:
В режиме просмотра PMC CLI вы можете:
просматривать состояние аппаратной платформы, версию основного ПО PMC и загрузчика, параметры конфигурации, сообщения об ошибках, активные сессии;
производить мониторинг сетевого окружения;
перезагружать устройство.
Чтобы посмотреть полный список команд, доступных в режиме просмотра PMC CLI, нажмите клавишу Tab.
PMC>
+ aux             AUX terminal support
+ autoboot        Run autoboot command
+ configure       Configuration mode
+ exit            Logout/Save config and exit
+ history         Display the history list
+ ping            Send ICMP ECHO_REQUEST to network host
+ reset           Reset peripheral sub-system or board
+ show            Show parameter
+ tcpdump         Print ethernet packets dump
+ traceroute      Print the route to network host using ICMP
+ version         Show version
aux
Команда для переключения на интерфейс UGOS CLI, если на платформе уже загружен образ UGOS. Для возвращения в PMC CLI используйте комбинацию клавиш Ctrl + ].
PMC> aux
Connected to CPU at speed 115200.
Escape character is '^]'.
UGOS login:
UGOS login: ^]
Disconnected from CPU
PMC>
autoboot
Команда для запуска UGOS и включение aux-режима (переход в UGOS CLI).
При выполнении команды без параметров запускается основной образ UGOS, при добавлении параметра
recovery
запускается образ для восстановления операционной системы (recovery-образ).
PMC> autoboot
Connected to CPU at speed 115200.
Escape character is '^]'.
NOTICE:  UDIMM M471A1K43EB1-CWE
NOTICE:  Build-in self test passed
NOTICE:  8 GB DDR4, 64-bit, CL=15, ECC off
NOTICE:  BL2: v2.4(release):
NOTICE:  BL2: Built : 03:40:29, Dec 30 2021
NOTICE:  BL2: Booting BL31
NOTICE:  BL31: v2.4(release):
NOTICE:  BL31: Built : 03:40:29, Dec 30 2021
NOTICE:  Welcome to ls1088ardb BL31 Phase
U-Boot 2021.04 (Dec 30 2021 - 03:40:29 +0000), Build: test-p4_ugos_g-380
Примечание
Выполнение этой команды в режиме загрузчика запускает основную прошивку PMC.
configure
Команда для перехода в режим конфигурирования. После выполнения этой команды меняется символ приглашения в консоли и появляется возможность конфигурирования параметров аппаратной платформы.
PMC> configure
PMC#
PMC# exit
PMC>
exit
Команда для выхода из терминала (в случае SSH — разрыва соединения).
PMC> exit
Press '^]' for autoboot and connect to aux
PMC login:
history
Команда для вывода списка выполненных ранее команд.
PMC> history
9 history
8 version
7 show network
6 show platform fan
5 show date
4 show factory
3 version
2 aux
1 autoboot
PMC>
ping
Команда для отправки ICMP ECHO-запроса. Выполняется пять раз с интервалом 1 сек. Опционально можно задавать размер данных в пакете.
Вы можете остановить выполнение команды, нажав комбинацию клавиш Сtrl + С.
PMC> ping 192.168.1.1
40 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0 ms
40 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=0 ms
40 bytes from 192.168.1.1: icmp_seq=3 ttl=64 time=0 ms
40 bytes from 192.168.1.1: icmp_seq=4 ttl=64 time=0 ms
40 bytes from 192.168.1.1: icmp_seq=5 ttl=64 time=0 ms
--- 192.168.1.1 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss
rtt min/avg/max = 0/0/0 ms
PMC>
PMC> ping 192.168.1.1 1400
1408 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=1 ms
1408 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=0 ms
1408 bytes from 192.168.1.1: icmp_seq=3 ttl=64 time=0 ms
1408 bytes from 192.168.1.1: icmp_seq=4 ttl=64 time=0 ms
1408 bytes from 192.168.1.1: icmp_seq=5 ttl=64 time=0 ms
--- 192.168.1.1 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss
rtt min/avg/max = 0/0/1 ms
reset
Команда для перезапуска устройства.
PMC> reset
PMC(Loader) Firmware 1.0 build dev (2021-12-27 - 10:01:23)
MCU: dev_id 0x450, rev_id 0x2003
Flash size: 128 KiB
Booting from Flash
Watchdog: Enabled
PMC[PWR]: Power Input 1 in state None
PMC[PWR]: Power Input 2 in state OK
PMC[PWR]: Power supplies are turned off.
Configure Clock Generator (SI5332):
.................OK
PMC[PWR]: Power supplies started.
show
Команда для просмотра состояния и параметров устройства.
PMC> show
+ <Enter>         Verbose diagnostics information
+ date            pmc date, time and timezone settings
+ uptime          pmc uptime
+ factory         Factory-settings sub-system (Type, S/N, MAC)
+ network         Network-settings sub-system
+ platform        Platform-settings sub-system
+ sessions        Showing ssh active sessions
+ users           Users-settings sub-system
При запуске команды укажите параметры для просмотра.
Параметр
Описание
Без параметров
Если запустить команду без параметров, будут последовательно выведены результаты срабатывания следующих команд:
version all
show factory
show uptime
show users
show platform
show network
show platform alarm log
show sessions
date
Вывод данных о дате, времени и часовом поясе
uptime
Вывод данных о текущем системном времени и времени работы устройства
factory
Вывод данных о типе устройства, серийном номере и исходном MAC-адресе интерфейса управления
network
Вывод данных о сетевых параметрах устройства:
об активных правилах доступа к устройству;
системных arp-таблицах;
имени устройства;
параметрах SSH-подключения;
состоянии и параметрах интерфейса управления MGMT
platform
Вывод данных о состоянии аппаратных компонентов платформы:
об активных ошибках;
состоянии системы питания;
состоянии процессора;
температурном режиме;
подключенных USB-устройствах
sessions
Вывод данных об активных сессиях на устройстве
users
Вывод данных о созданных на аппаратной платформе пользователях
Вывод телеметрии
Показания некоторых датчиков собираются в журналы. Хранятся журналы за последние 60 секунд, 60 минут и 72 часа. Есть два возможных формата вывода такой информации: графический (
graph
) и текстовый (
log
Пример вывода телеметрии в графическом формате:
Пример вывода телеметрии в текстовом формате:
Данные в виде таблицы или графика можно вывести за определенный период:
minute
hour
day
PMC> show platform soc mem graph hour
tcpdump
Захват и вывод в консоль пакетов сетевого трафика.
Вы можете остановить выполнение команды, нажав комбинацию клавиш Сtrl + С.
PMC> tcpdump
+ raw             Print the data of each packet (minus its link level header) in hex
+ verbose         Print more verbose data
+ ethVerbose      Print ethernet header
+ ethRaw          Print the data of each packet in hex
+ verboseEx       Print packet int wireshark stile (few supported protocols)
+ blocking        Printing dump blocks receiving/sending new packets
+ rawAscii        Print the data of each packet in hex with ASCII interpritation of each byte
traceroute
Проверка маршрута до запрашиваемого IP-адреса:
PMC> traceroute 192.168.70.11
traceroute to 192.168.70.11(192.168.70.11) 30 hops max 32(40) bytes of data
1    192.168.75.1 299 ms 94 ms 4 ms
2    192.168.70.11 0 ms 0 ms 0 ms
version
Просмотр версии основного ПО PMC и версии загрузчика.
PMC> version all
PMC(Main) Firmware 7.3.0 build  (2025-07-25 - 15:42:59)
PMC(Loader) Firmware 7.3.0 build 855 (2025-01-11 - 20:25:54)
Общие сведения
Режим конфигурирования PMC CLI

## Источник

https://docs.usergate.com/rezhim-prosmotra-pmc-cli_2287.html
