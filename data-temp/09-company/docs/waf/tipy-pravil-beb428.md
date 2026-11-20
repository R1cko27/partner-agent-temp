---
заголовок: Типы правил
url: https://docs.usergate.com/tipy-pravil_3027.html
получено: 2026-11-20 16:24 +0700
продукт: WAF
версия: 7.6.x
раздел: Типы правил
id_статьи: 3027
обновлено: 28 Apr, 2026
ревизия: 3
---

# Типы правил

Содержание:
Экспертные правила временной блокировки IP-адреса
Префиксы
Имя
Описание
DENY
Блокировка IP-адреса
Условия
http.response.code
Свойства
name
enabled
Пример
В примере для конкретного источника (условие
scr.ip
) настроен подсчет количества кодов ответа 404. Если количество таких ответов за последние 30 секунд превысит 10, IP-адрес этого источника будет заблокирован на одну минуту.
def var counter_404
init = 0
window = 00:00:30
key = src.ip
end
def var block
init = 0
window = 00:01:00
key = src.ip
end
DENY var.block = 1.. log_message("Black list") enabled(true) name("Black list")
http.response.code = 404 inc(var.counter_404, 1) log_message("Incriment counter")  enabled(true) name("Incriment counter")
DENY var.counter_404 = 10.. inc(var.block, 1) log_message("Enable block") enabled(true) name("Enable block")
Сетевые правила, настраиваемые с помощью CLI
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
time
url
Свойства
name
desc
enabled
rule_log
reject_with
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
rule_log(yes, "3/h", 5) \
enabled(true) \
name("Allow trusted to untrusted")
Правила публикации
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
request.header.User-Agent
url.port
Свойства
name
desc
enabled
rule_log
profile
certificate
is_https
ssl_profile
waf_profile
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
waf_profile("Example WAF profile") \
enabled(true) \
name("Example reverse proxy rule")
Правила балансировки
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
Список поддерживаемых HTTP-заголовков

## Источник

https://docs.usergate.com/tipy-pravil_3027.html
