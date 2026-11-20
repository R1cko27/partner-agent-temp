---
заголовок: SNMP-мониторинг устройств UserGate с помощью Zabbix
url: https://docs.usergate.com/snmp-monitoring-ustrojstv-usergate-s-pomosh6yu-zabbix_49.html
источник: портал документации
получено: 2026-11-20 16:11 +0700
продукт: NGFW
версия: 7.x
раздел: SNMP-мониторинг устройств UserGate с помощью Zabbix
id_статьи: 49
обновлено: 22 Jul, 2025
ревизия: 21
---

# SNMP-мониторинг устройств UserGate с помощью Zabbix

Содержание:
В статье рассматривается пример использования шаблона для устройств UserGate в системе SNMP-мониторинга с открытым исходным кодом Zabbix версии 7 с применением протокола SNMPv3.
Настройка управляемого устройства UserGate
Для интеграции устройства UserGate с внешним SMNP-менеджером выполните следующие шаги:
1. В веб-консоли устройства в разделе
Диагностика и мониторинг ➜ Оповещения ➜ Профили безопасности SNMP
создайте профиль для запросов от SNMP-менеджера.
2. В разделе
Диагностика и мониторинг ➜ Оповещения ➜ SNMP
добавьте правило SNMP, использующее созданный ранее профиль безопасности SNMP.
3. На вкладке
События
в свойствах правила добавьте типы событий, доступных для мониторинга по этому правилу.
4. В разделе
Настройки ➜ Сеть ➜ Зоны
в свойствах зоны интерфейса, к которому будет осуществляться подключение по протоколу SNMP, на вкладке
Контроль доступа
разрешите протокол SNMP.
Подробнее о настройке SNMP-мониторинга устройств UserGate  — в разделе «
Оповещения
Использование шаблона UserGate в системе мониторинга Zabbix
Для установки и настройки системы SNMP-мониторинга Zabbix обратитесь
к официальной документации Zabbix
Перед началом интеграции устройств UserGate с системой SNMP-мониторинга
скачайте
архив с шаблоном UserGate, MIB-файлами и скриптом для системного процесса обработки SNMP-уведомлений
snmptrapd
. Инструкцию по настройке и использованию скрипта можно найти
на официальном сайте Zabbix
MIB-файлы также можно скачать на самом устройстве UserGate, для этого в веб-консоли устройства перейдите в раздел
Диагностика и мониторинг ➜ Оповещения ➜ SNMP
и нажмите
Скачать MIBs
Импорт и настройка шаблона
Для интеграции устройств UserGate:
1. В системе Zabbix на странице «Шаблоны» импортируйте шаблон UserGate.
2. Используя параметры созданного ранее
профиля безопасности SNMP
, настройте в системе Zabbix подключение управляемого устройства UserGate по протоколу SNMPv3.
3. Настройте необходимые значения порогов реакции макросов в параметрах шаблона.
Ниже приведена информация о макросах шаблона. При необходимости состав макросов может быть изменен.
Макрос
Значение
Описание
{$DNS_REQ}
1000
Количество DNS-запросов на устройстве
{$HTTP_REQ}
1000
Количество HTTP-запросов на устройстве
{$ICMP_CON}
50
Количество ICMP-сессий на устройстве
{$IF_BCST_LIM}
25
Количество бродкаст-пакетов в интерфейсе
{$IF_LIMIT}
80
Предел загруженности интерфейса в процентах для входящего и исходящего трафика
{$IF_MCST_LIM}
50
Количество мультикаст-пакетов в интерфейсе
{$TCP_CON}
500
Количество TCP-сессий на устройстве
{$UDP_CON}
100
Количество UDP-сессий на устройстве
{$IF_UCST_LIM}
50
Количество юникаст-пакетов в интерфейсе
Соответствие макросов элементам и триггерам шаблона:
{$DNS_REQ}
—  Все шаблоны ➜ Template UserGate company ➜ Триггеры ➜ DNS_requests_count_over_[{$DNS_REQ}].
{$HTTP_REQ}
— Все шаблоны ➜ Template UserGate company ➜ Триггеры ➜ HTTP_requests_count_over_[{$HTTP_REQ}].
{$ICMP_CON}
— Все шаблоны ➜ Template UserGate company ➜ Триггеры ➜ ICMP_session_count_over_[{$ICMP_CON}].
{$IF_BCST_LIM}
— Все шаблоны ➜ Template UserGate company ➜ Список обнаружений ➜ UserGate_Network_Port_Discovery ➜ Прототипы триггеров ➜ Exceeding the limit broadcast value on interface [{#SNMPVALUE}].
{$IF_LIMIT}
— Все шаблоны ➜ Template UserGate company ➜ Список обнаружений ➜ UserGate_Network_Port_Discovery ➜ Прототипы триггеров ➜ Overload on interface [{#SNMPVALUE}].
{$IF_BCST_LIM}
— Все шаблоны ➜ Template UserGate company ➜ Список обнаружений ➜ UserGate_Network_Port_Discovery ➜ Прототипы триггеров ➜ Exceeding the limit multicast value on interface [{#SNMPVALUE}].
{$IF_UCST_LIM}
— Все шаблоны ➜ Template UserGate company ➜ Список обнаружений ➜ UserGate_Network_Port_Discovery ➜ Прототипы триггеров ➜ Exceeding the limit unicast value on interface [{#SNMPVALUE}].
{$TCP_CON}
— Все шаблоны ➜ Template UserGate company ➜ Триггеры ➜ TCP_session_count_over_[{$TCP_CON}].
{$UDP_CON}
— Все шаблоны ➜ Template UserGate company ➜ Триггеры ➜ UDP_session_count_over_[{$UDP_CON}].
Примечание
Указанные значения макросов не являются эталонными и должны быть настроены исходя из возможностей имеющегося оборудования и требований к выполняемым задачам по мониторингу. Параметры предварительной обработки элементов шаблона также могут быть изменены.
В шаблоне определены следующие элементы данных для мониторинга.
Наименование
Ед.
измерения
Тип
данных
Интервал
опроса
OID
MIB name
MIB root
обработка
Описание
Curr_ICMP_sessions_counter
sessions
INTEGER
5 сек.
.1.3.6.1.4.1.45741.2.2.1.1.7.0
icmpsessionsCounter
UTM-MIB
simple
Количество активных ICMP-сессий на текущий момент времени
Curr_IO_Disc_util
INTEGER
1 мин.
.1.3.6.1.4.1.45741.2.2.1.4.8.0
diskIOUtilization
UTM-MIB
none
Загруженность диска операциями ввода-вывода на текущий момент времени
Curr_TCP_sessions_counter
sessions
INTEGER
5 сек.
.1.3.6.1.4.1.45741.2.2.1.1.5.0
tcpsessionsCounter
UTM-MIB
simple
Количество активных TCP-сессий а текущий момент времени
Curr_UDP_sessions_counter
sessions
INTEGER
5 сек.
.1.3.6.1.4.1.45741.2.2.1.1.6.0
udpsessionsCounter
UTM-MIB
simple
Количество активных UDP-сессий на текущий момент времени
DNS_Blocked_Requests
req
INTEGER
1 мин.
.1.3.6.1.4.1.45741.2.2.1.1.21.0
dnsBlockedRequestCounter
UTM-MIB
simple
Общее количество заблокированных DNS-запросов
DNS_Requests_per_sec
req
INTEGER
5 сек.
.1.3.6.1.4.1.45741.2.2.1.1.22.0
dnsRequestRate.0
UTM-MIB
none
Количество DNS-запросов в секунду
DNS_Total_Requests
req
INTEGER
1 мин.
1.3.6.1.4.1.45741.2.2.1.1.20.0
dnsRequestCounter
UTM-MIB
simple
Общее количество DNS-запросов
FS_data_state
none
DisplayString
1 мин.
.1.3.6.1.4.1.45741.2.2.1.1.26.0
dataPartitionFSStatus
UTM-MIB
none
Состояние файловой системы диска
HA_Cluster_state
num
INTEGER
30 сек.
.1.3.6.1.4.1.45741.2.2.1.2.1.0
haStatus
UTM-MIB
none
Количество узлов в кластере
HTTP_Blocked_Requests
req
INTEGER
1 мин.
.1.3.6.1.4.1.45741.2.2.1.1.24.0
httpBlockedRequestCounter
UTM-MIB
simple
Общее количество заблокированных HTTP-запросов
HTTP_Requests_per_sec
req
INTEGER
5 сек.
.1.3.6.1.4.1.45741.2.2.1.1.25.0
httpRequestRate
UTM-MIB
none
Количество HTTP-запросов в секунду
HTTP_Total_Requests
req
INTEGER
1 мин.
.1.3.6.1.4.1.45741.2.2.1.1.23.0
httpRequestCounter
UTM-MIB
simple
Общее количество HTTP-запросов
Sys_cpu_load
INTEGER
10 сек.
.1.3.6.1.4.1.45741.2.2.1.4.1.0
cpuLoad
UTM-MIB
none
Загруженность центрального процессора системы
Sys_log_disk_usage
INTEGER
1 мин.
.1.3.6.1.4.1.45741.2.2.1.4.3.0
logDiskSpace
UTM-MIB
none
Пространство на диске, занимаемое журналами
Sys_memory_used
INTEGER
10 сек.
.1.3.6.1.4.1.45741.2.2.1.4.2.0
memoryUsed
UTM-MIB
none
Использование оперативной памяти
Sys_power_supply1_status
none
DisplayString
10 сек.
.1.3.6.1.4.1.45741.2.2.1.4.4.0
powerSupply1Status
UTM-MIB
none
Состояние первого источника питания
Sys_power_supply2_status
none
DisplayString
10 сек.
.1.3.6.1.4.1.45741.2.2.1.4.5.0
powerSupply2Status
UTM-MIB
none
Состояние второго источника питания
Sys_raid_status
none
DisplayString
30 сек.
.1.3.6.1.4.1.45741.2.2.1.4.7.0
raidStatus
UTM-MIB
change
Состояние RAID-массива
Sys_raid_type
none
DisplayString
30 сек.
.1.3.6.1.4.1.45741.2.2.1.4.6.0
raidType
UTM-MIB
none
Используемый тип RAID-массива
Sys_uptime
uptime
TimeTicks
10 сек.
.1.3.6.1.2.1.1.3.0
sysUpTime
RFC1213-MIB
multiplier
Время работы системы
Sys_vcpu_count
num
INTEGER
1 мин.
.1.3.6.1.4.1.45741.2.2.1.1.1.0
vcpuCount
UTM-MIB
multiplier
Количество виртуальных процессоров в системе
Sys_vcpu_usage
none
INTEGER
10 сек.
.1.3.6.1.4.1.45741.2.2.1.1.2.0
vcpuUsage
UTM-MIB
none
Загруженность виртуальных процессоров системы
Users_counter
usr
INTEGER
15 сек.
.1.3.6.1.4.1.45741.2.2.1.1.3.0
usersCounter
UTM-MIB
none
Количество активных пользователей на текущий момент времени
В шаблоне определены следующие SNMP-уведомления типа trap.
Наименование
Тип данных
Ключ
обработка
Описание
Trap_Cable_Status
LOG
trapCableStatus
regex
Статус подключения интерфейса изменился
Trap_Check_Sum_Fail
LOG
trapChecksumFailed
regex
Нарушение целостности бинарных файлов
Trap_Disk_high_IO
LOG
trapHighDiskIOUtilization
regex
Высокая загруженность диска операциями ввода-вывода. Оповещение отправляется при загруженности одного из дисковых устройств на 95% или больше в течение 5 минут
Trap_DROP_rule_match
LOG
trapTrafficDrop
regex
Срабатывание запрещающего правила межсетевого экрана
Trap_HA_Member_DOWN
LOG
trapMemberDown
regex
Узел отказоустойчивого кластера отключен
Trap_HA_Member_UP
LOG
trapMemberUp
regex
Статус узла отказоустойчивого кластера изменился на «Подключен»
Trap_High_CPU
LOG
trapHighCPUUsage
regex
Высокая загруженность центрального процессора (95% или больше)
Trap_IDPS_alarm
LOG
trapAttackDetected
regex
Обнаружение атаки системой СОВ
Trap_Low_Disk_Space
LOG
trapLowLogdiskSpace
regex
Недостаточно места на диске для хранения журналов
Trap_Memory_Low
LOG
trapLowMemory
regex
Высокая загруженность оперативной памяти (95% или больше)
Trap_Stat_Down
LOG
trapStatDown
regex
Сервис статистики (UserGate Log Analyzer) недоступен
Trap_Temp_Ubnormal
LOG
trapCriticalTemperature
regex
Критическая температура на одном из сенсоров
Trap_UTM_Core_Ready
LOG
trapCoreBootstrapEnd
regex
Загрузка сервера завершена успешно
Кроме элементов данных шаблон содержит набор триггеров.
Наименование
Элемент
Важность
Описание
DNS_requests_count_over_[{$DNS_REQ}]
DNS_Total_Requests
Средняя
Количество DNS-запросов превысило {$DNS_REQ}
HTTP_requests_count_over_[{$HTTP_REQ}]
HTTP_Total_Requests
Средняя
Количество HTTP-запросов превысило {$HTTP_REQ}
ICMP_session_count_over_[{$ICMP_CON}]
Curr_ICMP_sessions_counter
Средняя
Количество ICMP-сессий превысило {$ICMP_CON}
Sys_cpu_load > 60%
Sys_cpu_load
Предупреждение
Загруженность центрального процессора превысила 60%
Sys_cpu_load > 85%
Sys_cpu_load
Высокая
Загруженность центрального процессора превысила 85%
Sys_log_disk_space > 80%
Sys_log_disk_usage
Средняя
Загруженность раздела диска, выделенного под журналы, превысила 80%
Sys_memory_used > 60%
Sys_memory_used
Предупреждение
Загруженность оперативной памяти превысила 60%
Sys_memory_used > 85%
Sys_memory_used
Высокая
Загруженность оперативной памяти превысила 85%
Sys_power_supply1_status_Off
Sys_power_supply1_status
Информация
Отключение первого источника питания
Sys_power_supply2_status_Off
Sys_power_supply2_status
Информация
Отключение второго источника питания
Sys_raid_status_Degraded
Sys_raid_status
Высокая
Сбой в работе RAID-массива
Sys_raid_status_Rebuild
Sys_raid_status
Предупреждение
RAID-контроллер восстанавливает массив
Sys_vcpu_usage > 80%
Sys_vcpu_count
Предупреждение
Загруженность виртуальных процессоров системы превысила 80%
Sys_vcpu_usage > 95%
Sys_vcpu_count
Высокая
Загруженность виртуальных процессоров системы превысила 95%
TCP_session_count_over_[{$TCP_CON}]
Curr_TCP_sessions_counter
Высокая
Количество TCP-сессий превысило {$TCP_CON}
Trap_DROP_rule_match
Предупреждение
Сработало запрещающее правило межсетевого экрана, для которого включено журналирование
Trap_HA_Member_DOWN
Высокая
Обнаружено отключение узла кластера
Trap_HA_Member_UP
Информация
Обнаружено подключение узла кластера
Trap_High_CPU_Usage
Trap_High_CPU
Чрезвычайная
Загруженность центрального процессора превысила 95%
Trap_High_IO_Disk
Trap_Disk_high_IO
Высокая
Высокая загруженность диска операциями ввода-вывода. Оповещение отправляется при загруженности одного из дисковых устройств на 95% или больше в течение 5 минут
Trap_IDPS_attack_detected
Trap_IDPS_alarm
Высокая
Обнаружено срабатывание правил СОВ
Trap_Kernel_UTM_Loaded
Trap_UTM_Core_Ready
Информация
Загрузка системы прошла успешно
Trap_Low_Disk_Space
Чрезвычайная
Недостаточно места на диске для хранения журналов
Trap_Low_Memory
Trap_Memory_Low
Чрезвычайная
Загруженность оперативной памяти превысила 95%
Trap_Stat_Down
Высокая
Сервис статистики (UserGate Log Analyzer) недоступен
Trap_Sys_Check_Fail
Trap_Check_Sum_Fail
Чрезвычайное
Нарушение целостности бинарных файлов системы
Trap_Temp_Ubnormal
Чрезвычайное
Критически опасная температура на одном из сенсоров. Оповещение отправляется при пересечении границ рабочей температуры (нижней или верхней). Нижняя граница равна 0 °С (для устройств серии X -40 ºC), верхняя — 85 ºС
UDP_session_count_over_[{$UDP_CON}]
Curr_UDP_sessions_counter
Средняя
Количество UDP-сессий превысило {$UDP_CON}
The interface status has changed
Trap_Cable_Status
Информация
Состояние подключения одного из интерфейсов изменилось
Правила обнаружения сетевых устройств
Шаблон содержит два преднастроенных правила обнаружения устройств по SNMP OID:
Industrial_Network_Port_Discovery
UserGate_Network_Port_Discovery
Правило
Industrial_Network_Port_Discovery
включает в себя стандартные прототипы элементов данных
ifTable
, описанные в стандартных MIB-файлах.
Некоторые прототипы данных для этого правила обнаружения отключены, так как используются редко. При необходимости их можно включить.
В правиле
Industrial_Network_Port_Discovery
определены следующие элементы данных.
Наименование
Ед.
измерения
Тип
данных
Интервал
опроса
OID
MIB name
MIB root
обработка
Описание
Admin status on interface [{#SNMPVALUE}]
none
INTEGER
30 сек.
.1.3.6.1.2.1.2.2.1.7.{#SNMPINDEX}
ifAdminStatus
IF-MIB
none
Текущее административное состояние интерфейса. Программное отключение:
up(1);
down(2)
Incoming discard traffic on interface [{#SNMPVALUE}]
pkt
INTEGER
30 сек.
.1.3.6.1.2.1.2.2.1.13.{#SNMPINDEX}
ifInDiscards
IF-MIB
none
Количество входящих пакетов, отвергнутых, несмотря на то что не было обнаружено ошибок, мешающих доставке пакетов на верхний уровень стека протокола. Одна из причин отвержения пакета может быть освобождение места в буфере
Incoming traffic error on interface [{#SNMPVALUE}]
pkt
INTEGER
30 сек.
.1.3.6.1.2.1.2.2.1.14.{#SNMPINDEX}
ifInErrors
IF-MIB
none
Количество входящих пакетов, полученных с ошибкой, из за которой пакеты не были доставлены на верхний уровень стека протокола
Incoming unknown rejected traffic on interface [{#SNMPVALUE}]
pkt
INTEGER
30 сек.
.1.3.6.1.2.1.2.2.1.15.{#SNMPINDEX}
ifInUnknownProtos
IF-MIB
none
Количество пакетов, полученных через интерфейс, но отвергнутых из-за неизвестного или не поддерживаемого протокола
MTU size on interface [{#SNMPVALUE}]
bts
INTEGER
30 сек.
.1.3.6.1.2.1.2.2.1.4.{#SNMPINDEX}
ifMtu
RFC1213-MIB
none
Размер MTU
Oper status on interface [{#SNMPVALUE}]
INTEGER
30 сек.
.1.3.6.1.2.1.2.2.1.8.{#SNMPINDEX}
ifOperStatus
IF-MIB
none
Текущее рабочее состояние интерфейса. Физическое отключение:
up(1);
down(2)
Outgoing discard traffic on interface [{#SNMPVALUE}]
pkt
INTEGER
30 сек.
.1.3.6.1.2.1.2.2.1.19.{#SNMPINDEX}
ifOutDiscards
IF-MIB
none
Количество исходящих пакетов, которые были отвергнуты, несмотря на то что не было обнаружено ошибок, мешающих отправке. Одна из причин отвержения пакета может быть освобождение места в буфере
Outgoing queue length on interface [{#SNMPVALUE}]
pkt
INTEGER
30 сек.
.1.3.6.1.2.1.2.2.1.21.{#SNMPINDEX}
ifOutQLen
IF-MIB
none
Длина очереди исходящих пакетов (количество пакетов в очереди)
Outgoing traffic error on interface [{#SNMPVALUE}]
pkt
INTEGER
30 сек.
.1.3.6.1.2.1.2.2.1.20.{#SNMPINDEX}
ifOutErrors
IF-MIB
none
Количество исходящих пакетов, которые не могут быть отправлены из за ошибок
В правиле
Industrial_Network_Port_Discovery
определены следующие триггеры.
Наименование
Элемент
Важность
Описание
Admin check DOWN status on port [{#SNMPVALUE}]
Admin status on interface [{#SNMPVALUE}]
Предупреждение
Интерфейс был программно отключен. Данный триггер имеет условие восстановления
Admin check UP status on port [{#SNMPVALUE}]
Admin status on interface [{#SNMPVALUE}]
Информация
Интерфейс был программно включен
Oper check DOWN status on port [{#SNMPVALUE}]
Oper status on interface [{#SNMPVALUE}]
Предупреждение
Интерфейс был физически отключен. Данный триггер имеет условие восстановления
Oper check UP status on port [{#SNMPVALUE}]
Oper status on interface [{#SNMPVALUE}]
Информация
Интерфейс был физически включен
Правило
UserGate_Network_Port_Discovery
содержит:
расширенные элементы
ifXTable
(из стандартных и предоставляемых производителем MIB);
вычисляемые показатели загруженности в процентах от максимальных значений параметров оборудования, которые определяются отдельным SNMP-элементом.
Пример правила обнаружения, содержащего настроенные фильтры используемых продуктом интерфейсов.
В правиле
UserGate_Network_Port_Discovery
определены следующие элементы данных.
Наименование
Ед.
измерения
Тип
данных
Инт.
опроса
OID
MIB name
MIB root
обработка
Описание
UG_Current_bandwith_on [{#SNMPVALUE}]
bits
Counter64
1 мин.
.1.3.6.1.2.1.31.1.1.1.15.{#SNMPINDEX}
ifHighSpeed
UTM-INTERFACES-MIB
Multiplier
Оценка текущей полосы пропускания интерфейса
UG_Current_incoming_ALL_traff_in_pcnts_on [{#SNMPVALUE}]
INTEGER
30 сек.
Error check
Процент всего входящего трафика относительно максимальной пропускной способности интерфейса
UG_Current_Incoming_bcast_traff_in_pcnts_on [{#SNMPVALUE}]
INTEGER
30 сек.
Error check
Процент входящего бродкаст-трафика относительно максимальной пропускной способности интерфейса
UG_Current_Incoming_mcast_traff_in_pcnts_on [{#SNMPVALUE}]
INTEGER
30 сек.
Error check
Процент входящего мультикаст-трафика относительно максимальной пропускной способности интерфейса
UG_Current_Incoming_ucast_traff_in_pcnts_on [{#SNMPVALUE}]
INTEGER
30 сек.
Error check
Процент входящего юникаст-трафика относительно максимальной пропускной способности интерфейса
UG_Current_Outgoing_ALL_traff_in_pcnts_on [{#SNMPVALUE}]
INTEGER
30 сек.
Error check
Процент всего исходящего трафика относительно максимальной пропускной способности интерфейса
UG_Current_Outgoing_bcast_traff_in_pcnts_on [{#SNMPVALUE}]
INTEGER
30 сек.
Error check
Процент исходящего бродкаст-трафика относительно максимальной пропускной способности интерфейса
UG_Current_Outgoing_mcast_traff_in_pcnts_on [{#SNMPVALUE}]
INTEGER
30 сек.
Error check
Процент исходящего мультикаст-трафика относительно максимальной пропускной способности интерфейса
UG_Current_Outgoing_ucast_traff_in_pcnts_on [{#SNMPVALUE}]
INTEGER
30 сек.
Error check
Процент исходящего юникаст-трафика относительно максимальной пропускной способности интерфейса
UG_Incoming all broadcast traffic on interface [{#SNMPVALUE}]
pkt
Counter64
30 сек.
.1.3.6.1.2.1.31.1.1.1.9.{#SNMPINDEX}
ifHCInBroadcastPkts
UTM-INTERFACES-MIB
simple
Общее количество доставленных бродкаст-пакетов
UG_Incoming all broadcast traffic on interface per sec [{#SNMPVALUE}]
pkt
Counter64
1 мин.
.1.3.6.1.2.1.31.1.1.1.9.{#SNMPINDEX}
ifHCInBroadcastPkts
UTM-INTERFACES-MIB
simple/60
Количество доставленных бродкаст-пакетов в секунду
UG_Incoming all multicast traffic on interface per sec [{#SNMPVALUE}]
pkt
Counter64
1 мин.
.1.3.6.1.2.1.31.1.1.1.8.{#SNMPINDEX}
ifHCInMulticastPkts
UTM-INTERFACES-MIB
simple/60
Количество доставленных мультикаст-пакетов в секунду
UG_Incoming all multicast traffic on interface [{#SNMPVALUE}]
pkt
Counter64
30 сек.
.1.3.6.1.2.1.31.1.1.1.8.{#SNMPINDEX}
ifHCInMulticastPkts
UTM-INTERFACES-MIB
simple
Общее количество доставленных мультикаст-пакетов
UG_Incoming all traffic on interface per sec [{#SNMPVALUE}]
byte
Counter64
1 мин.
.1.3.6.1.2.1.31.1.1.1.6.{#SNMPINDEX}
ifHCInOctets
UTM-INTERFACES-MIB
multiplier
simple/60
Количество байтов, принятое интерфейсом в секунду, включая служебные
UG_Incoming all unicast traffic on interface per sec [{#SNMPVALUE}]
pkt
Counter64
1 мин.
.1.3.6.1.2.1.31.1.1.1.7.{#SNMPINDEX}
ifHCInUcastPkts
UTM-INTERFACES-MIB
simple/60
Количество доставленных юникаст-пакетов в секунду
UG_Incoming all unicast traffic on interface [{#SNMPVALUE}]
pkt
Counter64
30 сек.
.1.3.6.1.2.1.31.1.1.1.7.{#SNMPINDEX}
ifHCInUcastPkts
UTM-INTERFACES-MIB
simple
Общее количество доставленных юникаст-пакетов
UG_Outgoing all broadcast traffic on interface [{#SNMPVALUE}]
pkt
Counter64
30 сек.
.1.3.6.1.2.1.31.1.1.1.13.{#SNMPINDEX}
ifHCOutBroadcastPkts
UTM-INTERFACES-MIB
simple
Общее количество отправленных бродкаст-пакетов, включая пакеты, которые были отброшены или не отправлены
UG_Outgoing all broadcast traffic on interface per sec [{#SNMPVALUE}]
pkt
Counter64
1 мин.
.1.3.6.1.2.1.31.1.1.1.13.{#SNMPINDEX}
ifHCOutBroadcastPkts
UTM-INTERFACES-MIB
simple/60
Количество отправленных бродкаст-пакетов в секунду, включая пакеты, которые были отброшены или не отправлены
UG_Outgoing all multicast traffic on interface [{#SNMPVALUE}]
pkt
Counter64
30 сек.
.1.3.6.1.2.1.31.1.1.1.12.{#SNMPINDEX}
ifHCOutMulticastPkts
UTM-INTERFACES-MIB
simple
Общее количество отправленных мультикаст-пакетов, включая пакеты, которые были отброшены или не отправлены
UG_Outgoing all multicast traffic on interface per sec [{#SNMPVALUE}]
pkt
Counter64
1 мин.
.1.3.6.1.2.1.31.1.1.1.12.{#SNMPINDEX}
ifHCOutMulticastPkts
UTM-INTERFACES-MIB
simple/60
Количество отправленных мультикаст-пакетов в секунду, включая пакеты, которые были отброшены или не отправлены
UG_Outgoing all unicast traffic on interface [{#SNMPVALUE}]
pkt
Counter64
30 сек.
.1.3.6.1.2.1.31.1.1.1.11.{#SNMPINDEX}
ifHCOutUcastPkts
UTM-INTERFACES-MIB
simple
Общее количество отправленных юникаст-пакетов, включая пакеты, которые были отброшены или не отправлены
UG_Outgoing all unicast traffic on interface per sec [{#SNMPVALUE}]
pkt
Counter64
1 мин.
.1.3.6.1.2.1.31.1.1.1.11.{#SNMPINDEX}
ifHCOutUcastPkts
UTM-INTERFACES-MIB
simple/60
Количество отправленных юникаст-пакетов в секунду, включая пакеты, которые были отброшены или не отправлены
UG_Outgoing all traffic on interface per sec [{#SNMPVALUE}]
byte
Counter64
1 мин.
.1.3.6.1.2.1.31.1.1.1.10.{#SNMPINDEX}
ifHCOutOctets
UTM-INTERFACES-MIB
multiplier
simple/60
Количество байтов, отправленное интерфейсом в секунду, включая служебные
В правиле
UserGate_Network_Port_Discovery
определены следующие триггеры.
Наименование
Элемент
Важность
Описание
Exceeding the inbound limit broadcast pkt per sec value on interface [{#SNMPVALUE}]
UG_Incoming all broadcast traffic on interface per sec [{#SNMPVALUE}]
Высокая
Превышено значение входящего бродкаст-трафика в секунду {$IF_BCST_LIM}
Exceeding the outbound limit broadcast pkt per sec value on interface [{#SNMPVALUE}]
UG_Outgoing all broadcast traffic on interface per sec [{#SNMPVALUE}]
Высокая
Превышено значение исходящего бродкаст-трафика в секунду {$IF_BCST_LIM}
Exceeding the inbound limit multicast pkt per sec value on interface [{#SNMPVALUE}]
UG_Incoming all multicast traffic on interface per sec [{#SNMPVALUE}]
Высокая
Превышено значение входящего мультикаст-трафика в секунду {$IF_MCST_LIM}
Exceeding the outbound limit multicast pkt per sec value on interface [{#SNMPVALUE}]
UG_Outgoing all multicast traffic on interface per sec [{#SNMPVALUE}]
Высокая
Превышено значение исходящего мультикаст-трафика {$IF_MCST_LIM}
Exceeding the limit inbound unicast pkt per sec value on interface [{#SNMPVALUE}]
UG_Incoming all unicast traffic on interface per sec [{#SNMPVALUE}]
Высокая
Превышено значение входящего юникаст-трафика в секунду {$IF_UCST_LIM}
Exceeding the limit outbound unicast pkt per sec value on interface [{#SNMPVALUE}]
UG_Outgoing all unicast traffic on interface per sec [{#SNMPVALUE}]
Высокая
Превышено значение исходящего юникаст-трафика в секунду {$IF_UCST_LIM}
Overload inbound % on interface [{#SNMPVALUE}]
UG_Incoming all traffic on interface per sec [{#SNMPVALUE}]
Высокая
Значение общего входящего трафика в секунду выше {$IF_LIMIT}
Overload outbound % on interface [{#SNMPVALUE}]
UG_Outgoing all traffic on interface per sec [{#SNMPVALUE}]
Высокая
Значение общего исходящего трафика в секунду выше {$IF_LIMIT}
Поскольку разные типы устройств UserGate отличаются наборами используемых счетчиков, рекомендуется после подключения шаблона деактивировать неиспользуемые элементы для каждого конкретного типа устройств. Это позволит снизить нагрузку на SNMP-менеджер.
Пример отключения неиспользуемых элементов для устройства UserGate LogAn.
В шаблоне также представлен ряд базовых графиков.
Опрос всех доступных элементов можно проводить при помощи команды
snmpwalk
snmpwalk -v 3 -u <snmp.username> -l authPriv -a SHA256 -A <sec.passwd> -x AES128 -X <auth.passwd> <IP>
v7.x
Авторизация с помощью Kerberos
Балансировка трафика на межсетевые экраны UserGate с помощью...

## Источник

https://docs.usergate.com/snmp-monitoring-ustrojstv-usergate-s-pomosh6yu-zabbix_49.html
