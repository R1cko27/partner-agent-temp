---
заголовок: Типы правил
url: https://docs.usergate.com/tipy-pravil_1548.html
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 7.x
раздел: Типы правил
id_статьи: 1548
обновлено: 25 Apr, 2025
ревизия: 36
---

# Типы правил

Содержание:
Правила контентной фильтрации
Префиксы
Имя
Описание
PASS
Разрешение посещения.
DENY
Блокировка веб-страницы.
WARNING
Предупреждение пользователя о том, что страница нежелательна для посещения.
Условия
src.zone
src.geoip
src.ip
dst.zone
dst.geoip
dst.ip
category
morphology
scenario
time
url
user
request.header.Referer
— Список URL, в котором указаны рефереры для текущей страницы.
request.header.User-Agent
— Useragent пользовательских браузеров.
response.header.Content-Type
— Списки типов контента.
http.method
— Метод, используемый в HTTP-запросах.
Свойства
name
desc
enabled
rule_log
virus_heuristic
Пример
[content "Content Rules"]
% ----------------- 1 --- "Content Rules" --------------
PASS \
url = lib.url("Education institutions") \
src.zone = Trusted \
desc("Content filtering rule which allows access to the list of URLs. This is an example rule which can be changed or deleted if necessary.") \
rule_log(yes) \
enabled(true) \
name("Example white list")
% ----------------- 2 --- "Content Rules" --------------
DENY("Blockpage (EN)") \
url = lib.url("Education institutions") \
dst.zone = Untrusted \
rule_log(yes) \
enabled(false) \
name("Example block RU RKN by URL list")
% ----------------- 3 --- "Content Rules" --------------
DENY \
url = lib.network("Private IPs") \
morphology = lib.morphology(Drugs) \
src.zone = Trusted \
time = lib.time(Weekdays) \
rule_log(yes) \
redirect(302, "https://bing.com") \
enabled(false) \
name("Example redirect to safesearch engines")
Правила межсетевого экрана
Префиксы
Имя
Описание
PASS
Разрешение трафика.
DENY
Блокировка трафика.
Условия
src.zone
src.geoip
src.ip
dst.zone
dst.geoip
dst.ip
service
scenario
time
url
user,
hip_profile
Свойства
name
desc
enabled
rule_log
reject_with
ips_profile
l7_profile
Пример
[firewall "Firewall rules"]
% ----------------- 1 -----------------
DENY \
scenario = "Example torrent detection scenario" \
dst.zone = Untrusted \
dst.ip = lib.network("Botnets IP list") \
rule_log(session) \
reject_with("host-unreach") \
enabled(true) \
name("Example block RU RKN by IP list")
% ----------------- 2 -----------------
PASS \
scenario = "Example torrent detection scenario" \
src.zone = Trusted \
dst.zone = Untrusted \
hip_profile = "HIP profile" \
ips_profile("Default IDPS profile") \
l7_profile("Pass all applications") \
rule_log(yes, "3/h", 5) \
enabled(true) \
name("Allow trusted to untrusted")
Правила NAT и маршрутизации
Префиксы
Имя
Описание
Всегда ОК.
Тип правила определяется действием (
Action
nat
— правило NAT;
dnat
— правило DNAT;
port_mapping
— правило порт-форвардинга;
netmap
— правило Network mapping;
route
— правило policy-based.
Условия
src.zone
src.geoip
src.ip
src.mac
dst.zone
dst.geoip
dst.ip
service
scenario
time
url
user
Свойства
name
desc
enabled
rule_log
direction
target_ip
target_snat
snat_target_ip
port_map
gateway
Пример
[nat_routing "NAT and Routing Rules"]
% ----------------- 1 -----------------
OK \
src.zone = Trusted \
service = (HTTP, HTTPS) \
snat_target_ip("192.168.13.210") \
rule_log(session) \
enabled(true) \
name("NAT Rule")\
nat
% ----------------- 2 -----------------
OK \
src.zone = Management \
dst.ip = (lib.network("Private IPs"), lib.url("Microsoft Windows Internet checker")) \
target_ip("171.168.1.1") \
target_snat(yes) \
snat_target_ip("192.168.1.1") \
enabled(true) \
name("DNAY Rule")\
dnat
% ----------------- 3 -----------------
OK \
target_ip("172.168.1.1") \
snat_target_ip("192.168.1.1") \
port_map(tcp, 2000, 2000) \
enabled(true) \
name("Port-forwarding Rule")\
port_mapping
% ----------------- 4 -----------------
OK \
user = example \
scenario = "Example torrent detection scenario" \
gateway(My) \
enabled(true) \
name("Policy-base Rule")\
route
% ----------------- 5 -----------------
OK \
dst.geoip = (RW, SO) \
target_ip("172.168.1.1") \
direction(input) \
enabled(true) \
name("Network mapping Rule")\
netmap
Правила Captive-портала
Префиксы
Имя
Описание
PASS
Не использовать аутентификацию.
Использовать Captive-профиль.
Условия
src.zone
src.geoip
src.ip
dst.zone
dst.geoip
dst.ip
time
url
category
Свойства
name
desc
enabled
rule_log
profile
Пример
[captive "Captive Rules"]
% ----------------- 1 -----------------
PASS \
category = lib.category(Threats) \
url = lib.url("Microsoft Windows Internet checker") \
time = lib.time(Weekends) \
rule_log(yes) \
enabled(true) \
name("Skip auth for Microsoft Internet checker")
% ----------------- 2 -----------------
OK \
src.zone = Trusted \
profile("Example Captive profile") \
enabled(true) \
name("Example Captive portal")
Правила инспектирования SSL
Префиксы
Имя
Описание
PASS
Не расшифровывать передаваемые данные.
Расшифровать передаваемые данные.
Пересылка определяется действием (
Action
forward
— в случае успешной расшифровки трафика SSL/TLS копия трафика будет переслана в соответствии с правилом и профилем инспектирования SSL (
ssl_forward_profile
Условия
src.zone
src.geoip
src.ip
dst.geoip
dst.ip
time
service
user
category
Свойства
name
desc
enabled
rule_log
ssl_profile
ssl_forward_profile
block_invalid_cert
check_revoc_cert
block_expired_cert
block_self_signed_cert
Пример
[ssl "Decrypt Rules"]
% ----------------- 1 -----------------
PASS \
category = (Finance, "Information Security") \
rule_log(yes) \
ssl_profile("Default SSL profile") \
enabled(false) \
name("Example DO NOT Decrypt rule for Finance and Security sites")
% ----------------- 2 -----------------
OK \
category = lib.category(Threats) \
rule_log(yes) \
block_invalid_cert(yes) \
check_revoc_cert(yes) \
block_expired_cert(yes) \
block_self_signed_cert(yes) \
ssl_profile("Default SSL profile") \
enabled(false) \
name("Example decrypt rule for parental control")
% ----------------- 3 -----------------
OK \
url = lib.url("Default SSL profile") \
rule_log(yes) \
ssl_profile("Default SSL profile") \
ssl_forward_profile("SSL forward profile") \
enabled(false) \
name("Example decrypt RU RKN")\
forward
Правила инспектирования SSH
Префиксы
Имя
Описание
PASS
Не расшифровывать передаваемые данные.
Расшифровать передаваемые данные.
Условия
src.zone
src.geoip
src.ip
dst.geoip
dst.ip
time
service
user
Свойства
name
desc
enabled
rule_log
block_ssh_shell
block_ssh_exec
block_sftp
ssh_command
Пример
[ssh "SSH inspection Rules"]
% ----------------- 1 -----------------
PASS \
service = "Any UDP" \
rule_log(yes) \
enabled(true) \
name("Bypass Rule")
% ----------------- 2 -----------------
OK \
service = IMAP \
block_ssh_shell(yes) \
block_ssh_exec(yes) \
block_sftp(yes) \
ssh_command("command") \
rule_log(yes) \
enabled(true) \
name("Decrypy Rule")
DNS-правила
Префиксы
Имя
Описание
Всегда OK.
Условия
url.domain
Свойства
name
desc
enabled
dns_server
Пример
[dns "DNS Rules"]
% ----------------- 1 -----------------
OK \
url.domain = "*.example.com" \
dns_server(1.2.3.4) \
enabled(true) \
name("Dns rule")
DoS-правила
Префиксы
Имя
Описание
PASS
Разрешение трафика.
DENY
Безусловная блокировка трафика.
WARNING
Применение профиля защиты от DoS-атак.
Условия
src.zone
src.geoip
src.ip
dst.zone
dst.geoip
dst.ip
time
service
user
scenario
Свойства
name
desc
enabled
rule_log
profile
Пример
[dos "DoS Rules"]
% ----------------- 1 -----------------
PASS \
scenario = "Example torrent detection scenario" \
user = example \
src.ip = lib.url("Microsoft Windows Internet checker") \
dst.geoip = RW \
service = FTP \
rule_log(session) \
enabled(true) \
name("DoS Allow Rule")
% ----------------- 2 -----------------
DENY \
desc(api_dos_rule) \
rule_log(yes, "3/h", 5) \
enabled(true) \
name("DoS Deny Rule")
% ----------------- 3 -----------------
WARNING \
user = "CN=VPN users,DC=LOCAL" \
time = lib.time("Working hours") \
profile("DoS Profile") \
enabled(false) \
name("DoS Protect Rule")
ICAP-правила
Префиксы
Имя
Описание
PASS
Пропуск. Не посылать данные на ICAP-сервер.
Пересылка данных на ICAP-сервер.
Действие (
Action
ignore
— игнорировать ответ от ICAP-сервера.
Условия
src.zone
src.geoip
src.ip
dst.zone
dst.geoip
dst.ip
url
category
user
service
http.method
response.header.Content-Type
Свойства
name
desc
enabled
rule_log
profile
Пример
[dos "DoS Rules"]
% ----------------- 1 -----------------
PASS \
scenario = "Example torrent detection scenario" \
user = example \
src.ip = lib.url("Microsoft Windows Internet checker") \
dst.geoip = RW \
service = FTP \
rule_log(session) \
enabled(true) \
name("DoS Allow Rule")
% ----------------- 2 -----------------
DENY \
desc(api_dos_rule) \
rule_log(yes, "3/h", 5) \
enabled(true) \
name("DoS Deny Rule")
% ----------------- 3 -----------------
WARNING \
user = "CN=VPN users,DC=LOCAL" \
time = lib.time("Working hours") \
profile("DoS Profile") \
enabled(false) \
name("DoS Protect Rule")
Правила защиты почтового трафика
Префиксы
Имя
Описание
PASS
Пропуск трафика без изменений.
DENY ("with error")
Блокировка письма, при этом сообщается об ошибке доставки письма на сервер.
DENY
Блокировка письма без уведомления о блокировке.
WARNING
Маркировка почтовых сообщений.
Условия
src.zone
src.geoip
src.ip
dst.zone
dst.geoip
dst.ip
user
service
envelope_from
envelope_to
Свойства
name
desc
enabled
rule_log
mark_hdr
mark
antispam_usergate
dnsbl
Пример
[mailsecurity "Mail Security Rules"]
% ----------------- 1 -----------------
PASS \
user = (example, "CN=VPN users,DC=LOCAL") \
envelope_from = "Email froup from" \
envelope_to = "Email froup to" \
service = SMTP \
rule_log(yes) \
mark_hdr(Subject) \
enabled(true) \
name("Mail Pass Rule")
% ----------------- 2 -----------------
DENY("with error") \
service = (SMTPS, SMTP) \
rule_log(yes) \
mark_hdr(Subject) \
antispam_usergate(yes) \
enabled(true) \
name("Mail Drop Rule")
% ----------------- 3 -----------------
DENY \
src.zone = Untrusted \
service = SMTP \
mark_hdr(Subject) \
dnsbl(yes) \
enabled(false) \
name("DNSBL spam drop rule")
% ----------------- 4 -----------------
WARNING \
src.zone = Untrusted \
service = (SMTP, POP3, SMTPS, POP3S) \
mark_hdr(Subject) \
mark("[SPAM]") \
antispam_usergate(yes) \
enabled(false) \
name("SMTP and POP3 filtering")
Правила reverse-прокси
Префиксы
Имя
Описание
Всегда ОК.
Условия
src.zone
src.geoip
src.ip
src.mac
dst.zone
dst.geoip
dst.ip
user
request.header.User-Agent
url.port
Свойства
name
desc
enabled
rule_log
profile
certificate
cert_auth_enabled
is_https
ssl_profile
rewrite_path
Пример
[reverseproxy "Reverse proxy Rules"]
% ----------------- 1 -----------------
OK \
url.port = 80 \
src.zone = Untrusted \
desc("Example reverse proxy rule. This is an example rule which can be changed or deleted if necessary. ") \
profile("Example reverse proxy server") \
rewrite_path("example.com/path1", "example.local/path1") \
enabled(true) \
name("Example reverse proxy rule")
Правила веб-безопасности
Префиксы
Имя
Описание
Всегда ОК.
Условия
src.zone
src.geoip
src.ip
src.mac
dst.zone
dst.geoip
dst.ip
time
user
Свойства
name
desc
enabled
rule_log
enable_adblock
safe_search
search_history_logging
social_sites_block
enable_injector
custom_injector
url_list_exclusions
Пример
[safebrowsing "Safe browsing Rules"]
% ----------------- 1 -----------------
OK \
rule_log(yes) \
enable_adblock(yes) \
safe_search(yes) \
search_history_logging(yes) \
social_sites_block(yes) \
enable_injector(yes) \
custom_injector(code) \
url_list_exclusions(FISHING_BLACK_LIST) \
desc("Safebrowsing rule for all users. This is an example rule which can be changed or deleted if necessary.") \
enabled(false) \
name("Example safebrowsing")
Правила пропускной способности
Префиксы
Имя
Описание
Всегда ОК.
Условия
src.zone
src.geoip
src.ip
src.mac
dst.zone
dst.geoip
dst.ip
time
user
application
service
scenario
Свойства
name
desc
enabled
rule_log
bandwidth_pool
Пример
[shaper "Shaper Rules"]
% ----------------- 1 -----------------
OK \
scenario = "Example torrent detection scenario" \
service = "HTTP Proxy" \
rule_log(session) \
bandwidth_pool("1 Mbps") \
enabled(true) \
name("Example Bandwidth rule")
% ----------------- 2 -----------------
OK \
scenario = "Example torrent detection scenario" \
src.zone = Trusted \
application = lib.category("Coin Miners", Business) \
rule_log(yes, "3/h", 5) \
bandwidth_pool("100 Kbps") \
enabled(true) \
name("Example torrent shaper")
Правила инспектирования туннелей
Префиксы
Имя
Описание
Всегда ОК.
Условия
src.zone
src.geoip
src.ip
src.mac
dst.zone
dst.geoip
dst.ip
service
Свойства
name
desc
enabled
Пример
[tunnel "Tunnel inspection Rules"]
% ----------------- 1 -----------------
PASS \
src.zone = Trusted \
dst.zone = Untrusted \
service = gre \
enabled(true) \
name("Example Tonnel Incpection Bypass rule")
% ----------------- 2 -----------------
OK \
dst.geoip = YE \
service = gtpu \
enabled(true) \
name("Example Tonnel Incpection Rule")
Правила веб-портала
Префиксы
Имя
Описание
Всегда ОК.
Условия
url
user
url.domain
Свойства
name
desc
enabled
icon
ssl_profile
certificate
additional_url
rdp_check_session_alive
transparent_auth
Пример
[webportal "Web portal Rules"]
% ----------------- 1 -----------------
OK \
user = "CN=Default Group,DC=LOCAL" \
url = "http://www.intranet.loc" \
icon("default.svg") \
rdp_check_session_alive(yes) \
transparent_auth(yes) \
certificate("CA (Default)") \
ssl_profile("Default SSL profile") \
enabled(false) \
name("Example http application published via web portal")
Правила VPN-сервера
Префиксы
Имя
Описание
Всегда ОК.
Условия
src.zone
src.geoip
src.ip
src.mac
dst.geoip
dst.ip
user
Свойства
name
desc
enabled
profile
auth_profile
vpn_network
interface
Пример
[vpn_server "VPN server Rules"]
% ----------------- 1 -----------------
OK \
user = "CN=VPN users,DC=LOCAL" \
src.zone = Untrusted \
profile("Remote access VPN profile") \
auth_profile("Example user auth profile") \
vpn_network("Remote access VPN network") \
interface(tunnel1) \
enabled(false) \
name("Remote access VPN rule")
Правила VPN-клиента
Префиксы
Имя
Описание
Всегда ОК.
Свойства
name
desc
enabled
profile
interface
server_address
last_error
status
— информационное поле, недоступное для редактирования.
Пример
[vpn_client "VPN client Rules"]
% ----------------- 1 -----------------
OK \
server_address("10.10.10.10") \
last_error(Disabled) \
status(disconnected) \
profile("Client VPN profile") \
interface(tunnel3) \
enabled(true) \
name("Client VPN rule")
Правила сценариев
Префиксы
Имя
Описание
Всегда ОК.
Условия
scenario_cond
Свойства
name
desc
enabled
operation_mode
trigger
duration
Условия сценария
Категория URL (url_category)
Условия
category
Свойства
count_interval
max_event_count
scond_type
Обнаружение вируса (virus_detection)
Свойства
scond_type
Приложение (app)
Условия
application
Свойства
count_interval
max_event_count
scond_type
СОВ  (ips)
Свойства
ips_tl
scond_type
Тип котента (mime_type)
Условия
response.header.Content-Type
Свойства
count_interval
max_event_count
scond_type
Размер пакета  (net_packet_size)
Свойства
packet_size
scond_type
Сессий c одного IP  (sessions_per_ip)
Свойства
sessions_limit
scond_type
Объем трафика  (traffic)
Свойства
traffic_limit
period
scond_type
Проверка состояния (health_check)
Условия
url.address
url.domain
Свойства
health_check_method
health_result
health_request_timeout
health_type_request
health_answer_timeout
count_interval
max_event_count
scond_type
Пример
[scenarios "Scenario Rules"]
% ----------------- 1 -----------------
def scenario_cond example_scenario_define
category = (lib.category(Threats), "Advertisements & Pop-Ups") count_interval(10) max_event_count(3) scond_type(url_category)
scond_type(virus_detection)
application = lib.category(Threats) count_interval(2) max_event_count(1) scond_type(app)
ips_tl(medium) scond_type(ips)
response.header.Content-Type = lib.mime("Java script") count_interval(0) max_event_count(0) scond_type(mime_type)
packet_size(200MB) scond_type(net_packet_size)
sessions_limit(50) scond_type(sessions_per_ip)
traffic_limit(2GB) period(hour) scond_type(traffic)
url.address = "192.168.100.100" url.domain = "example.com" health_check_method(dns) \
health_result(negative) health_request_timeout(4) health_type_request(a) \
count_interval(5) max_event_count(3) scond_type(health_check)
url.domain = "example.com" health_check_method(get) \
health_result(negative) health_request_timeout(5) health_answer_timeout(10) \
count_interval(0) max_event_count(0) scond_type(health_check)
end
OK \
scenario_cond = example_scenario_define \
operation_mode(all) \
trigger(one_user) \
duration(5) \
enabled(false) \
name("Example torrent detection scenario")
Правила балансировки нагрузки TCP/UDP
Префиксы
Имя
Описание
Всегда ОК.
Условия
src.zone
src.geoip
src.ip
src.mac
service
url.address
url.port
Свойства
name
desc
enabled
scheduler
real_server
ipvs_fallback
monitor_kind
monitor_service
monitor_request
monitor_response
monitor_interval
monitor_timeout
monitor_failurecount
Пример
[ipvs_server "TCP/UDP load balancing Rules"]
% ----------------- 1 -----------------
OK \
src.geoip = RW \
url.address = 192.168.1.100 \
url.port = 80 \
service = tcp \
scheduler(rr) \
real_server(gate, 1.1.1.1:80, 50) \
ipvs_fallback(masq_snat, 8.8.8.8:10000) \
monitor_kind(negotiate) \
monitor_service(http) \
monitor_request("example.com") \
monitor_interval(60) \
monitor_timeout(60) \
monitor_failurecount(10) \
enabled(true) \
name("TCP load balancing")
Правила балансировки ICAP
Префиксы
Имя
Описание
Всегда ОК.
Свойства
name
desc
enabled
profile
Пример
[icap_balancing "ICAP load balancing Rules"]
% ----------------- 1 -----------------
OK \
profile("Example ICAP server") \
enabled(true) \
name("ICAP load balancing")
Правила балансировки reverse-прокси
Префиксы
Имя
Описание
Всегда ОК.
Свойства
name
desc
enabled
profile
Пример
[reverseproxy_balancing "Reverse proxy load balancing Rules"]
% ----------------- 1 -----------------
OK \
profile("Example reverse proxy server") \
enabled(true) \
name("Reverse-proxy load balancing")
v7.x
Список поддерживаемых HTTP-заголовков

## Источник

https://docs.usergate.com/tipy-pravil_1548.html
