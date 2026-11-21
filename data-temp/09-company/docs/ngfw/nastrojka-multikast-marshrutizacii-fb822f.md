---
заголовок: Настройка мультикаст маршрутизации
url: https://docs.usergate.com/nastrojka-mul6tikast-marshrutizacii_24.html
источник: портал документации
получено: 2026-11-20 16:12 +0700
продукт: NGFW
версия: 6.1.8, 6.1.9
раздел: Настройка мультикаст маршрутизации
id_статьи: 24
обновлено: 12 Jan, 2023
ревизия: 6
---

# Настройка мультикаст маршрутизации

Содержание:
KnowledgeBase:
Мультикаст (multicast) - технология широковещательной передачи данных, которая позволяет организовывать единовременную многоадресную рассылку и потоковую передачу данных в режиме реального времени.
Технология IP мультикастинга позволяет существенно сократить объем передаваемого трафика, тем самым обеспечивая рациональное использование пропускной способности, экономию вычислительных возможностей сервера и снижение нагрузки на сеть. Технология является особенно эффективной для доставки голосового и видео трафика, т.к. позволяет доставлять единый поток информации к тысячам потребителей.
Мультикаст маршрутизация позволяет доставлять трафик к группе хостов - мультикаст-группе, которая идентифицируется групповым адресом. Хосты (получатели), которые хотят получать данный трафик должны присоединиться к соответствующей мультикаст-группе по протоколу IGMP (Internet Group Management Protocol). Подробнее о технологии читайте в
UserGate 6. Руководство администратора
По представленной схеме произведём настройку мультикаст маршрутизации по протоколу маршрутизации многоадресных сообщений PIM-SM (Protocol Independent Multicast Sparse Mode) протокола с использованием протокола динамической маршрутизации OSPF для unicast пакетов.
Сначала происходит установка соседства между маршрутизаторами путём отправки Hello сообщений (сообщение отправляется всем соседям, кроме того, от кого был получен данный пакет). Остальные мультикаст маршрутизаторы повторяют данный процесс. Путь, который прошел мультикаст пакет от источника до конечных получателей, образует дерево, которое называется — source-based distribution tree, shortest-path tree (SPT), source tree.
При запуске на сервере приложения с поддержкой мультивещания, оно посылает в сеть уведомление, что соответствующая группа доступна для присоединения. Клиент, который хочет присоединиться к группе, посылает об этом уведомление. Все промежуточные маршрутизаторы записывают, что за соответствующим маршрутом есть клиент соответствующей мультикаст-группы.
После получения данных об отправителе и получателе трафика на роутерах формируются таблицы мультикаст маршрутизации. Для обеспечения актуальности информации о источнике и получателе трафика используется точки рандеву Rendezvous Point — RP благодаря которым происходит связность источника с приёмниками трафика. Запрос роутерами мультикастового трафика выполняется с помощью сообщения PIM Join. В начале весь мультикаст трафик идёт через RP, но после определения более короткого пути трафик пойдёт по нему.
Настройка UserGate.
В разделе
Сеть ➜ Зоны
во вкладке
Контроль доступа
необходимо разрешить OSPF и Multicast.
Произвести настройку виртуальных маршрутизаторов в разделе
Сеть ➜ Виртуальные маршрутизаторы
Настройка Default VRF.
OSPF:
Идентификатор маршрутизатора: 10.10.12.20.
Redistribute: connected.
Интерфейсы: port 2, port 3.
Области: area 1.
Мультикаст маршрутизатор:
Port 2: отключить чекбокс IGMP.
Port 3: включить чекбокс IGMP.
Настройка ISP1.
OSPF:
Идентификатор маршрутизатора: 10.10.11.13.
Redistribute: connected.
Интерфейсы: port 0, port 1.
Области: area 1.
Мультикаст маршрутизатор:
Port 0: включить чекбокс IGMP.
Port 1: отключить чекбокс IGMP.
IP-адрес Rendevouz points: 1.1.1.1.
В разделе
Политики сети ➜ Межсетевой экран
настроить разрешающее правило, указав IP-адреса назначения 225.1.2.3 и 239.1.2.3.
Настройка маршрутизаторов Cisco.
Далее будут представлены настройки маршрутизаторов R1, R2, R3 и R4.
Для маршрутизатора R1 с использованием следующей команды включить мультикаст маршрутизацию.
ip multicast-routing
Далее необходимо создать логический Loopback Interface с адресом 1.1.1.1 и настроить режим PIM-SM.
interface Loopback1
ip address 1.1.1.1 255.255.255.255
ip pim sparse-mode
С использованием следующих команд производится настройка интерфейсов Fast Ethernet 1/0, Fast Ethernet 1/1, Fast Ethernet 2/0 и Fast Ethernet2/1: им присваиваются соответствующие IP-адреса, настраивается использование режима PIM-SM и автоматическое согласование скорости и дуплексного режима.
interface FastEthernet1/0
ip address 10.10.11.16 255.255.255.0>
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet1/1
ip address 172.17.1.2 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet2/0
ip address 172.22.1.1 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet2/1
ip address 172.20.1.2 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
Далее необходимо настроить протокол OSPF на маршрутизаторе, чтобы роутеры могли постоянно обмениваться информацией про известные маршруты и состояние соединений (где 1 — это идентификатор процесса для маршрутизатора):
router ospf 1
router-id 1.1.1.1
Также можно включить журналирование протокола и перераспределение маршрутизатором всех подключённых сетей:
log-adjacency-changes>
redistribute connected subnets
Далее указываются сети, которые маршрутизатор будет транслировать в другие сети:
network 10.10.11.0 0.0.0.255 area 1
network 172.17.1.0 0.0.0.255 area 1
network 172.20.1.0 0.0.0.255 area 1
network 172.22.1.0 0.0.0.255 area 1
Далее задаются RP и указываются их IP-адреса:
ip pim rp-address 1.1.1.1 RP1
ip pim rp-address 3.3.3.3 RP2
С использованием следующих команд создаются именованные списки доступа, которые разрешают трафик с адресов 225.1.2.3 (RP1) и 239.1.2.3 (RP2).
ip access-list standard RP1
permit 225.1.2.3
ip access-list standard RP2>
permit 239.1.2.3
Настройка маршрутизаторов R2, R3 и R4 производится аналогично.
Конфигурация R2:
ip multicast-routing>
interface Loopback1
ip address 2.2.2.2 255.255.255.255>
ip pim sparse-mode
interface FastEthernet1/0
ip address 172.17.1.1 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet1/1
ip address 172.19.1.1 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet2/0
ip address 172.18.1.1 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet2/1
ip address 10.10.6.2 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
router ospf 1
router-id 2.2.2.2
log-adjacency-changes
redistribute connected subnets
network 172.17.1.0 0.0.0.255 area 1
network 172.18.1.0 0.0.0.255 area 1
network 172.19.1.0 0.0.0.255 area 1
ip pim rp-address 1.1.1.1 RP1
ip pim rp-address 3.3.3.3 RP2
ip access-list standard RP1
permit 225.1.2.3
ip access-list standard RP2
permit 239.1.2.3
Конфигурация R3:
nip multicast-routing
interface Loopback1
ip address 3.3.3.3 255.255.255.255
ip pim sparse-mode
interface FastEthernet1/0
ip address 172.21.1.1 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet1/1
ip address 172.19.1.2 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet2/0
ip address 172.20.1.1 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet2/1
no ip address
ip pim sparse-mode
duplex auto
speed auto
router ospf 1
router-id 3.3.3.3
log-adjacency-changes
redistribute connected subnets
network 172.19.1.0 0.0.0.255 area 1
network 172.20.1.0 0.0.0.255 area 1
network 172.21.1.0 0.0.0.255 area 1
ip pim rp-address 1.1.1.1 RP1
ip pim rp-address 3.3.3.3 RP2
ip access-list standard RP1
permit 225.1.2.3
ip access-list standard RP2
permit 239.1.2.3
Конфигурация R4:
ip multicast-routing
interface Loopback1
ip address 4.4.4.4 255.255.255.255
ip pim sparse-mode
interface FastEthernet1/0
ip address 172.22.1.2 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet1/1
ip address 172.21.1.2 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet2/0
ip address 172.18.1.2 255.255.255.0
ip pim sparse-mode
duplex auto
speed auto
interface FastEthernet2/1
ip address 10.10.12.23 255.255.255.0
ip pim sparse-mode
ip igmp query-interval 125
duplex auto
speed auto
router ospf 1
router-id 4.4.4.4
log-adjacency-changes
redistribute connected subnets
network 10.10.12.0 0.0.0.255 area 1
network 172.18.1.0 0.0.0.255 area 1
network 172.21.1.0 0.0.0.255 area 1
network 172.22.1.0 0.0.0.255 area 1
ip pim rp-address 1.1.1.1 RP1
ip pim rp-address 3.3.3.3 RP2
ip access-list standard RP1
permit 225.1.2.3
ip access-list standard RP2
permit 239.1.2.3
Если клиент больше не хочет получать мультикаст трафик, то ему необходимо отправить запрос на отсоединение от группы: сообщение PIM Prune.
Выявлениe ошибок мультикаст маршрутизации на оборудовании Cisco
С использованием команды show ip pim neighbor
на оборудовании Cisco можно посмотреть список соседних мультикаст маршрутизаторов.
R1#sh ip pim neighbor
PIM Neighbor Table
Mode: B - Bidir Capable, DR - Designated Router, N - Default DR Priority, S - State Refresh Capable
Neighbor Interface Uptime/Expires Ver DR
Address Prio/Mode
10.10.11.13 FastEthernet1/0 1d22h/00:01:28 v2 1 /
172.17.1.1 FastEthernet1/1 1d22h/00:01:23 v2 1 / S P
172.22.1.2 FastEthernet2/0 1d22h/00:01:35 v2 1 / DR S P
172.20.1.1 FastEthernet2/1 1d22h/00:01:15 v2 1 / S P
Команда show ip mroute отобразит мультикаст маршрут.
R1#sh ip mroute 225.1.2.3
IP Multicast Routing Table
Flags: D - Dense, S - Sparse, B - Bidir Group, s - SSM Group, C - Connected, L - Local, P - Pruned, R - RP-bit set, F - Register flag, T - SPT-bit set, J - Join SPT, M - MSDP created entry, X - Proxy Join Timer Running, A - Candidate for MSDP Advertisement, U - URD, I - Received Source Specific Host Report, Z - Multicast Tunnel, z - MDT-data group sender, Y - Joined MDT-data group, y - Sending to MDT-data group, V - RD & Vector, v – Vector
Outgoing interface flags: H - Hardware switched, A - Assert winner
Timers: Uptime/Expires
Interface state: Interface, Next-Hop or VCD, State/Mode
(*, 225.1.2.3), 1d22h/00:03:03, RP 1.1.1.1, flags: S - есть отправитель трафика
Incoming interface: Null, RPF nbr 0.0.0.0
Outgoing interface list:
FastEthernet1/0, Forward/Sparse, 00:01:01/00:03:03
FastEthernet1/1, Forward/Sparse, 01:06:06/00:02:51
(10.10.6.3, 225.1.2.3), 1d22h/00:03:22, flags: T - есть получатель трафика
Incoming interface: FastEthernet1/1, RPF nbr 172.17.1.1
Outgoing interface list:
FastEthernet1/0, Forward/Sparse, 00:00:30/00:03:03
v6.x
Варианты настройки BGP для кластера Актив-Пассив
Настройка статической маршрутизации

## Источник

https://docs.usergate.com/nastrojka-mul6tikast-marshrutizacii_24.html
