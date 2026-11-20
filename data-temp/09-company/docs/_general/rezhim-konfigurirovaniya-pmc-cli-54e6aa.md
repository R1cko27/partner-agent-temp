---
заголовок: Режим конфигурирования PMC CLI
url: https://docs.usergate.com/rezhim-konfigurirovaniya-pmc-cli_2296.html
источник: портал документации
получено: 2026-11-20 16:29 +0700
раздел: Интерфейс командной строки PMC
id_статьи: 2296
обновлено: 07 Apr, 2026
ревизия: 31
крошки: Главная / Аппаратные платформы / Интерфейс командной строки PMC / Режим конфигурирования PMC CLI
---

# Режим конфигурирования PMC CLI

Содержание:
В режиме конфигурирования PMC CLI помимо
команд режима просмотра
доступны команды управления компонентами платформы и настройки параметров устройства.
Примечание
Команды непосредственного управления платформой, которые не требуют сохранения параметров в энергонезависимой памяти, срабатывают сразу при запуске. Параметры, требующие сохранения, применяются и сохраняются в энергонезависимой памяти только после выполнения команды
exit
Просмотр заводских параметров
С помощью команды
show factory
вы можете посмотреть тип и серийный номер аппаратной платформы, исходный MAC-адрес интерфейса управления.
PMC# show factory
Factory-settings:
Device Type: UGAC-101
S/N:         UGAC21430000015
Base MAC:    34:91:6F:00:00:7F
PMC#
PMC# show factory mac
34:91:6F:00:00:7F
Управление системным временем, датой и часовым поясом
Вы можете посмотреть установленное системное время, дату и часовой пояс с помощью команды:
PMC# show date
Для установки времени, даты или часового пояса используйте команду:
PMC# set date dd.mm.yy hh:mm:ss [[+]|-]hh[:mm]
Где:
dd.mm.yy
— дата.
hh:mm:ss
— время.
[[+]|-]hh[:mm]
— часовой пояс. Знак плюс и минуты в команде указываются опционально. Диапазон установки часового пояса: от -12 до +14 часов включительно с шагом 15 минут.
Управление платформой
С помощью команд уровня конфигурации
platform
вы можете управлять различными компонентами аппаратных платформ UserGate.
Настройка работы байпас-реле
Команды управления режимами работы байпас-реле находятся на уровне
platform bypass
Функция байпас-реле поддерживается не на всех аппаратных платформах. О наличии сетевых интерфейсов с поддержкой режима байпас читайте в документации на аппаратные платформы.
Для установки режима работы байпас-реле используйте команду:
PMC# set platform bypass <relay-number> <state>
PMC# set platform bypass all <state>
<relay-number>
— номер настраиваемого реле.
<state>
— состояние реле. Возможны следующие значения:
Глобальные установки:
enable
— включение функции реле. Параметр сохраняется в энергонезависимой памяти. При отключенном питании реле будет замкнуто. В процессе работы можно размыкать и замыкать реле.
disable
& — отключение функции реле. Параметр сохраняется в энергонезависимой памяти. При отключенном питании реле будет разомкнуто. В процессе работы нельзя управлять состоянием реле.
Управление состоянием реле:
— замыкание байпас-реле (трафик идет в обход процессора). Состояние сбрасывается после перезапуска устройства.
off
— размыкание байпас-реле (трафик идет через процессор). Состояние сбрасывается после перезапуска устройства.
Примеры команд:
PMC# set platform bypass all enable
Enable all bypass relays
PMC# set platform bypass 1 disable
Disable bypass relay 1
PMC# set platform bypass 3 off
Set bypass relay 3 state OFF
Для просмотра состояния байпас-реле используйте команду:
PMC# show platform bypass
Bypass map:
Relay 1: port0 <-> port1
Relay 2: port2 <-> port3
Relay 3: port4 <-> port5
Relay 4: port6 <-> port7
Bypass state:
Relay 1: DISABLED
Relay 2: ON
Relay 3: OFF
Relay 4: ON
Управление вентиляторами охлаждения
Команды управления вентиляторами охлаждения находятся на уровне
platform fan
. С помощью команд этого уровня вы можете управлять режимами работы вентиляторов охлаждения и просматривать их текущее состояние. Функция управления вентиляторами поддерживается не на всех аппаратных платформах.
Вентиляторы могут работать в двух режимах: автоматическом и ручном. Установить режим работы вентиляторов можно с помощью команды:
PMC# set platform fan mode <auto|manual>
По умолчанию вентиляторы работают в автоматическом режиме. Скорость вращения вентиляторов контролируется процессором в зависимости от текущих температурных показателей.
В ручном режиме можно установить скорость вращения вентилятора в процентах:
PMC# set platform fan speed <0-100>
Если на платформе больше одного вентилятора, в ручном режиме можно управлять скоростью вращения каждого вентилятора по отдельности.
Параметры работы вентилятора охлаждения сохраняются в энергонезависимой памяти и не сбрасываются после перезагрузки устройства.
Примеры команд управления вентиляторами охлаждения:
PMC# set platform fan mode manual
Fan control will be switched to manual mode. These settings will be saved even after the device is rebooted.Do you really want to switch the fan control mode (y/n): y
set fan manual mode ok
PMC# set platform fan speed 50 0
set fan speed ok
PMC# show platform fan
Fan config:
direction            : front-to-back
Fan state:
Mode                 : manual
Fan 0:
Present              : Yes
Level                : 50%
Direction            : front-to-back
Speed                : 17024 RPM
Alarm                : No
Fan 1:
Present              : Yes
Level                : 25%
Direction            : front-to-back
Speed                : 10848 RPM
Alarm                : No
Fan 2:
Present              : Yes
Level                : 25%
Direction            : front-to-back
Speed                : 10904 RPM
Alarm                : No
PMC# set platform fan mode auto
set fan auto mode ok
На некоторых аппаратных платформах есть возможность установки системы охлаждения разного направления. Направление работы вентиляторов определяется автоматически после удаления предыдущего значения:
PMC# delete platform fan direction
Fan direction reset is complete.
Save config and restart device for autodetect fan direction.
PMC# exit
New configuration apply complete
PMC> reset
Device will be reset. Continue? (y/n): y
Для просмотра состояния вентилятора охлаждения используйте команду:
PMC# show platform fan <status|graph|log>
Пример команды просмотра состояния вентилятора охлаждения:
PMC# show platform fan
Fan state:
Mode:   manual
Level:  40
Speed:  6029 RPM
Параметры команды
graph
log
относятся к выводу телеметрии. Подробнее о примерах вывода телеметрии —
в описании команды просмотра
Управление процессором
Команды управления процессором находятся на уровне
platform soc
. С помощью команд этого уровня вы можете останавливать или запускать основной процессор и просматривать его текущее состояние.
Остановить или запустить процессор можно с помощью команды:
PMC# set platform soc <start|stop>
Посмотреть статус процессора можно с помощью команды:
PMC# show platform soc <log|load|frequency|mem>
Параметры
load
frequency
mem
относятся к выводу телеметрии. Подробнее о примерах вывода телеметрии —
в описании команды просмотра
Пример выполнения команды просмотра состояния процессора:
PMC# show platform soc
SoC is Running
System time: 08.06.2023 02:47:35
System uptime: 0 day(s), 0 hour(s), 12 minute(s)
Load average: 0.52 0.36 0.31
MemTotal: 61218 MiB
MemFree: 55064 MiB
CPU Frequency: 2200 MHz (Max 2200 MHz)
Пример команды просмотра последнего вывода процессора:
PMC№ show platform soc log
NOTICE:  UDIMM M471A1K43EB1-CWE
...
Server is starting, please wait...
Please press Enter to activate this console.
[   15.495488] kmodloader: loading kernel modules from /etc/modules.d/*
[   15.506171] kmodloader: done loading kernel modules from /etc/modules.d/*
[   15.577127] random: crng init done
[   15.580535] random: 4 urandom warning(s) missed due to ratelimiting
[   22.759147] IPv6: ADDRCONF(NETDEV_UP): port0: link is not ready
Мониторинг температуры
Команды мониторинга температуры процессора и платы находятся на уровне
platform therm
. С помощью команд этого уровня вы можете просматривать текущие значения температуры и аварийные сообщения.
Для просмотра текущего состояния и аварийных сообщений используйте команду:
PMC# show platform therm <value|status|graph|log>
Параметры
graph
log
относятся к выводу телеметрии. Подробнее о примерах вывода телеметрии —
в описании команды просмотра
Примеры использования команд мониторинга температуры:
PMC# show platform therm
Temperature:
Board                 :  58.000 C
CPU                   :  68.750 C
ALERT signal         : Inactive PMC>
PMC# show platform therm value
Temperature:
Board:  57.000 C
CPU:    69.000 C
Мониторинг источников питания
Команды мониторинга источников питания находятся на уровне
platform power
Для отображения информации о рабочем состоянии источников питания используйте команду:
PMC# show platform power <status|measurements|graph|log>
Параметры
graph
log
относятся к выводу телеметрии. Подробнее о примерах вывода телеметрии —
в описании команды просмотра
Пример использования команды:
PMC# show platform power
Power control signals:
LS1084_IO_PWR: Enabled
M2_PWR:     Enabled
CORE_PWR:   Enabled
DDR4_PWR:   Enabled
Power Inputs:
POW_IN1:    None
POW_IN2:    OK
PG signals:
LS1084_IO_PWR_PG_E: OK
CORE_PWR_PG_E:      OK
DDR4_PWR_PG_E:      OK
M2_PWR_PG_E:        OK
USB_PWR_PG_E:       OK
FPGA_PWR_PG_E:      OK
Voltages:
VDD: 1.039V - OK
SVDD: 1.012V - OK
XVDD: 1.401V - OK
DVDD: 3.382V - OK
OVDD: 1.845V - OK
GVDD: 1.245V - OK
FPGA: 3.404V - OK
Currents:
VDD: 7.006A - OK
GVDD: 0.473A - OK
PMC#
PMC# show platform power measurements
Voltages:
VDD: 1.040V - OK
SVDD: 1.013V - OK
XVDD: 1.403V - OK
DVDD: 3.384V - OK
OVDD: 1.846V - OK
GVDD: 1.248V - OK
FPGA: 3.404V - OK
Currents:
VDD: 7.018A - OK
GVDD: 0.516A - OK
Для включения или отключения всего питания платформы, кроме дежурного (PMC продолжит работу), используйте команду:
PMC# set platform power <on | off>
Пример команды отключения питания:
PMC# set platform power off
PMC[Netcard]: Power supplies are turned off.
PMC[PWR]: Power supplies are turned off.
Пример команды включения питания:
PMC# set platform power on
PMC[PWR]: Signal 'V3V3_PG_E' ready
PMC[PWR]: Signal 'KSZ_PG_E' ready
PMC[PWR]: Signal 'OVDD_PG_E' ready
PMC[PWR]: Signal 'USB_5V0_PG_E' ready
PMC[PWR]: Signal 'USB_SVDD_PG_E' ready
Configure Clock Generator (5P49V6901):
...........................OK
PMC[PWR]: Signal 'SVDD_PG_E' ready
PMC[PWR]: Signal 'GVDD_PG_E' ready
PMC[PWR]: Signal 'TA_BB_PG_N_E' ready
PMC[Netcard]: Power supplies started.
Configure Clock Generator (CDCM6208V2):
......OK
Configure Clock Generator (CDCM6208V2):
......OK
Configure Clock Generator (CDCM6208V2):
......OK
PMC[PWR]: Power supplies started.
Мониторинг аварий
Команды мониторинга аварий находятся на уровне
platform alarm
. С помощью команд этого уровня вы можете просматривать и очищать журнал аварий, управлять звуковым сигналом аварии (доступно не на всех платформах).
Пример команды просмотра аварийных сообщений:
PMC# show platform alarm log
01.07.2023 14:12:07 [POWER] VDD: Over/Under voltage condition detected
03.07.2023 11:13:14 [POWER] AVDD: Power good signal missing
05.07.2023 09:16:45 [POWER] GVDD: Over current condition detected
10.07.2023 15:16:47 [POWER] Power input 1: Present signal missing
12.07.2023 20:58:32 [POWER] Power input 2: Vin under voltage condition detected
15.07.2023 03:41:27 [POWER] Power input 2: Vout over/under voltage condition detected
15.07.2023 21:14:48 [POWER] Power input 1: Over current condition detected
18.07.2023 10:52:38 [POWER] Power input 2: Over heat condition detected
19.07.2023 02:29:46 [POWER] Power input 1: Fan fault condition detected
19.07.2023 23:09:56 [THERM] FPGA/SoC/PHY: Over heat condition detected
20.07.2023 06:14:31 [THERM] Common: Over heat shutdown occurred
21.07.2023 15:35:27 [THERM] FAN 1: Present signal missing
23.07.2023 21:59:31 [THERM] FAN 2: Wrong direction detected
25.07.2023 16:51:46 [THERM] FAN 3: Over current condition detected
27.07.2023 17:36:17 [THERM] FAN 4: Tachometer signal missing
29.07.2023 12:31:24 [THERM] FAN 5: Tachometer readings do not match the control signal
30.07.2023 10:39:54 [SYS] SoC: Main processor not respond
30.07.2023 19:48:26 [SYS] SoC: Main processor rebooted
31.07.2023 14:51:55 [SYS] SoC: High CPU load detected
31.07.2023 19:25:38 [SYS] SoC: High memory usage detected
Для отображения глобального статуса мониторинга аварий используйте команду:
PMC# show platform alarm status
Alarm disabled
Для очистки журнала аварийных сообщений используйте команду:
PMC# delete platform alarm log
Alarm log cleared
Для управления звуковым сигналом аварии используйте команду:
PMC# set platform alarm on
Alarm enabled
PMC# set platform alarm off
Alarm disabled
Управление сетевыми параметрами
Команды управления сетевыми параметрами находятся на уровне
network
. С помощью команд этого уровня вы можете настраивать и просматривать следующие параметры:
dhcp
— включение и отключение клиента DHCP;
— статический IP-адрес устройства;
netmask
— маска сети устройства;
gateway
— шлюз по умолчанию;
vlan
— VLAN ID сети устройства;
arp
— статические и динамические ARP-записи;
hostname
— имя устройства;
ssh-port
— порт для входящих подключений SSH-сервера;
nameserver
— адрес DNS сервера;
rule
— правила доступа к порту MGMT.
Для просмотра сетевых параметров используйте команду:
PMC# show network <parameters>
Пример команды просмотра всех сетевых параметров:
PMC# show network
------------------------------------
Network status:
IP address type: static
IP address: 192.168.1.6
Gateway address: 192.168.1.1
Netmask: 255.255.255.0
------------------------------------
Network settings:
DHCP: off
IP address: 192.168.1.6
Gateway address: 192.168.1.1
Netmask: 255.255.255.0/24
VLAN id: 0
SSH server port: 22
DNS address: 0.0.0.0
URL (for UGOS updating): none
------------------------------------
Address         HWaddress               Flags
192.168.1.80    34:67:8A:4F:91:10       static
192.168.1.1     50:3E:AA:16:2B:97       dynamic
------------------------------------
Access rules:
------------------------------------
Type: ip range
Start address: 192.168.1.1
End address: 192.168.1.10
Access: Drop
------------------------------------
Пример команды просмотра состояния интерфейса управления:
PMC# show network status
------------------------------------
Network status:
IP address type: static
IP address: 192.168.1.6
Gateway address: 192.168.1.1
Netmask: 255.255.255.0
------------------------------------
Пример команды просмотра ARP-таблицы:
PMC# show network arp
Address         HWaddress               Flags
192.168.1.80    34:67:8A:4F:91:10       static
Для установки значений сетевых параметров используйте команду:
PMC# set network <parameters>
Для сброса сетевых параметров до значений по умолчанию используйте команду:
PMC# delete network <ip|netmask|gateway|arp|vlan|ssh-port>
При выполнении команды без параметров все сетевые настройки сбрасываются до значений по умолчанию.
dhcp
Изначально режим DHCP отключен, в интерфейсе управления используется заданный по умолчанию IP-адрес (192.168.1.2).
Для включения режима DHCP используйте команду:
PMC# set network dhcp on
DHCP client start complete
Посмотреть полученные по DHCP сетевые параметры можно с помощью команды:
PMC# show network status
------------------------------------
Network status:
IP address type: dhcp
IP address: 192.168.75.238
Gateway address: 192.168.75.1
Netmask: 255.255.255.0
------------------------------------
По умолчанию интерфейс управления имеет следующий статический IP-адрес: 192.168.1.2.
Установить другой статический IP-адрес можно с помощью команды:
PMC# set network ip 192.168.1.75
Set ip complete
PMC# show network ip
IP address: 192.168.1.75
При установке IP-адреса вы можете указать маску подсети:
PMC# set network ip 192.168.75.88/24
Set ip address complete
PMC# set network ip 192.168.75.88 255.255.255.0
Set ip address complete
gateway
Шлюз по умолчанию имеет IP-адрес 192.168.1.1.
Изменить IP-адрес шлюза можно с помощью команды:
PMC# set network gateway 192.168.1.10
Set gateway complete
PMC# show network gateway
Gateway address: 192.168.1.10
nameserver
По умолчанию IP-адрес DNS-сервера не задан и имеет значение 0.0.0.0.
Установить IP-адрес DNS-сервера можно с помощью команды:
PMC# set network nameserver 192.168.1.1
Set nameserver complete
PMC# show network nameserver
DNS address: 192.168.1.1
vlan
По умолчанию значение
vlan id
— 0. Устройство получает все пакеты и при отправлении не использует
VLAN tag
Если значение
vlan id
не равно 0, все приходящие пакеты c другим тегом или без тега будут отброшены.
При отправке пакетов в ethernet-заголовок добавляется установленный тег.
Изменить значение
vlan id
можно с помощью команды:
PMC# set network vlan 12
Set vlan complete
PMC# show network vlan
VLAN id: 12
arp
ARP-таблица устройства по умолчанию пуста. При взаимодействии с другими узлами сети в нее добавляются динамические записи, которые имеют небольшое время жизни. После перезапуска такие записи всегда сбрасываются.
Вы можете задать статические записи ARP-таблицы с указанием соответствия IP-адресов и MAC-адресов. Если IP-адрес назначения присутствует в таблице, при отправке пакета устройство не делает ARP-запрос, а сразу подставляет в ethernet-заголовок MAC-адрес из таблицы.
Добавить статические ARP-записи можно с помощью команды:
PMC# set network arp <ip-addr> <hw-addr>
Удалить статические ARP-записи можно с помощью команды:
PMC# delete network arp <ip addr>
При выполнении команды
delete
без указания адреса будут удалены все записи.
Пример использования команд:
PMC# set network arp 192.168.1.55 34:67:8A:4F:91:55
PMC# show network arp
Address         HWaddress               Flags
192.168.1.80    34:67:8A:4F:91:10       static
192.168.1.65    34:67:8A:4F:91:43       static
192.168.1.55    34:67:8A:4F:91:55       static
PMC# delete network arp 192.168.1.65
PMC# show network arp
Address         HWaddress               Flags
192.168.1.80    34:67:8A:4F:91:10       static
192.168.1.55    34:67:8A:4F:91:55       static
PMC# delete network arp
PMC# show network arp
Address         HWaddress               Flags
hostname
Устройству может быть назначено имя. По умолчанию параметр
hostname
имеет значение
none
Чтобы установить новое значение параметра
hostname
используйте команду:
PMC# set network hostname <name>
Для просмотра имени устройства используйте команду:
PMC# show network hostname
Hostname: node_d200
ssh
Порт для входящих подключений PMC SSH-сервера. По умолчанию имеет значение 22 (в версии 7.5.0 и выше — 2220).
Вы можете изменить адрес порта с помощью команды:
PMC# set network ssh port 4001
Set ssh-port complete
PMC# show network ssh
SSH server port: 4001
rule
Правила доступа к интерфейсу управления устройством. Вы можете составлять белые и черные списки IP-адресов для контроля доступа к PMC.
Правила доступа применяются и записываются в память при выходе из режима конфигурирования по команде
exit
Примеры добавления правил:
PMC# set network rule allow 192.168.1.1 192.168.1.20
Access rule added successfully
PMC# set network rule drop 192.168.1.5 192.168.1.10
Access rule added successfully
Для просмотра правил используйте команду:
PMC# show network rule
Access rules:
------------------------------------
Type: ip range
Start address: 192.168.1.1
End address: 192.168.1.20
Access: Allow
------------------------------------
Type: ip range
Start address: 192.168.1.5
End address: 192.168.1.10
Access: Drop
------------------------------------
Для удаления правил используйте команду:
PMC# delete network rule 192.168.1.1 192.168.1.20
Access rule deleted successfully
interface
Включение или отключение интерфейса управления (MGMT).
Для включения интерфейса используйте команду:
PMC# set network interface up
MGMT interface up setted
Parameter will be applied after exit from configure mode
PMC# exit
New configuration apply complete
PMC> INFO: PMC[NET]: Link is up
По умолчанию интерфейс MGMT включен.
stats
Отображение статистики принятых и переданных данных.
Для отображения статистики используйте команду:
PMC# show network stats
Network statistics:
RX:     bytes        packets      errors
0            0            0
TX:     bytes        packets      errors
120          2            0
Для сброса собранной статистики используйте команду:
PMC# delete network stats
PMC# show network stats
Network statistics:
RX:     bytes        packets      errors
0            0            0
TX:     bytes        packets      errors
0            0            0
Управление пользователями
Команды управления пользователями находятся на уровне
users
. С помощью команд этого уровня вы можете создавать и удалять пользователей, настраивать методы авторизации для доступа к платформе, просматривать параметры созданных пользователей. В PMC CLI можно создать до 10 пользователей.
По умолчанию на устройстве создан один пользователь
admin
с паролем
password
. В версии 7.5.0 и выше —
Admin
с паролем
usergate
Для просмотра параметров созданных пользователей используйте команду:
PMC# show users
------------------
User1:
Login: admin
Public key type:
Public key:
Authentication methods: password
------------------
Создание пользователей
Для создания нового пользователя используйте команду:
PMC# create users <username>
Пример создания пользователя:
PMC# create users test1
New user test1 created
PMC# show users test1
Login: test1
Public key type:
Public key:
Authentication methods: none
Настройка метода авторизации
Созданному пользователю необходимо задать пароль или публичный ключ для авторизации на устройстве. До задания способа авторизации имя пользователя не может быть использовано для входа на устройство.
В качестве методов авторизации допускается использование пароля и публичного ключа ECDSA. Для пользователя может быть задан один или сразу оба метода авторизации.
Чтобы отключить один из методов авторизации, удалите ключ или пароль. Для удаления параметров авторизации используйте команду
delete
Пример настройки методов авторизации пользователя:
PMC# set users test1 password
Changing password for test1
Enter new password:
Retype new password:
Password for user test1 setted
PMC# show users test1
Login: test1
Public key type:
Public key:
Authentication methods: password
PMC#
PMC# set users test1 key ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEs+nzq8
LrO0OeniYHTYnTPtbc+CKaLAgvKz+3faiu5qQT7VN1kaPKx1hBV/e3HFzCen3XMVPerkOUEx0q2WrV0=
Public key for user test1 setted
PMC#
PMC# show users test1
Login: test1
Public key type: ecdsa-sha2-nistp256
Public key: AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEs+nzq8
LrO0OeniYHTYnTPtbc+CKaLAgvKz+3faiu5qQT7VN1kaPKx1hBV/e3HFzCen3XMVPerkOUEx0q2WrV0=
Authentication methods: password public_key
PMC# delete users test1 password
password for user test1 deleted
PMC# show users test1
Login: test1
Public key type: ecdsa-sha2-nistp256
Public key: AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEs+nzq8
LrO0OeniYHTYnTPtbc+CKaLAgvKz+3faiu5qQT7VN1kaPKx1hBV/e3HFzCen3XMVPerkOUEx0q2WrV0=
Authentication methods: public_key
Удаление пользователей
Для удаления пользователей используйте команду
delete
PMC# delete users test1
User test1 deleted
PMC# show users
------------------
User1:
Login: admin
Public key type:
Public key:
Authentication methods: password
------------------
Execute-команды
Ряд команд режима конфигурирования PMC CLI предназначен для управления конфигурацией:
diff
exit
revert
update
diff
Команда показывает отличия примененной на устройстве конфигурации и конфигурации, настроенной в данный момент в режиме конфигурирования.
Пример использования команды:
PMC# diff
IP address:
old: 192.168.75.92 new: 192.168.75.96
Netmask:
old: 255.255.255.0 new: 255.255.0.0
DHCP:
old: off new: on
exit
Запуск команды в режиме конфигурирования приводит к переходу в режим просмотра. Если в режиме конфигурирования была изменена конфигурация устройства, команда
exit
применяет обновленные параметры и сохраняет их в энергонезависимой памяти.
Пример использования команды в режиме конфигурирования:
PMC# set network ip 192.168.75.96
Set ip address complete
PMC# exit
New configuration apply complete
PMC>
revert
Команда сброса измененной конфигурации.
Пример использования команды:
PMC# revert
Temporary configuration revert complete
PMC# diff
Configuration not changed
update
Загрузка во флеш-память устройства образов ПО и ключей безопасности для SSH-сервера.
Для обновления ПО используйте команду:
PMC# update firmware <pmc|pmc-backup|boot|sys-recovery> tftp <address> <filename>
Для платформы UserGate FG можно обновить прошивки Netcard PMC (
ncpmc
) и образа FPGA (
fpga
После обновления
ncpmc
необходимо выполнить перезагрузку PMC.
Пример использования команды обновления прошивки PMC:
PMC# update firmware pmc tftp 192.168.1.1 pmc_main_C.img
TFTP from server 192.168.1.1; our IP address is 192.168.1.2
Filename 'pmc_main_C.img'.
Update at QSPI offset: 0x07000000.
Updating...
################################################################
Bytes transferred = 271480 (0x42478) in 1 seconds (265 KiB/s)
TFTP update OK
PMC#
PMC# update firmware fpga tftp 192.168.75.175 ngfw.img
TFTP from server 192.168.75.175; our IP address is 192.168.75.88
Filename 'ngfw.img'.
Update at QSPI offset: 0x00000000.
Updating...
################################################################
...
#############################################
Bytes transferred = 29282656 (0x1BED160) in 334 seconds (85 KiB/s)
TFTP update OK
Для обновления закрытого ключа SSH-сервера используйте команду:
PMC# update key ssh tftp <address> <filename>
Ключ должен быть предварительно создан и сохранен в DER-формате.
Пример создания ключа с помощью утилиты
openssl
openssl ecparam -genkey -name prime256v1 -noout -outform DER -out privatekey.der
В режиме конфигурации PMC CLI также доступны команды из режима просмотра:
aux
autoboot
history
ping
reset
tcpdump
traceroute
version
Подробнее о назначении этих команд и примерах их использования — в разделе «
Режим просмотра PMC CLI
Часто задаваемые вопросы

## Источник

https://docs.usergate.com/rezhim-konfigurirovaniya-pmc-cli_2296.html
