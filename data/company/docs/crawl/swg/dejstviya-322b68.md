---
заголовок: Действия
url: https://docs.usergate.com/dejstviya_2701.html
источник: портал документации
получено: 2026-11-20 16:25 +0700
продукт: SWG
версия: 7.5.x
раздел: Действия
id_статьи: 2701
обновлено: 23 Mar, 2026
ревизия: 5
---

# Действия

Содержание:
Действие (
action
) — это то, что будет выполнено, если условия в правиле истинны. В качестве параметров могут использоваться константные значения, или динамические значение там, где это предусмотрено.
Синтаксис
action = action_name | action_name '(' list_params ')'
action_name ::= warning | log_message | append | delete | set | replace | encrypt | inc|dec | reset | redirect | encrypt_body_url | decrypt_path | body_inject | set_cookie_token | body_replace | lookup_and_auth | encode_cookie | decode_cookie | sma | nat | dnat | route | port_mapping | netmap | forward | ignore | action_label
action_label ::= 'action'.<action_label_name>
action_label_name ::= atom
list_params ::= value ',' list_params
warning
Действия, которые разрешаются без выхода из обработки правил на текущем слое.
warning
ставит отметку о том, что необходимо вставить код с предупреждением в тело ответа.
Пример
category = lib.category(Productivity) warning
DENY user = user1
log_message
Записать сообщения в журнал.
Пример
DENY category = lib.category(Productivity) log_message("Deny porno")
append
Добавить заголовок к HTTP-запросу/ответу. Список поддерживаемых заголовков приведен в
Приложении
Первый параметр может быть опущен, если заголовок относится к одной группе
request
или
response
Синтаксис
append([request | response,] <headername>, value)
headername
— см. в
Приложении
value ::= string | numeric | condition_name.
set
Переписать значение конкретному HTTP-заголовку. Список поддерживаемых заголовков см. в
Приложении
Первый параметр может быть опущен, если заголовок относится к одной группе
request
или
response
Синтаксис
set([request | response,] <headername>, value)
headername
— см. в
Приложении
value ::= string | numeric | condition_name.
delete
Удалить HTTP-заголовок. Список поддерживаемых заголовков см. в
Приложении
Первый параметр может быть опущен, если заголовок относится к одной группе
request
или
response
Синтаксис
delete([request | response,] <headername>)
headername
— см. в
Приложении
replace
Модифицировать значение HTTP-заголовка. Список поддерживаемых заголовков см. в
Приложении
Первый параметр может быть опущен, если заголовок относится к одной группе
request
или
response
Синтаксис
replace([request | response,] <headername>, regex, value)
regex ::= string               %
регулярное выражение
value ::= string | condition_name
headername
— см. в
Приложении
Пример 1
Добавить заголовок Referer:
PASS append(Referer, "http://example.com") enabled(true)
Удалить заголовок:
PASS delete(Referer)
Переписать заголовок:
PASS set(request, Cache-Control, no-cache)
Модифицировать заголовок Location:
PASS response.header.Location.count = 1.. replace(response, Location, "http://example.com", url.host) enabled(true)
Пример 2
define action delete_referer
log_message("Referer header deleted")
delete(request, Referer)
end
encrypt
Шифровать часть пути в HTTP-заголовке. Список поддерживаемых заголовков см. в
Приложении
Первый параметр может быть опущен, если заголовок относится к одной группе
request
или
response
Ключ шифрования и флаг "Использовать IP как часть ключа шифрования" — необязательные параметры.
Синтаксис
encrypt([request | response,] <headername>, <url>[, <user_key>[, <add_ip>]])
url ::= string               %
часть url для фильтрации
user_key ::= string          %
пользовательский ключ шифрования (необязательный параметр)
add_ip ::= boolean           %
добавлять ли IP к ключу шифрования (логическое значение, необязательный параметр)
boolean ::= yes | no | true | false
headername
— см. в
Приложении
encrypt_body_url
Шифровать часть пути в ссылках тела ответа.
Ключ шифрования и флаг "Использовать IP как часть ключа шифрования"  — необязательные параметры.
Синтаксис
encrypt_body_url(<url>[, <user_key>[, <add_ip>]])
url ::= string               %
часть url для фильтрации
user_key ::= string          %
пользовательский ключ шифрования (необязательный параметр)
add_ip ::= boolean           %
добавлять ли IP к ключу шифрования (логическое значение, необязательный параметр)
boolean ::= yes | no | true | false
decrypt_path
Дешифровать часть пути запроса.
Первый параметр может быть опущен, если заголовок относится к одной группе
request
или
response
Ключ шифрования и флаг "Использовать IP как часть ключа шифрования"  — необязательные параметры.
Синтаксис
decrypt_path(<path>[, <user_key>[, <add_ip>]])
path ::= string              % часть пути для фильтрации
user_key ::= string          % пользовательский ключ шифрования (необязательный параметр)
add_ip ::= boolean           % добавлять ли IP к ключу шифрования (логическое значение, необязательный параметр)
boolean ::= yes | no | true | false
Пример
Шифровать все относительные пути в заголовке
Location
и теле ответа, и дешифровать путь запроса:
decrypt_path("/", "User_Key", true) enabled(true) name("Path decode")
http.response.code = 302 encrypt(Location, "/", "User_Key", true) enabled(true) name("Encrypt Location header")
encrypt_body_url("/", "User_Key", true) enabled(true) name("Encrypt all relative URL")
body_inject
Вставить скрипт в тело ответа.
Синтаксис
body_inject(inject_text)
inject_text ::= string
set_cookie_token
Добавить в ответ заголовок 'Set-Cookie' со сгенерированным токеном.
Синтаксис
set_cookie_token(cookie_name, parameter, expires_date)
cookie_name ::= string
parameter ::= string
expires_date ::= [DD_]HH:MM   %
время которое будет прибавлено к текущему времени
Пример
Реализация CSRF защиты:
DENY http.method = POST request.header.Referer.substring = "/login.php" qparam.UCSRF_TOKEN != request.header.Cookie.ucsrf_token enabled(true) name("Check CSRF")
url.path.prefix = "/login.php" set_cookie_token(ucsrf_token, "path=/", 01_00:00) body_inject("<script language='JavaScript'>
var tokenName = 'UCSRF_TOKEN';
document.addEventListener('DOMContentLoaded', function()
var t_res = document.cookie.match(/ucsrf_token=(.+?)(;|$)/);
var tokenValue = t_res ? t_res[1] : '';
var forms = document.getElementsByTagName('form');
for(i=0; i<forms.length; i++)
var html = forms[i].innerHTML;
html += '<input type=hidden name=' + tokenName + ' value=' + tokenValue + ' />';
forms[i].innerHTML = html;
});
</script>") enabled(true) name("Inject")
encode_cookie
Шифровать значения Cookie в заголовке
Set-Cookie
с заданным именем.
Синтаксис
encode_cookie(cookie_name[, condition_name][, user_kry_string][, f_encrypt])
cookie_name ::= string
condition_name                    %
условие используемое для кодирования (по умолчанию src.ip)
user_kry_string ::= string        %
пользовательский ключ шифрования (по умолчанию "")
f_encrypt := true                 %
необходимо шифрование  (по умолчанию false)
decode_cookie
Дешифровать токен в заголовке Cookie с заданным именем.
Синтаксис
decode_cookie(cookie_name[, condition_key][, user_kry_string][, f_decript])
cookie_name ::= string
condition_name                    %
условие используемое для декодирования (по умолчанию src.ip)
user_kry_string ::= string        %
пользовательский ключ шифрования (по умолчанию "")
f_encrypt := true                 %
необходимо шифрование  (по умолчанию false)
Пример
Шифрование и дешифрование Cookie с именем
security:
response.header.Set-Cookie.count != 0 encode_cookie("security", src.ip, true) enabled(true) name("encode_cookie")
request.header.Cookie.count != 0 decode_cookie("security", src.ip, true) enabled(true) name("decode_cookie")
body_replace
Модифицировать тело ответа. Выполняется не более двух (первых) модификаций для каждого ответа.
Синтаксис
body_replace(<regex>, <value>)
regex ::= string               %
регулярное выражение
value ::= string
Пример
PASS \
body_replace("(\\+7|8)[\\s(]?(\\d\{3})[\\s)]?(\\d\{3})[\\s-]?(\\d\{2})[\\s-]?(\\d\{2})", "+\\1 (\\2) \\3-XX-XX") \
body_replace("(\\w{1})[\\w\.]*(\\w{1})@([\\w]+)\\.([\\w]+)", "\\1***\\2@\\3.\\4") \
enabled(true) \
name("Replace mail and phone")
lookup_and_auth
Аутентифицировать пользователя. В случае если IP не указан, запрос маркируется имением пользователя.
Синтаксис
lookup_and_auth(<user_login>[, <ip_address>[, <session_timeout>]])
user_login ::= string | condition_name    %
Логин аутентификации
ip_address ::= string | condition_name    %
IP адрес
session_timeout ::= integer               %
тайм-аут сессии, по умолчанию 0.
Пример
lookup_and_auth(request.x_header.X-Authenticated-User, request.x_header.X-Forwarded-For, 300) enabled(true) name("User authentication")
lookup_and_auth(request.x_header.X-Authenticated-User) enabled(true) name("Mark request")
redirect
При блокировке перенаправить пользователя на адрес, который указан в редиректе.
Синтаксис
Redirect ::= redirect(RespCode[, RedirectText], Url)
RespCode ::= 301 | 302 | 305 | 307
RedirectText ::= string
Url ::= string
Пример
DENY src.zone = Trusted redirect(302, "Custom test (Moved)", "https://block.captive/block")
DENY src.zone = Untrusted redirect(302, "https://block.captive/block")
inc и dec
Используются для изменения значения переменных, объявленных как
def var
Синтаксис
inc(var.<var_name>, integer)
dec(var.<var_name>, integer)
Пример
На каждый
http.response.code = 500
увеличивается значение
rps
на 1. Если превысили 10 таких запросов за 5 минут, блокируем дальнейшие ответы. Через 5 минут переменная
rps
будет сброшена в 0:
def var rps
init = 0
window = 00:05
key = src.ip
end
http.response.code = 500 var.rps=..10 inc(var.rps, 1) enabled(true)
PASS var.rps = 5 log_message("Warning!") enabled(true)
DENY var.rps=11.. log_message("Too many 500 errors!") enabled(true)
reset
Сбросить значения переменных, объявленных как
init
def var
в начальное значение.
Синтаксис
reset(var.<var_name>)
sma
Используются для подсчета среднего значения в окне времени, которое определяется в переменной как
window
def var
Синтаксис
sma(var.<var_name>, integer)
Пример
Блокируются запросы, когда среднее время запроса за 30-секундный интервал превысит 2 секунды:
def var avg_time
init = 0
window = 00:00:30
key = src.ip
end
src.zone = Untrusted sma(var.avg_time, response_time) enabled(true) name("sma")
DENY src.zone = Untrusted var.avg_time = 2000.. enabled(true) name("sma res")
nat
NAT — подмена сетевых IP-адресов.
Пример
PASS src.zone = Trusted dst.zone = Untrusted nat
dnat
DNAT — подмена IP-адреса назначения.
Пример
PASS dnat target_ip("192.168.1.20")
port_mapping
Порт-форвардинг — перенаправление трафика на указанный IP-адрес c изменением номера порта публикуемого сервиса.
Пример
PASS port_mapping target_ip("192.168.1.20") port_map(tcp, 2000, 2001)
netmap
Network mapping — позволяет произвести замену IP-адресов источника или назначения одной сети на другую.
Пример
PASS netmap target_ip("192.168.32.0/24") direction(output)
route
Policy-based routing — позволяет маршрутизировать IP-пакеты на основе расширенной информации, например, сервисов, MAC-адресов или серверов (IP-адресов).
SNAT IP — Адрес, на который будет заменен адрес источника для трафика NAT.
Пример
PASS service = HTTP route getway(Шлюз1)
ignore
Игнорировать ответ от ICAP-сервера. В этом случае, вне зависимости от ответа ICAP-сервера, данные к пользователю уходят без модификации.
Пример
OK profile("Example ICAP server") enabled(true) name("ICAP rule") ignore
forward
Переслать. В случае успешной расшифровки трафика SSL/TLS копия трафика будет переслана в соответствии с правилом и профилем инспектирования SSL.
Пример
OK url = lib.url(ZAPRET_INFO_BLACK_LIST_DOMAIN)ssl_profile("Default SSL profile") ssl_forward_profile("Forward SSL profile") enabled(false) name("Decrypt rule") forward
v7.x
Свойства
Типы правил

## Источник

https://docs.usergate.com/dejstviya_2701.html
