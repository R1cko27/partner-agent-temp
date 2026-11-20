---
заголовок: Свойства
url: https://docs.usergate.com/svojstva_2700.html
получено: 2026-11-20 16:25 +0700
продукт: SWG
версия: 7.5.x
раздел: Свойства
id_статьи: 2700
обновлено: 17 Feb, 2026
ревизия: 3
---

# Свойства

Содержание:
Свойства (
properties
) — это некие атрибуты правила, например,
name
или
enabled
. Они используются для предоставления дополнительной информации в процессе обработки правил. Синтаксис свойств точно такой же, как у действий.
Синтаксис
property = prop_name | prop_name '(' list_params ')'
prop_name ::= name | desc | id | rule_log | enabled | scenario
list_params ::= value ',' list_params
name и desc
Атрибуты
имя
описание
для правила.
Синтаксис
Name ::= name '(' string|word ')'
Description ::= desc '(' string ')'
Пример
DENY hour = 9..18 category = News name("Запретить News")  desc("Запретить категорию News в рабочее время")
enabled
Атрибут, который включает или выключает работу правила.
Синтаксис
Enable ::= enabled '(' boolean ')'
boolean ::= yes | no | true | false       % (
по умолчанию
false)
rule_log
Устанавливает атрибут журналирования правила. Значение
session
действительно только для правил межсетевого экрана, защиты от dos-атак и пропускной способности.
Синтаксис
Logging ::= rule_log '(' boolean | session ')'
LoggingFwRule ::= rule_log '(' boolean , interval,  burst')'
boolean ::= yes | no | true | false         % (по умолчанию no)
interval ::= "integer/[s,m,h,d]"
burst ::= integer
interval
— среднее число пакетов, попадающих под условие
limit
в единицу времени (
1/s, 1/m, 1/h, 1/d)
default = 3/h
burst
— максимальное число пакетов, попадающих в под условие
limit
за один раз (
default = 5
profile
Устанавливает профиль правила.
Синтаксис
Profile ::= profile '(' string | word | list ')'
certificate
Сертификат, используемый для поддержки HTTPS-соединения. Действительно только для правил reverse-прокси.
Синтаксис
CertAuthEnabled ::= cert_auth_enabled '(' boolean ')'
Certificate ::= certificate '(' certificate_name ')'
certificate_name ::= string | word
gateway
Шлюз. Имя одного из существующих шлюзов. Действительно только для правил NAT и маршрутизации, и для условий сценария «Проверка состояния».
Синтаксис
Gateway ::= gateway '(' string | word ')'
Свойства правил межсетевого экрана
reject_with
Устанавливает способ, с помощью которого будет блокироваться трафик. Действительно только для правил межсетевого экрана.
Синтаксис
Reject ::= reject_with '(' "tcp-reset-both" | "tcp-rst" | "host-unreach" ')'
fragmented
Проверка на фрагментацию пакетов. Действительно только для правил межсетевого экрана.
Синтаксис
Fragmented ::= fragmented '(' boolean ')'
boolean ::= yes | no | true | false
yes
— проверяются только фрагментированные пакеты;
— проверяются только нефрагментированные пакеты;
—, если свойство
fragmented
не указано, то будут проверяться все пакеты.
Свойства правил инспектирования SSL
block_invalid_cert
Блокирование сайтов с некорректными сертификатами. Действительно только для правил инспектирования SSL.
Синтаксис
InvalidCertificate ::= block_invalid_cert '(' boolean ')'
boolean ::= yes | no | true | false
check_revoc_cert
Проверка по списку отозванных сертификатов. Действительно только для правил инспектирования SSL.
Синтаксис
ChekRevocation ::= check_revoc_cert '(' boolean ')'
boolean ::= yes | no | true | false
block_expired_cert
Блокировка сертификатов с истекшим сроком действия. Действительно только для правил инспектирования SSL.
Синтаксис
ExpiredCertificate ::= block_expired_cert '(' boolean ')'
boolean ::= yes | no | true | false
block_self_signed_cert
Блокировка самоподписанных сертификатов. Действительно только для правил инспектирования SSL.
Синтаксис
SelfSignedCertificate ::= block_self_signed_cert '(' boolean ')'
boolean ::= yes | no | true | false
ssl_profile
Профиль SSL. Действительно только для правил инспектирования SSL, reverse-прокси, веб-портала.
Синтаксис
SslProfile ::= ssl_profile '(' string | word ')'
ssl_forward_profile
Профиль пересылки SSL. Действительно только для правил инспектирования SSL.
Синтаксис
SslForwardProfile ::= ssl_forward_profile '(' string | word ')'
profile_id ::= integer
Свойства правил пропускной способности
bandwidth_pool
Полоса пропускания. Действительно только для правил пропускной способности.
Синтаксис
BandwidthPool ::= bandwidth_pool '(' bandwidth ')'
bandwidth ::= "100 Kbps" | "512 kbps" | "1 Mbps" | "2 Mbps" | "5 Mbps" | "10 Mbps" | "20 Mbps" | "50 Mbps" | "100 Mbps"
Пример
scenario = "Сценарий обнаружения torrent" bandwidth_pool("1 Mbps") enable(true) name("Пропускная способность torrent")
Свойства правил NAT и маршрутизации
target_ip
Адрес назначения DNAT, если задано действие
dnat
или
port_mapping
Новая IP-сеть/маска, если задано действие
netmap
Действительно только для правил NAT и маршрутизации.
Синтаксис
TargetIp ::= target_ip '(' ipv4 | ipv4_with_mask ')'
Пример
PASS target_ip("192.168.1.20") dnat
target_snat
Включение SNAT. При включении данной опции UserGate будет изменять адрес источника в пакетах из внешней сети на свой IP-адрес.
Действительно только для правил NAT и маршрутизации.
Синтаксис
TargetSnat ::= target_snat '(' boolean ')'
boolean ::= yes | no | true | false
snat_target_ip
SNAT IP (внешний адрес). Явно указывает IP-адрес, на который будет заменен адрес источника при подмене адресов пакетов.
Действительно только для правил NAT и маршрутизации.
Синтаксис
SnatTargetIp ::= snat_target_ip '(' ip_address ')'
port_map
Порт-форвардинг. Переопределение портов публикуемых сервисов. Действительно только для правил NAT и маршрутизации.
Синтаксис
PortMap ::= port_map '(' protocol, port_from, port_to ')'
protocol ::= tcp | udp | smtp | smpts
port_from ::= integer
port_to ::= integer
port_from
— номер TCP/UDP-порта, на который пользователи шлют запросы;
port_to
— номер TCP/UDP-порта, на который будут пересылаться запросы пользователей на внутренний публикуемый сервер.
direction
Направление подмены сетей. Действительно только для правил NAT и маршрутизации.
Синтаксис
Direction ::= direction '(' input | ouput ')'
input
— входящий, подменяется IP-сеть назначения. Будут изменены IP-адреса назначения в трафике;
ouput
— исходящий, подменяется IP-сеть источника. Будут изменены IP-адреса источника в трафике.
Свойства правил DNS-прокси
dns_server
Список IP-адресов DNS-серверов. Действительно только для правил DNS-прокси.
Синтаксис
DnsServer ::= dns_server '(' ip_address | ip_address_list ')'
Свойства правил reverse-прокси
cert_auth_enabled
Аутентификация по сертификату. Действительно только для правил reverse-прокси.
Синтаксис
CertAuthEnabled ::= cert_auth_enabled '(' boolean ')'
boolean ::= yes | no | true | false
is_https
Включение поддержки HTTPS. Действительно только для правил reverse-прокси.
Синтаксис
IsHttps ::= is_https '(' boolean ')'
boolean ::= yes | no | true | false
rewrite_path
Подмена путей. Действительно только для правил reverse-прокси.
Синтаксис
RewritePath ::= rewrite_path '(' path_from, path_to ')'
path_from
— изменить с (домен и/или путь URL, которые требуется изменить);
path_to
— изменить на (домен и/или путь URL, на которые требуется заменить старые).
Свойства правил веб-портала
icon
Иконка, которая будет отображаться на веб-портале для данной закладки. Действительно только для правил веб-портала.
Синтаксис
Icon ::= icon '(' string | word ')'
additional_url
Вспомогательные URL, необходимые для работы основного URL, но которые нет необходимости публиковать для пользователей.
Действительно только для правил веб-портала.
Синтаксис
AdditionalUrl ::= additional_url '(' string | word | list ')'
rdp_check_session_alive
Проверка авторизации для RDP-сессий. Действительно только для правил веб-портала.
Синтаксис
RdpCheckSessionAlive ::= rdp_check_session_alive '(' boolean ')'
boolean ::= yes | no | true | false
transparent_auth
Включение прозрачной аутентификации пользователя. Действительно только для правил веб-портала.
Синтаксис
TansparentAuth ::= transparent_auth '(' boolean ')'
boolean ::= yes | no | true | false
Свойства правил веб-безопасности (Safe browsing)
enable_adblock
Блокировка рекламы.
Синтаксис
EnableAdblock ::= enable_adblock '(' boolean ')'
boolean ::= yes | no | true | false
url_list_exclusions
URL-список сайтов исключений, для которых блокировать рекламу не требуется.
Синтаксис
UrlListExclusions ::= url_list_exclusions '(' list_libs ')'
list_libs :: = lib_name ','' list_libs
lib_name ::= word | string
enable_injector
Позволяет вставить произвольный код во все веб-страницы.
Синтаксис
EnableInjector ::= enable_injector '(' boolean ')'
boolean ::= yes | no | true | false
custom_injector
Код инжектора.
Синтаксис
СustomInjector ::= custom_injector '(' string ')'
safe_search
Функция безопасного поиска.
Синтаксис
SafeSearch ::= safe_search '(' boolean ')'
boolean ::= yes | no | true | false
search_history_logging
Запись в журнал поисковых запросов пользователей.
Синтаксис
SearchHistoryLogging ::= search_history_logging '(' boolean ')'
boolean ::= yes | no | true | false
social_sites_block
Блокировка приложения в популярных социальных сетях.
Синтаксис
SocialSitesBlock ::= social_sites_block '(' boolean ')'
boolean ::= yes | no | true | false
Свойства правил сценариев
trigger
Тип срабатывания сценария. Действительно только для правил сценариев.
Синтаксис
Trigger ::= trigger '(' trigger_type ')'
trigger_type ::= all_users | one_user
duration
Продолжительность. Время в минутах, в течение которого сценарий будет активным после его активации. Действительно только для правил сценариев.
Синтаксис
Duration ::= duration '(' integer ')'
operation_mode
Сценарий срабатывает при совпадении одного или всех условий.
Синтаксис
OperationMode ::= operation_mode '(' mode ')'
mode ::= all | any
Свойства условий сценария
scond_type
Тип условий сценария. Действительно только для условий сценария.
Синтаксис
SCondType ::= scond_type '(' type ')'
count_interval
Количество срабатываний. Действительно только для условий сценария «Категория URL» (
url_category
), «Приложение» (
app
), «Тип контента» (
mime_type
) и «Проверка состояния» (
health_check
Синтаксис
CountInterval ::= count_interval '(' integer ')'
max_event_count
Интервал времени в минутах, за который было обнаружено
count_interval
срабатываний. Действительно только для условий сценария «Категория URL» (
url_category
), «Приложение» (
app
), «Тип контента» (
mime_type
) и «Проверка состояния» (
health_check
Синтаксис
MaxEventCount ::= max_event_count '(' integer ')'
packet_size
Размер пакета. Размер пакета в трафике пользователя превысил указанное значение. Действительно только для условий сценария «Размер пакета» (
net_packet_size
Синтаксис
PacketSize ::= packet_size '(' size ')'
size ::= integer | integer KB | integer MB | integer GB
64 — размер в байтах;
2MB — размер в мегабайтах.
traffic_limit
Объем трафика. Действительно только для условий сценария «Ограничение трафика» (
traffic
Синтаксис
TrafficLimit ::= traffic_limit '(' size ')'
size ::= integer | integer KB | integer MB | integer GB
period
Период времени. Действительно только для условий сценария «Ограничение трафика» (
traffic
Синтаксис
Period ::= period '(' time_period ')'
time_period ::= minute | hour | day | week | month
health_check_method
Метод проверки. Действительно только для условий сценария «Проверка состояния» (
health_check
Синтаксис
CheckMethod ::= health_check_method '(' method ')'
method ::= ping | dns | get
health_result
Результат. Действительно только для условий сценария «Проверка состояния» (
health_check
Синтаксис
esult ::= health_result '(' result ')'
result ::= positive | negative
health_request_timeout
Тайм-аут подключения (сек). Действительно только для условий сценария «Проверка состояния» (
health_check
Синтаксис
RequestTimeout ::= health_request_timeout '(' integer ')'
health_answer_timeout
Тайм-аут ответа (сек). Действительно только для условий сценария «Проверка состояния» (
health_check
), «Метод проверки HTTP GET» (
get
Синтаксис
ut ::= health_answer_timeout '(' integer ')'
health_type_request
Тип DNS-запроса. Действительно только для условий сценария «Проверка состояния» (
health_check
), «Метод проверки DNS» (
dns
Синтаксис
TypeRequest ::= health_type_request '(' type_name ')'
type_name ::= word | string
Свойства правил балансировки нагрузки
scheduler
Метод балансировки. Действительно только для правил балансировки нагрузки TCP/UDP.
Синтаксис
Scheduler ::= scheduler '(' balancing_type ')'
balancing_type ::= wrr | rr | lc | wlc
wrr
— Weighted round robin;
— Round robin;
— Least connections;
wlc
— Weighted least connections.
real_server
Реальные серверы. Действительно только для правил балансировки нагрузки TCP/UDP.
Синтаксис
RealServer ::= real_server '(' mode, ipv4[:port], weight ')'
mode ::= gate | masq | masq_snat
port ::= integer
weight ::= integer
gate — шлюз;
masq
— маскарадинг;
masq_snat
— маскарадинг с подменой IP-адреса источника (SNAT).
Пример
OK \
url.address = 172.168.13.100 \
url.port = 10000 \
service = tcp \
scheduler(wlc) \
real_server(masq_snat, 172.168.13.11:10000, 50) \
ipvs_fallback(gate, 172.168.13.12)
monitor_kind(ping) \
monitor_interval(60) \
monitor_timeout(60) \
monitor_failurecount(10) \
enabled(true) \
name("TCP/UPD load balancing")
ipvs_fallback
Аварийный режим сервера. Действительно только для правил балансировки нагрузки TCP/UDP.
Синтаксис
IpvsFallback ::= ipvs_fallback '(' mode, ipv4[:port] ')'
mode ::= gate | masq | masq_snat
port ::= integer
monitor_kind
Режим. Действительно только для правил балансировки нагрузки TCP/UDP.
Синтаксис
MonitorKind ::= monitor_kind '(' kind ')'
kind ::= ping | connect | negotiate
monitor_service
Сервис. Действительно только для правил балансировки нагрузки TCP/UDP.
Синтаксис
MonitorService ::= monitor_service '(' service ')'
service ::= http | dns
monitor_request
Запрос. Действительно только для правил балансировки нагрузки TCP/UDP.
Синтаксис
MonitorRequest ::= monitor_request '(' string ')'
monitor_response
Ожидаемый ответ. Действительно только для правил балансировки нагрузки TCP/UDP.
Синтаксис
MonitorResponse ::= monitor_response '(' string ')'
monitor_interval
Интервал проверки. Действительно только для правил балансировки нагрузки TCP/UDP.
Синтаксис
MonitorInterval ::= monitor_interval '(' integer ')'
monitor_timeout
Время ожидания. Действительно только для правил балансировки нагрузки TCP/UDP.
Синтаксис
MonitorTimeout ::= monitor_timeout '(' integer ')'
monitor_failurecount
Число неудачных попыток. Действительно только для правил балансировки нагрузки TCP/UDP.
Синтаксис
MonitorFailurecount ::= monitor_failurecount '(' integer ')'
v7.x
Встроенные библиотеки

## Источник

https://docs.usergate.com/svojstva_2700.html
