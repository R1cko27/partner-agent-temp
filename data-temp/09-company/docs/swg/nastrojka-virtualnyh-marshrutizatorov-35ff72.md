---
заголовок: Настройка виртуальных маршрутизаторов
url: https://docs.usergate.com/nastrojka-virtual6nyh-marshrutizatorov_2667.html
получено: 2026-11-20 16:26 +0700
продукт: SWG
версия: 7.5.x
раздел: Настройка виртуальных маршрутизаторов
id_статьи: 2667
обновлено: 17 Mar, 2026
ревизия: 6
---

# Настройка виртуальных маршрутизаторов

Содержание:
Technology: Routing
Виртуальные маршрутизаторы настраиваются на уровне
network virtual-router
Команда для добавления нового виртуального маршрутизатора:
Admin@nodename# create network virtual-router <parameters>
Далее необходимо указать параметры виртуального маршрутизатора.
Параметр
Описание
name
Уникальное имя виртуального маршрутизатора
description
Описание виртуального маршрутизатора
node-name
Выбор узла, на котором будет создан виртуальный маршрутизатор (при наличии кластера)
interfaces
Интерфейсы, которые будут использованы в данном виртуальном маршрутизаторе. Интерфейсы, добавленные в другие виртуальные маршрутизаторы, добавлены быть не могут; любой из интерфейсов может принадлежать только одному виртуальному маршрутизатору. В виртуальный маршрутизатор разрешается добавлять интерфейсы всех типов — физические, виртуальные (VLAN), бонд-интерфейсы и другие
Команда для отображения информации о виртуальном маршрутизаторе:
Admin@nodename# show network virtual-router <virtual-router-name>
Пример создания виртуального маршрутизатора:
Admin@nodename# create network virtual-router name test_router description "Test virtual router" interfaces [ port2 ]
Admin@nodename# show network virtual-router test_router
name                : test_router
description         : Test virtual router
node-name           : node_1
interfaces          : port2
...
Команда для редактирования параметров виртуального маршрутизатора:
Admin@nodename# set network virtual-router <virtual-router-name>
Параметры, доступные для обновления, аналогичны параметрам команды
create
, кроме:
name
node-name
Пример редактирования параметров виртуального маршрутизатора:
Admin@nodename# set network virtual-router test_router interfaces [ port3 ]
Admin@nodename# show network virtual-router test_router
name                : test_router
description         : Test virtual router
node-name           : node_1
interfaces          : port2; port3
...
Команда для удаления виртуального маршрутизатора:
Admin@nodename# delete network virtual-router <virtual-router-name>
Настройка статических маршрутов
Для добавления нового статического маршрута используется команда:
Admin@nodename# set network virtual-router <virtual-router-name> routes new
Далее необходимо указать параметры маршрута.
Параметр
Описание
enabled
Включение или отключение использования статического маршрута:
on;
off
name
Имя маршрута
description
Описание маршрута
type
Тип маршрута:
unicast — стандартный тип маршрута. Пересылает трафик, адресованный на адреса назначения, через заданный шлюз.
unreachable — трафик отбрасывается. Источнику отправляется ICMP сообщение host unreachable (type 3 code 1).
prohibit — трафик отбрасывается. Источнику отправляется ICMP сообщение host unreachable (type 3 code 13).
blackhole — трафик отбрасывается (теряется), не сообщая источнику о том, что данные не достигли адресата
destination-ip
IP-адрес подсети назначения; указывается в формате <
ip/mask
gateway
IP-адрес шлюза, через который будет доступна указанная подсеть; этот IP-адрес должен быть доступен с узла UserGate
interface
Интерфейс, через который будет добавлен маршрут
metric
Метрика маршрута. Если маршрутов в данную сеть несколько: чем меньше метрика, тем приоритетней маршрут
Пример добавления статического маршрута:
Admin@nodename# set network virtual-router test_router routes new name "Test static route" description "Test static route description" destination-ip 192.168.200.0/24 gateway 192.168.100.100 interface port3 type unicast metric 1 enabled on
Admin@nodename#
Admin@nodename# show network virtual-router test_router
name                : test_router
description         : Test virtual router
node-name           : node_1
interfaces          : port2; port3
routes              :
Test static route
name              : Test static route
enabled           : on
description       : Test static route description
destination-ip    : 192.168.200.0/24
gateway           : 192.168.100.100
interface         : port3
metric            : 1
...
Команда для изменения параметров созданного ранее статического маршрута:
Admin@nodename# set network virtual-router <virtual-router-name> routes <static-route-name>
Параметры, доступные для изменения, представлены в таблице выше.
Пример редактирования статического маршрута:
Admin@nodename# set network virtual-router test_router routes "Test static route" metric 10
Admin@nodename# show network virtual-router test_router
name                : test_router
description         : Test virtual router
node-name           : node_1
interfaces          : port2; port3
routes              :
Test static route
name              : Test static route
enabled           : on
description       : Test static route description
destination-ip    : 192.168.200.0/24
gateway           : 192.168.100.100
interface         : port3
metric            : 10
...
Команда для удаления статического маршрута:
Admin@nodename# delete network virtual-router <virtual-router-name> routes <static-route-name>
Пример удаления статического маршрута:
Admin@nodename# delete network virtual-router test_router routes "Test static route"
Admin@nodename# show network virtual-router test_router
name                : test_router
description         : Test virtual router
node-name           : node_1
interfaces          : port2; port3
routes              : []
...
Команда для отображения статических маршрутов:
Admin@nodename# show network virtual-router <virtual-router-name> routes
Настройка OSPF
Для настройки OSPF используется команда:
Admin@nodename# set network virtual-router <virtual-router-name> ospf
Далее необходимо указать параметры OSPF.
Параметр
Описание
enabled
Включение или отключение OSPF-маршрутизатора:
on;
off
router-id
IP-адрес маршрутизатора. Должен быть уникальным и задан в формате IPv4 (для удобства может совпадать с одним из IP-адресов, назначенным сетевым интерфейсам устройства, относящимся к данному виртуальному маршрутизатору).
При выключении OSPF (enabled off) значение router-id может быть удалено (none)
metric
Метрика распространяемых маршрутов
default-originate
Оповещение других маршрутизаторов о том, что у данного роутера настроен маршрут по умолчанию:
on;
off
interfaces
Выбор одного из существующих в системе интерфейсов, на котором будет работать OSPF. Для выбора доступны только интерфейсы, входящие в данный виртуальный маршрутизатор.
Для добавления интерфейса или изменения параметров добавленного ранее интерфейса используются следующие команды:
Admin@nodename# set network virtual-router <virtual-router-name> ospf interfaces new
Admin@nodename# set network virtual-router <virtual-router-name> ospf interfaces <interface-name>
Далее указываются следующие параметры:
enabled <on | off>: включение/отключение использования интерфейса.
interface: название интерфейса, входящего в данный виртуальный маршрутизатор.
description: описание интерфейса.
bfd: добавить профиль bfd (Bidirectional Forwarding Detection). Профили bfd создаются в библиотеке элементов. Подробнее — в разделе «
Настройка библиотек
cost: стоимость канала данного интерфейса. Данное значение передается в LSA (объявления о состоянии канала, link-state advertisement) соседним маршрутизаторам и используется ими для вычисления кратчайшего маршрута. Значение по умолчанию 1.
priority: целое число от 0 до 255. Чем больше значение, тем выше шанс у маршрутизатора стать назначенным маршрутизатором (designated router) в сети для рассылки LSA. Значение 0 делает назначение для данного маршрутизатора невозможным. Значение по умолчанию 1.
network-type: выбор типа сети для оптимизации процесса установления соседства. Доступны:
none — не установлен.
bc — broadcast.
ptm — point to multipoint.
ptp — point to point.
passive-mode <on | off>: включение/отключение пассивного режима работы интерфейса, при котором через интерфейс запрещается слать пакеты обновления протокола маршрутизации.
hello-interval: время, через которое маршрутизатор посылает hello-пакеты; указывается в секундах. Это время должно быть одинаковым на всех маршрутизаторах в автономной системе. Значение по умолчанию 10 секунд.
dead-interval: время, по истечению которого маршрутизатор считается неработающим; указывается в секундах. Время исчисляется от момента приема последнего пакета hello от соседнего маршрутизатора. Значение по умолчанию 40 секунд.
retransmit-interval: временный интервал перед повторной отсылкой пакета LSA; указывается в секундах. Значение по умолчанию 5 секунд.
transmit-delay: примерное время, требуемое для доставки соседним маршрутизаторам обновления состояния каналов (link state); задаётся в секундах. Значение по умолчанию 1 секунда.
authentication: тип аутентификации. Доступны:
enabled <on | off> — включение/отключение требования аутентификации каждого принимаемого роутером OSPF-сообщения. Аутентификация обычно используется для предотвращения инъекции фальшивого маршрута от нелегитимных маршрутизаторов.
auth-type — выбор типа аутентификации: plain (передача ключа в открытом виде для аутентификации роутеров) или digest (использование MD5-хеша для ключа для аутентификации OSPF-пакетов).
md5 — идентификатор ключа.
key — ключ. Ключ может содержать только буквы латинского алфавита, цифры и символ подчёркивания. Максимальное количество символов — 16
areas
Настройка области OSPF.
Для добавления новой области или изменения параметров созданной ранее области используются следующие команды:
Admin@nodename# set network virtual-router <virtual-router-name> ospf areas new
Admin@nodename# set network virtual-router <virtual-router-name> ospf areas <area-name>
Далее указываются следующие параметры:
enabled <on | off>: включение/отключение использования данной области.
name: название области.
description: описание области.
cost: стоимость LSA, анонсируемых в stub-области.
area-id: идентификатор зоны (area ID). Идентификатор может быть указан в десятичном формате или в формате записи IP-адреса. Идентификатор области должен совпадать для установления соседства OSPF.
auth-type: тип аутентификации. Доступны следующие значения:
none — не требовать аутентификацию OSPF-пакетов.
plain — передача ключа в открытом виде для аутентификации OSPF-пакетов. Используется ключ, заданный в настройках интерфейсов.
digest — использование MD5-хеша для ключа для аутентификации OSPF-пакетов. Используется ключ, заданный в настройках интерфейсов.
Аутентификация на уровне интерфейсов имеет приоритет над аутентификацией на уровне зоны.
area-type: тип области OSPF. Доступны следующие типы:
normal — обычная зона, которая создается по умолчанию. Эта зона принимает обновления каналов, суммарные маршруты и внешние маршруты.
nssa — Not-So-Stubby Area определяет дополнительный тип LSA — LSA type 7. В NSSA зоне может находиться пограничный маршрутизатор (ASBR).
stub — тупиковая зона, не принимает информацию о внешних маршрутах для автономной системы, но принимает маршруты из других зон. Если маршрутизаторам из тупиковой зоны необходимо передавать информацию за границу автономной системы, то они используют маршрут по умолчанию. В тупиковой зоне не может находиться ASBR.
no-summary: разрешение/запрет инжекции суммированных маршрутов в тупиковые типы областей:
on.
off.
interfaces: выбор интерфейсов OSPF, на которых будет доступна данная зона.
virtual-links: Специальное соединение, которое позволяет соединять, например, разорванную на части зону или присоединить зону к магистральной через другую зону. Настраивается между двумя ABR.
Позволяет маршрутизаторам передать пакеты OSPF через виртуальные ссылки, инкапсулируя их в IP-пакеты. Этот механизм используется как временное решение или как backup на случай выхода из строя основных соединений.
Можно указать идентификаторы маршрутизаторов, которые доступны через данную зону
redistribute
Распространение OSPF маршрутов:
connected — распространение маршрутов в непосредственно подключённые к устройству сети.
kernel — распространение маршрутов, которые были добавлены администратором
Команда для отображения конфигурации OSPF в виртуальном маршрутизаторе:
Admin@nodename# show network virtual-router <virtual-router-name> ospf
Пример конфигурирования OSPF в виртуальном маршрутизаторе:
Admin@nodename# set network virtual-router test_router  ospf router-id 192.168.100.3 areas new area-id 1 area-type normal name "New OSPF area" enabled on interfaces [ ]
...
Admin@nodename# show network virtual-router test_router
name                : test_router
description         : Test virtual router
node-name           : node_1
interfaces          : port2; port3
routes              : []
ospf                :
router-id            : 192.168.100.3
enabled              : off
default-originate    : off
metric               : None
areas                :
New OSPF area
name             : New OSPF area
enabled          : on
cost             : 1
area-id          : 1
area-type        : normal
no-summary       : off
interfaces           : []
...
Команда для удаления настройки OSPF:
Admin@nodename# delete network virtual-router <virtual-router-name> ospf <parameter>
Параметры, доступные для удаления:
interface
area
Настройка BGP
Настройка протокола динамической маршрутизации BGP (Border Gateway Protocol) в виртуальном маршрутизаторе производится с использованием команды:
Admin@nodename# set network virtual-router <virtual-router-name> bgp
Далее необходимо указать параметры BGP.
Параметр
Описание
enabled
Включение/отключение OSPF-маршрутизатора:
on;
off
router-id
IP-адрес маршрутизатора. Должен совпадать с одним из IP-адресов, назначенным сетевым интерфейсам UserGate, относящимся к данному виртуальному маршрутизатору.
При выключении BGP (enabled off) значение router-id может быть удалено (none)
asn
Автономная система — это система IP-сетей и маршрутизаторов, управляемых одним или несколькими операторами, имеющими единую политику маршрутизации. Номер автономной системы задает принадлежность роутера к этой системе
multiple-path
Включение/отключение балансировки трафика на маршруты с одинаковой стоимостью:
on;
off
redistribute
Распространение BGP маршрутов:
connected — распространение маршрутов в непосредственно подключённые к устройству сети.
kernel — распространение маршрутов, которые были добавлены администратором.
ospf — распространение маршрутов, полученных по протоколу OSPF
networks
Список сетей, относящихся к данной автономной системе. Необходимо указать в формате <
ip/mask
routemaps
Routemaps используются для управления таблицами маршрутов и указания условий, при выполнении которых маршруты передаются между доменами.
Для создания routemap или изменения параметров созданного ранее routemap используются следующие команды:
Admin@nodename# set network virtual-router <virtual-router-name> bgp routemaps new
Admin@nodename# set network virtual-router <virtual-router-name> bgp routemaps <routemap-name>
Параметры routemap:
name — название routemap.
description — описание routemap.
action — действие:
allow — разрешить прохождение данных, попадающих под условия routemap.
block — запретить прохождение данных, попадающих под условия routemap.
next-hop — установка для отфильтрованных маршрутов значения next hop в указанный IP-адрес.
weight — установка для отфильтрованных маршрутов веса в указанное значение.
metric — установка для отфильтрованных маршрутов метрики в указанное значение.
position — порядковый номер routemap в общем списке.
preference — установка для отфильтрованных маршрутов предпочтения в указанное значение.
as-prepend — установка значения AS-prepend — список автономных систем, добавляемых для данного маршрута.
community — установка значения для BGP community для отфильтрованных маршрутов.
append-community — Добавлять community.
ip-match — необходимо добавить все необходимые IP-адреса при выборе сравнения по IP-адресу.
as-path-match — необходимо добавить все необходимые номера автономных сетей при выборе сравнения по AS-пути. Допускается указывать регулярные выражения формата POSIX 1003.2, а также дополнительный символ подчеркивания (_), который интерпретируется как:
Пробел.
Запятая.
Начало строки.
Конец строки.
AS set delimiter { and }.
AS confederation delimiter ( and ).
community-match — необходимо добавить строки всех необходимых BGP community при выборе сравнения по Community
filters
Фильтр позволяет фильтровать маршруты при перераспределении.
Для создания фильтра или изменения параметров созданного ранее фильтра используются следующие команды:
Admin@nodename# set network virtual-router <virtual-router-name> bgp filters new
Admin@nodename# set network virtual-router <virtual-router-name> bgp filters <filter-name>
Параметры:
name — название фильтра.
description — описание фильтра.
action — действие:
allow — разрешить прохождение данных, попадающих под условия routemap.
block — запретить прохождение данных, попадающих под условия routemap.
ip-filter — необходимо добавить все необходимые IP-адреса при выборе фильтрации по IP-адресу. Адреса могут быть указаны в следующих форматах:
10.0.0.0/8 — только сеть 10.0.0.0/8.
10.0.0.0./8:11 — маршруты, у которых первый октет 10 и префикс от 8 до 11.
10.0.0.0/8:11:13 — маршруты, у которых первый октет 10 и префикс от 11 до 13.
as-path-filter — необходимо добавить все необходимые номера автономных сетей при выборе фильтрации по AS пути.
position — порядковый номер фильтра в общем списке
neighbors
BGP-соседи.
Для добавления новых соседей или изменения данных о ранее добавленных соседях используются следующие команды:
Admin@nodename# set network virtual-router <virtual-router-name> bgp neighbors new
Admin@nodename# set network virtual-router <virtual-router-name> bgp neighbors <host-ip>
Параметры:
enabled — включение/отключение использования соседа:
on.
off.
description — описание BGP-соседа.
host — IP-адрес соседа.
remote-asn — номер автономной системы, к которой относится сосед.
weight — вес маршрутов, получаемых от данного соседа.
ttl — максимальное количество хопов, разрешенное до этого соседа.
allowas-in — эта функция позволяет получать и обрабатывать маршруты, даже если маршрутизатор обнаруживает собственный номер автономной системы в AS Path в маршруте агрегации.
on.
off.
allowas-in-number — количество раз, которое в AS Path может содержаться номер автономной системы BGP-соседа. Возможны значения от 0 до 10 (0 — origin)
bfd: добавить профиль bfd (Bidirectional Forwarding Detection). Профили bfd создаются в библиотеке элементов. Подробнее — в разделе «
Настройка библиотек
next-hop-self — замена значения next-hop-self на собственный IP-адрес, если сосед является BGP:
on.
off.
ebgp-multihop — до этого BGP-соседа непрямое соединение (более одного хопа):
on.
off.
route-reflector-client — определение, является ли BGP-сосед клиентом Route reflector:
on.
off.
soft-reconfiguration — использование soft reconfiguration (без разрыва соединений) для обновления конфигурации:
on.
off.
default-originate — анонс соседу маршрут по умолчанию:
on.
off.
send-community — пересылать community BGP-соседям:
on.
off.
enable-auth — включение/отключение аутентификации для соседа:
on.
off.
password — пароль для аутентификации соседа.
filter-in — ограничение информации о маршрутах, получаемых от соседей.
filter-out — ограничение информации о маршрутах, анонсируемых соседям.
routemap-in — ограничение маршрутизирующей информации, которую BGP получает от соседей.
routemap-out — ограничение маршрутизирующей информации, которую BGP отдаёт соседям
Команда для отображения конфигурации BGP в виртуальном маршрутизаторе:
Admin@nodename# show network virtual-router <virtual-router-name> bgp
Пример команды конфигурирования BGP в виртуальном маршрутизаторе:
Admin@nodename# set network virtual-router test_router bgp router-id 192.168.95.224 asn 1 networks [ 192.168.100.0/24 ] redistribute [ connected kernel ]
Admin@nodename# show network virtual-router test_router
name                : test_router
description         : Test virtual router
node-name           : node_1
interfaces          : port2; port3
...
bgp                 :
enabled          : off
asn              : 1
router-id        : 192.168.95.224
redistribute     : connected; kernel
multiple-path    : off
networks         : 192.168.100.0/24
routemaps        : []
neighbors        : []
filters          : []
...
Команда для удаления параметров BGP-маршрутизатора:
Admin@nodename# delete network virtual-router <virtual-router-name> bgp <parameter>
Для удаления доступны следующие параметры:
Адреса сетей, относящихся к данной автономной системе:
networks
Условия применения routemap:
routemaps <routemap-name> ip-match | community-match | as-path-match
Условия применения фильтра:
filters <filter-name> ip-filter | as-path-filter
Фильтры BGP-соседей и routemaps:
neighbors <host-ip> filter-in | filter-out | routemap-in | routemap-out
опции распространения BGP маршрутов:
redistribute [ connected | kernel ]
Настройка RIP
Настройка протокола маршрутизации RIP (Routing Information Protocol) в виртуальном маршрутизаторе производится с использованием команды:
Admin@nodename# set network virtual-router <virtual-router-name> rip
Далее необходимо указать параметры RIP.
Параметр
Описание
enabled
Включение/отключение RIP-маршрутизатора:
on;
off
version
Версия протокола RIP:
Как правило, используется версия протокола 2
metric
Метрика RIP. По умолчанию метрика равна 1; максимальное значение — 15. Значение 16 считается бесконечным
distance
Стоимость маршрутов, полученных с помощью протокола RIP. Значение по умолчанию для протокола RIP — 120. Используется для выбора маршрутов при наличии нескольких способов получения маршрутов (OSPF, BGP, статические)
originate
Отправлять себя в качестве маршрута по умолчанию
networks-cidr
Указание сети в виде CIDR. Указывается в формате <
ip/mask
networks-interface
Указание сетевого интерфейса, с которого будут отправлять обновления маршрутной информации; указываются интерфейсы, принадлежащие виртуальному маршрутизатору
redistribute
Распространение маршрутов:
connected — распространение другим роутерам RIP маршрутов в непосредственно подключённые к UserGate сети:
<metric> — значение метрики; может принимать значения от 0 до 16;
off.
static — распространение другим маршрутизаторам статических маршрутов:
<metric> — значение метрики; может принимать значения от 0 до 16;
off.
kernel — распространение другим роутерам RIP маршрутов, которые были добавлены администратором:
<metric> — значение метрики; может принимать значения от 0 до 16;
off.
ospf — распространение другим RIP-роутерам маршрутов, полученных по OSPF:
<metric> — значение метрики; может принимать значения от 0 до 16;
off.
bgp — распространение другим RIP-роутерам маршрутов, полученных по BGP:
<metric> — значение метрики; может принимать значения от 0 до 16;
off
interfaces
Настройка интерфейсов, на которых поддерживается протокол RIP; интерфейсы должны быть добавлены в виртуальный маршрутизатор.
Для добавления интерфейсов или изменения данных о ранее добавленных интерфейсах используются следующие команды:
Admin@UGOS# set network virtual-router <virtual-router-name> rip interfaces new
Admin@UGOS# set network virtual-router <virtual-router-name> rip interfaces <interface-name>
Параметры:
interface — выбор интерфейса.
send-version — версия протокола RIP, которую маршрутизатор будет отсылать. Доступны:
receive-version — версия протокола RIP, которую маршрутизатор будет принимать. Доступны:
password — строка для авторизации, которая будет посылаться и приниматься в пакетах RIP. Все роутеры, участвующие в обмене информации по протоколу RIP, должны иметь одинаковый пароль.
split-horizone — метод предотвращения петель маршрутизации, при котором маршрутизатор не распространяет информацию о сети через интерфейс, на который прибыло обновление.
on;
off.
poisoned-reverse — метод предотвращения петель маршрутизации, при котором маршрутизатор устанавливает стоимость маршрута в 16 и отсылает его соседу, от которого его получил.
on;
off.
passive-mode — режим работы интерфейса, при котором он принимает обновления RIP, но не отсылает их.
on;
off
Команда для отображения конфигурации RIP в виртуальном маршрутизаторе:
Admin@nodename# show network virtual-router <virtual-router-name> rip
Пример команды конфигурирования RIP в виртуальном маршрутизаторе:
Admin@nodename# set network virtual-router test_router rip version 2 originate on
Admin@nodename# show network virtual-router test_router
name                : test_router
description         : Test virtual router
node-name           : node_1
interfaces          : port2; port3
...
rip                 :
enabled               : off
distance              : 120
metric                : 1
originate             : on
interfaces            : []
redistribute          : {}
version               : 2
...
Admin@nodename# set network virtual-router test_router rip interfaces new interface port2
Admin@nodename# show network virtual-router test_router
name                : test_router
description         : Test virtual router
node-name           : node_1
interfaces          : port2; port3
...
rip                 :
enabled               : off
distance              : 120
metric                : 1
originate             : on
interfaces            :
port2
interface           : port2
passive-mode        : off
poisoned-reverse    : off
receive-version     : 0
send-version        : 0
split-horizone      : off
redistribute          : {}
version               : 2
...
Команда для удаления параметров RIP-маршрутизатора:
Admin@nodename# delete network virtual-router <virtual-router-name> rip <parameter>
Для удаления доступны следующие параметры:
Интерфейсы RIP:
interfaces
Сети RIP:
networks-cidr
Сетевого интерфейса, с которого будут отправлять обновления маршрутной информации:
networks-interface
Настройка мультикаст-маршрутизации
Настройка мультикаст-маршрутизации в виртуальном маршрутизаторе производится с использованием команды:
Admin@nodename# set network virtual-router <virtual-router-name> multicast-router
Далее необходимо указать параметры мультикаст-маршрутизации.
Параметр
Описание
enabled
Включение или отключение RIP-маршрутизатора:
on;
off
ecmp
Разрешение распределения трафика по нескольким маршрутам по технологии Equal Cost Multi Path (ECMP):
on;
off.
Требуется наличие нескольких маршрутов до необходимого сетевого узла. Если данная опция отключена, то весь трафик на определенный хост назначения будет пересылаться только через один из роутеров (next hop)
ecmp-rebalance
Использование ECMP rebalance:
on — если один из интерфейсов, через который отсылался трафик, отключился, то все существующие потоки будут перераспределены между оставшимися маршрутами (next hop).
off — если один из интерфейсов, через который отсылался трафик, отключился, то перераспределяются только те потоки, которые передавались через отключенный интерфейс
join-prune
Интервал отправки сообщений соседям PIM о мультикаст-группах, трафик которых маршрутизатор хочет принимать или более не хочет принимать
register-suppress
Интервал, после которого маршрутизатор отсылает сообщение register suppress
keep-alive
Интервал, через который маршрутизатор будет посылать сообщения keepalive соседям, а также интервал, который маршрутизатор будет ждать, прежде чем будет считать соседа недоступным
interfaces
Интерфейс, который будет использоваться для работы мультикаста; для указания доступны только интерфейсы, добавленные в виртуальный маршрутизатор.
Для добавления интерфейсов или изменения данных о ранее добавленных интерфейсах используются следующие команды:
Admin@nodename# set network virtual-router <virtual-router-name> multicast-router interfaces new
Admin@nodename# set network virtual-router <virtual-router-name> multicast-router interfaces <interface-name>
Далее необходимо указать параметры:
interface — выбор интерфейса для работы мультикаст. Для выбора доступны только те интерфейсы, которые входят в данный виртуальный маршрутизатор.
hello-timeout — интервал отправки PIM HELLO сообщений в секундах. PIM Hello сообщения отправляются периодически со всех интерфейсов, для которых включена поддержка мультикастинга. Эти сообщения позволяют узнать маршрутизатору о соседних маршрутизаторах, поддерживающих мультикастинг.
dr-priority — приоритет при выборе Designated router (DR), с помощью которого администратор может управлять процессом выбора DR для локальной сети.
bfd: добавить профиль bfd (Bidirectional Forwarding Detection). Профили bfd создаются в библиотеке элементов. Подробнее — в разделе «
Настройка библиотек
enable-igmp — приём сообщений IGMP report и IGMP query на данном интерфейсе.
use-igmpv2 — использование версии IGMP v2, по умолчанию используется IGMP v3
rendevouz-points
При настройке Rendevouz points можно указать следующие параметры:
enabled — включение/отключение данного RP:
on;
off.
name — название RP.
ip — Unicast IP-адрес RP.
asm-allowed-groups — список разрешенных групповых адресов для any source multicast с данного RP. Любые сети из диапазона 224.0.0.0/4. Если ничего не задано, то ограничений нет
ssm-allowed-groups
Настройка мультикаст роутера, определяющая список разрешенных групповых адресов для source specific multicast. Могут быть указаны любые сети из диапазона 232.0.0.0/8; если ничего не задано, то ограничений нет
spt-exclusions
Настройка мультикаст роутера, задающая список IPv4 мультикаст-групп, исключенных из переключения на shortest path tree
Команда для отображения конфигурации мультикастинга в виртуальном маршрутизаторе:
Admin@nodename# show network virtual-router <virtual-router-name> multicast-router
Пример команды конфигурирования мультикаст-маршрутизации в виртуальном маршрутизаторе:
Admin@nodename# set network virtual-router test_router multicast-router interfaces new interface port2 use-igmpv2 on
Admin@nodename# show network virtual-router test_router
name                : test_router
description         : Test virtual router
node-name           : node_1
interfaces          : port2; port3
...
multicast-router    :
enabled               : off
ecmp-rebalance        : off
ecmp                  : off
join-prune            : 60
keep-alive            : 31
register-suppress     : 5
interfaces            :
port2
interface        : port2
enabled          : off
enable-igmp      : off
use-igmpv2       : on
bfd              : Not set
rendevouz-points      : []
...
Команда для удаления параметров мультикаст-маршрутизатора:
Admin@nodename# delete network virtual-router <virtual-router-name> multicast-router
Для удаления доступны следующие параметры:
Интерфейсы, использующиеся для работы мультикаста:
interfaces
Rendevouz points:
rendevouz-points <rp-name>
, а также список разрешенных групповых адресов для any source multicast с данного RP:
rendevouz-points <rp-name> asm-allowed groups
Cписок разрешенных групповых адресов для source specific multicast:
ssm-allowed-groups
Cписок IPv4 мультикаст-групп, исключенных из переключения на shortest path tree:
spt-exclusions
DNS-настройки
Настройка WCCP

## Источник

https://docs.usergate.com/nastrojka-virtual6nyh-marshrutizatorov_2667.html
