---
заголовок: Настройка виртуальных маршрутизаторов
url: https://docs.usergate.com/nastrojka-virtual6nyh-marshrutizatorov_3010.html
получено: 2026-11-20 16:26 +0700
продукт: WAF
версия: 7.6.x
раздел: Настройка виртуальных маршрутизаторов
id_статьи: 3010
обновлено: 06 Apr, 2026
ревизия: 1
---

# Настройка виртуальных маршрутизаторов

Technology: Routing
В данном разделе описана настройка маршрутизации с использованием интерфейса командной строки (настройка рассмотрена в соответствующих разделах). Настройка производится на уровне
network virtual-router
Далее представлены команды, использующиеся для общей настройки виртуальных маршрутизаторов.
Команда для добавления нового виртуального маршрутизатора:
Admin@nodename# create network virtual-router <parameters>
Далее указываются параметры:
Параметр
Описание
name
Уникальное имя виртуального маршрутизатора.
description
Описание виртуального маршрутизатора
node-name
Выбор узла UserGate, на котором будет создан виртуальный маршрутизатор (при наличии кластера).
interfaces
Интерфейсы, которые будут использованы в данном виртуальном маршрутизаторе. Интерфейсы, добавленные в другие виртуальные маршрутизаторы, добавлены быть не могут; любой из интерфейсов может принадлежать только одному виртуальному маршрутизатору. В виртуальный маршрутизатор разрешается добавлять интерфейсы всех типов — физические, виртуальные, бондинг, и другие.
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
Чтобы удалить виртуальный маршрутизатор используется команда:
Admin@nodename# delete network virtual-router <virtual-router-name>
Настройка статических маршрутов
Для добавления нового статического маршрута используется команда:
Admin@nodename# set network virtual-router <virtual-router-name> routes new
Далее указываются параметры:
Параметр
Описание
enabled
Включение/отключение использования статического маршрута:
off
name
Имя маршрута.
description
Описание маршрута.
type
Тип маршрута:
unicast
— стандартный тип маршрута. Пересылает трафик, адресованный на адреса назначения, через заданный шлюз.
unreachable
— трафик отбрасывается. Источнику отправляется ICMP сообщение host unreachable (type 3 code 1).
prohibit
— трафик отбрасывается. Источнику отправляется ICMP сообщение host unreachable (type 3 code 13).
blackhole
— трафик отбрасывается (теряется), не сообщая источнику о том, что данные не достигли адресата.
destination-ip
IP-адрес подсети назначения; указывается в формате <ip/mask>.
gateway
IP-адрес шлюза, через который будет доступна указанная подсеть; этот IP-адрес должен быть доступен с сервера UserGate.
interface
Интерфейс, через который будет добавлен маршрут.
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
Чтобы изменить параметры созданного ранее статического маршрута, используйте команду:
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
Используйте следующую команду для удаления статического маршрута:
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
Для отображения статических маршрутов:
Admin@nodename# show network virtual-router <virtual-router-name> routes
v7.x
Шлюзы
Настройки раздела Политики сети

## Источник

https://docs.usergate.com/nastrojka-virtual6nyh-marshrutizatorov_3010.html
