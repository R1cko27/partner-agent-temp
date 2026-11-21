---
заголовок: Настройка клиентских правил VPN
url: https://docs.usergate.com/draft-750-nastrojka-klientskih-pravil-vpn_2383.html
источник: портал документации
получено: 2026-11-20 16:17 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка клиентских правил VPN
id_статьи: 2383
обновлено: 25 May, 2026
ревизия: 21
---

# Настройка клиентских правил VPN

Содержание:
Technology: VPN
Клиентские правила используются VPN-сервером, который инициирует подключение в сценарии site-to-site VPN. Подробнее о создании site-to-site VPN — в разделе «
Настройка VPN для защищенного соединения офисов
В интерфейсе командной строки клиентские правила VPN настраиваются на уровне
vpn-client
Настройка параметров подключения клиента
При настройке VPN-подключения указываются используемые протоколы для установления соединения, выбираются методы аутентификации, а также определяются параметры обеих фаз формирования защищенного канала.
Команда для создания подключения клиента:
Admin@nodename# create vpn-client connections [ikev2|ipsec|l2tp-ipsec] <parameters>
Дополнительные параметры команды.
Параметр
Описание
name
Название подключения
description
Описание подключения
ike-mode
Режим работы IKEv1:
main
aggressive
psk
Значение общего ключа (pre-shared key)
initiator-type
Параметр идентификации узла-инициатора:
ipv4
fqdn
initiator-value
Значение параметра идентификации узла-инициатора:
<ip>
— например,
192.168.0.1
<domain>
— например,
example.com
responder-type
Параметр идентификации узла-ответчика:
ipv4
fqdn
responder-value
Значение параметра идентификации узла-ответчика:
<ip>
— например,
192.168.0.1
<domain>
— например,
example.com
authentication-login
Логин для аутентификации узла-инициатора на узле-ответчике в сценарии c протоколом IPsec/L2TP
authentication-password
Пароль для аутентификации узла-инициатора на узле-ответчике в сценарии c протоколом IPsec/L2TP
check-ip
Параметр
check_ip
определяет, будет ли узел-инициатор соединения запрашивать проверку IP-адреса у VPN-сервера. VPN-сервер может принять предложенный IP-адрес или назначить другой.
Если параметр разрешен, узел-инициатор соединения добавляет параметр Payload Configuration в сообщение
IKE_AUTH
и передает в поле
INTERNAL_IP4_ADDRESS
значение, зависящее от типа туннельного интерфейса:
Для туннельного интерфейса с динамическим назначением IP-адреса в поле
INTERNAL_IP4_ADDRESS
передается значение
0.0.0.0/0
, что является запросом на динамическое выделение IP-адреса. VPN-сервер, получив значение
0.0.0.0/0
, выделяет IP-адрес из собственного пула, заданного в параметрах соединения на сервере.
Для туннельного интерфейса со статическим IP-адресом в поле
INTERNAL_IP4_ADDRESS
передается его IP-адрес. VPN-сервер использует это значение для проверки соответствия политике подключения.
Если параметр не разрешен, механизм согласования сетевых параметров для проверки IP-адреса туннельного интерфейса на VPN-сервере не применяется. Значение IP-адреса определяется настройками туннельного интерфейса на узле-инициаторе.
auth-mode
Режим аутентификации:
pki
— режим аутентификации с помощью сертификата;
psk
— режим аутентификации с помощью общего ключа
certificate
Сертификат узла-инициатора (клиента)
phase1-key-lifetime
Время жизни ключа. По истечении этого времени происходит повторная аутентификация и согласование настроек фазы 1:
num+s|m|h
, например
dpd-state
Режимы работы механизма Dead peer detection (DPD):
off
— механизм отключен. DPD-запросы не отсылаются.
always
— DPD-запросы всегда отсылаются через указанный интервал времени. Если ответ не пришел, последовательно с интервалом 5 сек. отсылаются дополнительные запросы в количестве, указанном в параметре
dpd-max-failures
. Если ответ пришел, работа механизма возвращается к изначальному интервалу отправки DPD запросов. Если ответ не пришел, соединение завершается.
idle
— DPD-запросы не отсылаются, пока есть ESP-трафик через созданный канал. Если в течение двойного указанного интервала времени нет ни одного пакета, происходит отсылка DPD-запроса. При ответе новый DPD-запрос будет отправлен снова через двойной интервал указанного времени. При отсутствии ответа последовательно с интервалом 5 сек. отсылаются дополнительные запросы в количестве, указанном указанном в параметре
dpd-max-failures
. Если нет ни одного ответа, соединение завершается
dpd-interval
Интервал отсылки дополнительных запросов DPD. Указывается в секундах
dpd-max-failures
Количество повторов отправки DPD-запросов
dh-groups
Группы Диффи-Хеллмана, которые будут использоваться для обмена ключами
phase1-security
Алгоритмы аутентификации и шифрования для фазы 1
phase2-key-lifetime
Время жизни ключа. По истечении этого времени происходит повторная аутентификация и согласование настроек фазы 2:
num+s|m|h
, например
key-lifesize-enabled
Включение параметра указания максимального размера данных, шифруемых одним ключом:
off
key-lifesize
Максимальный размер данных, шифруемых одним ключом:
num+KB|MB|GB
, например
1KB
2MB
3GB
dynamic-routing
Разрешить работу протоколов динамической маршрутизации через туннель (для протокола IKEv2)
local-networks
remote-networks
Адреса локальных и удаленных подсетей. Используются для определения селекторов трафика при организации защищенного канала передачи данных IPsec. В ходе фазы 2 стороны туннеля обмениваются своими предложениями по селекторам трафика. Для успешного установления туннеля сети в селекторах трафика от обеих сторон соединения должны совпасть или пересечься. Если нет совпадения хотя бы по одной из сторон, фаза 2 завершится ошибкой соединения.
Адреса указываются в формате
[ <ip/mask> <ip/mask> ... ]
phase2-security
Алгоритмы аутентификации и шифрования канала передачи данных (для фазы 2)
Пример настройки клиентского подключения с протоколом L2TP/IPsec:
Admin@nodename# create vpn-client connections l2tp-ipsec name Connection1 description "Test connection" ike-mode main authentication-login vpn_client1 authentication-password password111 psk 123321 initiator-type ipv4 initiator-value 172.16.1.10 responder-type ipv4 responder-value 172.16.1.1 phase1-key-lifetime 1h dpd-state off dh-groups [ "Group 2 Prime 1024 bit" "Group 14 Prime 2048 bit" ] phase1-security [ SHA1/AES256 SHA256/AES256 ] phase2-key-lifetime 1h key-lifesize 100MB key-lifesize-enabled on phase2-security [ SHA1/AES256 SHA256/AES256 ]
Repeat preshared key:
Admin@nodename# show vpn-client connections l2tp-ipsec Connection1
name                    : Connection1
description             : Test connection
ike-mode                : main
authentication-login    : vpn_client1
phase1-key-lifetime     : 1 h
phase2-key-lifetime     : 1 h
key-lifesize-enabled    : on
key-lifesize            : 100.0 MB
initiator-type          : ipv4
initiator-value         : 172.16.1.10
responder-type          : ipv4
responder-value         : 172.16.1.1
dpd-state               : off
dpd-interval            : 60
dpd-max-failures        : 5
dh-groups               : Group 2 Prime 1024 bit; Group 14 Prime 2048 bit
phase1-security         :
authentication    : SHA1
encryption        : AES256
authentication    : SHA256
encryption        : AES256
phase2-security         :
authentication    : SHA1
encryption        : AES256
authentication    : SHA256
encryption        : AES256
Admin@nodename#
Для изменения параметров клиентского подключения используется команда:
Admin@nodename# set vpn-client connections [ikev2|ipsec|l2tp-ipsec] <connection-name>
Для просмотра параметров клиентских подключений используется команда:
Admin@nodename# show vpn-client connections [ikev2|ipsec|l2tp-ipsec] <connection-name>
Для удаления клиентского подключения используется команда:
Admin@nodename# delete vpn-client connections [ikev2|ipsec|l2tp-ipsec] <connection-name>
Настройка клиентских правил
Клиентское правило в сценарии site-to-site VPN используется для инициирования подключения к VPN-серверу (узлу-ответчику).
Клиентские правила VPN создаются с помощью синтаксиса языка
UPL
Команда для создания клиентских правил:
Admin@nodename# create vpn-client rules [position] upl-rule
Дополнительные параметры команды.
Параметр
Описание
Действие для создания правила с помощью UPL
enabled
Включение или отключение правила:
enabled(yes)
или
enabled(true)
enabled(no)
или
enabled(false)
Если при создании правила не указывать, то правило будет включено после создания
name
Название правила.
Например:
name("VPN rule example")
desc
Описание правила.
Например:
desc("VPN rule example configured in CLI")
connection
Название ранее созданного клиентского подключения.
Например:
connection(Connection1)
interface
VPN-интерфейс, который будет использоваться для подключения.
Например, чтобы указать интерфейс tunnel3:
interface(tunnel3)
server_address
Адрес VPN-сервера (IP-адрес или доменное имя).
Например:
server_address("172.16.1.1")
Пример клиентского правила с протоколом L2TP/IPsec:
Admin@nodename# create vpn-client rules 5 upl-rule \
...OK
...server_address(172.16.1.1)
...connection(Connection1)
...interface(tunnel3)
...enabled(false)
...name(Rule1)
Для изменения параметров правила используется команда:
Admin@nodename# set vpn-client rules [position] upl-rule
Для просмотра созданных правил используется команда:
Admin@nodename# show vpn-client rules <position>
Для удаления правил используется команда:
Admin@nodename# delete vpn-client rules [position]
Просмотр журналов диагностики VPN-сервера, работающего в режиме инициатора соединения
В режиме диагностики интерфейса командной строки вы можете просматривать события журналов диагностики VPN-сервера (когда UserGate NGFW выступает в роли узла-инициатора соединения в сценарии site-to-site VPN), в статическом и динамическом режиме.
Для вывода всего журнала диагностики VPN-сервера в консоль используйте команду:
Admin@nodename> show logs log vpn-client static
Для вывода событий журнала диагностики VPN-сервера в консоль в реальном времени используйте команду:
Admin@nodename> show logs log vpn-client dynamic
Для отключения вывода событий журнала используйте комбинацию клавиш
Ctrl + C
В командах раздела может использоваться фильтрация вывода. Пример команды с фильтрацией вывода:
Admin@nodename> show logs log vpn-client static | grep l2tp
Подробнее о функции фильтрации вывода — в разделе «
Общие положения
Настройка серверных правил VPN
Управление VPN-сессиями в CLI

## Источник

https://docs.usergate.com/draft-750-nastrojka-klientskih-pravil-vpn_2383.html
