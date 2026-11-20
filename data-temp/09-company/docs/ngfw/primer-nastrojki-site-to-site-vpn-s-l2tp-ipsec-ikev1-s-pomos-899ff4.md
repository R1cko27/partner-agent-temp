---
заголовок: Пример настройки Site-to-Site VPN с L2TP/IPSec(IKEv1) с помощью интерфейса CLI
url: https://docs.usergate.com/primer-nastrojki-site-to-site-vpn-s-l2tpipsec(ikev1)-s-pomosh6yu-interfejsa-cli_1340.html
получено: 2026-11-20 16:12 +0700
продукт: NGFW
версия: 7.x
раздел: Пример настройки Site-to-Site VPN с L2TP/IPSec(IKEv1) с помощью интерфейса CLI
id_статьи: 1340
обновлено: 26 Aug, 2024
ревизия: 18
---

# Пример настройки Site-to-Site VPN с L2TP/IPSec(IKEv1) с помощью интерфейса CLI

Содержание:
Technology: VPN
В качестве примера для создания Site-to-Site VPN-туннеля будет рассмотрена следующая схема:
Настройка VPN-сервера
Для настройки узла NGFW 1 в качестве VPN-сервера необходимо выполнить следующие шаги:
Шаг 1
. Контроль доступа зоны.
Разрешим сервис VPN в контроле доступа зоны, c которой будут подключаться VPN-клиенты.
Для редактирования параметров зоны используется следующая команда:
Admin@ug# set network zone <parameters>
Подробнее о командах и параметрах для создания/редактирования зон в CLI смотрите в статье
Зоны
Пример редактирования зоны
Untrusted
с целью разрешить сервис VPN в этой зоне:
Admin@ug# set network zone Untrusted enabled-services [ VPN ]
Шаг 2
. Создание зоны для VPN подключений.
Для создания зон используется следующая команда:
Admin@ug# create network zone <parameters>
Подробнее о командах и параметрах для создания/редактирования зон в CLI смотрите в статье
Зоны
На узле уже создана зона
VPN for Site-to-Site
. Воспользуемся этой зоной для рассматриваемого примера:
Admin@ug# show network zone
+ <Enter>                      Finish input
+ (                            Start complex filter
+ Cluster
+ DMZ
+ Management
+ Trusted
+ "Tunnel inspection zone"
+ Untrusted
+ "VPN for remote access"
+ "VPN for Site-to-Site"
Admin@ug# show network zone "VPN for Site-to-Site"
name                        : VPN for Site-to-Site
antispoof-enable            : off
antispoof-negate            : off
dos-protection-syn          :
enabled            : on
aggregate          : off
alert-threshold    : 3000
drop-threshold     : 6000
dos-protection-udp          :
enabled            : on
aggregate          : off
alert-threshold    : 3000
drop-threshold     : 6000
dos-protection-icmp         :
enabled            : on
aggregate          : off
alert-threshold    : 100
drop-threshold     : 200
services-access             :
service              : Any ICMP
allowed-addresses    : Any
enabled              : on
service              : reponse_pages
allowed-addresses    : Any
enabled              : on
service              : DNS
allowed-addresses    : Any
enabled              : on
service              : HTTP Proxy
allowed-addresses    : Any
enabled              : on
service              : Endpoint connect
allowed-addresses    : Any
enabled              : on
sessions-limit-enabled      : off
sessions-limit-threshold    : 0
Шаг 3
. Настройка параметров аутентификации.
1. Создадим локальную учетную запись для аутентификации сервера, выступающего в роли VPN-клиента.
Для этого используется следующая команда:
Admin@ug# create users user <parameters>
Подробнее о командах и параметрах для создания локальных пользователей в CLI смотрите в статье
Настройки пользователей
Пример создания учетной записи vpn client 1 с логином
vpnclnt1
, входящего в группу
VPN servers
Admin@ug# create users user name "vpn client 1" login vpnclnt1 groups [ "VPN servers" ] enabled on
2. Создадим профиль аутентификации для VPN пользователей.
Для этого используется следующая команда:
Admin@ug# create users auth-profile <parameter>
Подробнее о порядке создания профилей аутентификации для пользователей в CLI смотрите в статье
Настройка профилей аутентификации
Пример создания профиля аутентификации local с аутентификацией по базе данных локально заведенных пользователей:
Admin@ug# create users auth-profile name local auth-methods local-user-auth on
Шаг 4
. Создание профиля безопасности VPN-сервера.
Для создания профиля безопасности VPN-сервера используется следующая команда:
Admin@ug# create vpn server-security-profiles <parameters>
Подробнее о порядке создания профилей безопасности VPN в CLI смотрите в статье
Настройка профилей безопасности VPN
Изначально для примера на узле уже создан профиль безопасности
Site-to-Site VPN profile
, задающий необходимые настройки:
Admin@ug# show vpn server-security-profiles
Site-to-Site VPN profile
name                    : Site-to-Site VPN profile
description             : Example VPN security profile for Site-to-Site VPN. Preshared key is "examplepresharedkey" - it must be changed! This profile can be changed or deleted if necessary.
ike-version             : 1
ike-mode                : main
local-id-type           : none
certificate             : no certificate
authentication-mode     : any
dh-groups               : Group 2 Prime 1024 bit; Group 14 Prime 2048 bit
dpd-state               : off
dpd-interval            : 60
dpd-max-failures        : 5
phase1-security         :
authentication    : SHA1
encryption        : AES256
authentication    : SHA256
encryption        : AES256
phase1-key-lifetime     : 1 d
phase2-key-lifetime     : 12 h
key-lifesize-enabled    : off
key-lifesize            : 4 GB
phase2-security         :
authentication    : SHA1
encryption        : AES256
authentication    : SHA256
encryption        : AES256
nat-keepalive           : 0
Admin@ug# set vpn server-security-profiles "Site-to-Site VPN profile" ike-version 1 psk 123456
Шаг 5
. Создание VPN-интерфейса.
Для создания VPN-интерфейса используется следующая команда:
Admin@ug# create network interface vpn <parameters>
Подробнее о порядке создания VPN-интерфейса в CLI смотрите в статье
Интерфейсы
Для примера на узле уже создан VPN-интерфейс
tunnel2
, который может быть использован для настройки Site-to-Site VPN:
Admin@ug# show network interface vpn tunnel2
type               : vpn
node_name          : cluster
name               : tunnel2
description        : Example VPN interface to be used in Site-to-Site VPN server rule. This is an example VPN interface which
can be changed or deleted if necessary.
enabled            : on
netflow-profile    : Undefined
iface-mode         : manual
mtu                : 1420
speed              : 0
zone               : VPN for Site-to-Site
running            : off
master             : off
Admin@ug# set network interface vpn tunnel2 ip-addresses [ 172.30.255.1/24 ]
Admin@ug# show network interface vpn tunnel2
type               : vpn
node_name          : cluster
name               : tunnel2
description        : Example VPN interface to be used in Site-to-Site VPN server rule. This is an example VPN interface which
can be changed or deleted if necessary.
enabled            : on
netflow-profile    : Undefined
iface-mode         : static
mtu                : 1420
speed              : 0
zone               : VPN for Site-to-Site
running            : off
master             : off
ip-addresses       : 172.30.255.1/24
Шаг 6
. Создание сети VPN.
Для создания сети VPN используется следующая команда:
Admin@ug# create vpn networks <parameters>
Подробнее о порядке создания сети VPN в CLI смотрите в статье
Настройка сетей VPN
Для примера на узле уже создана сеть
Site-to-Site VPN network
с настройками по умолчанию. Скорректируем в ней диапазон IP-адресов для установления VPN с NGFW 2:
Admin@ug# show vpn networks
Site-to-Site VPN network
name                   : Site-to-Site VPN network
description            : Example VPN network for Site-to-Site VPN. It can be changed or deleted if necessary.
mask                   : 255.255.255.0
use-system-dns         : on
ip-range               : 172.30.255.2-172.30.255.254
all-routes             : off
restrict-lan-access    : off
Admin@ug# set vpn networks "Site-to-Site VPN network" ip-range 172.30.255.2-172.30.255.2
Admin@ug# show vpn networks
Site-to-Site VPN network
name                   : Site-to-Site VPN network
description            : Example VPN network for Site-to-Site VPN. It can be changed or deleted if necessary.
mask                   : 255.255.255.0
use-system-dns         : on
ip-range               : 172.30.255.2-172.30.255.2
all-routes             : off
restrict-lan-access    : off
В качестве маршрута, передаваемого VPN-клиенту, добавим в настройки этой сети заранее созданный список Local network, включающий в себя подсеть 192.168.1.0/24:
Admin@ug# set vpn networks "Site-to-Site VPN network routes-ip-list [ "Local network" ]
Admin@ug# show vpn networks
Site-to-Site VPN network
name                   : Site-to-Site VPN network
description            : Example VPN network for Site-to-Site VPN. It can be changed or deleted if necessary.
mask                   : 255.255.255.0
use-system-dns         : on
routes-ip-list         : Local network
ip-range               : 172.30.255.2-172.30.255.2
all-routes             : off
restrict-lan-access    : off
Шаг 7
. Создание серверного правила VPN.
Правила для VPN-сервера создаются с помощью синтаксиса UPL командой:
Admin@ug# create vpn server-rules <position> upl-rule <commands>
Подробнее о порядке настройки серверных правил VPN в CLI смотрите в статье
Настройка серверных правил
Для примера на узле создано серверное правило
Site-to-Site VPN rule
, в котором используются необходимые настройки для Site-to-Site VPN, а доступ к VPN разрешен членам локальной группы
VPN servers
Admin@ug# show vpn server-rules
% ----------------- 1 -----------------
OK \
user = "CN=VPN servers,DC=LOCAL" \
src.zone = Untrusted \
profile("Site-to-Site VPN profile") \
auth_profile(local) \
vpn_network("Site-to-Site VPN network") \
interface(tunnel2) \
desc("Example VPN server rule which allows access for Site-to-Site VPN clients connections from Untrusted zone and places them to VPN for Site-to-Site zone (zone assigned to VPN interface). This rule can be changed or deleted if necessary.") \
enabled(false) \
name("Site-to-Site VPN rule")
В качестве адреса назначения добавим в правило заранее созданный список Ext. address, в который входит внешний IP-адрес VPN-сервера NGFW 1 — 203.0.113.1, и включим это правило:
Admin@ug# set vpn server-rules 1 upl-rule OK \
...dst.ip = lib.network("Ext. address") \
...enabled(true)
Admin@ug# show vpn server-rules
% ----------------- 1 -----------------
OK \
user = "CN=VPN servers,DC=LOCAL" \
src.zone = Untrusted \
dst.ip = lib.network("Ext. address") \
profile("Site-to-Site VPN profile") \
auth_profile(local) \
vpn_network("Site-to-Site VPN network") \
interface(tunnel2) \
desc("Example VPN server rule which allows access for Site-to-Site VPN clients connections from Untrusted zone and places them to VPN for Site-to-Site zone (zone assigned to VPN interface). This rule can be changed or deleted if necessary.") \
enabled(true) \
name("Site-to-Site VPN rule")
Шаг 8
. Контроль доступа к ресурсам.
Правила межсетевого экрана создаются с помощью синтаксиса UPL командой:
Admin@ug# create network-policy firewall <position> upl-rule <commands>
Подробнее о порядке настройки правил межсетевого экрана в CLI смотрите в статье
Настройка правил межсетевого экрана
Изначально для примера на узле уже создано правило межсетевого экрана
VPN for Site-to-Site to Trusted and Untrusted
, разрешающее весь трафик из зоны
VPN for Site-to-Site
в зоны
Trusted
Untrusted
. Правило выключено по умолчанию, необходимо его включить:
Admin@ug# show network-policy firewall
% ----------------- 1 -----------------
PASS \
src.zone = Trusted \
dst.zone = Untrusted \
desc("Firewall rule which allows traffic from Trusted zone to Untrusted zone. This is an example rule which can be changed or deleted if necessary.") \
rule_log(session) \
enabled(false) \
name("Allow trusted to untrusted")
% ----------------- 2 -----------------
PASS \
src.zone = "VPN for Site-to-Site" \
dst.zone = (Untrusted, Trusted) \
desc("Example firewall rule which allows traffic from VPN for Site-to-Site zone to Trusted and Untrusted zones. This is an example rule which can be changed or deleted if necessary.") \
rule_log(session) \
enabled(false) \
name("VPN for Site-to-Site to Trusted and Untrusted")
Admin@ug# set network-policy firewall 2 upl-rule PASS \
...enabled(true)
Admin@ug# show network-policy firewall 2
% ----------------- 2 -----------------
PASS \
src.zone = "VPN for Site-to-Site" \
dst.zone = (Untrusted, Trusted) \
desc("Example firewall rule which allows traffic from VPN for Site-to-Site zone to Trusted and Untrusted zones. This is an example rule which can be changed or deleted if necessary.") \
rule_log(session) \
enabled(true) \
name("VPN for Site-to-Site to Trusted and Untrusted")
Чтобы трафик передавался клиенту из разрешенных зон через VPN-туннель, необходимо создать разрешающее правило межсетевого экрана, указав нужную зону источника и зону назначения, например,
VPN for Site-to-Site
Пример создания правила межсетевого экрана для разрешения трафика из зоны
VPN for Site-to-Site
в зоны
Trusted
Untrusted:
Admin@ug# create network-policy firewall 3 upl-rule PASS \
...src.zone = "VPN for Site-to-Site" \
...dst.zone = (Trusted, Untrusted) \
...rule_log(session) \
...name("VPN for Site-to-Site to Trusted and Untrusted") \
...enabled(true)
Настройка VPN-клиента
Для настройки NGFW 2 в качестве VPN-клиента необходимо выполнить следующие шаги:
Шаг 1
. Создание зоны, в которую будут помещен интерфейс, используемый для подключения по VPN.
На узле уже создана зона
VPN for Site-to-Site
. Воспользуемся этой зоной для рассматриваемого примера:
Admin@ug2# show network zone "VPN for Site-to-Site"
name                        : VPN for Site-to-Site
antispoof-enable            : off
antispoof-negate            : off
dos-protection-syn          :
enabled            : on
aggregate          : off
alert-threshold    : 3000
drop-threshold     : 6000
dos-protection-udp          :
enabled            : on
aggregate          : off
alert-threshold    : 3000
drop-threshold     : 6000
dos-protection-icmp         :
enabled            : on
aggregate          : off
alert-threshold    : 100
drop-threshold     : 200
services-access             :
service              : Any ICMP
allowed-addresses    : Any
enabled              : on
service              : reponse_pages
allowed-addresses    : Any
enabled              : on
service              : DNS
allowed-addresses    : Any
enabled              : on
service              : HTTP Proxy
allowed-addresses    : Any
enabled              : on
service              : Endpoint connect
allowed-addresses    : Any
enabled              : on
sessions-limit-enabled      : off
sessions-limit-threshold    : 0
Шаг 2
. Создать VPN-интерфейс.
Для примера на узле уже создан VPN-интерфейс
tunnel3
, который может быть использован для настройки Site-to-Site VPN.
Admin@ug2# show network interface vpn tunnel3
type               : vpn
node_name          : cluster
name               : tunnel3
description        : Example VPN interface to be used in Site-to-Site VPN client rule. This is an example VPN interface which
can be changed or deleted if necessary.
enabled            : off
netflow-profile    : Undefined
iface-mode         : dynamic
mtu                : 1420
speed              : 0
zone               : VPN for Site-to-Site
running            : off
master             : off
Admin@ug2# set network interface vpn tunnel3 enabled on
Admin@ug2# show network interface vpn tunnel3
type               : vpn
node_name          : cluster
name               : tunnel3
description        : Example VPN interface to be used in Site-to-Site VPN client rule. This is an example VPN
interface which can be changed or deleted if necessary.
enabled            : on
netflow-profile    : Undefined
iface-mode         : dynamic
mtu                : 1420
speed              : 0
zone               : VPN for Site-to-Site
running            : off
master             : off
Шаг 3
. Контроль доступа к ресурсам.
Настройки в CLI аналогичны настройкам на NGFW 1 (См.
Шаг 8
настройки NGFW 1 в cli).
Шаг 4
. Создать профиль безопасности VPN-клиента.
Для создания профиля безопасности VPN-клиента используется следующая команда:
Admin@ug2# create vpn client-security-profiles <parameters>
Подробнее о порядке создания профилей безопасности VPN в CLI смотрите в статье
Настройка профилей безопасности VPN
Для примера на узле уже создан профиль безопасности
Client VPN profile
, задающий необходимые настройки.  Добавим в профиль общий ключ, аналогичный заданному в настройках VPN-сервера на
Шаге 4
, и логин/пароль созданной на
Шаге 3
учетной записи для аутентификации VPN-клиента при установлении L2TP туннеля:
Admin@ug2# show vpn client-security-profiles
Client VPN profile
name                    : Client VPN profile
description             : Example VPN security profile for client VPN rule. Preshared key is
"examplepresharedkey" - it must be changed! This profile can be changed or deleted if
necessary.
protocol                : ipsec2
ike-mode                : main
local-id-type           : none
certificate             : no certificate
dh-groups               : Group 2 Prime 1024 bit; Group 14 Prime 2048 bit
dpd-state               : off
dpd-interval            : 60
dpd-max-failures        : 5
phase1-security         :
authentication    : SHA1
encryption        : AES256
authentication    : SHA256
encryption        : AES256
phase1-key-lifetime     : 1 d
phase2-key-lifetime     : 12 h
key-lifesize-enabled    : off
key-lifesize            : 4 GB
phase2-security         :
authentication    : SHA1
encryption        : AES256
authentication    : SHA256
encryption        : AES256
nat-keepalive           : 0
Admin@ug2# set vpn client-security-profiles "Client VPN profile" protocol ipsec2 psk 123456 authentication-login vpnclnt1 authentication-password 123123
Шаг 5
. Создать клиентское правило VPN.
Правила для VPN-клиента создаются с помощью синтаксиса UPL командой:
Admin@ug2# create vpn client-rules <position> upl-rule <commands>
Подробнее о порядке настройки клиентских правил VPN в CLI смотрите в статье
Настройка клиентских правил
Для примера на узле уже создано серверное правило
Client VPN rule
, в котором используются необходимые настройки для Site-to-Site VPN. Необходимо добавить в это правило IP-адрес VPN-сервера, куда подключается данный VPN-клиент. В рассматриваемом примере это IP-адрес интерфейса в зоне
Untrusted
на NGFW 1 — 203.0.113.1.
Admin@ug2# set vpn client-rules 1 upl-rule OK \
...server_address("203.0.113.1") \
...enabled(true)
Admin@ug2# show vpn client-rules
% ----------------- 1 -----------------
OK \
server_address("203.0.113.1") \
last_error(Disabled) \
status(disconnected) \
connection_time(0) \
profile("Client VPN profile") \
interface(tunnel3) \
desc("Example VPN client rule which connect UserGate server as client to another UserGate server acting as VPN server. This rule can be changed or deleted if necessary.") \
enabled(true) \
name("Client VPN rule")
После завершения настройки VPN-сервера и VPN-клиента и активации правил VPN клиент инициирует соединение в сторону сервера, и в случае корректности настроек, поднимается VPN-туннель. Для отключения туннеля выключите клиентское (на клиенте) или серверное (на сервере) правило VPN.
Проверка VPN-соединения
Проверка доступности соседнего узла и маршрута в сеть удаленного офиса.
Со стороны NGFW 1:
Admin@ug> show network route
Codes: K - kernel route, C - connected, S - static, R - RIP,
O - OSPF, B - BGP, T - Table, v - VNC, V - VNC-Direct,
> - selected route, * - FIB route, q - queued, r - rejected, b - backup
t - trapped, o - offload failure
C>* 203.0.113.0/24 is directly connected, port2, 04:20:11
K>* 100.100.0.0/24 [0/0] via 172.30.255.2, tunnel2, 04:19:43
C>* 172.30.255.0/24 is directly connected, tunnel2, 04:20:11
C>* 192.168.1.0/24 is directly connected, port1, 04:20:11
C>* 192.168.56.0/24 is directly connected, port0, 04:20:11
Admin@ug> ping host 172.30.255.2
PING 172.30.255.2 (172.30.255.2) 56(84) bytes of data.
64 bytes from 172.30.255.2: icmp_req=1 ttl=64 time=3.34 ms
64 bytes from 172.30.255.2: icmp_req=2 ttl=64 time=2.49 ms
64 bytes from 172.30.255.2: icmp_req=3 ttl=64 time=1.04 ms
--- 172.30.255.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 1.041/2.292/3.347/0.953 ms
Со стороны NGFW 2:
Admin@ug2> show network route
Codes: K - kernel route, C - connected, S - static, R - RIP,
O - OSPF, B - BGP, T - Table, v - VNC, V - VNC-Direct,
> - selected route, * - FIB route, q - queued, r - rejected, b - backup
t - trapped, o - offload failure
C>* 198.51.100.0/24 is directly connected, port2, 04:18:41
C>* 100.100.0.0/24 is directly connected, port1, 04:18:41
C>* 172.30.255.0/24 is directly connected, tunnel3, 00:08:00
C>* 192.168.56.0/24 is directly connected, port0, 04:18:41
Admin@ug2> ping host 172.30.255.1
PING 172.30.255.1 (172.30.255.1) 56(84) bytes of data.
64 bytes from 172.30.255.1: icmp_req=1 ttl=64 time=2.92 ms
64 bytes from 172.30.255.1: icmp_req=2 ttl=64 time=2.04 ms
64 bytes from 172.30.255.1: icmp_req=3 ttl=64 time=1.13 ms
--- 172.30.255.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2001ms
rtt min/avg/max/mdev = 1.138/2.032/2.920/0.729 ms
Также опубликовано в
Документация -> NGFW -> NGFW 7.x Руководство администратора -> Настройка VPN -> Примеры настройки VPN
Пример настройки Site-to-Site VPN с IPSec(IKEv2)
Пример настройки Site-to-Site VPN с L2TP/IPSec(IKEv1)

## Источник

https://docs.usergate.com/primer-nastrojki-site-to-site-vpn-s-l2tpipsec(ikev1)-s-pomosh6yu-interfejsa-cli_1340.html
