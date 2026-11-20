---
заголовок: Настройка сетей VPN
url: https://docs.usergate.com/nastrojka-setej-vpn_1721.html
получено: 2026-11-20 16:26 +0700
продукт: DCFW
версия: 8.x
раздел: Настройка сетей VPN
id_статьи: 1721
обновлено: 19 Nov, 2024
ревизия: 3
---

# Настройка сетей VPN

Technology: VPN
Настройка VPN-сетей производится на уровне
vpn networks
Для создания сети VPN необходимо использовать следующую команду:
Admin@nodename# create vpn networks <parameters>
Настраиваемые параметры сети VPN:
Параметр
Описание
name
Название сети VPN.
description
Описание сети VPN.
ip-range
Диапазон IP-адресов, которые будут использованы клиентами и сервером; указывается в формате: <IP_start-IP_end>.
Исключите из диапазона адреса, которые назначены VPN-интерфейсу, используемому совместно с данной сетью. Не указывайте здесь адреса сети и широковещательный адрес.
mask
Маска сети, например, 255.255.255.0.
use-system-dns
Назначение клиенту DNS-серверов, которые использует UserGate:
: использовать системных DNS-серверов.
off
: не использовать системных DNS-серверов.
dns-servers
DNS-серверы, которые будут переданы клиенту.
routes-ip
Маршрут VPN. Необходимо указать IP-адрес в формате "A.B.C.D" или "A.B.C.D/m".
routes-ip-list
Маршрут VPN. Необходимо указать группу IP-адресов. Подробнее о создании групп IP-адресов через CLI читайте в разделе
Настройка IP-адресов
all-routes
Отсутствие ограничений на маршрутизацию по VPN соединению при использовании UserGate VPN клиента.
include-routes-ip
IP-адреса, доступ к которым должен маршрутизироваться через VPN соединение при использовании UserGate VPN клиента.
include-routes-ip-list
Список IP-адресов, доступ к которым должен маршрутизироваться через VPN соединение при использовании UserGate VPN клиента.
exclude-routes-ip
IP-адреса, доступ к которым зарыт через VPN соединение при использовании UserGate VPN клиента.
exclude-routes-ip-list
Список IP-адресов, доступ к которым закрыт через VPN соединение при использовании UserGate VPN клиента.
restrict-lan-access
Запрет доступа к локальной сети при использовании UserGate VPN клиента.
Пример команды создания сети VPN:
Admin@nodename# create vpn networks name "Test VPN network" description "This is a new test VPN network" ip-range 10.10.3.2-10.10.2.200 mask 255.255.255.0
Редактирование параметров сети:
Admin@nodename# set vpn networks <network-name> <parameters>
Удаление сети VPN или отдельных парамеров сети VPN:
Admin@nodename# delete vpn networks <network-name>
Просмотр информации о сети VPN:
Admin@nodename# show vpn networks <network-name>
v8.x
Настройка клиентских правил
Настройка профилей безопасности VPN

## Источник

https://docs.usergate.com/nastrojka-setej-vpn_1721.html
