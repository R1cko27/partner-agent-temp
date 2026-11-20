---
заголовок: Условия
url: https://docs.usergate.com/usloviya_3022.html
получено: 2026-11-20 16:23 +0700
продукт: WAF
версия: 7.6.x
раздел: Условия
id_статьи: 3022
обновлено: 06 Apr, 2026
ревизия: 8
---

# Условия

Содержание:
Условие (condition) в языке UPL является логической комбинацией триггеров. Триггеры — это отдельные тесты, которые можно выполнить с компонентами запроса, ответа, связанными пользователями или состоянием системы. Все триггеры условия сравниваются со значениями с помощью операторов "=" и "!=". В роли значения могут выступать константные значения, такие как строки, целочисленные значения, диапазоны значений, динамические значения.
Синтаксис
condition ::= condition_name   ('=' | '!=')  condition_value
condition_value ::= pattern | list
list ::= '(' ((pattern ',')* pattern)? ')'
pattern ::= word | string | integer | float | boolean| range | condition_name
string ::= '"' произвольная строка '"'
word ::= [a-zA-Z][0-9a-zA-Z_\-]*
boolean ::= yes|no|true|false
range ::= integer .. [integer] | [integer] .. integer | float .. [float] | [float] .. float
numeric :: = integer | range
http.method
Проверка используемого HTTP-метода. Метод можно указывать как в кавычках, так и без.
Синтаксис
http.method =   GET | CONNECT | DELETE | HEAD | POST | PUT | TRACE | OPTIONS | TUNNEL | LINK | UNLINK | PATCH | PROPFIND | PROPPATCH | MKCOL | COPY | MOVE | LOCK | UNLOCK | MKDIR | INDEX | RMDIR | COPY | MOVE
http.request.version
Проверка версии HTTP-запроса.
Синтаксис
http.request.version = 0.9 | 1.0 | 1.1
http.response.version
Проверка версии HTTP-ответа.
Синтаксис
http.response.version = 0.9 | 1.0 | 1.1
http.response.code
Проверка HTTP-кода ответа. Валидные значения: 100 - 999.
Синтаксис
http.response.code = NNN  %(где NNN число от 100 до 999)
http.request.body, http.request.body.nocase, http.response.body и http.response.body.nocase
Проверка тела запроса/ответа HTTP на содержание определенной сигнатуры.
Пример
DENY http.response.body.nocase = "<title>index of" http.response.body = ">"
http.request.body.re2, http.response.body.re2
Проверка тела HTTP-запроса или HTTP-ответа с использованием регулярных выражений.
Синтаксис
request.body.re2 = string
response.body.re2 = string
Пример:
http.request.body.re2 = "example|test"
request.header.<h_name> и response.header.<h_name>
Проверка HTTP-заголовка запроса/ответа.
h_name
может принимать одно из поддерживаемых значений. Подробнее о поддерживаемых HTTP-заголовках — в разделе «
Список поддерживаемых HTTP-заголовков
Синтаксис
request.header.<h_name>[.base64][.nocase] = string
Пример
DENY url="http://usergate.com" request.header.Pragma="no-cache"
PASS request.header.User-Agent = lib.useragent("Browsers")
PASS request.header.Content-Type = lib.mime("Applications")
DENY request.header.Connection.substring = "Upgrade"
request.header.<h_name>.substring и response.header.<h_name>.substring
Проверка HTTP-заголовка запроса/ответа на вхождение подстроки.
h_name
может принимать одно из поддерживаемых значений. Подробнее о поддерживаемых HTTP-заголовках — в разделе «
Список поддерживаемых HTTP-заголовков
Синтаксис
request.header.<h_name>[.base64]substring[.nocase] = string
Пример
DENY request.header.User-Agent.substring = "curl/"
request.header.<h_name>.regex и response.header.<h_name>.regex
Проверка HTTP-заголовка запроса/ответа на регулярное выражение PCRE.
h_name
может принимать одно из поддерживаемых значений. Подробнее о поддерживаемых HTTP-заголовках — в разделе «
Список поддерживаемых HTTP-заголовков
Синтаксис
request.header.<h_name>[.base64].regex = string
Пример
DENY("Accept only digits in content length") request.header.Content-Length.regex != "[0-9]*"
request.header.<h_name>.re2 и response.header.<h_name>.re2
Проверка HTTP-заголовка запроса/ответа на регулярное выражение RE2.
h_name
может принимать одно из поддерживаемых значений. Подробнее о поддерживаемых HTTP-заголовках — в разделе «
Список поддерживаемых HTTP-заголовков
Синтаксис
request.header.<h_name>[.base64].re2 = string
Пример
DENY("Accept only digits in content length") request.header.Content-Length.re3 != "[0-9]*"
request.header.<h_name>.count и response.header.<h_name>.count
Проверка количества заголовков <
h_name
> в HTTP-запросе/ответе.
h_name
может принимать одно из поддерживаемых значений. Подробнее о поддерживаемых HTTP-заголовках — в разделе «
Список поддерживаемых HTTP-заголовков
Синтаксис
request.header.<h_name>.count = integer | range
Пример
DENY("Too many Host headers") request.header.Host.count = 2..
request.header.<h_name>.length и response.header.<h_name>.length
Проверка длины значений всех заголовков <
h_name
> в HTTP-запросе/ответе.
h_name
может принимать одно из поддерживаемых значений. Подробнее о поддерживаемых HTTP-заголовках — в разделе «
Список поддерживаемых HTTP-заголовков
Синтаксис
request.header.<h_name>.length = integer | range
Пример
DENY("Too much Cookie data") request.header.Cookie.length = 2048..
request.header_names, request.header_values, response.header_names и response.header_values
Проверка имени/значения всех HTTP-заголовков запроса/ответа на значение.
Синтаксис
request.header_values[.base64].regex = string
request.header_values[.base64].re2 = string
request.header_values[.base64].substring[.nocase] = string
request.header_values.count = integer | range
request.header_values.length = integer | range
request.x_header.<xh_name> и response.x_header.<xh_name>
Проверка HTTP-заголовка запроса/ответа на значение.
xh_name
— произвольный HTTP-заголовок.
Синтаксис
request.x_header.<xh_name>[.base64][.nocase] = string
request.x_header.<xh_name>[.base64].regex = string
request.x_header.<xh_name>[.base64].re2 = string
request.x_header.<xh_name>[.base64].substring[.nocase] = string
request.x_header.<xh_name>.count = integer | range
request.x_header.<xh_name>.length = integer | range
Пример
DENY url="http://usergate.com" request.x_header.Test="test1"
Возможны также суффиксы
length
count
regex
re2
как и в случае с <
h_name
DENY("Too much X-Test data") request.x_header.X-Test.length = 2048..
DENY("Too much X-Test2 headers data") request.x_header.X-Test2.count = 2..
PASS request.x_header.Test.regex = "[0-9]*"
request.header.Cookie.<cookie_name>
Проверка заголовка запроса Cookie на значение.
Синтаксис
request.header.Cookie.<cookie_name>[.base64][.(nocase | substring | substring.nocase | regex | re2)] = string
Пример
DENY http.method = POST request.header.Cookie.csrf_token != qparam.CSRF_TOKEN enabled(true) name("Check CSRF")
time, day, hour, minute
Проверка соответствия текущего времени заданному условию. Если не указан суффикс
utc
, время берется локальное, иначе — по Гринвичу.
Синтаксис
day[.utc] = monday | tuesday | wednesday | thursday | friday | saturday | sunday | DD | list
time[.utc] = HH:MM | range | lib.time(<name>)
hour[.utc] = HH | range
minute[.utc] = MM | range
HH ::= 00 - 23
MM ::= 00 - 59
DD ::= 1 - 31
Пример
PASS time = 12:00..13:00  % разрешить каждый день с 12 до 13 часов
PASS time = lib.time("Праздники") % использовать библиотеку "Праздники"
DENY day = (sunday, saturday) % запретить на выходных
DENY day = (monday, 15) hour = 9..18  % запретить каждый понедельник и каждое 15 число месяца с 9 до 18 часов
Открытые интервалы учитываются по границе суток/часа.
PASS hour = 18.. % означает, что разрешено с 18 часов до полуночи
minute = ..10 % первые 10 минут каждого часа
url, url.host и url.address
Проверка url или его части на значение. Проверка использует нормализованный URI c декодированными *
Синтаксис
url[.(prefix | substring | substring.nocase | suffix | regex | re2)] = string
url.host[.(prefix | substring | suffix | regex | re2)] = string
url.domain[.(prefix | substring | suffix | regex | re2)] = string
url.address = ip_address | subnet | subnet_label
url.port = [low_port]..[high_port] | port
url.path[.base64][.(prefix | substring | substring.nocase | suffix | regex | re2)] = string
url.is_absolute = yes | no     % полный или нет URL
prefix ::= string              % начало строки
substring ::= string           % подстрока
suffix ::= string              % окончание строки
regex ::= string               % регулярное выражение PCRE
re2 ::= string                 % регулярное выражение RE2
url.address
— это, по сути, синоним
dst.ip
Пример
DENY url.path.base64.re2 = "(?i)\bondisconnecting\W*=" enabled(true) name("ondisconnecting (URI)")
qparam.<name>, qparam.values и qparam.names
Проверка значения параметров запроса. Проверка использует имена и значения параметров c декодированными *
Синтаксис
qparam.length = numeric     % проверить общую длину query-параметров
qparam.count = numeric   % проверить количество query-параметров
qparam.<name>[.(length | count)] = numeric   % Проверить длину/количество query-параметров <name>
qparam.<name>[.base64][.(nocase | substring | substring.nocase | regex | re2)] = string   %
проверить имя <name> на вхождение подстроки/регулярные выражения
qparam.values[.base64].substring[.nocase] = string   % проверить все значения на вхождение подстроки
qparam.names[.base64].substring[.nocase] = string   % проверить все имена на вхождение подстроки
qparam.values[.base64].regex = string   % проверить все значения на регулярное выражение
qparam.names[.base64].regex = string   % проверить все имена на регулярные выражения
qparam.values[.base64].re2 = string   % проверить все значения на регулярное выражение
qparam.names[.base64].re2 = string   % проверить все имена на регулярные выражения
numeric ::= integer | range   % число либо диапазон
qparam.values.length = numeric   % проверить длину всех значений
qparam.names.length = numeric   % проверить длину всех имен
regex ::= string   % регулярное выражение PCRE
re2 ::= string   % регулярное выражение RE2
Пример
DENY("limit arguments total length") qparam.length = 1024..                 % total
DENY("Limit argument value length") qparam.values.length = 1024..           % for each
DENY("Limit argument name length") qparam.names.length = 1024..             % for each
DENY("Maximum number of arguments in request limited") qparam.count  = 12.. % total
DENY("PHP injection attempt") qparam.values.base64.substring.nocase = "${@print"
src и dst
Проверка условия на IP-адрес, зону или GeoIP источника/назначения.
Синтаксис
src.ip = ip_address | subnet | subnet_label | list | lib
dst.ip = ip_address | subnet | subnet_label | list | lib
src.zone = integer | zone_name
dst.zone = integer | zone_name
src.geoip = iso3166 | list
dst.geoip = iso3166 | list
src.mac = mac_address | list
dst.mac = mac_address | list
lib ::= lib.(network | url) '(' list_libs ')'
list_libs :: = lib_name ','' list_libs
lib_name ::= word | string
iso3166 ::= [A-Z][A-Z]
url.address
— это, по сути, синоним
dst.ip
response_time
Проверка времени ответа в миллисекундах.
Синтаксис
response_time = integer
v7.x
Общие положения
Встроенные библиотеки

## Источник

https://docs.usergate.com/usloviya_3022.html
