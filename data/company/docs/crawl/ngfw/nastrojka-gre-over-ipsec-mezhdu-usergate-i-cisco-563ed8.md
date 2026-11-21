---
заголовок: Настройка GRE over IPsec между UserGate и Cisco
url: https://docs.usergate.com/nastrojka-gre-over-ipsec-mezhdu-usergate-i-cisco_47.html
источник: портал документации
получено: 2026-11-20 16:12 +0700
продукт: NGFW
версия: 6.1.8, 6.1.9
раздел: Настройка GRE over IPsec между UserGate и Cisco
id_статьи: 47
обновлено: 02 Apr, 2024
ревизия: 10
---

# Настройка GRE over IPsec между UserGate и Cisco

Содержание:
KnowledgeBase:
В данной статье рассматривается настройка между UserGate и Cisco зашифрованного канала связи (IPsec) с использованием GRE-туннеля.
Адресация на UserGate:
Выход в интернет настроен через интерфейс port0 с IP-адресом 192.168.57.243 (шлюз по умолчанию: 192.168.57.1).
Локальная сеть подключена через port1 c IP-адресом 10.10.2.1.
Адресация на Cisco:
Выход в интернет настроен через интерфейс FastEthernet0/0 с IP-адресом 192.168.57.150 (шлюз по умолчанию: 192.168.57.1).
Локальная сеть подключена через FastEthernet1/0 c IP-адресом 10.10.3.1.
Конфигурация IPsec на Cisco.
Настроить интерфейс Loopback0:
interface Loopback0
ip address 11.11.3.1 255.255.255.0
Настроить политику ISAKMP:
crypto isakmp policy 1
encr aes
authentication pre-share
group 2
Определить Pre-Shared ключ (указать вместо <psk>):
crypto isakmp key <psk> address 192.168.57.243
Создать расширенный ACL:
ip access-list extended <list-name>
permit ip 11.11.3.0 0.0.0.255 11.11.2.0 0.0.0.255
Создать набор преобразований (Transform Set):
crypto ipsec transform-set <TS-name> esp-aes esp-sha-hmac
mode tunnel
Создать Crypto Map:
crypto map <CMAP-name> 10 ipsec-isakmp
set peer 192.168.57.243
set transform-set <TS-name>
match address <list-name>
Применить Crypto Map к интерфейсу FastEthernet0/0:
interface FastEthernet0/0
ip address 192.168.57.150 255.255.255.0
duplex full
crypto map <CMAP-name>
Настройка IPsec на UserGate.
В разделе
Сеть ➜ Интерфейсы
добавить VPN интерфейс tunnel с произвольным номером, и назначить на него IP-адрес, например, 11.11.2.1/24. В данном случае интерфейс tunnel будет являться loopback-интерфейсом со стороны UserGate.
Произвести настройки для VPN-подключения Site-to-Site.
Перейдите в раздел
Сеть ➜ Интерфейсы
и активируйте интерфейс
tunnel2
. Данный интерфейс находится в зоне
VPN for Site-to-Site
и имеет IP-адрес 172.30.255.1/24.
Далее необходимо произвести настройку профиля безопасности в разделе
VPN ➜ Профили безопасности VPN
. Можно создать новый профиль безопасности или использовать созданный по умолчанию (
Client VPN profile
Во вкладке
Общие
укажите:
Название
профиля безопасности VPN.
Описание
(опционально).
IKE версия
: IKEv1.
Режим IKE
: Основной.
Аутентификация с пиром
: Общий ключ.
Общий ключ
: общий ключ, указанный при настройке оборудования Cisco - <psk>.
Во вкладке
Фаза 1
Diffie-Hellman группы
: Группа 2 Prime 1024 бит.
Алгоритмы авторизации и шифрования
: SHA1 – AES128.
Во вкладке
Фаза 2
Алгоритмы авторизации и шифрования
: SHA1 – AES128.
Перейдите в раздел
VPN ➜ Клиентские правила
. Для подключения можно использовать правило, созданное по умолчанию (
Client VPN rule
), или создать новое. Укажите:
Включено
— поставьте флажок.
Название
правила.
Описание
(опционально).
Профиль безопасности
, настроенный ранее.
Интерфейс
: tunnel2.
Адрес сервера
: 192.168.57.150.
Протокол VPN
: IPsec-туннель.
Разрешённые подсети со стороны UserGate
: 11.11.2.0/24.
Разрешённые подсети со стороны Cisco
: 11.11.3.0/24.
Настройка IPsec-туннеля между UserGate и Cisco завершена, далее настройка GRE.
Настройка GRE-туннеля на Cisco.
Создать туннельный интерфейс и назначить ему адрес из сети 172.30.222.0/24; в качестве адреса источника укажите адрес интерфейса Loopback0 Cisco, в качестве адреса назначения — secondary адрес интерфейса UserGate
port1
interface Tunnel0
ip address 172.30.222.2 255.255.255.0
tunnel source 11.11.3.1
tunnel destination 11.11.2.1
Добавить статический маршрут в сеть 10.10.2.0/24 со шлюзом 172.30.222.1:
ip route 10.10.2.0 255.255.255.0 172.30.222.1
Настройка GRE-туннеля на UserGate.
Перейдите в раздел
Сеть ➜ Интерфейсы
нажмите
Добавить
и выберите
Добавить туннель
Во вкладке
Общие
укажите:
Порядковый номер туннельного интерфейса.
Описание
(опционально).
Зону
, которой будет относиться интерфейс: VPN for Site-to-Site.
Перейдите во вкладку
Сеть
и задайте следующие параметры (в качестве локального и удалённого IP-адресов используются IP-адреса VPN-интерфейсов):
MTU
Локальный IP
: 11.11.2.1 – IP-адрес loopback-интерфейса со стороны UserGate.
Удалённый IP
: 11.11.3.1 – IP-адрес loopback-интерфейса со стороны Cisco.
Режим
: GRE.
IP-адрес интерфейса и маску
: 172.30.222.1/24.
Перейдите в раздел
Сеть ➜ Виртуальные маршрутизаторы
и настройте статический маршрут в сеть с IP-адресом 10.10.3.0/24 и шлюзом 172.30.222.2.
Создайте правило межсетевого экрана, разрешающее трафик из зоны
VPN for Site-to-Site
в зону
Trusted
и обратно.
ПРОВЕРКА.
В случае успешного подключения в разделе
VPN ➜ Клиентские правила
отобразится индикатор зелёного цвета.
Во вкладке
Диагностика и мониторинг
в разделе
Мониторинг ➜ Ping
возможна проверка сетевой доступности узлов.
Проверка IPsec-туннеля на UserGate:
PING 11.11.3.1 (11.11.3.1) from 11.11.2.1 : 56(84) bytes of data.
64 bytes from 11.11.3.1: icmp_seq=1 ttl=255 time=9.59 ms
64 bytes from 11.11.3.1: icmp_seq=2 ttl=255 time=4.19 ms
64 bytes from 11.11.3.1: icmp_seq=3 ttl=255 time=8.90 ms
64 bytes from 11.11.3.1: icmp_seq=4 ttl=255 time=2.68 ms
64 bytes from 11.11.3.1: icmp_seq=5 ttl=255 time=7.62 ms
64 bytes from 11.11.3.1: icmp_seq=6 ttl=255 time=2.14 ms
--- 11.11.3.1 ping statistics ---
6 packets transmitted, 6 received, 0% packet loss, time 5006ms
rtt min/avg/max/mdev = 2.140/5.857/9.596/2.974 ms
Проверка IPSec-туннеля на Cisco:
R1#show crypto session
Crypto session current status
Interface: FastEthernet0/0
Session status: UP-ACTIVE
Peer: 192.168.57.243 port 500
IKEv1 SA: local 192.168.57.150/500 remote 192.168.57.243/500 Active
IPSEC FLOW: permit ip 11.11.3.0/255.255.255.0 11.11.2.0/255.255.255.0
Active SAs: 2, origin: crypto map
R1#ping 11.11.2.1 source 11.11.3.1
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 11.11.2.1, timeout is 2 seconds:
Packet sent with a source address of 11.11.3.1
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 8/14/24 ms
Проверка сетевой доступности туннельного интерфейса на UserGate:
PING 172.30.222.2 (172.30.222.2) from 172.30.222.1 : 56(84) bytes of data.
64 bytes from 172.30.222.2: icmp_seq=1 ttl=255 time=10.6 ms
64 bytes from 172.30.222.2: icmp_seq=2 ttl=255 time=5.04 ms
64 bytes from 172.30.222.2: icmp_seq=3 ttl=255 time=8.96 ms
64 bytes from 172.30.222.2: icmp_seq=4 ttl=255 time=2.65 ms
64 bytes from 172.30.222.2: icmp_seq=5 ttl=255 time=7.08 ms
64 bytes from 172.30.222.2: icmp_seq=6 ttl=255 time=11.2 ms
--- 172.30.222.2 ping statistics ---
6 packets transmitted, 6 received, 0% packet loss, time 5008ms
rtt min/avg/max/mdev = 2.652/7.611/11.232/3.055 ms
Проверка доступности локальных шлюзов на UserGate:
PING 10.10.3.1 (10.10.3.1) from 10.10.2.1 : 56(84) bytes of data.
64 bytes from 10.10.3.1: icmp_seq=1 ttl=255 time=16.5 ms
64 bytes from 10.10.3.1: icmp_seq=2 ttl=255 time=10.6 ms
64 bytes from 10.10.3.1: icmp_seq=3 ttl=255 time=5.23 ms
64 bytes from 10.10.3.1: icmp_seq=4 ttl=255 time=9.93 ms
64 bytes from 10.10.3.1: icmp_seq=5 ttl=255 time=3.65 ms
64 bytes from 10.10.3.1: icmp_seq=6 ttl=255 time=7.37 ms
--- 10.10.3.1 ping statistics ---
6 packets transmitted, 6 received, 0% packet loss, time 5008ms
rtt min/avg/max/mdev = 3.656/8.893/16.546/4.197 ms
Проверка доступности конечных узлов:
C:Usersadmin>ping 10.10.3.3 -S 10.10.2.2
Обмен пакетами с 10.10.3.3 по с 10.10.2.2 с 32 байтами данных:
Ответ от 10.10.3.3: число байт=32 время=17мс TTL=62
Ответ от 10.10.3.3: число байт=32 время=20мс TTL=62
Ответ от 10.10.3.3: число байт=32 время=21мс TTL=62
Статистика Ping для 10.10.3.3:
Пакетов: отправлено = 4, получено = 4, потеряно = 0
(0% потерь)
Приблизительное время приема-передачи в мс:
Минимальное = 17мсек, Максимальное = 21 мсек, Среднее = 19 мсек
v6.x
Также опубликовано в
Документация -> Общие сведения -> Взаимодействие со сторонними решениями
Использование двухфакторной аутентификации через Контур.ID в...
Настройка VPN туннеля между UserGate NGFW и CheckPoint

## Источник

https://docs.usergate.com/nastrojka-gre-over-ipsec-mezhdu-usergate-i-cisco_47.html
